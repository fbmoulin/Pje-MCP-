"""Shared utility functions for TJES PJE MCP servers.

This module provides common utility functions used across multiple MCP servers:
- Environment variable parsing and validation
- Text formatting and display utilities
"""

import os
import logging
from typing import Optional

from .constants import BOX_WIDTH, ICONS

logger = logging.getLogger(__name__)


# =============================================================================
# ENVIRONMENT VARIABLE UTILITIES
# =============================================================================

def get_int_env(
    var_name: str,
    default: int,
    min_value: int = 1,
    max_value: Optional[int] = None
) -> int:
    """Obtém variável de ambiente inteira com validação robusta.

    Esta função lê uma variável de ambiente, converte para inteiro e aplica
    validações de limites mínimo e máximo. Se a conversão falhar ou o valor
    estiver fora dos limites, retorna o valor padrão com um aviso no log.

    Args:
        var_name: Nome da variável de ambiente a ler
        default: Valor padrão se a variável não existir ou for inválida
        min_value: Valor mínimo permitido (padrão: 1)
        max_value: Valor máximo permitido (padrão: None, sem limite)

    Returns:
        int: Valor da variável validado ou valor padrão

    Examples:
        >>> # Ler timeout com limites
        >>> timeout = get_int_env("TIMEOUT", default=30, min_value=5, max_value=120)

        >>> # Ler tentativas de retry
        >>> retries = get_int_env("RETRIES", default=3, min_value=1, max_value=10)

    Comportamento:
        - Variável não definida → retorna default
        - Valor inválido (não numérico) → retorna default com warning
        - Valor < min_value → retorna min_value com warning
        - Valor > max_value → retorna max_value com warning
        - Valor válido dentro dos limites → retorna valor convertido
    """
    value_str = os.getenv(var_name)

    # Variável não definida
    if value_str is None:
        return default

    # Tentar converter para inteiro
    try:
        value = int(value_str)
    except (ValueError, TypeError) as e:
        logger.warning(
            f"{var_name}='{value_str}' não é um inteiro válido. "
            f"Usando valor padrão: {default}. Erro: {e}"
        )
        return default

    # Validar limite mínimo
    if value < min_value:
        logger.warning(
            f"{var_name}={value} é menor que o mínimo permitido ({min_value}). "
            f"Usando {min_value}."
        )
        return min_value

    # Validar limite máximo
    if max_value is not None and value > max_value:
        logger.warning(
            f"{var_name}={value} é maior que o máximo permitido ({max_value}). "
            f"Usando {max_value}."
        )
        return max_value

    # Valor válido
    return value


# =============================================================================
# TEXT FORMATTING UTILITIES
# =============================================================================

def format_box(title: str, content: str, width: int = BOX_WIDTH) -> str:
    """Formata conteúdo dentro de uma caixa com título.

    Args:
        title: Título da caixa
        content: Conteúdo a ser exibido
        width: Largura da caixa em caracteres (padrão: BOX_WIDTH)

    Returns:
        str: Texto formatado em caixa

    Example:
        >>> print(format_box("Status", "Sessão ativa"))
        ╔════════════════════════════════════════╗
        ║              Status                     ║
        ╠════════════════════════════════════════╣
        ║ Sessão ativa                           ║
        ╚════════════════════════════════════════╝
    """
    # Caracteres de caixa
    top_left = "╔"
    top_right = "╗"
    bottom_left = "╚"
    bottom_right = "╝"
    horizontal = "═"
    vertical = "║"
    left_divider = "╠"
    right_divider = "╣"

    # Linha superior
    top_line = f"{top_left}{horizontal * (width - 2)}{top_right}"

    # Título centralizado
    title_padding = width - 2 - len(title)
    left_padding = title_padding // 2
    right_padding = title_padding - left_padding
    title_line = f"{vertical}{' ' * left_padding}{title}{' ' * right_padding}{vertical}"

    # Divisor
    divider = f"{left_divider}{horizontal * (width - 2)}{right_divider}"

    # Conteúdo (quebrar em linhas se necessário)
    content_lines = []
    for line in content.split("\n"):
        # Se a linha for muito longa, quebrar
        if len(line) > width - 4:
            # Quebrar linha longa em múltiplas linhas
            while len(line) > width - 4:
                content_lines.append(line[:width - 4])
                line = line[width - 4:]
        if line:  # Adicionar linha restante
            content_lines.append(line)

    # Formatar linhas de conteúdo
    formatted_content = []
    for line in content_lines:
        padding = width - 2 - len(line)
        formatted_content.append(f"{vertical} {line}{' ' * (padding - 1)}{vertical}")

    # Linha inferior
    bottom_line = f"{bottom_left}{horizontal * (width - 2)}{bottom_right}"

    # Juntar todas as partes
    parts = [top_line, title_line, divider] + formatted_content + [bottom_line]
    return "\n".join(parts)


