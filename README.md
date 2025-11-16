# TJES PJE MCP Server

**Servidor MCP completo para integração com o Processo Judicial Eletrônico (PJE) do Tribunal de Justiça do Espírito Santo**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-1.0+-green.svg)](https://modelcontextprotocol.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Visão Geral

Este projeto fornece **3 servidores MCP integrados** para acesso completo aos sistemas judiciais do TJES:

### 1. 🌐 Playwright MCP (Microsoft Oficial)
- Automação web e scraping
- Interface de jurisprudência TJES
- Autenticação browser-based com certificados A1
- Downloads de PDFs e documentos

### 2. 🔐 TJES PJE MCP Server (Custom - Python)
- **8 ferramentas MCP autenticadas**
- Suporte a certificados digitais A1 e A3
- APIs do PJE (1º e 2º grau)
- Gerenciamento completo de processos

### 3. 📊 DataJud MCP Server (Custom - Python)
- **5 ferramentas MCP públicas**
- API pública do DataJud (CNJ)
- Consultas sem autenticação complexa
- Estatísticas e agregações

## 🎯 Características Principais

- ✅ **Autenticação robusta** com certificados digitais A1/A3
- ✅ **13+ ferramentas MCP** especializadas
- ✅ **Arquitetura multi-servidor** otimizada
- ✅ **Playwright integration** para scraping e automação
- ✅ **Retry logic** e tratamento de erros
- ✅ **Logging estruturado** e monitoramento
- ✅ **Documentação completa** com exemplos

## 🚀 Quick Start

### Pré-requisitos

- Python 3.10+
- Node.js 18+ (para Playwright)
- Certificado digital A1 ou A3 (para PJE autenticado)
- Claude Desktop

### Instalação

```bash
# 1. Clone o repositório
cd /mnt/c/Projetos2/mcp_pje

# 2. Instale dependências Python
pip install -r datajud_mcp/requirements.txt
pip install -r tjes_pje_mcp/requirements.txt

# 3. Configure variáveis de ambiente
cp .env.example .env
# Edite .env com suas credenciais

# 4. Configure Claude Desktop
# Copie o conteúdo de claude_desktop_config.json para:
# ~/.config/Claude/claude_desktop_config.json (Linux)
# ou
# %APPDATA%\Claude\claude_desktop_config.json (Windows)

# 5. Reinicie Claude Desktop
```

### Configuração Rápida

Edite o arquivo `.env`:

```bash
# DataJud (API Pública)
DATAJUD_API_KEY="cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw=="

# TJES PJE (Certificado A1)
PJE_CERT_TYPE="A1"
PJE_CERT_PATH="/home/seu_usuario/.certificates/tjes_pje.pfx"
PJE_CERT_PASSWORD="sua_senha_certificado"
```

## 🔧 Ferramentas Disponíveis

### DataJud MCP (Público - 5 ferramentas)

| Ferramenta | Descrição |
|------------|-----------|
| `datajud_query_process` | Consulta processo por número CNJ |
| `datajud_search_by_class` | Busca por classe processual |
| `datajud_search_by_date_range` | Busca por período |
| `datajud_advanced_search` | Query Elasticsearch customizada |
| `datajud_get_statistics` | Estatísticas por período |

### TJES PJE MCP (Autenticado - 8 ferramentas)

| Ferramenta | Descrição |
|------------|-----------|
| `pje_certificate_status` | Status do certificado digital |
| `pje_search_process` | Busca processo (autenticado) |
| `pje_list_processes` | Lista processos com filtros |
| `pje_get_movements` | Movimentações do processo |
| `pje_list_documents` | Documentos do processo |
| `pje_list_classes` | Classes processuais |
| `pje_list_organs` | Órgãos julgadores |
| `pje_list_subjects` | Assuntos processuais |

### Playwright MCP (Automação Web)

- `browser_navigate` - Navegar para URL
- `browser_snapshot` - Capturar estado da página
- `browser_click` - Clicar em elementos
- `browser_fill_form` - Preencher formulários
- `browser_take_screenshot` - Capturar screenshot
- E mais 20+ ferramentas de automação web

## 📖 Exemplos de Uso

### Consultar Processo (DataJud - Público)

```
Use a ferramenta datajud_query_process com:
- numero_processo: "0000166-19.2023.8.08.0035"
```

### Buscar Processos por Classe (PJE - Autenticado)

```
Use a ferramenta pje_list_processes com:
- classe: "1234"
- orgao_julgador: "5678"
- limit: 20
- grau: "1"
```

### Scraping Jurisprudência (Playwright)

```
1. browser_navigate para: https://sistemas.tjes.jus.br/consulta-jurisprudencia/
2. browser_fill_form com os critérios de busca
3. browser_click no botão "Pesquisar"
4. browser_snapshot para capturar resultados
```

### Verificar Certificado

```
Use a ferramenta pje_certificate_status
```

## 🏗️ Arquitetura

```
┌─────────────────────────────────────┐
│      Claude Desktop (Host)          │
│  ┌───────────────────────────────┐ │
│  │   MCP Client Manager          │ │
│  └───────────┬───────────────────┘ │
└──────────────┼──────────────────────┘
               │
       ┌───────┼───────┐
       │       │       │
       ▼       ▼       ▼
    ┌────┐ ┌────┐ ┌────┐
    │Play│ │PJE │ │Data│
    │wrgh│ │    │ │Jud │
    └────┘ └────┘ └────┘
```

## 📁 Estrutura do Projeto

```
mcp_pje/
├── datajud_mcp/              # Servidor DataJud
│   ├── server.py             # Servidor principal
│   ├── requirements.txt      # Dependências
│   └── README.md             # Documentação
├── tjes_pje_mcp/             # Servidor TJES PJE
│   ├── server.py             # Servidor principal
│   ├── cert_manager.py       # Gerenciador de certificados
│   ├── requirements.txt      # Dependências
│   └── README.md             # Documentação
├── tests/                    # Testes
│   ├── test_datajud.py
│   ├── test_tjes_pje.py
│   └── test_integration.py
├── docs/                     # Documentação adicional
├── .gitignore                # Arquivos ignorados
├── .env.example              # Exemplo de configuração
├── claude_desktop_config.json # Configuração Claude Desktop
├── LICENSE                   # Licença MIT
└── README.md                 # Este arquivo
```

## 🔐 Certificados Digitais

### Certificado A1 (Arquivo PFX)

```bash
# 1. Coloque seu certificado em local seguro
mkdir -p ~/.certificates
chmod 700 ~/.certificates
cp seu_certificado.pfx ~/.certificates/tjes_pje.pfx
chmod 600 ~/.certificates/tjes_pje.pfx

# 2. Configure no .env
PJE_CERT_TYPE="A1"
PJE_CERT_PATH="$HOME/.certificates/tjes_pje.pfx"
PJE_CERT_PASSWORD="sua_senha"
```

### Certificado A3 (Smart Card/Token)

⚠️ **Suporte limitado via httpx**. Para A3, considere:
1. Exportar certificado para A1 temporário
2. Usar Playwright com autenticação browser-based
3. Configurar Windows Certificate Store (Windows apenas)

## 🧪 Testes

```bash
# Testar DataJud (não requer certificado)
python tests/test_datajud.py

# Testar TJES PJE (requer certificado)
python tests/test_tjes_pje.py

# Testar integração completa
python tests/test_integration.py
```

## 📚 Documentação Adicional

- [Instalação Detalhada](docs/INSTALACAO.md) - Guia passo-a-passo
- [Exemplos de Uso](docs/EXEMPLOS_USO.md) - 50+ exemplos práticos
- [Certificados](docs/CERTIFICADOS.md) - Guia de certificados A1/A3
- [Arquitetura](docs/ARQUITETURA.md) - Detalhes técnicos
- [Playwright Integration](docs/PLAYWRIGHT_INTEGRATION.md) - Automação web

## 🔒 Segurança

- ✅ **Nunca** commite certificados ou senhas
- ✅ Certificados em diretório seguro (`chmod 600`)
- ✅ Senhas via variáveis de ambiente
- ✅ `.gitignore` configurado para segurança
- ✅ Logs não expõem credenciais
- ✅ Validação de certificados
- ✅ Conexões HTTPS verificadas

## 🐛 Troubleshooting

### Erro: "Certificado não encontrado"

```bash
# Verificar caminho do certificado
ls -la ~/.certificates/tjes_pje.pfx

# Verificar permissões
chmod 600 ~/.certificates/tjes_pje.pfx
```

### Erro: "Senha incorreta"

```bash
# Testar certificado com openssl
openssl pkcs12 -info -in ~/.certificates/tjes_pje.pfx -nodes
```

### Playwright não encontrado

```bash
# Instalar Playwright
npx -y @playwright/mcp@latest

# Verificar Node.js
node --version  # Deve ser 18+
```

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👤 Autor

Desenvolvido por **Claude Code** para integração com TJES.

## 🔗 Links Úteis

- [DataJud Wiki](https://datajud-wiki.cnj.jus.br/api-publica/)
- [Tutorial DataJud PDF](https://www.cnj.jus.br/wp-content/uploads/2023/05/tutorial-api-publica-datajud-beta.pdf)
- [TJES - Jurisprudência](https://sistemas.tjes.jus.br/consulta-jurisprudencia/)
- [Playwright MCP](https://github.com/microsoft/playwright-mcp)
- [Model Context Protocol](https://modelcontextprotocol.io/)

## 📊 Status do Projeto

- ✅ DataJud MCP Server - Completo
- ✅ TJES PJE MCP Server - Completo
- ✅ Certificate Manager - Completo
- ✅ Playwright Integration - Configurado
- ⏳ Documentação detalhada - Em progresso
- ⏳ Testes automatizados - Em progresso

## 🎯 Roadmap

- [ ] Testes automatizados completos
- [ ] CI/CD com GitHub Actions
- [ ] Docker containers
- [ ] Suporte A3 melhorado
- [ ] Cache distribuído
- [ ] Webhooks para notificações
- [ ] Dashboard de monitoramento

---

**Nota**: Este projeto utiliza APIs públicas e autenticadas do CNJ e TJES. Certifique-se de ter as devidas autorizações antes de usar em produção.

**Desenvolvido com ❤️ usando Claude Code**
