import streamlit as st
import sys
import os
from pathlib import Path

# Adiciona o diretório src ao path para importar os módulos
sys.path.append('src')

from graph import run_research
from knowledge_graph import KnowledgeGraph
from graph_visualization import (
    create_interactive_graph_visualization, 
    display_knowledge_graph_stats,
    display_top_concepts,
    display_suggestions
)

# Configuração da página
st.set_page_config(
    page_title="AI Research Agent",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar Knowledge Graph no session state
if 'knowledge_graph' not in st.session_state:
    st.session_state['knowledge_graph'] = KnowledgeGraph()
    try:
        st.session_state['knowledge_graph'].load_from_file('knowledge_graph.json')
    except:
        pass  # Arquivo não existe ainda, começar com grafo vazio

kg = st.session_state['knowledge_graph']

# Título principal
st.title("🔍 AI Research Agent")

# Criar tabs para diferentes funcionalidades
tab1, tab2, tab3 = st.tabs(["🔍 Pesquisa", "🧠 Mapa de Conhecimento", "📊 Estatísticas"])


with tab1:
    st.markdown("---")

    # Sidebar com informações
    with st.sidebar:
        st.header("ℹ️ Sobre")
        st.markdown("""
        Este agente de pesquisa utiliza IA para:
        - Gerar consultas de pesquisa relevantes
        - Buscar informações online
        - Sintetizar resultados
        - Fornecer uma resposta abrangente com referências
        - Construir um mapa de conhecimento interativo
        """)
        
        st.header("🛠️ Tecnologias")
        st.markdown("""
        - **LangGraph**: Orquestração de agentes
        - **Ollama**: Modelos de linguagem locais
        - **Tavily**: API de busca web
        - **Streamlit**: Interface de usuário
        - **NetworkX**: Análise de grafos
        - **Plotly**: Visualizações interativas
        """)
        
        # Mostrar estatísticas rápidas do Knowledge Graph
        stats = kg.get_graph_stats()
        st.header("🧠 Knowledge Graph")
        st.metric("Conceitos", stats["total_concepts"])
        st.metric("Conexões", stats["total_connections"])

    # Interface principal
    st.header("📝 Faça sua pergunta")

    # Check se há sugestão do Knowledge Graph
    suggested_query = st.session_state.get('suggested_query', '')
    if suggested_query:
        st.info(f"💡 Tópico sugerido: {suggested_query}")
        
    # Input do usuário
    default_value = suggested_query if suggested_query else ""
    user_query = st.text_area(
        "Digite sua pergunta ou tópico de pesquisa:",
        height=100,
        placeholder="Ex: Quais são as últimas tendências em inteligência artificial para 2024?",
        value=default_value
    )
    
    # Limpar sugestão após usar
    if suggested_query and user_query == suggested_query:
        st.session_state.pop('suggested_query', None)

    # Botões de controle
    col1, col2 = st.columns([1, 4])
    with col1:
        search_button = st.button("🔍 Pesquisar", type="primary")
    with col2:
        clear_button = st.button("🗑️ Limpar")

    # Limpar campos
    if clear_button:
        st.session_state.pop('suggested_query', None)
        st.rerun()

    # Processar pesquisa
    if search_button and user_query:
        if user_query.strip():
            try:
                # Mostrar indicador de progresso
                with st.spinner("🔍 Pesquisando e analisando informações..."):
                    # Executar a pesquisa
                    result = run_research(user_query.strip())
                    
                    # Extrair conceitos da query e resultado para o Knowledge Graph
                    concepts_from_query = kg.extract_concepts(user_query, query_context=user_query)
                    concepts_from_result = kg.extract_concepts(result, query_context=user_query)
                    
                    # Combinar conceitos
                    all_concepts = list(set(concepts_from_query + concepts_from_result))
                    
                    # Adicionar ao Knowledge Graph
                    if all_concepts:
                        kg.add_concept_connections(all_concepts, context=user_query[:100], weight=1.0)
                        
                        # Salvar Knowledge Graph
                        kg.save_to_file('knowledge_graph.json')
                
                # Exibir resultado
                st.markdown("---")
                st.header("📊 Resultado da Pesquisa")
                
                # Container para o resultado
                with st.container():
                    st.markdown(result)
                
                # Mostrar conceitos extraídos
                if all_concepts:
                    with st.expander("🔍 Conceitos Identificados"):
                        st.write("Conceitos extraídos desta pesquisa:")
                        for concept in all_concepts:
                            st.code(concept)
                
                # Sugestões baseadas no Knowledge Graph
                current_concepts = concepts_from_query + concepts_from_result
                suggestions = kg.suggest_next_research(current_concepts, limit=5)
                
                if suggestions:
                    st.markdown("---")
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
    
    if kg.get_graph_stats()["total_concepts"] > 0:
        # Controles para a visualização
        col1, col2 = st.columns([3, 1])
        
        with col2:
            st.subheader("⚙️ Controles")
            min_weight = st.slider(
                "Peso mínimo das conexões:",
                min_value=0.1,
                max_value=5.0,
                value=1.0,
                step=0.1,
                help="Conexões com peso menor que este valor serão ocultadas"
            )
            
            show_stats = st.checkbox("Mostrar estatísticas", value=True)
        
        with col1:
            # Criar e exibir a visualização interativa
            try:
                fig = create_interactive_graph_visualization(kg, min_weight=min_weight)
                if fig is not None:
                    st.plotly_chart(fig, use_container_width=True)
                
            except Exception as e:
                st.error(f"Erro ao criar visualização: {str(e)}")
        
        if show_stats:
            st.markdown("---")
            display_knowledge_graph_stats(kg)
            
        # Buscar conceito específico
        st.markdown("---")
        st.subheader("🔍 Explorar Conceito")
        
        all_concepts = list(kg.concept_frequency.keys())
        if all_concepts:
            selected_concept = st.selectbox(
                "Selecione um conceito para explorar:",
                options=[""] + sorted(all_concepts),
                format_func=lambda x: "Selecione um conceito..." if x == "" else f"{x} (freq: {kg.concept_frequency[x]})"
            )
            
            if selected_concept:
                related = kg.get_related_concepts(selected_concept, min_weight=0.1)
                
                if related:
                    st.write(f"**Conceitos relacionados a '{selected_concept}':**")
                    
                    for related_concept, weight in related[:10]:  # Top 10
                        st.write(f"• {related_concept} (peso: {weight:.2f})")
                        
                    # Mostrar contextos
                    contexts = kg.concept_contexts.get(selected_concept, [])
                    if contexts:
                        with st.expander("📝 Contextos onde aparece"):
                            for i, context in enumerate(contexts[-5:]):  # Últimos 5 contextos
                                st.write(f"{i+1}. {context}")
                else:
                    st.info("Nenhum conceito relacionado encontrado.")
        else:
            st.info("Faça algumas pesquisas primeiro para popular o mapa de conhecimento!")
    
    else:
        st.info("🔍 O mapa de conhecimento está vazio. Faça algumas pesquisas para começar a construí-lo!")
        st.markdown("""
        **Como funciona:**
        1. Faça perguntas na aba de Pesquisa
        2. O sistema extrairá conceitos automaticamente
        3. Os conceitos serão conectados formando um mapa
        4. Use este mapa para descobrir novas direções de pesquisa
        """)

with tab3:
    st.header("📊 Estatísticas e Análises")
    
    if kg.get_graph_stats()["total_concepts"] > 0:
        # Estatísticas gerais
        display_knowledge_graph_stats(kg)
        
        st.markdown("---")
        
        # Gráfico de conceitos mais frequentes
        col1, col2 = st.columns(2)
        
        with col1:
            display_top_concepts(kg)
        
        with col2:
            st.subheader("🔗 Conceitos Mais Conectados")
            # Calcular conceitos com mais conexões
            connection_counts = {}
            for concept, connections in kg.adjacency_list.items():
                connection_counts[concept] = len(connections)
            
            top_connected = sorted(connection_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            
            if top_connected:
                concepts, counts = zip(*top_connected)
                
                import plotly.express as px
                fig = px.bar(
                    x=list(counts),
                    y=list(concepts),
                    orientation='h',
                    labels={'x': 'Número de Conexões', 'y': 'Conceitos'},
                    title="Top 10 Conceitos por Conexões"
                )
                fig.update_layout(height=400, yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig, use_container_width=True)
        
        # Análise de centralidade
        st.markdown("---")
        st.subheader("🎯 Análise de Centralidade")
        
        try:
            G = kg.create_networkx_graph(min_weight=0.5)
            if len(G.nodes()) > 0:
                import networkx as nx
                
                # Calcular diferentes medidas de centralidade
                degree_centrality = nx.degree_centrality(G)
                betweenness_centrality = nx.betweenness_centrality(G)
                closeness_centrality = nx.closeness_centrality(G)
                
                # Criar dataframe para comparação
                import pandas as pd
                centrality_data = []
                
                for concept in G.nodes():
                    centrality_data.append({
                        'Conceito': concept,
                        'Grau': degree_centrality.get(concept, 0),
                        'Intermediação': betweenness_centrality.get(concept, 0),
                        'Proximidade': closeness_centrality.get(concept, 0),
                        'Frequência': kg.concept_frequency.get(concept, 1)
                    })
                
                df = pd.DataFrame(centrality_data).sort_values('Grau', ascending=False)
                
                # Mostrar top 10
                st.dataframe(
                    df.head(10),
                    use_container_width=True,
                    hide_index=True
                )
                
                st.caption("""
                **Grau**: Quantas conexões diretas o conceito tem
                **Intermediação**: O quanto o conceito atua como "ponte" entre outros
                **Proximidade**: O quão próximo o conceito está de todos os outros
                """)
        
        except Exception as e:
            st.error(f"Erro na análise de centralidade: {str(e)}")
        
        # Opções de gerenciamento
        st.markdown("---")
        st.subheader("🔧 Gerenciamento")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💾 Salvar Grafo", help="Salva o grafo atual em arquivo"):
                kg.save_to_file('knowledge_graph.json')
                st.success("Grafo salvo com sucesso!")
        
        with col2:
            if st.button("📤 Exportar JSON", help="Download do grafo em formato JSON"):
                import json
                graph_data = {
                    "stats": kg.get_graph_stats(),
                    "concepts": dict(kg.concept_frequency),
                    "adjacency_list": {
                        concept: [
                            {"target": conn.target, "weight": conn.weight, "context": conn.context}
                            for conn in connections
                        ]
                        for concept, connections in kg.adjacency_list.items()
                    }
                }
                
                st.download_button(
                    label="Download JSON",
                    data=json.dumps(graph_data, ensure_ascii=False, indent=2),
                    file_name="knowledge_graph.json",
                    mime="application/json"
                )
        
        with col3:
            if st.button("🗑️ Limpar Grafo", type="secondary", help="Remove todos os dados do grafo"):
                if st.session_state.get('confirm_clear'):
                    st.session_state['knowledge_graph'] = KnowledgeGraph()
                    st.session_state.pop('confirm_clear', None)
                    st.success("Grafo limpo com sucesso!")
                    st.rerun()
                else:
                    st.session_state['confirm_clear'] = True
                    st.warning("⚠️ Clique novamente para confirmar a limpeza!")
    
    else:
        st.info("📊 Nenhuma estatística disponível ainda. Faça algumas pesquisas primeiro!")

# Rodapé
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        Desenvolvido por Jfdeev usando Streamlit, LangGraph e NetworkX
    </div>
    """,
    unsafe_allow_html=True
)
