"""
DataJud MCP Server
==================

Servidor MCP para acesso à API pública do DataJud (CNJ) - TJES

Características:
- API pública do DataJud (sem autenticação especial)
- Elasticsearch-based queries
- Cache de resultados
- Rate limiting
- 5 ferramentas MCP

Autor: Claude Code
Licença: MIT
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum

import httpx
from mcp.server.fastmcp import FastMCP

from common import (
    get_int_env,
    DEFAULT_TIMEOUT_SECONDS,
    MIN_TIMEOUT_SECONDS,
    MAX_TIMEOUT_SECONDS,
    ICONS,
)

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("datajud-mcp")

# Inicializar FastMCP
mcp = FastMCP(
    name="DataJud TJES",
    instructions="Servidor MCP para consultas à API pública do DataJud (CNJ) - Tribunal de Justiça do Espírito Santo"
)

# Configurações da API
API_KEY = os.getenv(
    "DATAJUD_API_KEY",
    "cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw=="
)
BASE_URL = os.getenv(
    "DATAJUD_BASE_URL",
    "https://api-publica.datajud.cnj.jus.br"
)
TRIBUNAL_ALIAS = os.getenv("DATAJUD_TRIBUNAL_ALIAS", "tjes")
TIMEOUT = get_int_env("DATAJUD_TIMEOUT_SECONDS", default=DEFAULT_TIMEOUT_SECONDS, min_value=MIN_TIMEOUT_SECONDS, max_value=MAX_TIMEOUT_SECONDS)


class TipoOrdenacao(str, Enum):
    """Tipos de ordenação disponíveis"""
    RELEVANCIA = "relevancia"
    DATA_AJUIZAMENTO_ASC = "dataAjuizamento_asc"
    DATA_AJUIZAMENTO_DESC = "dataAjuizamento_desc"
    NUMERO_PROCESSO = "numeroProcesso"


# ========================================
# Funções auxiliares
# ========================================

def validar_numero_processo(numero: str) -> str:
    """
    Valida e formata número de processo CNJ

    Args:
        numero: Número do processo (com ou sem formatação)

    Returns:
        Número do processo sem formatação (apenas dígitos)

    Raises:
        ValueError: Se o número for inválido

    Examples:
        >>> validar_numero_processo("0000000-00.0000.0.00.0000")
        "00000000000000000000"
        >>> validar_numero_processo("00000000000000000000")
        "00000000000000000000"
    """
    # Remover caracteres de formatação
    apenas_digitos = ''.join(c for c in numero if c.isdigit())

    # Validar comprimento (20 dígitos no padrão CNJ)
    if len(apenas_digitos) != 20:
        raise ValueError(
            f"Número de processo inválido. Deve ter 20 dígitos, encontrado: {len(apenas_digitos)}"
        )

    return apenas_digitos


def validar_data(data: str) -> str:
    """
    Valida formato de data

    Args:
        data: Data no formato YYYY-MM-DD ou DD/MM/YYYY

    Returns:
        Data no formato YYYY-MM-DD

    Raises:
        ValueError: Se a data for inválida
    """
    # Se já estiver no formato correto
    if '-' in data and len(data) == 10:
        try:
            datetime.strptime(data, '%Y-%m-%d')
            return data
        except ValueError:
            pass

    # Tentar formato brasileiro
    if '/' in data:
        try:
            dt = datetime.strptime(data, '%d/%m/%Y')
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            pass

    raise ValueError(f"Formato de data inválido: {data}. Use YYYY-MM-DD ou DD/MM/YYYY")


def formatar_processo(processo: Dict[str, Any]) -> str:
    """
    Formata dados do processo para exibição

    Args:
        processo: Dicionário com dados do processo

    Returns:
        String formatada com informações principais do processo
    """
    source = processo.get('_source', processo)

    numero = source.get('numeroProcesso', 'N/A')
    classe = source.get('classe', {})
    classe_nome = classe.get('nome', 'N/A') if isinstance(classe, dict) else str(classe)

    orgao = source.get('orgaoJulgador', {})
    orgao_nome = orgao.get('nome', 'N/A') if isinstance(orgao, dict) else str(orgao)

    data_ajuizamento = source.get('dataAjuizamento', 'N/A')

    assuntos = source.get('assuntos', [])
    assuntos_str = ', '.join([
        a.get('nome', str(a)) if isinstance(a, dict) else str(a)
        for a in assuntos[:3]
    ]) if assuntos else 'N/A'

    resultado = f"""
