# 🧠 AI Research Agent com Mapa de Conhecimento

Um agente de pesquisa inteligente que utiliza **Lista de Adjacência** para construir e visualizar mapas de conhecimento interativos baseados em pesquisas web.

![Python](https://img.shields.io/badge/python-3.13+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.49+-red.svg)
![LangGraph](https://img.shields.io/badge/langgraph-0.6+-green.svg)
![NetworkX](https://img.shields.io/badge/networkx-3.0+-purple.svg)

## 🌟 Características Principais

- 🤖 **Agente de Pesquisa IA**: Geração automática de queries e síntese de resultados
- 🗂️ **Lista de Adjacência**: Implementação da estrutura de dados para grafo de conhecimento
- 🧠 **Mapa de Conhecimento Interativo**: Visualização dinâmica de conceitos e relacionamentos
- 🔍 **Extração de Conceitos**: Identificação automática de entidades e termos técnicos
- 📊 **Análise de Relacionamentos**: Conecta conceitos baseado em co-ocorrência
- 💡 **Sugestões Inteligentes**: Recomendações de próximos tópicos baseadas no grafo
- 💾 **Persistência**: Salva e carrega o grafo de conhecimento

## 🏗️ Arquitetura

### Estrutura de Dados Principal: Lista de Adjacência

```python
adjacency_list: Dict[str, List[ConceptConnection]] = {
    "LangGraph": [
        ConceptConnection(target="LangChain", weight=2.0, context="Framework"),
        ConceptConnection(target="Python", weight=1.5, context="Language"),
        ConceptConnection(target="AI", weight=3.0, context="Domain")
    ],
    "LangChain": [
        ConceptConnection(target="LangGraph", weight=2.0, context="Related"),
        ConceptConnection(target="OpenAI", weight=1.0, context="Provider")
    ]
}
```

### Componentes

1. **🔍 Pipeline de Pesquisa** (`src/graph.py`)
   - Geração de queries com LLM
   - Busca web com Tavily API
   - Síntese de resultados

2. **🗂️ Grafo de Conhecimento** (`src/knowledge_graph.py`)
   - Lista de Adjacência para armazenar relacionamentos
   - Extração de conceitos com regex patterns
   - Algoritmos de sugestão baseados em centralidade

3. **📊 Visualização** (`src/graph_visualization.py`)
   - Grafo interativo com NetworkX + Plotly
   - Estatísticas e métricas do grafo
   - Interface responsiva no Streamlit

4. **🖥️ Interface Web** (`app.py`)
   - 3 abas: Pesquisar, Mapa, Estatísticas
   - Controles interativos
   - Sistema de sugestões

## 🚀 Instalação e Configuração

### Pré-requisitos

- Python 3.13+
- Poetry
- Ollama (com modelos `gemma3:1b` e `gemma2:2b`)
- Conta Tavily API

### 1. Clone o repositório

```bash
git clone https://github.com/Jfdeev/search-ai-agent-langgraph.git
cd search-ai-agent-langgraph
```

### 2. Instale dependências

```bash
poetry install
```

### 3. Configure variáveis de ambiente

Crie um arquivo `.env`:

```env
TAVILY_API_KEY=sua_chave_tavily_aqui
LANGSMITH_API_KEY=sua_chave_langsmith_aqui  # Opcional
```

### 4. Configure Ollama

```bash
# Instalar modelos necessários
ollama pull gemma3:1b
ollama pull gemma2:2b
```

### 5. Execute a aplicação

```bash
poetry run streamlit run app.py
```

A aplicação estará disponível em `http://localhost:8501`

## 📖 Como Usar

### 🔍 Aba Pesquisar

1. **Digite sua pergunta** no campo de texto
2. **Clique em "Pesquisar"** para iniciar o processo
3. **Visualize o resultado** com referências automáticas
4. **Confira sugestões** de tópicos relacionados

### 🧠 Aba Mapa de Conhecimento

1. **Visualize o grafo** construído automaticamente
2. **Ajuste filtros** para mostrar conexões por peso mínimo
3. **Explore conceitos** passando o mouse sobre os nós
4. **Analise relacionamentos** através das conexões visuais

**Legenda do Mapa:**
- 🔵 **Tamanho do nó**: Frequência do conceito
- 🌈 **Cor do nó**: Centralidade/importância no grafo
- ➡️ **Espessura da linha**: Força da conexão

### 📊 Aba Estatísticas

1. **Métricas gerais**: Número de conceitos, conexões, densidade
2. **Top conceitos**: Gráfico dos mais frequentes
3. **Estrutura interna**: Visualização da Lista de Adjacência

## 🎯 Exemplos de Uso

### Pesquisa Acadêmica
```
Pergunta: "O que são transformers em deep learning?"
Resultado: Mapa conectando conceitos como:
- Transformers ↔ Attention Mechanism
- BERT ↔ Natural Language Processing
- PyTorch ↔ Machine Learning Framework
```

### Análise Tecnológica
```
Pergunta: "Principais ferramentas de desenvolvimento Python em 2024"
Resultado: Grafo mostrando:
- FastAPI ↔ Web Framework
- Docker ↔ Containerization
- pytest ↔ Testing Framework
```

## 🔧 Estrutura do Projeto

```
grafos-trabalho/
├── src/
│   ├── knowledge_graph.py      # Lista de Adjacência e lógica do grafo
│   ├── graph.py               # Pipeline de pesquisa LangGraph
│   ├── graph_visualization.py # Visualizações interativas
│   ├── schemas.py             # Modelos de dados Pydantic
│   └── prompts.py             # Templates para LLMs
├── app.py                     # Interface Streamlit principal
├── pyproject.toml             # Configuração Poetry
├── .env                       # Variáveis de ambiente
└── knowledge_graph.json      # Persistência do grafo
```

## 🧮 Algoritmos e Estruturas de Dados

### Lista de Adjacência
- **Complexidade de inserção**: O(1)
- **Complexidade de busca**: O(k) onde k = número de conexões
- **Vantagens**: Eficiente para grafos esparsos, fácil adição de arestas
- **Uso no projeto**: Armazenar relacionamentos conceito → [conceitos_relacionados]

### Algoritmos Implementados

1. **Extração de Conceitos**: Regex patterns + NLP básico
2. **Construção de Grafo**: Conectar conceitos co-ocorrentes
3. **Cálculo de Centralidade**: NetworkX degree centrality
4. **Sugestões**: Ordenação por peso das conexões
5. **Persistência**: Serialização JSON da Lista de Adjacência

## 📊 Métricas e Análises

### Métricas Disponíveis
- **Número de conceitos**: Total de nós no grafo
- **Número de conexões**: Total de arestas na Lista de Adjacência
- **Densidade do grafo**: Conexões reais / conexões possíveis
- **Conceitos mais frequentes**: Ranking por aparições
- **Centralidade**: Importância de cada conceito na rede

### Visualizações
- **Grafo interativo**: Plotly + NetworkX
- **Gráfico de barras**: Top conceitos
- **Métricas em tempo real**: Streamlit metrics

## 🛠️ Tecnologias Utilizadas

| Categoria | Tecnologia | Propósito |
|-----------|------------|-----------|
| **Framework IA** | LangGraph | Orquestração de agentes |
| **Estrutura de Dados** | Lista de Adjacência | Armazenar grafo de conhecimento |
| **LLM** | Ollama (Gemma3, Gemma2) | Geração e síntese de conteúdo |
| **API de Busca** | Tavily | Pesquisa web em tempo real |
| **Visualização** | NetworkX + Plotly | Grafos interativos |
| **Interface** | Streamlit | Aplicação web |
| **Extração** | Regex + Python | Identificação de conceitos |
| **Persistência** | JSON | Salvamento do grafo |

## 🔍 API de Desenvolvimento

### Usar o Grafo Programaticamente

```python
from src.knowledge_graph import KnowledgeGraph

# Criar instância
kg = KnowledgeGraph()

# Adicionar conceitos
concepts = ["Python", "Machine Learning", "Data Science"]
kg.add_concept_connections(concepts, "Curso de IA", 2.0)

# Buscar relacionados
related = kg.get_related_concepts("Python")
print(related)  # [("Machine Learning", 2.0), ("Data Science", 2.0)]

# Sugerir próximos tópicos
suggestions = kg.suggest_next_research(["Python"], limit=3)
print(suggestions)  # ["Machine Learning", "Data Science", ...]

# Salvar/carregar
kg.save_to_file("meu_grafo.json")
kg.load_from_file("meu_grafo.json")
```

### Executar Pesquisa

```python
from src.graph import run_research

# Pesquisar e construir grafo automaticamente
result = run_research("O que é inteligência artificial?")
print(result)  # Resposta completa com referências
```

## 🎓 Aspectos Educacionais

### Conceitos de Grafos Demonstrados
- ✅ **Lista de Adjacência**: Implementação completa e funcional
- ✅ **Grafo não-direcionado**: Conexões bidirecionais entre conceitos
- ✅ **Grafo ponderado**: Pesos representam força da relação
- ✅ **Algoritmos de grafo**: Centralidade, busca, sugestões
- ✅ **Persistência**: Serialização e deserialização

### Aplicação Prática
- **Mineração de conhecimento** a partir de textos
- **Análise de relacionamentos** entre conceitos
- **Sistema de recomendação** baseado em grafo
- **Visualização de dados** complexos

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para detalhes.

## 👨‍💻 Autor

**Jfdeev**
- GitHub: [@Jfdeev](https://github.com/Jfdeev)
- Email: jfrsoares161205@gmail.com

## 🙏 Agradecimentos

- **LangGraph** pela excelente framework de agentes
- **NetworkX** pela biblioteca robusta de grafos
- **Streamlit** pela interface web simples e poderosa
- **Ollama** pelos modelos de linguagem locais
- **Tavily** pela API de busca web

---

<div align="center">

**⭐ Se este projeto foi útil, considere dar uma estrela!**

</div>
