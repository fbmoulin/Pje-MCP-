# 🧪 Guia de Teste - Safe ID Integration

**Teste Manual Passo-a-Passo**

---

## ✅ Testes Automatizados - CONCLUÍDOS

```
Session Manager Tests: 8/8 PASSOU ✅
- Criação SessionManager: ✅
- Metadados da Sessão: ✅
- Verificação de Expiração: ✅
- Informações da Sessão: ✅
- Remoção de Sessão: ✅
- Configuração Playwright: ✅
- Instruções Helper: ✅
- Formatação de Info: ✅
```

**Resultado**: Session Manager está 100% funcional!

---

## 🧪 Teste Manual com Safe ID Real

Agora vamos testar com seu certificado Safe ID real!

### Pré-requisitos

- [x] Certificado Safe ID válido
- [x] Senha/biometria Safe ID configurada
- [x] Claude Desktop instalado
- [x] Node.js 18+ instalado
- [ ] Playwright MCP instalado
- [ ] Claude Desktop configurado

---

## Parte 1: Verificar Dependências

### 1.1 Node.js

```bash
node --version
```

**Esperado**: v18.0.0 ou superior

**Se não tiver**:
```bash
# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# macOS
brew install node@18

# Windows
# Download em: https://nodejs.org/
```

### 1.2 Playwright MCP

```bash
npx -y @playwright/mcp@latest
```

**Esperado**: Playwright MCP inicia sem erros

**Se der erro**:
```bash
npm cache clean --force
npx -y @playwright/mcp@latest
```

### 1.3 Claude Desktop Config

```bash
# Linux
cat ~/.config/Claude/claude_desktop_config.json

# Windows
type %APPDATA%\Claude\claude_desktop_config.json
```

**Esperado**: Ver configuração dos 3 servidores MCP

**Se não existir**:
```bash
# Linux
mkdir -p ~/.config/Claude
cp claude_desktop_config.json ~/.config/Claude/

# Windows (PowerShell)
xcopy claude_desktop_config.json "%APPDATA%\Claude\"
```

---

## Parte 2: Iniciar Claude Desktop

### 2.1 Reiniciar Claude Desktop

**Linux/Windows**:
- Fechar Claude Desktop completamente
- Abrir novamente
- Aguardar 10-15 segundos para servidores MCP iniciarem

### 2.2 Verificar Servidores MCP

No Claude Code, tente usar uma ferramenta:

```
Use a ferramenta: pje_check_session
```

**Esperado**:
```
❌ STATUS DA SESSÃO PJE TJES
Status: NÃO ENCONTRADA

Você precisa autenticar pela primeira vez
```

**Se der erro "Tool not found"**:
- Verificar logs: `~/.config/Claude/logs/mcp*.log`
- Verificar se servidores estão rodando
- Reiniciar Claude Desktop

---

## Parte 3: Primeira Autenticação Safe ID 🔐

### 3.1 Preparar Autenticação

**No Claude Code**:
```
Use a ferramenta: pje_authenticate_safe_id
```

**Esperado**:
```
🔐 AUTENTICAÇÃO SAFE ID PREPARADA

Instruções passo-a-passo:
1. Navegue para: https://sistemas.tjes.jus.br/pje
2. Clique em "Acesso com Certificado Digital"
...
```

✅ **CHECKPOINT**: Instruções exibidas

### 3.2 Navegar ao PJE

**No Claude Code**:
```
Use a ferramenta Playwright: browser_navigate

Parâmetros:
- url: https://sistemas.tjes.jus.br/pje
```

**O que acontece**:
- Browser Chromium abre
- Carrega página do PJE
- Você vê tela de login

✅ **CHECKPOINT**: Browser abriu com PJE

**Screenshot**: Tirar foto da tela para documentar

### 3.3 Capturar Snapshot da Página

**No Claude Code**:
```
Use a ferramenta Playwright: browser_snapshot
```

**Esperado**:
- Snapshot da página em formato acessível
- Elementos identificados (botões, links, etc.)

✅ **CHECKPOINT**: Snapshot capturado

**Procure**: Botão ou link "Certificado Digital" ou similar

### 3.4 Clicar em "Certificado Digital"

