"""
TJES PJE MCP Server
===================

Servidor MCP para acesso autenticado à API do PJE (Processo Judicial Eletrônico)
do Tribunal de Justiça do Espírito Santo.

Características:
- Autenticação com certificados digitais A1/A3
- 8 ferramentas MCP especializadas
- Suporte a operações autenticadas do PJE
- Gerenciamento robusto de certificados
- Retry logic e error handling

Autor: Claude Code
Licença: MIT
"""

import asyncio
import json
import logging
import os
import tempfile
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum

import httpx
from mcp.server.fastmcp import FastMCP
from tenacity import retry, stop_after_attempt, wait_exponential

from .cert_manager import (
    CertificateManager,
    CertificateError,
    load_certificate_from_env
)
from .session_manager import (
    SessionManager,
    PlaywrightSessionHelper,
    get_default_session_manager,
    format_session_info_detailed
)

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("tjes-pje-mcp")

# Inicializar FastMCP
mcp = FastMCP(
    name="TJES PJE",
    instructions="Servidor MCP para PJE do TJES com autenticação por certificado digital"
)

# Função auxiliar para validação de variáveis de ambiente numéricas
def get_int_env(var_name: str, default: int, min_value: int = 1, max_value: int = None) -> int:
    """
    Obtém variável de ambiente inteira com validação robusta

    Args:
        var_name: Nome da variável de ambiente
        default: Valor padrão se não configurado
        min_value: Valor mínimo permitido
        max_value: Valor máximo permitido (opcional)

    Returns:
        Valor inteiro validado
    """
    value_str = os.getenv(var_name)

    if value_str is None:
        return default

    try:
        value = int(value_str)

        # Validar limites
        if value < min_value:
            logger.warning(
                f"{var_name}={value} é menor que o mínimo permitido ({min_value}). "
                f"Usando {min_value}."
            )
            return min_value

        if max_value is not None and value > max_value:
            logger.warning(
                f"{var_name}={value} é maior que o máximo permitido ({max_value}). "
                f"Usando {max_value}."
            )
            return max_value

        return value

    except (ValueError, TypeError) as e:
        logger.warning(
            f"{var_name}='{value_str}' não é um número válido. "
            f"Usando valor padrão: {default}. Erro: {e}"
        )
        return default


# Configurações
PJE_BASE_URL = os.getenv("PJE_BASE_URL", "https://sistemas.tjes.jus.br/pje")
PJE_2G_BASE_URL = os.getenv("PJE_2G_BASE_URL", "https://sistemas.tjes.jus.br/pje2g")
TIMEOUT = get_int_env("PJE_TIMEOUT_SECONDS", default=60, min_value=5, max_value=300)
RETRY_ATTEMPTS = get_int_env("PJE_RETRY_ATTEMPTS", default=3, min_value=1, max_value=10)

# Gerenciador de certificados global
cert_manager: Optional[CertificateManager] = None
cert_files: Optional[tuple] = None  # (cert_path, key_path) temporários


class TipoDocumento(str, Enum):
    """Tipos de documentos do PJE"""
    PETICAO_INICIAL = "1"
    PROCURACAO = "2"
    DOCUMENTO_PESSOAL = "3"
    CONTESTACAO = "4"
    SENTENCA = "5"
    ACORDAO = "6"
    OUTRO = "99"


class SituacaoProcesso(str, Enum):
    """Situações do processo"""
    ATIVO = "1"
    BAIXADO = "2"
    SUSPENSO = "3"
    ARQUIVADO = "4"


# ========================================
# Inicialização e gerenciamento de certificados
# ========================================

def initialize_certificate() -> None:
    """
    Inicializa o gerenciador de certificados a partir das variáveis de ambiente

    Raises:
        CertificateError: Se houver erro ao carregar certificado
    """
    global cert_manager, cert_files

    logger.info("Inicializando gerenciador de certificados...")

    try:
        cert_manager = load_certificate_from_env()

        # Validar certificado
        is_valid, message = cert_manager.validate_certificate()
        logger.info(f"Status do certificado: {message}")

        if not is_valid:
            logger.error(f"Certificado inválido: {message}")
            raise CertificateError(message)

        # Obter info do certificado
        info = cert_manager.get_certificate_info()
        logger.info(f"Certificado carregado: {info.subject}")
        logger.info(f"Válido até: {info.not_valid_after.date()}")
        logger.info(f"Dias até expiração: {info.days_until_expiry}")

        # Para certificados A1, criar arquivos temporários para httpx
        if cert_manager.cert_type == "A1":
            cert_files = cert_manager.get_cert_and_key_for_requests()
            logger.info("Arquivos temporários de certificado criados")

    except Exception as e:
        logger.exception("Erro ao inicializar certificado")
        raise CertificateError(f"Falha ao inicializar certificado: {str(e)}") from e


