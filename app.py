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
    page_title="AI Research Agent com Mapa de Conhecimento",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar session state
if 'suggested_query' not in st.session_state:
    st.session_state['suggested_query'] = ""

# Título principal
st.title("🧠 AI Research Agent com Mapa de Conhecimento")
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
                with st.spinner("🔍 Pesquisando e construindo mapa de conhecimento..."):
                    # Executar a pesquisa
                    result = run_research(user_query.strip())
                
                # Exibir resultado
                st.markdown("---")
                st.header("📊 Resultado da Pesquisa")
                
                # Container para o resultado
                with st.container():
                    st.markdown(result)
                    
                # Exibir sugestões se disponíveis
                st.markdown("---")
                latest_stats = knowledge_graph.get_graph_stats()
                if latest_stats["total_concepts"] > 0:
                    # Gerar sugestões baseadas no grafo atual
                    all_concepts = list(knowledge_graph.concept_frequency.keys())
                    suggestions = knowledge_graph.suggest_next_research(all_concepts[-5:], limit=3)
                    display_suggestions(suggestions)
                    
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

with tab2:
    st.header("🧠 Mapa de Conhecimento Interativo")
    st.markdown("*Visualização baseada em Lista de Adjacência*")
    
    # Controles do mapa
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        min_weight = st.slider("Peso mínimo das conexões", 0.5, 5.0, 1.0, 0.5)
    with col2:
        if st.button("🔄 Atualizar Mapa"):
            st.rerun()
    with col3:
        if st.button("🗑️ Limpar Grafo"):
            knowledge_graph.adjacency_list.clear()
            knowledge_graph.concept_frequency.clear()
            knowledge_graph.concept_contexts.clear()
            knowledge_graph.save_to_file("knowledge_graph.json")
            st.success("Grafo limpo com sucesso!")
            st.rerun()
    
    # Visualização principal
    try:
        fig = create_interactive_graph_visualization(knowledge_graph, min_weight)
        if fig:
            # Exibir o grafo
            st.plotly_chart(fig, use_container_width=True)
            
            # Informações sobre interatividade
            st.info("""
            🖱️ **Como usar o mapa:**
            - **Hover**: Passe o mouse sobre os nós para ver detalhes
            - **Zoom**: Use a roda do mouse ou controles para ampliar
            - **Pan**: Clique e arraste para mover o mapa
            - **Tamanho do nó**: Representa a frequência do conceito
            - **Cor do nó**: Representa a importância/centralidade
            """)
            
        else:
            st.info("🔍 **Faça algumas pesquisas primeiro para ver o mapa de conhecimento!**")
            st.markdown("""
            O mapa será construído automaticamente conforme você faz pesquisas.
            Cada pesquisa extrai conceitos e cria conexões usando **Lista de Adjacência**.
            """)
            
    except Exception as e:
        st.error(f"Erro ao criar visualização: {str(e)}")

with tab3:
    st.header("📊 Estatísticas do Conhecimento")
    
    # Estatísticas principais
    display_knowledge_graph_stats(knowledge_graph)
    
    st.markdown("---")
    
    # Conceitos mais frequentes
    col1, col2 = st.columns([1, 1])
    
    with col1:
        display_top_concepts(knowledge_graph)
    
    with col2:
        st.subheader("🔗 Estrutura da Lista de Adjacência")
        
        # Mostrar exemplo da estrutura de dados
        if knowledge_graph.adjacency_list:
            st.markdown("**Exemplo da estrutura interna:**")
            
            # Pegar alguns conceitos para mostrar
            sample_concepts = list(knowledge_graph.adjacency_list.keys())[:3]
            
            for concept in sample_concepts:
                connections = knowledge_graph.adjacency_list[concept]
                st.markdown(f"**{concept}** → [")
                for conn in connections[:3]:  # Mostrar apenas 3 conexões
                    st.markdown(f"  • {conn.target} (peso: {conn.weight:.1f})")
                if len(connections) > 3:
                    st.markdown(f"  ... e mais {len(connections) - 3} conexões")
                st.markdown("]")
                st.markdown("")
            
        else:
            st.info("A Lista de Adjacência ainda está vazia. Faça algumas pesquisas!")

# Rodapé
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        Desenvolvido com ❤️ usando Streamlit, LangGraph e <strong>Lista de Adjacência</strong>
    </div>
    """,
    unsafe_allow_html=True
)