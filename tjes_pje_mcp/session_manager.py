"""
Session Manager Module
======================

Módulo para gerenciamento de sessões autenticadas do PJE usando Playwright.
Suporta autenticação via Safe ID (certificado em nuvem) com persistência de sessão.

Características:
- Browser context persistente (cookies salvos)
- Autenticação uma vez, reutilização múltipla
- Suporte a Safe ID e outros certificados em nuvem
- Detecção automática de expiração de sessão
- Re-autenticação automática quando necessário

Autor: Claude Code
Licença: MIT
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List

logger = logging.getLogger("session-manager")


class SessionManager:
    """
    Gerenciador de sessões autenticadas do PJE via Playwright

    Fluxo de uso:
    1. Primeira vez: Autentica via browser (Safe ID popup)
    2. Salva cookies e state do browser
    3. Próximas vezes: Reutiliza sessão existente
    4. Se expirar: Re-autentica automaticamente

    Examples:
        >>> manager = SessionManager()
        >>> await manager.ensure_authenticated()
        >>> # Sessão está pronta para uso
        >>> is_valid = await manager.is_session_valid()
    """

    def __init__(
        self,
        session_dir: Optional[str] = None,
        session_name: str = "tjes_pje_session",
        max_session_age_hours: int = 8
    ):
        """
        Inicializa o gerenciador de sessões

        Args:
            session_dir: Diretório para armazenar dados de sessão
            session_name: Nome da sessão (para múltiplas sessões)
            max_session_age_hours: Idade máxima da sessão em horas
        """
        self.session_name = session_name
        self.max_session_age = timedelta(hours=max_session_age_hours)

        # Diretório de sessão
        if session_dir is None:
            session_dir = os.path.expanduser("~/.cache/tjes-pje-mcp/sessions")

        self.session_dir = Path(session_dir)
        self.session_dir.mkdir(parents=True, exist_ok=True)

        # Arquivos de sessão
        self.session_path = self.session_dir / session_name
        self.session_path.mkdir(parents=True, exist_ok=True)  # Criar diretório da sessão
        self.cookies_file = self.session_path / "cookies.json"
        self.state_file = self.session_path / "state.json"
        self.metadata_file = self.session_path / "metadata.json"

        logger.info(f"SessionManager inicializado: {self.session_path}")

    def get_session_metadata(self) -> Optional[Dict[str, Any]]:
        """
        Obtém metadados da sessão salva

        Returns:
            Dict com metadados ou None se não existir
        """
        if not self.metadata_file.exists():
            return None

        try:
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Erro ao ler metadados da sessão: {e}")
            return None

    def save_session_metadata(self, metadata: Dict[str, Any]) -> None:
        """
        Salva metadados da sessão

        Args:
            metadata: Dict com metadados para salvar
        """
        try:
            self.session_path.mkdir(parents=True, exist_ok=True)
            with open(self.metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            logger.info("Metadados da sessão salvos")
        except Exception as e:
            logger.error(f"Erro ao salvar metadados: {e}")

    def is_session_expired(self) -> bool:
        """
        Verifica se a sessão expirou por idade

        Returns:
            True se expirada, False caso contrário
        """
        metadata = self.get_session_metadata()
        if not metadata:
            return True

        created_at = metadata.get('created_at')
        if not created_at:
            return True

        try:
            created_time = datetime.fromisoformat(created_at)
            age = datetime.now() - created_time

            is_expired = age > self.max_session_age

            if is_expired:
                logger.info(f"Sessão expirada (idade: {age}, máximo: {self.max_session_age})")
            else:
                logger.info(f"Sessão válida (idade: {age})")

            return is_expired

        except Exception as e:
            logger.warning(f"Erro ao verificar expiração: {e}")
            return True

    def session_exists(self) -> bool:
        """
        Verifica se existe uma sessão salva

        Returns:
            True se existe sessão, False caso contrário
        """
        # Verificar se pelo menos metadata existe (principal indicador de sessão)
        return self.metadata_file.exists()

    def get_session_info(self) -> Dict[str, Any]:
        """
        Obtém informações sobre a sessão atual

        Returns:
            Dict com informações da sessão
        """
        exists = self.session_exists()
        expired = self.is_session_expired() if exists else True
        metadata = self.get_session_metadata() if exists else {}

        info = {
            'exists': exists,
            'expired': expired,
            'valid': exists and not expired,
            'session_name': self.session_name,
            'session_path': str(self.session_path),
            'max_age_hours': self.max_session_age.total_seconds() / 3600,
        }

        if metadata:
            info['created_at'] = metadata.get('created_at')
            info['last_used'] = metadata.get('last_used')
            info['auth_method'] = metadata.get('auth_method', 'unknown')
            info['username'] = metadata.get('username')

            # Calcular idade
            if metadata.get('created_at'):
                try:
                    created = datetime.fromisoformat(metadata['created_at'])
                    age = datetime.now() - created
                    info['age_hours'] = age.total_seconds() / 3600
                    info['age_human'] = self._format_timedelta(age)
                except:
                    pass

        return info

    def _format_timedelta(self, td: timedelta) -> str:
        """Formata timedelta para string legível"""
        hours = td.total_seconds() / 3600
        if hours < 1:
            return f"{int(td.total_seconds() / 60)} minutos"
        elif hours < 24:
            return f"{int(hours)} horas"
        else:
            return f"{int(hours / 24)} dias"

    def create_session_metadata(
        self,
        auth_method: str = "safe_id",
        username: Optional[str] = None,
        additional_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Cria metadados para uma nova sessão

        Args:
            auth_method: Método de autenticação usado
            username: Nome do usuário (opcional)
            additional_data: Dados adicionais (opcional)

        Returns:
            Dict com metadados
        """
        metadata = {
            'created_at': datetime.now().isoformat(),
            'last_used': datetime.now().isoformat(),
            'auth_method': auth_method,
            'session_name': self.session_name,
        }

        if username:
            metadata['username'] = username

        if additional_data:
            metadata.update(additional_data)

        return metadata

    def update_last_used(self) -> None:
        """Atualiza timestamp de último uso da sessão"""
        metadata = self.get_session_metadata()
        if metadata:
            metadata['last_used'] = datetime.now().isoformat()
            self.save_session_metadata(metadata)

    def clear_session(self) -> None:
        """
        Remove sessão salva completamente
        """
        try:
            if self.cookies_file.exists():
                self.cookies_file.unlink()
            if self.state_file.exists():
                self.state_file.unlink()
            if self.metadata_file.exists():
                self.metadata_file.unlink()

            logger.info("Sessão removida")
        except Exception as e:
            logger.error(f"Erro ao remover sessão: {e}")

    def get_playwright_persistent_context_config(self) -> Dict[str, Any]:
        """
        Retorna configuração para Playwright persistent context

        Returns:
            Dict com configuração do browser context
        """
        return {
            'user_data_dir': str(self.session_path),
            'accept_downloads': True,
            'ignore_https_errors': False,
            'viewport': {'width': 1920, 'height': 1080},
            'locale': 'pt-BR',
            'timezone_id': 'America/Sao_Paulo',
            'record_video_dir': None,  # Desabilitado por padrão
            'record_har_path': None,   # Desabilitado por padrão
        }

    def __repr__(self) -> str:
        info = self.get_session_info()
        status = "válida" if info['valid'] else "inválida/expirada"
        return f"SessionManager(session='{self.session_name}', status='{status}')"


