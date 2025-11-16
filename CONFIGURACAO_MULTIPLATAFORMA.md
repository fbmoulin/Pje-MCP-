# 🔧 Configuração Multiplataforma - TJES PJE MCP

Este projeto fornece arquivos de configuração específicos para cada plataforma.

---

## 📁 Arquivos Disponíveis

| Arquivo | Plataforma | Destino |
|---------|-----------|---------|
| `claude_desktop_config.json` | **WSL/Linux** | `~/.config/Claude/claude_desktop_config.json` |
| `claude_desktop_config.linux.json` | **Linux nativo** | `~/.config/Claude/claude_desktop_config.json` |
| `claude_desktop_config.windows.json` | **Windows** | `%APPDATA%\Claude\claude_desktop_config.json` |
| `claude_desktop_config.macos.json` | **macOS** | `~/Library/Application Support/Claude/claude_desktop_config.json` |

---

## 🚀 Instalação por Plataforma

### 🐧 Linux / WSL

```bash
# 1. Copiar configuração
cp claude_desktop_config.json ~/.config/Claude/claude_desktop_config.json

# 2. Ajustar path do projeto (se necessário)
# Edite o arquivo e mude 'cwd' para o caminho correto:
# "cwd": "/mnt/c/Projetos2/mcp_pje"  (WSL)
# "cwd": "${HOME}/projetos/mcp_pje"  (Linux nativo)

# 3. Reiniciar Claude Desktop
```

**Path atual (WSL)**: `/mnt/c/Projetos2/mcp_pje`

**Para Linux nativo**: Use `claude_desktop_config.linux.json`

---

### 🪟 Windows

```powershell
# 1. Copiar configuração
copy claude_desktop_config.windows.json "%APPDATA%\Claude\claude_desktop_config.json"

# 2. Ajustar path do projeto
# Edite o arquivo e mude 'cwd' para o caminho correto:
# "cwd": "C:\\Projetos2\\mcp_pje"

# 3. Reiniciar Claude Desktop
```

**Path atual**: `C:\Projetos2\mcp_pje`

---

### 🍎 macOS

```bash
# 1. Copiar configuração
cp claude_desktop_config.macos.json ~/Library/Application\ Support/Claude/claude_desktop_config.json

# 2. Ajustar path do projeto
# Edite o arquivo e mude 'cwd' para o caminho correto:
# "cwd": "${HOME}/projetos/mcp_pje"

# 3. Reiniciar Claude Desktop
```

**Path típico**: `~/projetos/mcp_pje`

---

## ⚙️ Ajustes Necessários

### 1. Working Directory (`cwd`)

**Você DEVE ajustar** o caminho do projeto em cada configuração:

**WSL**:
```json
"cwd": "/mnt/c/Projetos2/mcp_pje"
```

**Linux**:
```json
"cwd": "${HOME}/projetos/mcp_pje"
```

**Windows**:
```json
"cwd": "C:\\Projetos2\\mcp_pje"
```

**macOS**:
```json
"cwd": "${HOME}/projetos/mcp_pje"
```

### 2. Certificado Digital (A1)

Ajuste o caminho do certificado PFX:

**WSL/Linux/macOS**:
```json
"PJE_CERT_PATH": "${HOME}/.certificates/tjes_pje.pfx"
```

**Windows**:
```json
"PJE_CERT_PATH": "${USERPROFILE}\\.certificates\\tjes_pje.pfx"
```

### 3. Senha do Certificado

Configure a variável de ambiente **antes** de abrir Claude Desktop:

**WSL/Linux/macOS**:
```bash
export PJE_CERT_PASSWORD="sua_senha_aqui"
```

**Windows (PowerShell)**:
```powershell
$env:PJE_CERT_PASSWORD = "sua_senha_aqui"
```

**Windows (CMD)**:
```cmd
set PJE_CERT_PASSWORD=sua_senha_aqui
```

---

## 🔍 Diferenças Entre Versões

### Comando Python