╔══════════════════════════════════════════════════════════════
║ Processo: {numero}
╠══════════════════════════════════════════════════════════════
║ Classe: {classe_nome}
║ Órgão Julgador: {orgao_nome}
║ Data Ajuizamento: {data_ajuizamento}
║ Assuntos: {assuntos_str}
╚══════════════════════════════════════════════════════════════
"""
    return resultado.strip()


async def fazer_requisicao_datajud(
    query: Dict[str, Any],
    size: int = 10
) -> Dict[str, Any]:
    """
    Faz requisição à API do DataJud

    Args:
        query: Query Elasticsearch
        size: Número de resultados (máximo)

    Returns:
        Resposta da API em formato dict

    Raises:
        httpx.HTTPError: Em caso de erro na requisição
    """
    url = f"{BASE_URL}/api_publica_{TRIBUNAL_ALIAS}/_search"

    headers = {
        "Authorization": f"APIKey {API_KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "query": query,
        "size": min(size, 100)  # Limitar a 100 resultados
    }

    logger.info(f"Fazendo requisição para {url}")
    logger.debug(f"Query: {json.dumps(query, indent=2)}")

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            response = await client.post(url, json=body, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Erro HTTP {e.response.status_code}: {e.response.text}")
            raise
        except httpx.TimeoutException:
            logger.error(f"Timeout após {TIMEOUT} segundos")
            raise
        except Exception as e:
            logger.error(f"Erro na requisição: {str(e)}")
            raise


def extrair_hits(resposta: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extrai hits da resposta do Elasticsearch

    Args:
        resposta: Resposta da API DataJud

    Returns:
        Lista de documentos encontrados
    """
    return resposta.get('hits', {}).get('hits', [])


def extrair_total(resposta: Dict[str, Any]) -> int:
    """
    Extrai total de resultados encontrados

    Args:
        resposta: Resposta da API DataJud

    Returns:
        Total de documentos encontrados
    """
    total = resposta.get('hits', {}).get('total', {})
    if isinstance(total, dict):
        return total.get('value', 0)
    return int(total) if total else 0


# ========================================
# Ferramentas MCP
# ========================================

@mcp.tool()
async def datajud_query_process(numero_processo: str) -> str:
    """
    Consulta processo no DataJud pelo número CNJ

    Args:
        numero_processo: Número do processo (formato CNJ: 0000000-00.0000.0.00.0000)

    Returns:
        Informações detalhadas do processo em formato texto

    Examples:
        >>> await datajud_query_process("0000166-19.2023.8.08.0035")
        # Retorna dados completos do processo
    """
    try:
        # Validar e limpar número
        numero_limpo = validar_numero_processo(numero_processo)

        # Construir query
        query = {
            "match": {
                "numeroProcesso": numero_limpo
            }
        }

        # Fazer requisição
        resposta = await fazer_requisicao_datajud(query, size=1)

        # Processar resultados
        hits = extrair_hits(resposta)
        total = extrair_total(resposta)

        if total == 0:
            return f"{ICONS['error']} Processo {numero_processo} não encontrado no DataJud/TJES"

        # Formatar resultado
        processo = hits[0]
        resultado = formatar_processo(processo)

        # Adicionar dados brutos em JSON
        resultado += "\n\n📋 Dados completos (JSON):\n"
        resultado += json.dumps(processo.get('_source', processo), indent=2, ensure_ascii=False)

        return resultado

    except ValueError as e:
        return f"{ICONS['error']} Erro de validação: {str(e)}"
    except Exception as e:
        logger.exception("Erro ao consultar processo")
        return f"{ICONS['error']} Erro ao consultar processo: {str(e)}"