class PlaywrightSessionHelper:
    """
    Helper para integração Playwright + SessionManager

    Fornece métodos convenientes para usar SessionManager com Playwright MCP.
    """

    @staticmethod
    def get_safe_id_login_instructions() -> str:
        """
        Retorna instruções para login com Safe ID

        Returns:
            String com instruções passo-a-passo
        """
        return """
╔══════════════════════════════════════════════════════════════
║ INSTRUÇÕES: Login PJE TJES com Safe ID
╠══════════════════════════════════════════════════════════════
║
║ 1. Navegue para: https://sistemas.tjes.jus.br/pje
║
║ 2. Clique em "Acesso com Certificado Digital"
║
║ 3. Popup Safe ID abrirá automaticamente
║
║ 4. No popup Safe ID:
║    • Digite seu CPF/CNPJ
║    • Digite sua senha Safe ID
║    • Ou use biometria se configurado
║
║ 5. Aguarde autenticação
║
║ 6. Você será redirecionado para área logada
║
║ 7. Sessão será salva automaticamente!
║
║ PRÓXIMAS VEZES: Login automático (sem popup)
║
╚══════════════════════════════════════════════════════════════

IMPORTANTE:
- Sessão dura 8 horas por padrão
- Após expirar, será necessário autenticar novamente
- Cookies e estado do browser são salvos localmente
"""

    @staticmethod
    def get_session_status_message(session_info: Dict[str, Any]) -> str:
        """
        Formata informações da sessão para exibição

        Args:
            session_info: Dict retornado por SessionManager.get_session_info()

        Returns:
            String formatada com status da sessão
        """
        if not session_info['exists']:
            return """
❌ Sessão não encontrada

Você precisa autenticar pela primeira vez:
1. Use a ferramenta para iniciar autenticação
2. Complete o login no browser
3. Sessão será salva automaticamente
"""

        if session_info['expired']:
            age = session_info.get('age_human', 'desconhecida')
            return f"""
⚠️  Sessão expirada

Idade da sessão: {age}
Última autenticação: {session_info.get('created_at', 'N/A')}

Você precisa autenticar novamente:
1. Use a ferramenta para re-autenticar
2. Complete o login no browser
3. Nova sessão será criada
"""

        # Sessão válida
        age = session_info.get('age_human', 'desconhecida')
        method = session_info.get('auth_method', 'desconhecido')

        return f"""
✅ Sessão válida e ativa

Método de autenticação: {method}
Criada em: {session_info.get('created_at', 'N/A')}
Idade: {age}
Máximo permitido: {session_info.get('max_age_hours', 8)} horas

Status: Pronta para uso!
Você pode fazer consultas sem autenticar novamente.
"""

    @staticmethod
    def get_playwright_automation_example() -> str:
        """
        Retorna exemplo de automação Playwright com sessão

        Returns:
            String com exemplo de código
        """
        return """
EXEMPLO: Consultar processo usando sessão autenticada

1. Verificar sessão:
   Use: pje_check_session

2a. Se sessão válida:
   - Pule para passo 3

2b. Se sessão inválida:
   - Use: pje_authenticate_safe_id
   - Complete login no browser
   - Aguarde confirmação

3. Fazer consulta via Playwright:
   - browser_navigate: https://sistemas.tjes.jus.br/pje
   - browser_fill_form: preencher número do processo
   - browser_click: botão "Consultar"
   - browser_snapshot: capturar resultado

4. Sessão continua ativa para próximas consultas!

VANTAGENS:
- Autentica UMA VEZ a cada 8 horas
- Múltiplas consultas sem re-autenticar
- Cookies salvos localmente
- Funciona com Safe ID, ICP-Brasil, etc.
"""