| Plataforma | Comando |
|-----------|---------|
| WSL | `python` |
| Linux | `python3` |
| Windows | `python` |
| macOS | `python3` |

### Variáveis de Ambiente

| Plataforma | Home Directory |
|-----------|---------------|
| WSL/Linux/macOS | `${HOME}` |
| Windows | `${USERPROFILE}` |

### Atalho Global

| Plataforma | Atalho |
|-----------|--------|
| WSL/Linux/Windows | `Ctrl+Space` |
| macOS | `Cmd+Space` |

---

## ✅ Verificação

Após copiar a configuração, verifique se está correta:

### 1. Verificar arquivo copiado

**WSL/Linux**:
```bash
cat ~/.config/Claude/claude_desktop_config.json
```

**Windows**:
```powershell
type "%APPDATA%\Claude\claude_desktop_config.json"
```

**macOS**:
```bash
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

### 2. Testar execução manual

**Todos os sistemas**:
```bash
cd /caminho/do/projeto
python -m tjes_pje_mcp.server
python -m datajud_mcp.server
```

Se mostrar erro de MCP (normal), significa que a execução está funcionando!

### 3. Verificar logs do Claude Desktop

**WSL/Linux**:
```bash
tail -f ~/.config/Claude/logs/mcp*.log
```

**Windows**:
```powershell
Get-Content "$env:APPDATA\Claude\logs\mcp*.log" -Wait
```

**macOS**:
```bash
tail -f ~/Library/Logs/Claude/mcp*.log
```

---

## 🐛 Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'tjes_pje_mcp'"

**Causa**: `cwd` (working directory) está incorreto.

**Solução**: Ajuste o caminho `cwd` na configuração para o diretório raiz do projeto.

---

### Erro: "No such file or directory"

**Causa**: Path do projeto está errado.

**Solução**:
1. Verifique o caminho real do projeto
2. Ajuste `cwd` na configuração
3. Use caminhos absolutos (não relativos)

---

### Erro: "python: command not found"

**Causa**: Python não está instalado ou não está no PATH.

**Solução**:
- **Linux**: `sudo apt install python3`
- **macOS**: `brew install python3`
- **Windows**: Instalar do [python.org](https://python.org)

---

### MCP não aparece no Claude Desktop

**Soluções**:

1. **Reiniciar Claude Desktop** completamente (fechar todas as janelas)
2. **Verificar logs** para erros
3. **Testar execução manual** dos servidores
4. **Verificar sintaxe JSON** da configuração

---

## 📝 Exemplo Completo (WSL)

```bash
# 1. Clone/navegue para o projeto
cd /mnt/c/Projetos2/mcp_pje

# 2. Instale dependências
pip install -r tjes_pje_mcp/requirements.txt
pip install -r datajud_mcp/requirements.txt

# 3. Configure certificado
mkdir -p ~/.certificates
# Copie seu certificado .pfx para ~/.certificates/

# 4. Configure senha
export PJE_CERT_PASSWORD="sua_senha"
# Adicione ao ~/.bashrc para persistir:
echo 'export PJE_CERT_PASSWORD="sua_senha"' >> ~/.bashrc

# 5. Copie configuração
cp claude_desktop_config.json ~/.config/Claude/claude_desktop_config.json

# 6. Reinicie Claude Desktop

# 7. Teste no Claude Desktop
# Use ferramenta: pje_check_session
```

---

## 🎯 Resumo

1. ✅ Escolha o arquivo de configuração da sua plataforma
2. ✅ Copie para o diretório correto do Claude Desktop
3. ✅ Ajuste `cwd` para o caminho real do projeto
4. ✅ Configure variável `PJE_CERT_PASSWORD`
5. ✅ Reinicie Claude Desktop
6. ✅ Teste com `pje_check_session`

---

**Desenvolvido para**: WSL, Linux, Windows e macOS
**Última atualização**: 2025-11-16
**Versão**: 1.0.0 (Safe ID Edition)