def cleanup_certificate() -> None:
    """
    Limpa recursos do certificado (arquivos temporários)
    """
    global cert_files

    if cert_files:
        cert_path, key_path = cert_files
        try:
            if os.path.exists(cert_path):
                os.unlink(cert_path)
            if os.path.exists(key_path):
                os.unlink(key_path)
            logger.info("Arquivos temporários de certificado removidos")
        except Exception as e:
            logger.warning(f"Erro ao remover arquivos temporários: {e}")
        finally:
            cert_files = None


# ========================================
# Funções auxiliares de API
# ========================================

@retry(
    stop=stop_after_attempt(RETRY_ATTEMPTS),
    wait=wait_exponential(multiplier=1, min=2, max=30)
)
async def fazer_requisicao_pje(
    endpoint: str,
    method: str = "GET",
    params: Optional[Dict] = None,
    json_data: Optional[Dict] = None,
    base_url: Optional[str] = None
) -> Dict[str, Any]:
    """
    Faz requisição autenticada à API do PJE

    Args:
        endpoint: Endpoint da API (ex: "/api/v1/processos")
        method: Método HTTP (GET, POST, etc.)
        params: Parâmetros de query string
        json_data: Dados JSON para POST/PUT
        base_url: URL base customizada (opcional)

    Returns:
        Resposta da API em formato dict

    Raises:
        httpx.HTTPError: Em caso de erro na requisição
        CertificateError: Se certificado não estiver inicializado
    """
    if cert_manager is None:
        raise CertificateError("Certificado não inicializado. Execute initialize_certificate() primeiro")

    if cert_files is None and cert_manager.cert_type == "A1":
        raise CertificateError("Arquivos de certificado não disponíveis")

    url_base = base_url or PJE_BASE_URL
    url = f"{url_base}{endpoint}"

    logger.info(f"Requisição PJE: {method} {endpoint}")

    # Configurar cliente HTTP com certificado
    if cert_manager.cert_type == "A1":
        cert_path, key_path = cert_files
        cert_config = (cert_path, key_path)
    else:
        # A3 - usar certificado do Windows Store (mais complexo)
        logger.warning("Certificado A3 - suporte limitado via httpx")
        cert_config = None

    async with httpx.AsyncClient(
        cert=cert_config,
        verify=True,
        timeout=TIMEOUT,
        follow_redirects=True
    ) as client:
        try:
            response = await client.request(
                method=method,
                url=url,
                params=params,
                json=json_data
            )

            response.raise_for_status()

            # Tentar parsear JSON
            try:
                return response.json()
            except json.JSONDecodeError:
                # Se não for JSON, retornar texto
                return {"content": response.text, "status_code": response.status_code}

        except httpx.HTTPStatusError as e:
            logger.error(f"Erro HTTP {e.response.status_code}: {e.response.text}")

            # Retry para erros 5xx
            if 500 <= e.response.status_code < 600:
                logger.info("Erro de servidor, tentando novamente...")
                raise

            # Não retry para erros 4xx
            return {
                "error": True,
                "status_code": e.response.status_code,
                "message": e.response.text
            }

        except httpx.TimeoutException:
            logger.error(f"Timeout após {TIMEOUT} segundos")
            raise

        except Exception as e:
            logger.exception("Erro na requisição PJE")
            raise


def formatar_processo_pje(processo: Dict[str, Any]) -> str:
    """
    Formata dados do processo PJE para exibição

    Args:
        processo: Dicionário com dados do processo

    Returns:
        String formatada
    """
    numero = processo.get('numeroProcesso', 'N/A')
    classe = processo.get('classe', {}).get('nome', 'N/A')
    orgao = processo.get('orgaoJulgador', {}).get('nome', 'N/A')
    situacao = processo.get('situacao', 'N/A')
    data_autuacao = processo.get('dataAutuacao', 'N/A')

    partes = processo.get('partes', [])
    partes_str = '\n'.join([
        f"  • {p.get('tipoParticipacao', 'Parte')}: {p.get('nome', 'N/A')}"
        for p in partes[:5]
    ]) if partes else "  Não informado"

    return f"""
╔══════════════════════════════════════════════════════════════
║ 📁 Processo: {numero}
╠══════════════════════════════════════════════════════════════
║ Classe: {classe}
║ Órgão Julgador: {orgao}
║ Situação: {situacao}
║ Data Autuação: {data_autuacao}
║
║ Partes:
{partes_str}
╚══════════════════════════════════════════════════════════════
""".strip()