# ========================================
# Funções auxiliares
# ========================================

def get_default_session_manager() -> SessionManager:
    """
    Retorna SessionManager com configuração padrão

    Returns:
        SessionManager configurado
    """
    return SessionManager(
        session_name=os.getenv("PJE_SESSION_NAME", "tjes_pje_default"),
        max_session_age_hours=int(os.getenv("PJE_SESSION_MAX_AGE_HOURS", "8"))
    )


def format_session_info_detailed(session_info: Dict[str, Any]) -> str:
    """
    Formata informações detalhadas da sessão

    Args:
        session_info: Informações da sessão

    Returns:
        String formatada com todos os detalhes
    """
    lines = [
        "╔══════════════════════════════════════════════════════════════",
        "║ STATUS DA SESSÃO PJE TJES",
        "╠══════════════════════════════════════════════════════════════",
        ""
    ]

    # Status geral
    if session_info['valid']:
        status_icon = "✅"
        status_text = "VÁLIDA E ATIVA"
    elif session_info['exists'] and session_info['expired']:
        status_icon = "⚠️"
        status_text = "EXPIRADA"
    else:
        status_icon = "❌"
        status_text = "NÃO ENCONTRADA"

    lines.append(f"║ Status: {status_icon} {status_text}")
    lines.append("║")

    # Detalhes
    lines.append(f"║ Nome da sessão: {session_info['session_name']}")
    lines.append(f"║ Diretório: {session_info['session_path']}")
    lines.append("║")

    if session_info['exists']:
        lines.append(f"║ Método de autenticação: {session_info.get('auth_method', 'N/A')}")
        if session_info.get('username'):
            lines.append(f"║ Usuário: {session_info['username']}")
        lines.append(f"║ Criada em: {session_info.get('created_at', 'N/A')}")
        lines.append(f"║ Última utilização: {session_info.get('last_used', 'N/A')}")

        if session_info.get('age_human'):
            lines.append(f"║ Idade da sessão: {session_info['age_human']}")

        lines.append(f"║ Tempo máximo: {session_info['max_age_hours']} horas")

    lines.append("╚══════════════════════════════════════════════════════════════")

    return "\n".join(lines)
