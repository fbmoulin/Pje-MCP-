# Guia Completo: Safe ID com TJES PJE MCP Server

**Solução Híbrida: Autenticação Browser + Sessão Persistente**

---

## 📋 O Que É Safe ID?

**Safe ID** (Safeweb/Certisign) é um **certificado digital A3 em nuvem** onde:

- ✅ Certificado armazenado em HSM na nuvem (não no seu computador)
- ✅ Acesso via navegador web (sem smart card físico)
- ✅ Autenticação com senha ou biometria
- ✅ Compatível com PJE e sistemas judiciais
- ❌ **NÃO** fornece arquivo .pfx para download
- ❌ **NÃO** instala no Windows Certificate Store

## 🎯 Como Funciona a Integração

Nossa solução usa **Playwright MCP** para:

1. **Primeira vez**: Autentica via browser (popup Safe ID)
2. **Salva sessão**: Cookies e estado do browser persistidos
3. **Próximas vezes**: Reutiliza sessão automaticamente
4. **Resultado**: Autentica uma vez a cada 8 horas!

### Arquitetura

```
┌─────────────────┐
│  Claude Code    │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌─────┐   ┌──────┐
│ PJE │   │Play  │
│ MCP │   │wright│
└─────┘   └──┬───┘
              │
          ┌───┴────┐
          │Browser │
          │Context │ ← Sessão salva aqui!
          └───┬────┘
              │
         ┌────┴─────┐
         │ Safe ID  │
         │   HSM    │
         └──────────┘
```

---

## 🚀 Setup Inicial (Uma Vez)

### 1. Verificar Dependências

```bash
# Node.js 18+
node --version

# Playwright MCP
npx -y @playwright/mcp@latest
```

### 2. Configurar Claude Desktop

Seu `claude_desktop_config.json` já está configurado com os 3 servidores:

```json
{
  "mcpServers": {
    "playwright-tjes": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp@latest"]
    },
    "tjes-pje": {
      "command": "python",
      "args": ["/mnt/c/Projetos2/mcp_pje/tjes_pje_mcp/server.py"]
    },
    "datajud-tjes": {
      "command": "python",
      "args": ["/mnt/c/Projetos2/mcp_pje/datajud_mcp/server.py"]
    }
  }
}
```

### 3. Reiniciar Claude Desktop

Após copiar a configuração para:
- **Linux**: `~/.config/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

---

## 🔐 Autenticação (Primeira Vez)

### Passo 1: Verificar Sessão

```
Use a ferramenta: pje_check_session
```

**Resultado esperado**: "❌ Sessão não encontrada"

### Passo 2: Iniciar Autenticação

```
Use a ferramenta: pje_authenticate_safe_id
```

**Resultado**: Instruções detalhadas do que fazer

### Passo 3: Navegar ao PJE

```
Use a ferramenta Playwright: browser_navigate
Parâmetros:
- url: "https://sistemas.tjes.jus.br/pje"
```

**O que acontece**:
- Browser abre (ou reutiliza contexto existente)
- Página do PJE carrega
- Você vê opções de login

### Passo 4: Clicar em "Certificado Digital"

```
Use a ferramenta Playwright: browser_snapshot
```

**Primeiro captura a página para ver elementos disponíveis**

```
Use a ferramenta Playwright: browser_click
Parâmetros:
- element: "Botão ou link de acesso com certificado"
- ref: <referência do snapshot>
```

### Passo 5: Autenticar no Safe ID

**Popup Safe ID abrirá automaticamente!**

No popup:
1. Digite seu CPF/CNPJ
2. Digite sua senha Safe ID
3. OU use biometria (se configurado)
4. Clique em "Entrar" ou "Autenticar"

**Aguarde...** Safe ID valida certificado no HSM

### Passo 6: Confirmar Login

Após autenticação bem-sucedida:

```
Use a ferramenta Playwright: browser_snapshot
```

**Você deve ver**: Página autenticada do PJE (menu, processos, etc.)

### Passo 7: Verificar Sessão Salva

```
Use a ferramenta: pje_check_session
```

**Resultado esperado**: "✅ Sessão válida e ativa"

---

## 🎉 Uso Normal (Após Primeira Autenticação)

### Consultar Processo

```
1. Verificar sessão (opcional):
   pje_check_session

2. Navegar ao PJE:
   browser_navigate -> https://sistemas.tjes.jus.br/pje

3. Preencher número do processo:
   browser_fill_form com número CNJ

4. Clicar em Pesquisar:
   browser_click no botão

5. Capturar resultado:
   browser_snapshot
```

**IMPORTANTE**: Não precisa autenticar novamente! Sessão reutilizada automaticamente.

### Listar Processos com Filtros

```
1. browser_navigate -> PJE

2. browser_fill_form:
   - Órgão julgador: "1ª Vara Cível"
   - Classe: "Ação Civil Pública"
   - Data início: "01/01/2024"
   - Data fim: "31/12/2024"

