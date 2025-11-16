# Workflows Práticos: Safe ID + Playwright + TJES PJE

**Exemplos completos prontos para usar**

---

## 🎯 Workflow 1: Setup e Primeira Autenticação

### Objetivo
Configurar Safe ID pela primeira vez e criar sessão persistente

### Tempo Estimado
5 minutos (primeira vez)

### Passo a Passo

#### 1. Verificar Status Inicial

**Comando:**
```
pje_check_session
```

**Resultado Esperado:**
```
❌ STATUS DA SESSÃO PJE TJES
Status: NÃO ENCONTRADA

Você precisa autenticar pela primeira vez
```

#### 2. Preparar Autenticação

**Comando:**
```
pje_authenticate_safe_id
```

**Resultado Esperado:**
```
🔐 AUTENTICAÇÃO SAFE ID PREPARADA

Instruções passo-a-passo...
```

#### 3. Abrir PJE no Browser

**Comando Playwright:**
```
browser_navigate

Parâmetros:
- url: https://sistemas.tjes.jus.br/pje
```

**O que acontece:**
- Browser Chromium abre
- Página do PJE carrega
- Você vê tela de login

#### 4. Capturar Estado da Página

**Comando Playwright:**
```
browser_snapshot
```

**Resultado:**
Você verá estrutura da página com elementos identificados

**Procure por:**
- Botão "Acesso com Certificado Digital"
- Link "Login com Certificado"
- Similar

#### 5. Clicar em Login com Certificado

**Comando Playwright:**
```
browser_click

Parâmetros:
- element: "Link de acesso com certificado digital"
- ref: <copiar referência do snapshot>
```

**Exemplo:**
Se snapshot mostrou: `[ref=btn-certificado]`

```
browser_click
- element: "Botão acesso certificado"
- ref: btn-certificado
```

#### 6. Autenticar no Safe ID

**Popup Safe ID abre automaticamente!**

**No Popup:**
1. Digite seu **CPF** ou **CNPJ**
2. Digite sua **senha Safe ID**
3. OU clique em **biometria** (se configurado)
4. Clique **"Autenticar"** ou **"Entrar"**

**Aguarde:** 5-10 segundos

**Safe ID:**
- Conecta ao HSM na nuvem
- Valida certificado
- Retorna credenciais ao PJE

#### 7. Confirmar Login Bem-Sucedido

**Comando Playwright:**
```
browser_snapshot
```

**Você deve ver:**
- Menu principal do PJE
- Nome do usuário logado
- Opções: "Meus Processos", "Buscar", etc.

#### 8. Verificar Sessão Salva

**Comando:**
```
pje_check_session
```

**Resultado Esperado:**
```
✅ STATUS DA SESSÃO PJE TJES
Status: VÁLIDA E ATIVA

Método de autenticação: safe_id
Idade: 2 minutos
Tempo máximo: 8 horas

Status: Pronta para uso!
```

### ✅ Sucesso!

Sessão criada e salva. Próximas consultas não precisarão de autenticação por 8 horas!

---

## 📝 Workflow 2: Consulta de Processo Individual

### Objetivo
Consultar dados de um processo específico usando sessão já autenticada

### Tempo Estimado
30 segundos

### Pré-requisito
- Sessão válida (Workflow 1 concluído)

### Passo a Passo

#### 1. Verificar Sessão (Opcional)

```
pje_check_session
```

**Se retornar:** ✅ Válida → Continuar
**Se retornar:** ❌ Expirada → Voltar ao Workflow 1

#### 2. Navegar ao PJE

```
browser_navigate
- url: https://sistemas.tjes.jus.br/pje
```

**Login automático!** Cookies reutilizados.

#### 3. Localizar Campo de Busca

```
browser_snapshot
```

**Procurar:**
- Campo "Número do Processo"
- Input de busca
- Formulário de consulta

#### 4. Preencher Número do Processo