**No Claude Code**:
```
Use a ferramenta Playwright: browser_click

Parâmetros:
- element: "Acesso com certificado digital"
- ref: <copiar REF do snapshot>
```

**Exemplo de ref**: Se snapshot mostrou `[ref=btn-cert-123]`, usar:
```
- element: "Botão certificado"
- ref: btn-cert-123
```

**O que acontece**:
- Clique executado no browser
- Redirecionamento ou popup inicia

✅ **CHECKPOINT**: Clique executado

### 3.5 Popup Safe ID Abre 🎯

**O QUE VOCÊ DEVE VER**:
- Popup Safe ID abre automaticamente
- Formulário com campos:
  - CPF/CNPJ
  - Senha
  - OU opção de biometria

✅ **CHECKPOINT**: Popup Safe ID aberto

**Se popup não abrir**:
- Verificar bloqueador de popups
- Tentar `browser_navigate` novamente
- Verificar se Safe ID está ativo na sua conta

### 3.6 Autenticar no Safe ID ✍️

**NO POPUP SAFE ID** (manual):
1. Digite seu **CPF** ou **CNPJ**
2. Digite sua **senha Safe ID**
3. **OU** use **biometria** (se configurado)
4. Clique **"Entrar"** ou **"Autenticar"**

**Aguarde**: 5-15 segundos

**O que acontece**:
- Safe ID conecta ao HSM na nuvem
- Valida certificado
- Retorna credenciais ao PJE
- Popup fecha automaticamente
- PJE autentica você

✅ **CHECKPOINT**: Popup fechou, você está logado no PJE

### 3.7 Confirmar Login Bem-Sucedido

**No Claude Code**:
```
Use a ferramenta Playwright: browser_snapshot
```

**Esperado - Você deve ver**:
- Menu principal do PJE
- Nome do usuário logado
- Opções: "Meus Processos", "Consultar", etc.
- **SEM** tela de login

✅ **CHECKPOINT**: Login confirmado

**Screenshot**: Tirar foto da tela autenticada

### 3.8 Verificar Sessão Salva 💾

**No Claude Code**:
```
Use a ferramenta: pje_check_session
```

**Esperado**:
```
✅ STATUS DA SESSÃO PJE TJES
Status: VÁLIDA E ATIVA

Método de autenticação: safe_id
Criada em: 2025-11-16 10:30:00
Idade: 2 minutos
Tempo máximo: 8 horas

Status: Pronta para uso!
```

✅ **CHECKPOINT**: Sessão salva e válida!

**Verificar arquivos locais**:
```bash
ls -la ~/.cache/tjes-pje-mcp/sessions/tjes_pje_default/
```

**Esperado**:
```
cookies.json    (cookies HTTP)
state.json      (estado Playwright)
metadata.json   (info da sessão)
```

---

## Parte 4: Testar Reutilização de Sessão 🔄

### 4.1 Fechar Browser

**No browser Chromium**:
- Fechar completamente o browser
- Aguardar 5 segundos

### 4.2 Navegar Novamente SEM Re-Autenticar

**No Claude Code**:
```
Use a ferramenta Playwright: browser_navigate

Parâmetros:
- url: https://sistemas.tjes.jus.br/pje
```

**O que DEVE acontecer**:
- Browser abre
- PJE carrega
- **Login automático** (cookies reutilizados)
- **SEM popup Safe ID!**
- Você já está logado

✅ **CHECKPOINT**: Login automático funcionou!

**Se pedir login novamente**:
- Sessão pode ter expirado
- Verificar: `pje_check_session`
- Cookies podem não ter sido salvos
- Verificar permissões: `chmod 600 ~/.cache/tjes-pje-mcp/sessions/*/*`

### 4.3 Fazer Consulta Teste

**No Claude Code**:
```
Use Playwright: browser_snapshot
```

**Identificar campo de busca de processo**

```
Use Playwright: browser_fill_form

Parâmetros:
- fields: [
    {
      "name": "Número do Processo",
      "type": "textbox",
      "ref": "<ref do campo>",
      "value": "0000166-19.2023.8.08.0035"
    }
  ]
```

```
Use Playwright: browser_click

Parâmetros:
- element: "Botão Pesquisar"
- ref: <ref do botão>
```

```
Use Playwright: browser_snapshot
```