# ========================================
# Ferramentas MCP
# ========================================

@mcp.tool()
async def pje_certificate_status() -> str:
    """
    Verifica o status do certificado digital

    Returns:
        Status detalhado do certificado incluindo validade e dias para expiração
    """
    try:
        if cert_manager is None:
            initialize_certificate()

        info = cert_manager.get_certificate_info()
        is_valid, message = cert_manager.validate_certificate()

        status_icon = "✅" if is_valid else "❌"

        resultado = f"""
{status_icon} Status do Certificado Digital
{'=' * 70}

Tipo: {info.cert_type}
Subject: {info.subject}
Emissor: {info.issuer}
Serial: {info.serial_number}

Validade:
  Válido desde: {info.not_valid_before.strftime('%d/%m/%Y %H:%M:%S')}
  Válido até: {info.not_valid_after.strftime('%d/%m/%Y %H:%M:%S')}
  Dias até expiração: {info.days_until_expiry} dias

Thumbprint (SHA-1): {info.thumbprint}

Status: {message}
"""
        return resultado.strip()

    except Exception as e:
        logger.exception("Erro ao verificar status do certificado")
        return f"❌ Erro ao verificar certificado: {str(e)}"


@mcp.tool()
async def pje_search_process(numero_processo: str, grau: str = "1") -> str:
    """
    Busca processo no PJE pelo número

    Args:
        numero_processo: Número do processo (formato CNJ)
        grau: Grau de jurisdição ("1" ou "2")

    Returns:
        Informações detalhadas do processo

    Examples:
        >>> await pje_search_process("0000166-19.2023.8.08.0035", grau="1")
    """
    try:
        # Inicializar certificado se necessário
        if cert_manager is None:
            initialize_certificate()

        # Escolher URL base
        base_url = PJE_2G_BASE_URL if grau == "2" else PJE_BASE_URL

        # Endpoint de busca (ajustar conforme API real do TJES)
        endpoint = f"/api/v1/processos/{numero_processo}"

        # Fazer requisição
        resposta = await fazer_requisicao_pje(
            endpoint=endpoint,
            method="GET",
            base_url=base_url
        )

        if resposta.get("error"):
            return f"❌ Erro ao buscar processo: {resposta.get('message', 'Erro desconhecido')}"

        # Formatar resultado
        resultado = f"🔍 Busca de Processo - {grau}º Grau\n\n"
        resultado += formatar_processo_pje(resposta)

        # Adicionar JSON completo
        resultado += "\n\n📋 Dados completos (JSON):\n"
        resultado += json.dumps(resposta, indent=2, ensure_ascii=False)

        return resultado

    except CertificateError as e:
        return f"❌ Erro de certificado: {str(e)}"
    except Exception as e:
        logger.exception("Erro ao buscar processo")
        return f"❌ Erro ao buscar processo: {str(e)}"


@mcp.tool()
async def pje_list_processes(
    orgao_julgador: Optional[str] = None,
    classe: Optional[str] = None,
    limit: int = 10,
    grau: str = "1"
) -> str:
    """
    Lista processos com filtros

    Args:
        orgao_julgador: Código do órgão julgador (opcional)
        classe: Código da classe processual (opcional)
        limit: Número máximo de resultados
        grau: Grau de jurisdição ("1" ou "2")

    Returns:
        Lista de processos encontrados
    """
    try:
        if cert_manager is None:
            initialize_certificate()

        base_url = PJE_2G_BASE_URL if grau == "2" else PJE_BASE_URL

        # Construir parâmetros
        params = {"size": min(limit, 100)}

        if orgao_julgador:
            params["orgaoJulgador"] = orgao_julgador

        if classe:
            params["classe"] = classe

        # Endpoint de listagem
        endpoint = "/api/v1/processos"

        # Fazer requisição
        resposta = await fazer_requisicao_pje(
            endpoint=endpoint,
            method="GET",
            params=params,
            base_url=base_url
        )

        if resposta.get("error"):
            return f"❌ Erro ao listar processos: {resposta.get('message')}"

        # Processar resultados
        processos = resposta.get("result", [])
        total = resposta.get("page-info", {}).get("count", len(processos))

        resultado = f"📋 Listagem de Processos - {grau}º Grau\n"
        resultado += f"Total encontrado: {total} (mostrando {len(processos)})\n\n"

        for i, proc in enumerate(processos, 1):
            resultado += f"\n{'=' * 70}\n"
            resultado += f"Processo {i}/{len(processos)}\n"
            resultado += formatar_processo_pje(proc)
            resultado += "\n"

        return resultado

    except Exception as e:
        logger.exception("Erro ao listar processos")
        return f"❌ Erro: {str(e)}"


