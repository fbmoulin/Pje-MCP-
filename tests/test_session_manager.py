"""
Testes para Session Manager (Safe ID)

Execute: python test_session_manager.py
"""

import asyncio
import sys
import os
import json
import tempfile
from pathlib import Path

# Adicionar diretório pai ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tjes_pje_mcp.session_manager import (
    SessionManager,
    PlaywrightSessionHelper,
    get_default_session_manager,
    format_session_info_detailed
)

# Cores ANSI
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'


def print_success(msg):
    print(f"{Colors.GREEN}✓{Colors.RESET} {msg}")


def print_error(msg):
    print(f"{Colors.RED}✗{Colors.RESET} {msg}")


def print_info(msg):
    print(f"{Colors.BLUE}ℹ{Colors.RESET} {msg}")


def print_warning(msg):
    print(f"{Colors.YELLOW}⚠{Colors.RESET} {msg}")


# ========================================
# Testes SessionManager
# ========================================

def test_create_session_manager():
    """Testa criação do SessionManager"""
    print_info("Testando criação do SessionManager...")

    try:
        # Criar diretório temporário para testes
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = SessionManager(
                session_dir=tmpdir,
                session_name="test_session",
                max_session_age_hours=2
            )

            assert manager.session_name == "test_session", "Nome da sessão incorreto"
            assert manager.session_path.exists(), "Diretório de sessão não criado"
            print_success("SessionManager criado corretamente")

            return True

    except Exception as e:
        print_error(f"Erro ao criar SessionManager: {str(e)}")
        return False


def test_session_metadata():
    """Testa salvamento e leitura de metadados"""
    print_info("Testando metadados da sessão...")

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = SessionManager(session_dir=tmpdir, session_name="test_meta")

            # Criar metadados
            metadata = manager.create_session_metadata(
                auth_method="safe_id",
                username="teste@example.com",
                additional_data={"test": "value"}
            )

            # Verificar estrutura
            assert 'created_at' in metadata, "created_at ausente"
            assert 'last_used' in metadata, "last_used ausente"
            assert metadata['auth_method'] == "safe_id", "auth_method incorreto"
            assert metadata['username'] == "teste@example.com", "username incorreto"
            assert metadata['test'] == "value", "additional_data não salvo"

            print_success("Metadados criados corretamente")

            # Salvar metadados
            manager.save_session_metadata(metadata)

            # Ler metadados
            loaded_metadata = manager.get_session_metadata()
            assert loaded_metadata is not None, "Metadados não carregados"
            assert loaded_metadata['auth_method'] == "safe_id", "Metadados corrompidos"

            print_success("Metadados salvos e carregados corretamente")

            return True

    except Exception as e:
        print_error(f"Erro com metadados: {str(e)}")
        return False


def test_session_expiration():
    """Testa verificação de expiração de sessão"""
    print_info("Testando verificação de expiração...")

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            # Sessão com 1 segundo de duração
            manager = SessionManager(
                session_dir=tmpdir,
                session_name="test_expire",
                max_session_age_hours=0.0001  # ~0.36 segundos
            )

            # Criar sessão
            metadata = manager.create_session_metadata(auth_method="test")
            manager.save_session_metadata(metadata)

            # Verificar que não está expirada imediatamente
            is_expired = manager.is_session_expired()
            assert not is_expired, "Sessão não deveria estar expirada imediatamente"
            print_success("Sessão nova não está expirada")

            # Aguardar expiração
            import time
            time.sleep(1)

            # Verificar que expirou
            is_expired = manager.is_session_expired()
            assert is_expired, "Sessão deveria estar expirada"
            print_success("Sessão expirou corretamente após timeout")

            return True

    except Exception as e:
        print_error(f"Erro ao testar expiração: {str(e)}")
        return False


def test_session_info():
    """Testa obtenção de informações da sessão"""
    print_info("Testando informações da sessão...")

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = SessionManager(session_dir=tmpdir, session_name="test_info")

            # Sessão não existe
            info = manager.get_session_info()
            assert not info['exists'], "Sessão não deveria existir"
            assert info['expired'], "Sessão inexistente deveria ser marcada como expirada"
            assert not info['valid'], "Sessão inexistente não deveria ser válida"
            print_success("Info de sessão inexistente correta")

            # Criar sessão
            metadata = manager.create_session_metadata(auth_method="safe_id")
            manager.save_session_metadata(metadata)

            # Sessão existe
            info = manager.get_session_info()
            assert info['exists'], "Sessão deveria existir"
            assert not info['expired'], "Sessão nova não deveria estar expirada"
            assert info['valid'], "Sessão nova deveria ser válida"
            assert info['auth_method'] == "safe_id", "auth_method incorreto"
            print_success("Info de sessão válida correta")

            return True

    except Exception as e:
        print_error(f"Erro ao obter info: {str(e)}")
        return False


def test_clear_session():
    """Testa remoção de sessão"""
    print_info("Testando remoção de sessão...")

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = SessionManager(session_dir=tmpdir, session_name="test_clear")

            # Criar sessão
            metadata = manager.create_session_metadata(auth_method="test")
            manager.save_session_metadata(metadata)

            # Verificar que existe
            assert manager.session_exists(), "Sessão deveria existir"
            print_success("Sessão criada")

            # Limpar sessão
            manager.clear_session()

            # Verificar que foi removida
            assert not manager.session_exists(), "Sessão deveria ter sido removida"
            print_success("Sessão removida corretamente")

            return True

    except Exception as e:
        print_error(f"Erro ao limpar sessão: {str(e)}")
        return False