3. browser_click -> Botão "Buscar"

4. browser_snapshot -> Ver resultados
```

### Download de Documentos

```
1. browser_navigate -> Processo específico

2. browser_click -> Documento desejado

3. Aguardar download automático

4. Arquivo salvo em ~/Downloads/
```

---

## ⏱️ Duração da Sessão

### Parâmetros Padrão

- **Duração**: 8 horas
- **Localização**: `~/.cache/tjes-pje-mcp/sessions/tjes_pje_default/`
- **Arquivos salvos**:
  - `cookies.json` - Cookies do browser
  - `state.json` - Estado da sessão
  - `metadata.json` - Informações da sessão

### Customizar Duração

Edite `.env`:

```bash
# Aumentar para 12 horas
PJE_SESSION_MAX_AGE_HOURS=12

# Ou reduzir para 4 horas
PJE_SESSION_MAX_AGE_HOURS=4
```

### Verificar Status

```
Use: pje_check_session

Retorna:
- Idade da sessão
- Tempo até expiração
- Método de autenticação
- Última utilização
```

---

## 🔄 Re-autenticação (Após Expiração)

### Quando Sessão Expira

Após 8 horas (ou tempo configurado):

```
pje_check_session

Retorna: "⚠️ Sessão expirada"
```

### Como Re-autenticar

**Opção 1: Automática**

Simplesmente use qualquer ferramenta Playwright:

```
browser_navigate -> PJE
```

**Sistema detecta**: Sessão expirada
**Safe ID abre**: Popup de autenticação
**Você autentica**: Mesmos passos da primeira vez
**Sessão renovada**: Mais 8 horas!

**Opção 2: Manual**

```
1. pje_clear_session
   -> Remove sessão antiga

2. pje_authenticate_safe_id
   -> Prepara nova autenticação

3. Seguir passos de autenticação
```

---

## 🛠️ Troubleshooting

### Problema 1: "Safe ID não abre"

**Sintomas**: Popup Safe ID não aparece

**Soluções**:

```bash
# 1. Verificar se Playwright está instalado
npx -y @playwright/mcp@latest