@mcp.tool()
async def pje_get_movements(numero_processo: str, grau: str = "1") -> str:
    """
    Consulta movimentações de um processo

    Args:
        numero_processo: Número do processo
        grau: Grau de jurisdição ("1" ou "2")

    Returns:
        Lista de movimentações do processo
    """
    try:
        if cert_manager is None:
            initialize_certificate()

        base_url = PJE_2G_BASE_URL if grau == "2" else PJE_BASE_URL
        endpoint = f"/api/v1/processos/{numero_processo}/movimentacoes"

        resposta = await fazer_requisicao_pje(
            endpoint=endpoint,
            method="GET",
            base_url=base_url
        )

        if resposta.get("error"):
            return f"❌ Erro: {resposta.get('message')}"

        movimentos = resposta.get("result", [])

        resultado = f"📊 Movimentações do Processo {numero_processo}\n"
        resultado += f"Total: {len(movimentos)} movimentações\n\n"

        for i, mov in enumerate(movimentos, 1):
            data = mov.get('dataHora', 'N/A')
            descricao = mov.get('nome', 'N/A')
            resultado += f"{i}. [{data}] {descricao}\n"

        return resultado

    except Exception as e:
        logger.exception("Erro ao consultar movimentações")
        return f"❌ Erro: {str(e)}"


@mcp.tool()
async def pje_list_documents(numero_processo: str, grau: str = "1") -> str:
    """
    Lista documentos de um processo

    Args:
        numero_processo: Número do processo
        grau: Grau de jurisdição ("1" ou "2")

    Returns:
        Lista de documentos do processo
    """
    try:
        if cert_manager is None:
            initialize_certificate()

        base_url = PJE_2G_BASE_URL if grau == "2" else PJE_BASE_URL
        endpoint = f"/api/v1/processos/{numero_processo}/documentos"

        resposta = await fazer_requisicao_pje(
            endpoint=endpoint,
            method="GET",
            base_url=base_url
        )

        if resposta.get("error"):
            return f"❌ Erro: {resposta.get('message')}"

        documentos = resposta.get("result", [])

        resultado = f"📄 Documentos do Processo {numero_processo}\n"
        resultado += f"Total: {len(documentos)} documentos\n\n"

        for i, doc in enumerate(documentos, 1):
            tipo = doc.get('tipoDocumento', {}).get('nome', 'N/A')
            descricao = doc.get('descricao', 'N/A')
            data = doc.get('dataInclusao', 'N/A')
            id_doc = doc.get('id', 'N/A')

            resultado += f"""
{i}. Documento ID: {id_doc}
   Tipo: {tipo}
   Descrição: {descricao}
   Data: {data}
   {'─' * 65}
"""

        return resultado

    except Exception as e:
        logger.exception("Erro ao listar documentos")
        return f"❌ Erro: {str(e)}"


@mcp.tool()
async def pje_list_classes(grau: str = "1") -> str:
    """
    Lista classes processuais disponíveis

    Args:
        grau: Grau de jurisdição ("1" ou "2")

    Returns:
        Lista de classes processuais
    """
    try:
        if cert_manager is None:
            initialize_certificate()

        base_url = PJE_2G_BASE_URL if grau == "2" else PJE_BASE_URL
        endpoint = "/api/v1/classes"

        resposta = await fazer_requisicao_pje(
            endpoint=endpoint,
            method="GET",
            base_url=base_url
        )

        if resposta.get("error"):
            return f"❌ Erro: {resposta.get('message')}"

        classes = resposta.get("result", [])

        resultado = f"📑 Classes Processuais - {grau}º Grau\n"
        resultado += f"Total: {len(classes)} classes\n\n"

        for classe in classes[:50]:  # Limitar a 50 para não sobrecarregar
            codigo = classe.get('codigo', 'N/A')
            nome = classe.get('nome', 'N/A')
            resultado += f"{codigo:>6} - {nome}\n"

        if len(classes) > 50:
            resultado += f"\n... e mais {len(classes) - 50} classes"

        return resultado

    except Exception as e:
        logger.exception("Erro ao listar classes")
        return f"❌ Erro: {str(e)}"