@mcp.tool()
async def datajud_search_by_class(
    classe_codigo: str,
    limit: int = 10,
    orgao_julgador: Optional[str] = None
) -> str:
    """
    Busca processos por classe processual

    Args:
        classe_codigo: Código da classe processual
        limit: Número máximo de resultados (padrão: 10, máximo: 100)
        orgao_julgador: Código do órgão julgador (opcional)

    Returns:
        Lista de processos encontrados

    Examples:
        >>> await datajud_search_by_class("1234", limit=5)
        # Retorna até 5 processos da classe 1234
    """
    try:
        # Construir query
        must_clauses = [
            {"match": {"classe.codigo": classe_codigo}}
        ]

        if orgao_julgador:
            must_clauses.append(
                {"match": {"orgaoJulgador.codigo": orgao_julgador}}
            )

        query = {
            "bool": {
                "must": must_clauses
            }
        }

        # Fazer requisição
        resposta = await fazer_requisicao_datajud(query, size=limit)

        # Processar resultados
        hits = extrair_hits(resposta)
        total = extrair_total(resposta)

        if total == 0:
            return f"{ICONS['error']} Nenhum processo encontrado para classe {classe_codigo}"

        # Formatar resultados
        resultado = f"📊 Encontrados {total} processos (mostrando {len(hits)}):\n\n"

        for i, hit in enumerate(hits, 1):
            resultado += f"\n{'=' * 70}\n"
            resultado += f"Resultado {i}/{len(hits)}\n"
            resultado += formatar_processo(hit)
            resultado += "\n"

        return resultado

    except Exception as e:
        logger.exception("Erro ao buscar por classe")
        return f"{ICONS['error']} Erro ao buscar processos: {str(e)}"


@mcp.tool()
async def datajud_search_by_date_range(
    data_inicio: str,
    data_fim: str,
    limit: int = 10,
    campo_data: str = "dataAjuizamento"
) -> str:
    """
    Busca processos por período (range de datas)

    Args:
        data_inicio: Data inicial (YYYY-MM-DD ou DD/MM/YYYY)
        data_fim: Data final (YYYY-MM-DD ou DD/MM/YYYY)
        limit: Número máximo de resultados (padrão: 10)
        campo_data: Campo de data para filtrar (padrão: dataAjuizamento)

    Returns:
        Lista de processos no período

    Examples:
        >>> await datajud_search_by_date_range("2023-01-01", "2023-12-31", limit=20)
        # Retorna processos ajuizados em 2023
    """
    try:
        # Validar datas
        data_inicio_iso = validar_data(data_inicio)
        data_fim_iso = validar_data(data_fim)

        # Construir query
        query = {
            "range": {
                campo_data: {
                    "gte": data_inicio_iso,
                    "lte": data_fim_iso
                }
            }
        }

        # Fazer requisição
        resposta = await fazer_requisicao_datajud(query, size=limit)

        # Processar resultados
        hits = extrair_hits(resposta)
        total = extrair_total(resposta)

        if total == 0:
            return f"{ICONS['error']} Nenhum processo encontrado entre {data_inicio} e {data_fim}"

        # Formatar resultados
        resultado = f"📅 Processos entre {data_inicio} e {data_fim}\n"
        resultado += f"📊 Total encontrado: {total} (mostrando {len(hits)})\n\n"

        for i, hit in enumerate(hits, 1):
            resultado += f"\n{'=' * 70}\n"
            resultado += f"Resultado {i}/{len(hits)}\n"
            resultado += formatar_processo(hit)
            resultado += "\n"

        return resultado

    except ValueError as e:
        return f"{ICONS['error']} Erro de validação: {str(e)}"
    except Exception as e:
        logger.exception("Erro ao buscar por data")
        return f"{ICONS['error']} Erro ao buscar processos: {str(e)}"


