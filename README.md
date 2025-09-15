# 🔍 AI Research Agent with LangGraph

Um agente inteligente de pesquisa que utiliza LangGraph para orquestrar múltiplos LLMs e APIs de busca, fornecendo respostas abrangentes e bem fundamentadas para perguntas de pesquisa.

## ✨ Características

- **Geração Inteligente de Consultas**: Cria automaticamente 3-5 consultas otimizadas para pesquisa
- **Busca Paralela**: Executa múltiplas pesquisas simultaneamente usando Tavily API
- **Síntese Automática**: Analisa e resume conteúdo web relevante
- **Resposta Estruturada**: Gera respostas de 500-800 palavras com referências citadas
- **Interface Web**: Interface Streamlit intuitiva e responsiva
- **Modelos Locais**: Utiliza Ollama para execução local dos LLMs

## 🏗️ Arquitetura

O projeto utiliza LangGraph para criar um pipeline de processamento com os seguintes nós:

```
START → build_first_queries → spawn_researches → single_search → final_writer → END
```

### Componentes Principais

- **[`ReportState`](src/schemas.py)**: Estado compartilhado entre os nós do grafo
- **[`build_first_queries`](src/graph.py)**: Gera consultas de pesquisa baseadas no input do usuário
- **[`single_search`](src/graph.py)**: Executa busca individual e extrai conteúdo relevante
- **[`final_writer`](src/graph.py)**: Sintetiza resultados em uma resposta final estruturada

## 🛠️ Tecnologias

- **[LangGraph](https://github.com/langchain-ai/langgraph)**: Orquestração de workflows de IA
- **[Ollama](https://ollama.ai/)**: Execução local de modelos de linguagem
- **[Tavily API](https://tavily.com/)**: API de busca web especializada
- **[Streamlit](https://streamlit.io/)**: Interface web interativa
- **[Pydantic](https://pydantic.dev/)**: Validação e serialização de dados

## 📦 Instalação

### Pré-requisitos

1. **Python 3.13+**
2. **Poetry** (gerenciador de dependências)
3. **Ollama** instalado localmente
4. **Conta Tavily** para API key

### Passo a Passo

1. **Clone o repositório**:
```bash
git clone <repository-url>
cd search-ai-agent-langgraph
```

2. **Instale as dependências**:
```bash
poetry install
```

3. **Configure o Ollama**:
```bash
# Baixe os modelos necessários
ollama pull gemma2:2b
ollama pull gemma3:1b
```

4. **Configure as variáveis de ambiente**:
Crie um arquivo `.env` na raiz do projeto:
```env
TAVILY_API_KEY=sua_api_key_aqui
```

5. **Execute a aplicação**:
```bash
poetry run streamlit run app.py
```

## 🚀 Uso

### Interface Web

1. Acesse `http://localhost:8501` após executar a aplicação
2. Digite sua pergunta de pesquisa na área de texto
3. Clique em "🔍 Pesquisar" e aguarde o processamento
4. Visualize a resposta estruturada com referências

### Uso Programático

```python
from src.graph import run_research

# Execute uma pesquisa
resultado = run_research("Quais são as tendências de IA para 2024?")
print(resultado)
```

## 📁 Estrutura do Projeto

```
├── app.py              # Interface Streamlit
├── src/
│   ├── __init__.py
│   ├── graph.py        # Lógica principal do grafo LangGraph
│   ├── prompts.py      # Templates de prompts para os LLMs
│   └── schemas.py      # Modelos Pydantic para validação
├── pyproject.toml      # Configuração de dependências
├── poetry.lock         # Lock file das dependências
└── README.md           # Este arquivo
```

## 🔧 Configuração Avançada

### Modelos Ollama

Por padrão, o projeto usa:
- `gemma2:2b` para raciocínio complexo
- `gemma3:1b` para tarefas mais simples

Para alterar os modelos, edite [`src/graph.py`](src/graph.py):
```python
llm = ChatOllama(model="seu_modelo_aqui")
reasoning_llm = ChatOllama(model="seu_modelo_de_raciocinio")
```

### Personalização de Prompts

Os prompts estão organizados em [`src/prompts.py`](src/prompts.py):
- `build_queries`: Geração de consultas
- `resume_search`: Síntese de resultados
- `build_final_response`: Resposta final

## 📊 Fluxo de Dados

1. **Input do Usuário** → Pergunta inicial
2. **Geração de Consultas** → 3-5 consultas otimizadas
3. **Busca Paralela** → Execução simultânea via Tavily
4. **Extração de Conteúdo** → Análise e síntese por LLM
5. **Resposta Final** → Documento estruturado com referências

## 🤝 Contribuições

Contribuições são bem-vindas! Por favor:

1. Faça fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a licença MIT. Veja o arquivo LICENSE para detalhes.

## 👨‍💻 Autor

**Jfdeev**
- Email: jfrsoares161205@gmail.com

## 🐛 Problemas Conhecidos

- Certifique-se de que os modelos Ollama estão baixados e funcionando
- A API key do Tavily deve estar configurada corretamente
- Algumas consultas podem demorar devido ao processamento sequencial de extração

## 🔮 Roadmap

- [ ] Suporte a múltiplos idiomas de resposta
- [ ] Cache de resultados de pesquisa
- [ ] Interface para seleção de modelos
- [ ] Exportação de relatórios em PDF
- [ ] Integração com outras APIs de busca