@mcp.tool()
async def pje_list_organs(grau: str = "1") -> str:
    """
    Lista órgãos julgadores disponíveis

    Args:
        grau: Grau de jurisdição ("1" ou "2")

    Returns:
        Lista de órgãos julgadores
    """
    try:
        if cert_manager is None:
            initialize_certificate()

        base_url = PJE_2G_BASE_URL if grau == "2" else PJE_BASE_URL
        endpoint = "/api/v1/orgaos-julgadores"

        resposta = await fazer_requisicao_pje(
            endpoint=endpoint,
            method="GET",
            base_url=base_url
        )

        if resposta.get("error"):
            return f"❌ Erro: {resposta.get('message')}"

        orgaos = resposta.get("result", [])

        resultado = f"🏛️  Órgãos Julgadores - {grau}º Grau\n"
        resultado += f"Total: {len(orgaos)} órgãos\n\n"

        for orgao in orgaos:
            codigo = orgao.get('codigo', 'N/A')
            nome = orgao.get('nome', 'N/A')
            resultado += f"{codigo:>6} - {nome}\n"

        return resultado

    except Exception as e:
        logger.exception("Erro ao listar órgãos")
        return f"❌ Erro: {str(e)}"


@mcp.tool()
async def pje_list_subjects(grau: str = "1") -> str:
    """
    Lista assuntos processuais disponíveis

    Args:
        grau: Grau de jurisdição ("1" ou "2")

    Returns:
        Lista de assuntos
    """
    try:
        if cert_manager is None:
            initialize_certificate()

        base_url = PJE_2G_BASE_URL if grau == "2" else PJE_BASE_URL
        endpoint = "/api/v1/assuntos"

        resposta = await fazer_requisicao_pje(
            endpoint=endpoint,
            method="GET",
            base_url=base_url
        )

        if resposta.get("error"):
            return f"❌ Erro: {resposta.get('message')}"

        assuntos = resposta.get("result", [])

        resultado = f"📚 Assuntos Processuais - {grau}º Grau\n"
        resultado += f"Total: {len(assuntos)} assuntos\n\n"

        for assunto in assuntos[:50]:  # Limitar a 50
            codigo = assunto.get('codigo', 'N/A')
            nome = assunto.get('nome', 'N/A')
            resultado += f"{codigo:>6} - {nome}\n"

        if len(assuntos) > 50:
            resultado += f"\n... e mais {len(assuntos) - 50} assuntos"

        return resultado

    except Exception as e:
        logger.exception("Erro ao listar assuntos")
        return f"❌ Erro: {str(e)}"


# ========================================
# Ferramentas MCP - Gerenciamento de Sessão
# (Para Safe ID e certificados em nuvem)
# ========================================

@mcp.tool()
async def pje_check_session() -> str:
    """
    Verifica status da sessão autenticada do PJE (Playwright)

    Útil para certificados em nuvem (Safe ID, etc.) que usam autenticação via browser.
    A sessão é persistida entre execuções para evitar re-autenticação.

    Returns:
        Status detalhado da sessão incluindo validade e idade

    Examples:
        >>> await pje_check_session()
        # Retorna se sessão está ativa ou se precisa autenticar
    """
    try:
        session_manager = get_default_session_manager()
        session_info = session_manager.get_session_info()

        # Formatar informações detalhadas
        resultado = format_session_info_detailed(session_info)

        # Adicionar instruções se sessão inválida
        if not session_info['valid']:
            helper = PlaywrightSessionHelper()
            resultado += "\n\n" + helper.get_session_status_message(session_info)

        return resultado

    except Exception as e:
        logger.exception("Erro ao verificar sessão")
        return f"❌ Erro ao verificar sessão: {str(e)}"