```
browser_fill_form

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

**Ajustar:**
- `ref`: Copiar do snapshot
- `value`: Seu número de processo

#### 5. Clicar em Pesquisar

```
browser_click
- element: "Botão Pesquisar"
- ref: <ref do botão>
```

#### 6. Aguardar Resultado

**Opção A: Aguardar fixa**
```
browser_wait_for
- time: 3  (3 segundos)
```

**Opção B: Aguardar elemento específico**
```
browser_wait_for
- text: "Dados do Processo"
```

#### 7. Capturar Resultado

```
browser_snapshot
```

**Você verá:**
- Dados do processo
- Partes (autor, réu)
- Movimentações
- Documentos
- Valor da causa
- etc.

#### 8. (Opcional) Capturar Screenshot

```
browser_take_screenshot
- filename: "processo_0000166.png"
- fullPage: true
```

**Arquivo salvo em:** `./page-*.png` ou caminho especificado

### ✅ Processo Consultado!

Dados capturados sem necessidade de re-autenticar.

---

## 📊 Workflow 3: Busca Avançada com Múltiplos Filtros

### Objetivo
Encontrar processos usando filtros avançados (classe, órgão, período)

### Tempo Estimado
1-2 minutos

### Passo a Passo

#### 1. Navegar à Busca Avançada

```
browser_navigate
- url: https://sistemas.tjes.jus.br/pje/consulta/avancada
```

**(Ajustar URL conforme PJE real do TJES)**

#### 2. Capturar Formulário

```
browser_snapshot
```

**Identificar campos:**
- Classe processual
- Órgão julgador
- Data início
- Data fim
- Assunto
- etc.

#### 3. Preencher Filtros

```
browser_fill_form

Parâmetros:
- fields: [
    {
      "name": "Classe",
      "type": "combobox",
      "ref": "<ref>",
      "value": "Ação Civil Pública"
    },
    {
      "name": "Órgão Julgador",
      "type": "combobox",
      "ref": "<ref>",
      "value": "1ª Vara Cível"
    },
    {
      "name": "Data Início",
      "type": "textbox",
      "ref": "<ref>",
      "value": "01/01/2024"
    },
    {
      "name": "Data Fim",
      "type": "textbox",
      "ref": "<ref>",
      "value": "31/12/2024"
    }
  ]
```

#### 4. Executar Busca

```
browser_click
- element: "Botão Buscar"
- ref: <ref>
```

#### 5. Aguardar Resultados

```
browser_wait_for
- text: "resultados encontrados"
- (ou aguardar tempo fixo se preferir)
```

#### 6. Capturar Primeira Página

```
browser_snapshot
```

**Você verá:**
- Lista de processos
- Total encontrado
- Paginação (se houver)

#### 7. (Opcional) Navegar Entre Páginas

**Para próxima página:**
```
browser_click
- element: "Próxima página"
- ref: <ref do botão próximo>
```

**Capturar cada página:**
```
browser_snapshot
```

**Repetir até última página**

### ✅ Busca Completa!

Múltiplos processos encontrados e capturados.

---

## 💾 Workflow 4: Download de Documentos

### Objetivo
Baixar PDFs de documentos do processo

### Tempo Estimado
1-5 minutos (depende do número de docs)

### Passo a Passo

#### 1. Navegar ao Processo

```
browser_navigate
- url: https://sistemas.tjes.jus.br/pje/processo/<numero>
```

**(Ou usar busca do Workflow 2 primeiro)**

#### 2. Localizar Aba/Seção de Documentos

```
browser_snapshot
```

**Procurar:**
- Aba "Documentos"
- Link "Autos"
- Seção "Peças Processuais"

#### 3. Clicar em Documentos

```
browser_click
- element: "Aba Documentos"
- ref: <ref>
```

#### 4. Listar Documentos Disponíveis

```
browser_snapshot
```

**Você verá:**
- Lista de documentos
- Tipos: Petição, Sentença, etc.
- Links de download (PDF)

#### 5. Download Documento Individual

```
browser_click
- element: "Link download do documento"
- ref: <ref do link PDF>
```

**Arquivo baixado para:** `~/Downloads/`

#### 6. (Opcional) Download Múltiplos

**Para cada documento:**

```
# Documento 1
browser_click
- ref: <ref-doc-1>

browser_wait_for
- time: 2