**Esperado**:
- Consulta executada
- Resultado exibido
- **SEM re-autenticação!**

✅ **CHECKPOINT**: Consulta sem re-autenticar!

---

## Parte 5: Testar Múltiplas Consultas

### 5.1 Fazer 5 Consultas Seguidas

**Repetir 5 vezes**:
1. `browser_fill_form` (número diferente)
2. `browser_click` (pesquisar)
3. `browser_snapshot` (resultado)
4. Aguardar 5 segundos

**Esperado**:
- Todas as 5 consultas executadas
- **ZERO re-autenticações**
- Sessão mantida

✅ **CHECKPOINT**: Múltiplas consultas sem re-auth!

### 5.2 Verificar Status da Sessão

```
Use: pje_check_session
```

**Esperado**:
```
✅ STATUS DA SESSÃO PJE TJES
Status: VÁLIDA E ATIVA

Idade: 15 minutos
Tempo máximo: 8 horas
```

✅ **CHECKPOINT**: Sessão ainda válida após uso!

---

## Parte 6: Testar Limpeza de Sessão

### 6.1 Limpar Sessão (Logout)

**No Claude Code**:
```
Use: pje_clear_session
```

**Esperado**:
```
✅ Sessão removida com sucesso

Detalhes da sessão removida:
Método: safe_id
Criada em: 2025-11-16 10:30:00
Idade: 20 minutos
```

✅ **CHECKPOINT**: Sessão removida

### 6.2 Verificar Arquivos Removidos

```bash
ls -la ~/.cache/tjes-pje-mcp/sessions/tjes_pje_default/
```

**Esperado**:
```
(vazio ou diretório não existe)
```

### 6.3 Confirmar Sessão Inválida

```
Use: pje_check_session
```

**Esperado**:
```
❌ STATUS DA SESSÃO PJE TJES
Status: NÃO ENCONTRADA
```

✅ **CHECKPOINT**: Logout confirmado!

---

## Parte 7: Teste de Expiração (Opcional)

### 7.1 Alterar Tempo de Expiração

**Editar `.env`**:
```bash
# Reduzir para 5 minutos (para teste)
PJE_SESSION_MAX_AGE_HOURS=0.083
```

### 7.2 Criar Nova Sessão

- Repetir Parte 3 (autenticação)
- Verificar sessão criada

### 7.3 Aguardar Expiração

- Aguardar 6 minutos

### 7.4 Verificar Expiração

```
Use: pje_check_session
```

**Esperado**:
```
⚠️ Sessão expirada

Idade da sessão: 6 minutos
Você precisa autenticar novamente
```

✅ **CHECKPOINT**: Expiração detectada!

### 7.5 Restaurar Configuração

**Editar `.env`**:
```bash
# Voltar para 8 horas
PJE_SESSION_MAX_AGE_HOURS=8
```

---

## 📊 Checklist de Validação Final

### Funcionalidades Testadas

- [ ] **Playwright MCP instalado**
- [ ] **Claude Desktop configurado**
- [ ] **Primeira autenticação Safe ID**
- [ ] **Popup Safe ID abriu**
- [ ] **Login bem-sucedido**
- [ ] **Sessão salva localmente**
- [ ] **Login automático (reutilização)**
- [ ] **Múltiplas consultas sem re-auth**
- [ ] **Limpeza de sessão (logout)**
- [ ] **Detecção de expiração**

### Métricas de Sucesso

- **Tempo primeira auth**: ~60 segundos ⏱️
- **Tempo login automático**: ~5 segundos ⚡
- **Consultas sem re-auth**: Ilimitadas ♾️
- **Duração sessão**: 8 horas 🕐
- **Taxa de sucesso**: 100% ✅

---

## 🎯 Resultados Esperados

### ✅ SUCESSO Total

Se você conseguiu:
1. ✅ Autenticar com Safe ID no popup
2. ✅ Sessão salva em `~/.cache/tjes-pje-mcp/`
3. ✅ Login automático sem popup
4. ✅ Múltiplas consultas sem re-autenticar
5. ✅ Logout e limpeza funcionam

**PARABÉNS! 🎉 Safe ID está 100% funcional!**

### ⚠️ PARCIAL

