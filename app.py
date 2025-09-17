import streamlit as st
import sys
import os
from pathlib import Path

# Adiciona o diretório src ao path para importar os módulos
sys.path.append('src')

from graph import run_research, knowledge_graph
from graph_visualization import (
    create_interactive_graph_visualization,
    display_knowledge_graph_stats,
    display_top_concepts,
    display_suggestions
)

# Configuração da página
st.set_page_config(
    page_title="AI Research Agent",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar session state
if 'suggested_query' not in st.session_state:
    st.session_state['suggested_query'] = ""

# Título principal
st.title("🧠 AI Research Agent")
st.markdown("---")

# Abas principais
tab1, tab2, tab3 = st.tabs(["🔍 Pesquisar", "🧠 Mapa de Conhecimento", "📊 Estatísticas"])

with tab1:
    # Sidebar com informações
    with st.sidebar:
        st.header("ℹ️ Sobre")
        st.markdown("""
        Este agente de pesquisa utiliza IA para:
        - Gerar consultas de pesquisa relevantes
        - Buscar informações online
        - Sintetizar resultados
        - **Construir mapa de conhecimento interativo**
        - Fornecer sugestões de tópicos relacionados
        """)
        
        st.header("🛠️ Tecnologias")
        st.markdown("""
        - **LangGraph**: Orquestração de agentes
        - **Lista de Adjacência**: Estrutura de dados para grafo
        - **NetworkX + Plotly**: Visualização interativa
        - **Ollama**: Modelos de linguagem locais
        - **Tavily**: API de busca web
        - **Streamlit**: Interface de usuário
        """)
        
        # Estatísticas rápidas do grafo
        st.header("📈 Grafo Atual")
        stats = knowledge_graph.get_graph_stats()
        st.metric("Conceitos", stats["total_concepts"])
        st.metric("Conexões", stats["total_connections"])

    # Interface principal
    st.header("📝 Faça sua pergunta")

    # Verificar se há sugestão do mapa de conhecimento
    suggested_query = st.session_state.get('suggested_query', "")
    
    # Input do usuário
    user_query = st.text_area(
        "Digite sua pergunta ou tópico de pesquisa:",
        height=100,
        value=suggested_query,
        placeholder="Ex: Quais são as últimas tendências em inteligência artificial para 2024?"
    )
    
    # Limpar sugestão após usar
    if suggested_query:
        st.session_state['suggested_query'] = ""

# Botões de controle
col1, col2 = st.columns([1, 4])
with col1:
    search_button = st.button("🔍 Pesquisar", type="primary")
with col2:
    clear_button = st.button("🗑️ Limpar")

# Limpar campos
if clear_button:
    st.rerun()

# Processar pesquisa
if search_button and user_query:
    if user_query.strip():
        try:
            # Mostrar indicador de progresso
            with st.spinner("🔍 Pesquisando e analisando informações..."):
                # Executar a pesquisa
                result = run_research(user_query.strip())
            
            # Exibir resultado
            st.markdown("---")
            st.header("📊 Resultado da Pesquisa")
            
            # Container para o resultado
            with st.container():
                st.markdown(result)
                
        except Exception as e:
            st.error(f"❌ Erro durante a pesquisa: {str(e)}")
            st.info("💡 Verifique se:")
            st.markdown("""
            - As variáveis de ambiente estão configuradas corretamente
            - A API do Tavily está funcionando
            - Os modelos do Ollama estão disponíveis
            """)
    else:
        st.warning("⚠️ Por favor, digite uma pergunta válida.")

elif search_button:
    st.warning("⚠️ Por favor, digite uma pergunta antes de pesquisar.")

# Rodapé
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        Desenvolvido por Jfdeev usando Streamlit e LangGraph
    </div>
    """,
    unsafe_allow_html=True
)