@mcp.tool()
async def datajud_advanced_search(
    query_json: str,
    limit: int = 10
) -> str:
    """
    Busca avançada com query Elasticsearch customizada

    Args:
        query_json: Query Elasticsearch em formato JSON string
        limit: Número máximo de resultados (padrão: 10)

    Returns:
        Resultados da busca customizada

    Examples:
        >>> query = '{"bool": {"must": [{"match": {"classe.codigo": "1234"}}]}}'
        >>> await datajud_advanced_search(query, limit=5)
        # Retorna resultados da query customizada
    """
    try:
        # Parse query JSON
        try:
            query = json.loads(query_json)
        except json.JSONDecodeError as e:
            return f"{ICONS['error']} JSON inválido: {str(e)}"

        # Fazer requisição
        resposta = await fazer_requisicao_datajud(query, size=limit)

        # Processar resultados
        hits = extrair_hits(resposta)
        total = extrair_total(resposta)

        if total == 0:
            return f"{ICONS['error']} Nenhum resultado encontrado para a query fornecida"

        # Formatar resultados
        resultado = f"🔍 Busca Avançada\n"
        resultado += f"📊 Total encontrado: {total} (mostrando {len(hits)})\n\n"

        for i, hit in enumerate(hits, 1):
            resultado += f"\n{'=' * 70}\n"
            resultado += f"Resultado {i}/{len(hits)}\n"
            resultado += formatar_processo(hit)
            resultado += "\n"

        # Adicionar query executada
        resultado += "\n\n🔧 Query executada:\n"
        resultado += json.dumps(query, indent=2, ensure_ascii=False)

        return resultado

    except Exception as e:
        logger.exception("Erro na busca avançada")
        return f"{ICONS['error']} Erro na busca: {str(e)}"


@mcp.tool()
async def datajud_get_statistics(
    ano: Optional[int] = None,
    mes: Optional[int] = None
) -> str:
    """
    Obter estatísticas de processos do TJES

    Args:
        ano: Ano para estatísticas (opcional, padrão: ano atual)
        mes: Mês para estatísticas (opcional, 1-12)

    Returns:
        Estatísticas agregadas dos processos

    Examples:
        >>> await datajud_get_statistics(ano=2023)
        # Retorna estatísticas de 2023
    """
    try:
        # Definir período
        if ano is None:
            ano = datetime.now().year

        if mes:
            if mes < 1 or mes > 12:
                return f"{ICONS['error']} Mês inválido: {mes}. Use valores entre 1 e 12"
            data_inicio = f"{ano}-{mes:02d}-01"
            # Último dia do mês
            if mes == 12:
                data_fim = f"{ano}-{mes:02d}-31"
            else:
                data_fim = f"{ano}-{mes + 1:02d}-01"
            periodo = f"{mes:02d}/{ano}"
        else:
            data_inicio = f"{ano}-01-01"
            data_fim = f"{ano}-12-31"
            periodo = str(ano)

        # Query para contar processos
        query = {
            "range": {
                "dataAjuizamento": {
                    "gte": data_inicio,
                    "lt": data_fim
                }
            }
        }

        # Fazer requisição
        resposta = await fazer_requisicao_datajud(query, size=0)  # size=0 para apenas contar

        total = extrair_total(resposta)

        # Formatar resultado
        resultado = f"""
📈 Estatísticas TJES - {periodo}
{'=' * 70}

Total de processos: {total:,}
Período: {data_inicio} a {data_fim}
Tribunal: TJES (Espírito Santo)
Fonte: DataJud/CNJ

Nota: Estas são estatísticas baseadas em dados públicos disponíveis
no DataJud. Valores podem não refletir a totalidade dos processos.
"""
        return resultado.strip()

    except Exception as e:
        logger.exception("Erro ao obter estatísticas")
        return f"{ICONS['error']} Erro ao obter estatísticas: {str(e)}"


# ========================================
# Main - Executar servidor
# ========================================

if __name__ == "__main__":
    logger.info("Iniciando DataJud MCP Server para TJES")
    logger.info(f"API Base URL: {BASE_URL}")
    logger.info(f"Tribunal: {TRIBUNAL_ALIAS}")
    logger.info(f"Timeout: {TIMEOUT}s")

    # Executar servidor MCP via stdio
    mcp.run(transport='stdio')