Se algumas partes funcionaram:
- Verificar logs: `~/.config/Claude/logs/`
- Ver seção Troubleshooting abaixo
- Reportar issues específicos

### ❌ FALHA

Se nada funcionou:
- Verificar pré-requisitos
- Revisar configuração
- Ver documentação completa
- Pedir ajuda com logs

---

## 🐛 Troubleshooting

### Problema 1: Popup Safe ID não abre

**Causas possíveis**:
- Bloqueador de popups ativo
- Safe ID não configurado na conta
- URL incorreta

**Soluções**:
```bash
# 1. Desativar bloqueador de popups no Chromium
# 2. Verificar conta Safe ID em https://www.safeid.com.br/
# 3. Tentar URL direta de login
```

### Problema 2: Sessão não salva

**Causas possíveis**:
- Permissões incorretas
- Disco cheio
- Path inexistente

**Soluções**:
```bash
# Verificar permissões
ls -la ~/.cache/tjes-pje-mcp/

# Criar diretório manualmente
mkdir -p ~/.cache/tjes-pje-mcp/sessions/
chmod 700 ~/.cache/tjes-pje-mcp/

# Verificar espaço
df -h ~
```

### Problema 3: Login não reutiliza sessão

**Causas possíveis**:
- Cookies expiraram
- Browser em modo incógnito
- Session path incorreto

**Soluções**:
```bash
# Verificar arquivos de sessão
cat ~/.cache/tjes-pje-mcp/sessions/tjes_pje_default/metadata.json

# Ver idade da sessão
Use: pje_check_session

# Re-criar sessão
Use: pje_clear_session
Use: pje_authenticate_safe_id
```

### Problema 4: Erro "Tool not found"

**Causas possíveis**:
- Servidor MCP não iniciou
- Configuração incorreta
- Path do Python incorreto

**Soluções**:
```bash
# Verificar logs
tail -f ~/.config/Claude/logs/mcp*.log

# Testar servidor manualmente
python /mnt/c/Projetos2/mcp_pje/tjes_pje_mcp/server.py

# Verificar config
cat ~/.config/Claude/claude_desktop_config.json | python -m json.tool
```

---

## 📝 Relatório de Teste

### Template

```markdown
# Relatório de Teste Safe ID - TJES PJE MCP

**Data**: ___/___/2025
**Testador**: ________________
**Ambiente**: Linux / Windows / macOS

## Resultados

- [ ] Testes automatizados: ___/8
- [ ] Primeira autenticação: OK / FALHOU
- [ ] Popup Safe ID: OK / FALHOU
- [ ] Sessão salva: OK / FALHOU
- [ ] Login automático: OK / FALHOU
- [ ] Múltiplas consultas: OK / FALHOU
- [ ] Limpeza sessão: OK / FALHOU

## Métricas

- Tempo primeira auth: ___ segundos
- Tempo login automático: ___ segundos
- Consultas executadas: ___
- Re-autenticações necessárias: ___

## Observações

___________________________________________
___________________________________________
___________________________________________

## Conclusão

✅ SUCESSO / ⚠️ PARCIAL / ❌ FALHA

## Screenshots

(Anexar screenshots dos checkpoints)
```

---

## 🎓 Próximos Passos

### Após Teste Bem-Sucedido

1. **Uso no dia-a-dia**:
   - Integrar no workflow diário
   - Explorar workflows práticos (`WORKFLOWS_SAFE_ID.md`)
   - Medir economia de tempo real

2. **Otimizações**:
   - Ajustar tempo de expiração conforme necessidade
   - Configurar modo headless para automações
   - Criar atalhos para consultas frequentes

3. **Documentação**:
   - Documentar casos de uso específicos
   - Criar biblioteca de queries comuns
   - Compartilhar experiência

---

## 📚 Recursos

- **Guia Completo**: `docs/SAFE_ID_GUIDE.md`
- **Workflows Práticos**: `docs/WORKFLOWS_SAFE_ID.md`
- **Resumo Executivo**: `docs/SAFE_ID_SUMMARY.md`
- **README Principal**: `README.md`
- **Status do Projeto**: `STATUS.md`

---

**Boa sorte com os testes! 🚀**

**Em caso de dúvidas, consulte a documentação ou abra um issue.**

---

**Desenvolvido com ❤️ por Claude Code**