@mcp.tool()
async def pje_authenticate_safe_id() -> str:
    """
    Inicia processo de autenticação com Safe ID (certificado em nuvem)

    Este comando prepara a autenticação via Playwright. Após executar, você deve:
    1. Usar Playwright para navegar ao PJE
    2. Completar login com Safe ID no browser
    3. Sessão será salva automaticamente

    Returns:
        Instruções detalhadas para completar autenticação

    Examples:
        >>> await pje_authenticate_safe_id()
        # Retorna instruções passo-a-passo
    """
    try:
        session_manager = get_default_session_manager()
        helper = PlaywrightSessionHelper()

        # Verificar se já existe sessão válida
        session_info = session_manager.get_session_info()
        if session_info['valid']:
            return f"""
✅ Sessão já está ativa!

Não é necessário autenticar novamente.
Idade da sessão: {session_info.get('age_human', 'N/A')}

Se quiser forçar re-autenticação:
1. Use: pje_clear_session
2. Depois use este comando novamente
"""

        # Criar metadados para nova sessão
        metadata = session_manager.create_session_metadata(
            auth_method="safe_id",
            additional_data={'status': 'iniciando'}
        )
        session_manager.save_session_metadata(metadata)

        # Retornar instruções
        resultado = """
🔐 AUTENTICAÇÃO SAFE ID PREPARADA

A sessão está pronta para ser criada. Siga estas etapas:

"""
        resultado += helper.get_safe_id_login_instructions()

        resultado += """

APÓS COMPLETAR O LOGIN:

1. Use: pje_check_session
   - Verificará se login foi bem-sucedido

2. Sessão ficará ativa por 8 horas

3. Você poderá fazer consultas sem autenticar novamente:
   - pje_search_process
   - pje_list_processes
   - etc.

IMPORTANTE:
- Os cookies e estado do browser serão salvos localmente
- Próximas execuções reutilizarão a sessão
- Após 8 horas, será necessário autenticar novamente
"""

        resultado += "\n\n" + helper.get_playwright_automation_example()

        return resultado

    except Exception as e:
        logger.exception("Erro ao preparar autenticação")
        return f"❌ Erro: {str(e)}"


@mcp.tool()
async def pje_clear_session() -> str:
    """
    Remove sessão autenticada do PJE (logout)

    Limpa completamente a sessão salva, incluindo cookies e estado do browser.
    Útil para:
    - Fazer logout
    - Forçar re-autenticação
    - Trocar de usuário
    - Resolver problemas de sessão

    Returns:
        Confirmação de remoção da sessão

    Examples:
        >>> await pje_clear_session()
        # Sessão é removida, próxima consulta pedirá autenticação
    """
    try:
        session_manager = get_default_session_manager()

        # Verificar se existe sessão
        session_info = session_manager.get_session_info()

        if not session_info['exists']:
            return """
ℹ️  Nenhuma sessão encontrada

Não há sessão para remover.
A próxima autenticação criará uma nova sessão.
"""

        # Remover sessão
        session_manager.clear_session()

        resultado = """
✅ Sessão removida com sucesso

Detalhes da sessão removida:
"""

        if session_info.get('auth_method'):
            resultado += f"\nMétodo: {session_info['auth_method']}"
        if session_info.get('created_at'):
            resultado += f"\nCriada em: {session_info['created_at']}"
        if session_info.get('age_human'):
            resultado += f"\nIdade: {session_info['age_human']}"

        resultado += """

PRÓXIMOS PASSOS:

1. Use: pje_authenticate_safe_id
   - Para criar nova sessão

2. Ou use qualquer ferramenta de consulta
   - Sistema pedirá autenticação automaticamente

Os dados foram removidos de:
""" + session_info['session_path']

        return resultado

    except Exception as e:
        logger.exception("Erro ao remover sessão")
        return f"❌ Erro ao remover sessão: {str(e)}"


# ========================================
# Main - Executar servidor
# ========================================

if __name__ == "__main__":
    logger.info("Iniciando TJES PJE MCP Server")
    logger.info(f"PJE Base URL: {PJE_BASE_URL}")
    logger.info(f"PJE 2G Base URL: {PJE_2G_BASE_URL}")
    logger.info(f"Timeout: {TIMEOUT}s")
    logger.info(f"Retry attempts: {RETRY_ATTEMPTS}")

    try:
        # Executar servidor MCP via stdio
        mcp.run(transport='stdio')
    finally:
        # Limpar certificados ao sair
        cleanup_certificate()
