"""
Testes para DataJud MCP Server

Execute: python test_datajud.py
"""

import asyncio
import sys
import os

# Adicionar diretório pai ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datajud_mcp.server import (
    validar_numero_processo,
    validar_data,
    formatar_processo,
    fazer_requisicao_datajud
)

# Cores ANSI para output
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
# Testes Síncronos (Validação)
# ========================================

def test_validar_numero_processo():
    """Testa validação de número de processo"""
    print_info("Testando validação de número de processo...")

    try:
        # Teste 1: Número válido com formatação
        resultado = validar_numero_processo("0000166-19.2023.8.08.0035")
        assert resultado == "00001661920238080035", f"Esperado 00001661920238080035, obtido {resultado}"
        print_success("Número com formatação validado corretamente")

        # Teste 2: Número válido sem formatação
        resultado = validar_numero_processo("00001661920238080035")
        assert resultado == "00001661920238080035"
        print_success("Número sem formatação validado corretamente")

        # Teste 3: Número inválido (muito curto)
        try:
            validar_numero_processo("123456")
            print_error("Deveria ter rejeitado número curto")
            return False
        except ValueError:
            print_success("Número curto rejeitado corretamente")

        return True

    except Exception as e:
        print_error(f"Erro no teste: {str(e)}")
        return False


def test_validar_data():
    """Testa validação de data"""
    print_info("Testando validação de data...")

    try:
        # Teste 1: Data ISO válida
        resultado = validar_data("2023-01-15")
        assert resultado == "2023-01-15"
        print_success("Data ISO validada corretamente")

        # Teste 2: Data brasileira válida
        resultado = validar_data("15/01/2023")
        assert resultado == "2023-01-15"
        print_success("Data brasileira convertida corretamente")

        # Teste 3: Data inválida
        try:
            validar_data("2023-13-45")
            print_error("Deveria ter rejeitado data inválida")
            return False
        except ValueError:
            print_success("Data inválida rejeitada corretamente")

        return True

    except Exception as e:
        print_error(f"Erro no teste: {str(e)}")
        return False


def test_formatar_processo():
    """Testa formatação de processo"""
    print_info("Testando formatação de processo...")

    try:
        # Processo de exemplo
        processo = {
            '_source': {
                'numeroProcesso': '00001661920238080035',
                'classe': {
                    'codigo': '1234',
                    'nome': 'Ação Civil Pública'
                },
                'orgaoJulgador': {
                    'codigo': '5678',
                    'nome': '1ª Vara Cível'
                },
                'dataAjuizamento': '2023-01-15',
                'assuntos': [
                    {'codigo': '9876', 'nome': 'Direito Civil'}
                ]
            }
        }

        resultado = formatar_processo(processo)

        # Verificar se contém informações essenciais
        assert 'Processo:' in resultado
        assert '00001661920238080035' in resultado
        assert 'Ação Civil Pública' in resultado
        print_success("Processo formatado corretamente")

        return True

    except Exception as e:
        print_error(f"Erro no teste: {str(e)}")
        return False


# ========================================
# Testes Assíncronos (API)
# ========================================

async def test_api_conectividade():
    """Testa conectividade com API DataJud"""
    print_info("Testando conectividade com API DataJud...")

    try:
        # Query simples para testar API
        query = {
            "match_all": {}
        }

        resultado = await fazer_requisicao_datajud(query, size=1)

        # Verificar estrutura da resposta
        assert 'hits' in resultado, "Resposta deve conter 'hits'"
        print_success(f"API DataJud respondeu corretamente")

        # Verificar se retornou dados
        total = resultado.get('hits', {}).get('total', {})
        if isinstance(total, dict):
            total_value = total.get('value', 0)
        else:
            total_value = int(total) if total else 0

        print_info(f"Total de processos no índice: {total_value:,}")

        return True

    except Exception as e:
        print_error(f"Erro ao conectar com API: {str(e)}")
        print_warning("Verifique se a chave API está correta e se há conexão com internet")
        return False


async def test_busca_por_classe():
    """Testa busca por classe processual"""
    print_info("Testando busca por classe processual...")

    try:
        query = {
            "bool": {
                "must": [
                    {"match": {"classe.codigo": "1234"}}
                ]
            }
        }

        resultado = await fazer_requisicao_datajud(query, size=5)

        assert 'hits' in resultado
        print_success("Busca por classe executada com sucesso")

        hits = resultado.get('hits', {}).get('hits', [])
        print_info(f"Encontrados {len(hits)} processos")

        return True

    except Exception as e:
        print_error(f"Erro na busca: {str(e)}")
        return False


# ========================================
# Runner principal
# ========================================

async def run_async_tests():
    """Executa testes assíncronos"""
    print(f"\n{Colors.BLUE}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BLUE}TESTES ASSÍNCRONOS (API){Colors.RESET}")
    print(f"{Colors.BLUE}{'=' * 70}{Colors.RESET}\n")

    tests = [
        ("Conectividade API", test_api_conectividade()),
        ("Busca por Classe", test_busca_por_classe()),
    ]

    results = []
    for name, test in tests:
        try:
            result = await test
            results.append((name, result))
        except Exception as e:
            print_error(f"{name}: {str(e)}")
            results.append((name, False))

    return results


def run_sync_tests():
    """Executa testes síncronos"""
    print(f"\n{Colors.BLUE}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BLUE}TESTES SÍNCRONOS (Validação){Colors.RESET}")
    print(f"{Colors.BLUE}{'=' * 70}{Colors.RESET}\n")

    tests = [
        ("Validação de Número de Processo", test_validar_numero_processo),
        ("Validação de Data", test_validar_data),
        ("Formatação de Processo", test_formatar_processo),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print_error(f"{name}: {str(e)}")
            results.append((name, False))

    return results


def main():
    """Função principal"""
    print(f"\n{Colors.BLUE}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BLUE}TESTE SUITE - DataJud MCP Server{Colors.RESET}")
    print(f"{Colors.BLUE}{'=' * 70}{Colors.RESET}")

    # Executar testes síncronos
    sync_results = run_sync_tests()

    # Executar testes assíncronos
    async_results = asyncio.run(run_async_tests())

    # Consolidar resultados
    all_results = sync_results + async_results

    # Sumário
    print(f"\n{Colors.BLUE}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BLUE}SUMÁRIO{Colors.RESET}")
    print(f"{Colors.BLUE}{'=' * 70}{Colors.RESET}\n")

    passed = sum(1 for _, result in all_results if result)
    failed = len(all_results) - passed

    for name, result in all_results:
        status = f"{Colors.GREEN}PASSOU{Colors.RESET}" if result else f"{Colors.RED}FALHOU{Colors.RESET}"
        print(f"{name}: {status}")

    print(f"\n{Colors.BLUE}{'=' * 70}{Colors.RESET}")
    print(f"Total: {len(all_results)} testes")
    print(f"{Colors.GREEN}Passou: {passed}{Colors.RESET}")
    print(f"{Colors.RED}Falhou: {failed}{Colors.RESET}")
    print(f"{Colors.BLUE}{'=' * 70}{Colors.RESET}\n")

    # Código de saída
    if failed == 0:
        print(f"{Colors.GREEN}✓ Todos os testes passaram!{Colors.RESET}\n")
        return 0
    elif failed < len(all_results) / 2:
        print(f"{Colors.YELLOW}⚠ Alguns testes falharam{Colors.RESET}\n")
        return 1
    else:
        print(f"{Colors.RED}✗ Muitos testes falharam{Colors.RESET}\n")
        return 2


if __name__ == "__main__":
    sys.exit(main())