def test_playwright_config():
    """Testa configuração do Playwright persistent context"""
    print_info("Testando configuração Playwright...")

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = SessionManager(session_dir=tmpdir, session_name="test_pw")

            config = manager.get_playwright_persistent_context_config()

            # Verificar campos essenciais
            assert 'user_data_dir' in config, "user_data_dir ausente"
            assert config['accept_downloads'] == True, "accept_downloads incorreto"
            assert config['locale'] == 'pt-BR', "locale incorreto"
            assert config['timezone_id'] == 'America/Sao_Paulo', "timezone incorreto"

            print_success("Configuração Playwright correta")

            return True

    except Exception as e:
        print_error(f"Erro na configuração: {str(e)}")
        return False


def test_helper_instructions():
    """Testa geração de instruções"""
    print_info("Testando instruções do helper...")

    try:
        helper = PlaywrightSessionHelper()

        # Instruções de login
        instructions = helper.get_safe_id_login_instructions()
        assert "Safe ID" in instructions, "Instruções não mencionam Safe ID"
        assert "CPF" in instructions, "Instruções não mencionam CPF"
        print_success("Instruções de login geradas")

        # Mensagem de status
        session_info = {
            'exists': True,
            'expired': False,
            'valid': True,
            'auth_method': 'safe_id',
            'age_human': '30 minutos'
        }
        status_msg = helper.get_session_status_message(session_info)
        assert "válida" in status_msg.lower(), "Status não indica válida"
        print_success("Mensagem de status gerada")

        # Exemplo de automação
        example = helper.get_playwright_automation_example()
        assert "pje_check_session" in example, "Exemplo não menciona check_session"
        print_success("Exemplo de automação gerado")

        return True

    except Exception as e:
        print_error(f"Erro nas instruções: {str(e)}")
        return False


def test_format_session_info():
    """Testa formatação de informações da sessão"""
    print_info("Testando formatação de informações...")

    try:
        session_info = {
            'exists': True,
            'expired': False,
            'valid': True,
            'session_name': 'test_session',
            'session_path': '/tmp/test',
            'max_age_hours': 8,
            'auth_method': 'safe_id',
            'username': 'teste@example.com',
            'created_at': '2024-11-16T10:00:00',
            'last_used': '2024-11-16T10:30:00',
            'age_human': '30 minutos'
        }

        formatted = format_session_info_detailed(session_info)

        # Verificar conteúdo
        assert "STATUS DA SESSÃO" in formatted, "Título ausente"
        assert "VÁLIDA E ATIVA" in formatted, "Status ausente"
        assert "safe_id" in formatted, "Método de auth ausente"
        assert "teste@example.com" in formatted, "Username ausente"

        print_success("Informações formatadas corretamente")

        return True

    except Exception as e:
        print_error(f"Erro na formatação: {str(e)}")
        return False


# ========================================
# Runner principal
# ========================================

def main():
    """Função principal"""
    print(f"\n{Colors.BLUE}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BLUE}TESTE SUITE - Session Manager (Safe ID){Colors.RESET}")
    print(f"{Colors.BLUE}{'=' * 70}{Colors.RESET}\n")

    tests = [
        ("Criação SessionManager", test_create_session_manager),
        ("Metadados da Sessão", test_session_metadata),
        ("Verificação de Expiração", test_session_expiration),
        ("Informações da Sessão", test_session_info),
        ("Remoção de Sessão", test_clear_session),
        ("Configuração Playwright", test_playwright_config),
        ("Instruções Helper", test_helper_instructions),
        ("Formatação de Info", test_format_session_info),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
            print()  # Linha em branco entre testes
        except Exception as e:
            print_error(f"{name}: {str(e)}")
            results.append((name, False))
            print()

    # Sumário
    print(f"\n{Colors.BLUE}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BLUE}SUMÁRIO{Colors.RESET}")
    print(f"{Colors.BLUE}{'=' * 70}{Colors.RESET}\n")

    passed = sum(1 for _, result in results if result)
    failed = len(results) - passed

    for name, result in results:
        status = f"{Colors.GREEN}PASSOU{Colors.RESET}" if result else f"{Colors.RED}FALHOU{Colors.RESET}"
        print(f"{name}: {status}")

    print(f"\n{Colors.BLUE}{'=' * 70}{Colors.RESET}")
    print(f"Total: {len(results)} testes")
    print(f"{Colors.GREEN}Passou: {passed}{Colors.RESET}")
    print(f"{Colors.RED}Falhou: {failed}{Colors.RESET}")
    print(f"{Colors.BLUE}{'=' * 70}{Colors.RESET}\n")

    # Código de saída
    if failed == 0:
        print(f"{Colors.GREEN}✓ Todos os testes passaram!{Colors.RESET}")
        print(f"\n{Colors.BLUE}Session Manager está funcionando corretamente!{Colors.RESET}")
        print(f"{Colors.BLUE}Pronto para usar com Safe ID.{Colors.RESET}\n")
        return 0
    elif failed < len(results) / 2:
        print(f"{Colors.YELLOW}⚠ Alguns testes falharam{Colors.RESET}\n")
        return 1
    else:
        print(f"{Colors.RED}✗ Muitos testes falharam{Colors.RESET}\n")
        return 2


if __name__ == "__main__":
    sys.exit(main())
