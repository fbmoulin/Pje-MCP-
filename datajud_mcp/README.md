# DataJud MCP Server - TJES

Servidor MCP para acesso à API pública do DataJud (CNJ) - Tribunal de Justiça do Espírito Santo.

## 🎯 Características

- ✅ Acesso à API pública do DataJud sem autenticação complexa
- ✅ Queries Elasticsearch avançadas
- ✅ 5 ferramentas MCP especializadas
- ✅ Formatação amigável dos resultados
- ✅ Validação robusta de dados
- ✅ Logging estruturado

## 🔧 Ferramentas Disponíveis

### 1. `datajud_query_process`
Consulta processo específico pelo número CNJ

**Parâmetros:**
- `numero_processo`: Número do processo (formato CNJ)

**Exemplo:**
```
Consultar processo 0000166-19.2023.8.08.0035
```

### 2. `datajud_search_by_class`
Busca processos por classe processual

**Parâmetros:**
- `classe_codigo`: Código da classe
- `limit`: Máximo de resultados (padrão: 10)
- `orgao_julgador`: Código do órgão (opcional)

### 3. `datajud_search_by_date_range`
Busca processos por período

**Parâmetros:**
- `data_inicio`: Data inicial (YYYY-MM-DD)
- `data_fim`: Data final (YYYY-MM-DD)
- `limit`: Máximo de resultados (padrão: 10)
- `campo_data`: Campo de data (padrão: dataAjuizamento)

### 4. `datajud_advanced_search`
Busca avançada com query Elasticsearch customizada

**Parâmetros:**
- `query_json`: Query Elasticsearch em JSON
- `limit`: Máximo de resultados (padrão: 10)

### 5. `datajud_get_statistics`
Estatísticas de processos por período

**Parâmetros:**
- `ano`: Ano (opcional, padrão: ano atual)
- `mes`: Mês (opcional, 1-12)

## 📦 Instalação

```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp ../.env.example ../.env
# Editar .env com suas configurações
```

## ⚙️ Configuração

### Variáveis de Ambiente

```bash
DATAJUD_API_KEY="sua_chave_api"
DATAJUD_BASE_URL="https://api-publica.datajud.cnj.jus.br"
DATAJUD_TRIBUNAL_ALIAS="tjes"
DATAJUD_TIMEOUT_SECONDS="30"
```

### Claude Desktop

Adicione ao `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "datajud": {
      "command": "python",
      "args": ["-m", "datajud_mcp.server"],
      "env": {
        "DATAJUD_API_KEY": "${DATAJUD_API_KEY}",
        "DATAJUD_TRIBUNAL_ALIAS": "tjes"
      }
    }
  }
}
```

## 🚀 Execução

```bash
# Executar servidor
python -m datajud_mcp.server

# Ou via módulo Python
python server.py
```

## 📚 Documentação da API

- [DataJud Wiki](https://datajud-wiki.cnj.jus.br/api-publica/)
- [Tutorial PDF](https://www.cnj.jus.br/wp-content/uploads/2023/05/tutorial-api-publica-datajud-beta.pdf)
- [Portal CNJ](https://www.cnj.jus.br/sistemas/datajud/api-publica/)

## 📊 Exemplos de Uso

### Consultar processo específico
```
Use a ferramenta datajud_query_process com:
- numero_processo: "0000166-19.2023.8.08.0035"
```

### Buscar por classe
```
Use datajud_search_by_class com:
- classe_codigo: "1234"
- limit: 20
```

### Buscar por período
```
Use datajud_search_by_date_range com:
- data_inicio: "2023-01-01"
- data_fim: "2023-12-31"
- limit: 50
```

### Query avançada
```json
Use datajud_advanced_search com query_json:
{
  "bool": {
    "must": [
      {"match": {"classe.codigo": "1234"}},
      {"match": {"orgaoJulgador.codigo": "5678"}}
    ]
  }
}
```

## 🔒 Segurança

- ✅ Chave API pública (fornecida pelo CNJ)
- ✅ Sem dados sensíveis no código
- ✅ Variáveis de ambiente para configuração
- ✅ Validação de entradas

## 📄 Licença

MIT License

## 👤 Autor

Desenvolvido por Claude Code para integração com TJES.