# 2. Limpar cache do browser
rm -rf ~/.cache/tjes-pje-mcp/sessions/*

# 3. Tentar novamente
pje_authenticate_safe_id
```

### Problema 2: "Sessão não salva"

**Sintomas**: Sempre pede autenticação

**Soluções**:

```bash
# 1. Verificar permissões
ls -la ~/.cache/tjes-pje-mcp/sessions/

# 2. Criar diretório se não existir
mkdir -p ~/.cache/tjes-pje-mcp/sessions/
chmod 755 ~/.cache/tjes-pje-mcp/sessions/

# 3. Verificar espaço em disco
df -h ~
```

### Problema 3: "Browser não mantém login"

**Sintomas**: Logout após fechar browser

**Causa**: Persistent context não configurado

**Solução**: Verificar que Playwright usa `user_data_dir`:

```python
# Já está configurado no código!
# session_manager.py linha ~250
'user_data_dir': str(self.session_path)
```

### Problema 4: "Erro de certificado"

**Sintomas**: Safe ID retorna erro de certificado

**Possíveis causas**:
- Certificado Safe ID expirado
- Senha incorreta
- Problema no HSM da Safeweb

**Soluções**:
1. Verificar validade do certificado no portal Safe ID
2. Confirmar senha digitada corretamente
3. Entrar em contato com suporte Safeweb

---

## 📊 Comparação: Safe ID vs Certificado A1

| Característica | Safe ID | Certificado A1 |
|----------------|---------|----------------|
| **Armazenamento** | Nuvem (HSM) | Arquivo local (.pfx) |
| **Hardware** | Nenhum | Nenhum |
| **Autenticação** | Senha/Bio | Senha do arquivo |
| **Setup no projeto** | Playwright | Certificate Manager |
| **Primeira vez** | Popup browser | Instalar .pfx |
| **Uso contínuo** | Sessão 8h | Sempre disponível |
| **Segurança** | Alta (HSM) | Média (local) |
| **Mobilidade** | Total (qualquer PC) | Limitada (arquivo) |
| **Automação** | Parcial (1ª vez manual) | Total (senha em .env) |

---

## 🎯 Workflows Recomendados

### Workflow 1: Consulta Rápida

```
Tempo total: ~30 segundos (após 1ª autenticação)

1. pje_check_session (5s)
   ✅ Sessão válida

2. browser_navigate PJE (10s)
   ✅ Login automático

3. browser_fill_form + click (10s)
   ✅ Busca processo

4. browser_snapshot (5s)
   ✅ Resultado capturado
```

### Workflow 2: Múltiplas Consultas

```
Tempo total: ~2 minutos para 10 processos

1. pje_check_session
   ✅ Uma vez no início

2. Para cada processo (loop):
   - browser_fill_form
   - browser_click
   - browser_snapshot
   - Aguardar 5s entre consultas

3. Resultado: 10 processos consultados
   Sem re-autenticação!
```

### Workflow 3: Download em Massa

```
Tempo total: Depende do tamanho dos arquivos

1. pje_check_session

2. browser_navigate -> Lista de processos

3. Para cada processo:
   - browser_click -> Abrir processo
   - Para cada documento:
     - browser_click -> Download
     - Aguardar conclusão
   - Voltar à lista

4. Resultado: Todos documentos em ~/Downloads/
```

---

## 🔒 Segurança

### Dados Salvos Localmente

```bash
~/.cache/tjes-pje-mcp/sessions/tjes_pje_default/
├── cookies.json       # Cookies HTTP
├── state.json         # Estado do Playwright
└── metadata.json      # Informações da sessão
```

**Conteúdo**:
- ✅ Cookies de sessão (não contém senha Safe ID)
- ✅ Tokens temporários (expiram)
- ❌ **NÃO** contém senha do Safe ID
- ❌ **NÃO** contém certificado digital

### Boas Práticas

1. **Proteção do Diretório**:
```bash
chmod 700 ~/.cache/tjes-pje-mcp/
```

2. **Limpar Sessão ao Sair**:
```bash
# Ao terminar trabalho:
pje_clear_session
```

3. **Não Compartilhar**:
- Nunca compartilhe arquivos de `sessions/`
- São específicos para sua autenticação

4. **Backup Seguro**:
- NÃO incluir `sessions/` em backups públicos
- Se necessário backup, criptografar

---

## 🎓 Exemplos Avançados

### Exemplo 1: Monitoramento de Processos

```python
# Pseudocódigo do workflow

PROCESSOS = [
    "0001-19.2023.8.08.0001",
    "0002-19.2023.8.08.0001",
    ...
]

for numero in PROCESSOS:
    # 1. Verificar se há movimentações novas
    browser_navigate(f"PJE/processo/{numero}")

    # 2. Capturar última movimentação
    snapshot = browser_snapshot()

    # 3. Comparar com estado anterior
    if snapshot != last_state[numero]:
        # 4. Notificar mudança
        send_notification(numero, snapshot)

    # 5. Aguardar entre consultas
    sleep(10)
```

### Exemplo 2: Extração de Dados

```python
# Workflow completo

1. Autenticar (se necessário)
2. Navegar à busca avançada
3. Preencher filtros:
   - Período: 01/2024 a 12/2024
   - Classe: Ação Civil Pública
   - Órgão: 1ª Vara Cível

4. Executar busca
5. Para cada página de resultados:
   - browser_snapshot
   - Extrair dados (número, partes, etc.)
   - Próxima página

6. Exportar para CSV
```

### Exemplo 3: Download Automático

```python
# Download de todos PDFs de um processo

1. browser_navigate(processo_url)
2. browser_snapshot() -> identificar documentos
3. Para cada documento:
   - browser_click(link_documento)
   - browser_wait_for(download_complete)
   - Renomear arquivo com metadados
4. Organizar em pastas por processo
```

---

## 📝 Checklist de Uso

### Primeira Vez (Setup)

- [ ] Node.js 18+ instalado
- [ ] Playwright MCP testado (`npx -y @playwright/mcp@latest`)
- [ ] Claude Desktop configurado
- [ ] Claude Desktop reiniciado
- [ ] Senha Safe ID em mãos

### Autenticação Inicial

- [ ] `pje_check_session` executado
- [ ] `pje_authenticate_safe_id` executado
- [ ] `browser_navigate` para PJE
- [ ] Clicar em "Certificado Digital"
- [ ] Popup Safe ID aberto
- [ ] Autenticação completada
- [ ] `pje_check_session` retorna "válida"

### Uso Diário

- [ ] Verificar sessão antes de começar
- [ ] Usar Playwright para consultas
- [ ] Limpar sessão ao terminar (opcional)

---

## 🆘 Suporte

### Logs do Sistema

```bash
# Ver logs do MCP Server
tail -f ~/.config/Claude/logs/mcp*.log

# Ver logs do Playwright
# (mostrados no browser console se headless=false)
```

### Contatos

- **Safe ID**: https://www.safeid.com.br/suporte
- **Safeweb**: suporte@safeweb.com.br
- **TJES**: https://www.tjes.jus.br/

---

## 🎉 Resultado Final

Com Safe ID + Playwright + Sessão Persistente você tem:

✅ **Primeira autenticação**: ~60 segundos (popup Safe ID)
✅ **Próximas consultas**: ~10 segundos (sem autenticar)
✅ **Duração da sessão**: 8 horas
✅ **Segurança**: Certificado em HSM (nuvem)
✅ **Mobilidade**: Funciona em qualquer computador
✅ **Automação**: Múltiplas consultas sem intervenção

**Melhor dos dois mundos**: Segurança do A3 + Praticidade do A1!

---

**Desenvolvido com ❤️ usando Claude Code e Playwright**