def format_key_value(
    key: str,
    value: str,
    icon: Optional[str] = None,
    width: int = BOX_WIDTH
) -> str:
    """Formata par chave-valor com alinhamento e ícone opcional.

    Args:
        key: Chave (nome do campo)
        value: Valor (dados do campo)
        icon: Ícone opcional para prefixar a linha
        width: Largura máxima da linha

    Returns:
        str: Linha formatada

    Example:
        >>> print(format_key_value("Status", "Ativo", icon="✅"))
        ✅ Status: Ativo
    """
    prefix = f"{icon} " if icon else ""
    return f"{prefix}{key}: {value}"


def format_section(title: str, items: list[tuple[str, str]], icon: Optional[str] = None) -> str:
    """Formata uma seção com título e itens chave-valor.

    Args:
        title: Título da seção
        items: Lista de tuplas (chave, valor)
        icon: Ícone opcional para o título

    Returns:
        str: Seção formatada

    Example:
        >>> items = [("Nome", "João"), ("Idade", "30")]
        >>> print(format_section("Dados Pessoais", items, icon="ℹ️"))
        ℹ️ Dados Pessoais
        ────────────────
        Nome: João
        Idade: 30
    """
    lines = []

    # Título com ícone
    title_line = f"{icon} {title}" if icon else title
    lines.append(title_line)
    lines.append("─" * len(title_line))

    # Itens
    for key, value in items:
        lines.append(f"{key}: {value}")

    return "\n".join(lines)


def format_bullet_list(items: list[str], bullet: str = "•") -> str:
    """Formata lista com bullets.

    Args:
        items: Lista de itens
        bullet: Caractere do bullet (padrão: "•")

    Returns:
        str: Lista formatada

    Example:
        >>> items = ["Item 1", "Item 2", "Item 3"]
        >>> print(format_bullet_list(items))
        • Item 1
        • Item 2
        • Item 3
    """
    return "\n".join([f"{bullet} {item}" for item in items])


def format_success(message: str) -> str:
    """Formata mensagem de sucesso com ícone.

    Args:
        message: Mensagem a formatar

    Returns:
        str: Mensagem formatada

    Example:
        >>> print(format_success("Operação concluída"))
        ✅ Operação concluída
    """
    return f"{ICONS['success']} {message}"


def format_error(message: str) -> str:
    """Formata mensagem de erro com ícone.

    Args:
        message: Mensagem a formatar

    Returns:
        str: Mensagem formatada

    Example:
        >>> print(format_error("Falha na operação"))
        ❌ Falha na operação
    """
    return f"{ICONS['error']} {message}"


def format_warning(message: str) -> str:
    """Formata mensagem de aviso com ícone.

    Args:
        message: Mensagem a formatar

    Returns:
        str: Mensagem formatada

    Example:
        >>> print(format_warning("Atenção necessária"))
        ⚠️ Atenção necessária
    """
    return f"{ICONS['warning']} {message}"


def format_info(message: str) -> str:
    """Formata mensagem informativa com ícone.

    Args:
        message: Mensagem a formatar

    Returns:
        str: Mensagem formatada

    Example:
        >>> print(format_info("Informação útil"))
        ℹ️ Informação útil
    """
    return f"{ICONS['info']} {message}"