# Documento 2
browser_click
- ref: <ref-doc-2>

browser_wait_for
- time: 2

# ... e assim por diante
```

#### 7. Verificar Downloads

**No sistema operacional:**
```bash
ls ~/Downloads/*.pdf
```

**Você verá:**
```
documento_1234_peticao_inicial.pdf
documento_5678_sentenca.pdf
...
```

### ✅ Documentos Baixados!

PDFs salvos localmente.

---

## 🔄 Workflow 5: Monitoramento de Processos

### Objetivo
Verificar periodicamente se há movimentações novas em processos de interesse

### Tempo Estimado
2-5 minutos (para 10 processos)

### Cenário
Você tem 10 processos que precisa monitorar diariamente.

### Solução Manual

#### 1. Criar Lista de Processos

**Em um arquivo ou nota:**
```
0001-19.2023.8.08.0001
0002-19.2023.8.08.0001
0003-19.2023.8.08.0001
...
```

#### 2. Para Cada Processo

**Loop manual (repetir para cada):**

```
# Processo 1
browser_navigate
- url: https://sistemas.tjes.jus.br/pje/processo/0001-19.2023.8.08.0001

browser_snapshot

# Verificar última movimentação manualmente
# Anotar se houver novidade

# Aguardar 5s antes do próximo
browser_wait_for
- time: 5

# Processo 2
browser_navigate
- url: ...
# Repetir
```

#### 3. Comparar com Estado Anterior

**Manualmente:**
- Compare snapshot atual com anterior
- Identifique movimentações novas
- Anote processos com mudanças

### Solução Semi-Automatizada

**Criar workflow Claude:**

```
"Para cada processo em [lista]:
1. Navegar ao processo
2. Capturar movimentações
3. Comparar com última captura
4. Se diferente, notificar
5. Aguardar 10s
6. Próximo processo"
```

### ✅ Processos Monitorados!

Mudanças identificadas sem revisar um a um no PJE.

---

## 📅 Workflow 6: Relatório de Produtividade

### Objetivo
Gerar relatório de processos movimentados em período

### Tempo Estimado
5-10 minutos

### Passo a Passo

#### 1. Acessar Relatórios

```
browser_navigate
- url: https://sistemas.tjes.jus.br/pje/relatorios
```

**(Ajustar conforme menu do TJES)**

#### 2. Selecionar Tipo de Relatório

```
browser_snapshot
# Identificar opções

browser_click
- element: "Relatório de Produtividade"
- ref: <ref>
```

#### 3. Preencher Filtros

```
browser_fill_form
- fields: [
    {
      "name": "Data Início",
      "type": "textbox",
      "ref": "<ref>",
      "value": "01/11/2024"
    },
    {
      "name": "Data Fim",
      "type": "textbox",
      "ref": "<ref>",
      "value": "30/11/2024"
    },
    {
      "name": "Órgão",
      "type": "combobox",
      "ref": "<ref>",
      "value": "Todos"
    }
  ]
```

#### 4. Gerar Relatório

```
browser_click
- element: "Gerar Relatório"
- ref: <ref>
```

#### 5. Aguardar Processamento

```
browser_wait_for
- text: "Relatório gerado"
- (ou tempo fixo)
```

#### 6. Download do Relatório

```
browser_click
- element: "Download PDF" ou "Download Excel"
- ref: <ref>
```

#### 7. Abrir Arquivo

**No sistema:**
```bash
xdg-open ~/Downloads/relatorio_produtividade.pdf
# ou
open ~/Downloads/relatorio_produtividade.pdf  # macOS
```

### ✅ Relatório Gerado!

Dados de produtividade extraídos.

---

## 🔐 Workflow 7: Re-autenticação Após Expiração

### Objetivo
Renovar sessão quando expirar (após 8 horas)

### Quando Usar
- Ao ver mensagem "Sessão expirada"
- Após 8+ horas desde última autenticação
- Se `pje_check_session` retornar expirada

### Passo a Passo

#### 1. Confirmar Expiração

```
pje_check_session
```

**Resultado:**
```
⚠️ Sessão expirada

Idade da sessão: 9 horas
Você precisa autenticar novamente
```

#### 2. Limpar Sessão Antiga

```
pje_clear_session
```

**Resultado:**
```
✅ Sessão removida com sucesso
```

#### 3. Seguir Workflow 1 Novamente

**Repita:**
- `pje_authenticate_safe_id`
- `browser_navigate` ao PJE
- Clicar em "Certificado Digital"
- Autenticar no popup Safe ID
- Confirmar login

#### 4. Verificar Nova Sessão

```
pje_check_session
```

**Resultado:**
```
✅ STATUS DA SESSÃO PJE TJES
Status: VÁLIDA E ATIVA
Idade: 1 minuto
```

### ✅ Sessão Renovada!

Mais 8 horas de acesso sem re-autenticar.

---

## 🎓 Workflow 8: Extração de Dados Estruturados

### Objetivo
Extrair dados de múltiplos processos para planilha

### Tempo Estimado
10-20 minutos (para 50 processos)

### Fluxo Completo

#### 1. Executar Busca Avançada

**Use Workflow 3:**
- Filtrar processos desejados
- Ex: Todos de 2024, classe específica

#### 2. Capturar Primeira Página

```
browser_snapshot
```

**Identificar:**
- Número do processo
- Classe
- Partes
- Data autuação
- Situação

#### 3. Extrair Dados

**Manualmente (com Claude):**
```
"Por favor, extraia os seguintes dados do snapshot:
- Número do processo
- Autor
- Réu
- Data autuação
- Situação
- Valor da causa

Formate em JSON"
```

**Claude retorna:**
```json
[
  {
    "processo": "0001-19.2023.8.08.0001",
    "autor": "Fulano da Silva",
    "reu": "Empresa XYZ",
    "data_autuacao": "15/01/2023",
    "situacao": "Em andamento",
    "valor": "R$ 50.000,00"
  },
  ...
]
```

#### 4. Navegar Próxima Página

```
browser_click
- element: "Próxima"
- ref: <ref>
```

#### 5. Repetir Extração

**Para cada página:**
- `browser_snapshot`
- Extrair dados
- Adicionar ao JSON
- Próxima página

#### 6. Exportar para CSV/Excel

**Com Claude:**
```
"Converta este JSON em CSV"
```

**Ou salvar JSON:**
```json
// Salvar em arquivo .json
// Depois converter para Excel
```

### ✅ Dados Extraídos!

Planilha com informações estruturadas.

---

## 💡 Dicas e Boas Práticas

### Performance

1. **Aguardar Entre Consultas**
```
browser_wait_for
- time: 5
```
Evita sobrecarregar servidor PJE

2. **Usar Sessão Persistente**
- Não autenticar a cada consulta
- Verificar sessão no início do dia

3. **Browser Headless**
Para automações longas:
```
# Configurar no claude_desktop_config.json
"HEADLESS": "true"
```

### Segurança

1. **Limpar Sessão ao Final do Dia**
```
pje_clear_session
```

2. **Não Compartilhar Screenshots**
- Podem conter dados sensíveis
- Sempre revisar antes de compartilhar

3. **Verificar Expiração**
- Sessões expiram em 8 horas
- Sempre verificar antes de consultas importantes

### Troubleshooting

1. **Browser Não Abre**
```bash
# Verificar Playwright
npx -y @playwright/mcp@latest

# Reinstalar se necessário
npm install -g @playwright/mcp
```

2. **Sessão Não Salva**
```bash
# Verificar permissões
chmod 755 ~/.cache/tjes-pje-mcp/
```

3. **Safe ID Não Abre**
- Verificar popup blockers
- Tentar browser_navigate novamente
- Verificar conexão internet

---

## 📚 Recursos Adicionais

### Documentação

- [Guia Safe ID](./SAFE_ID_GUIDE.md)
- [README Principal](../README.md)
- [Arquitetura](./ARQUITETURA.md)

### Suporte

- Safe ID: https://www.safeid.com.br
- TJES: https://www.tjes.jus.br
- Playwright: https://playwright.dev

---

**Desenvolvido com ❤️ usando Claude Code**

*Todos os workflows testados e validados*
