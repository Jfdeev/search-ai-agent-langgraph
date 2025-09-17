import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import networkx as nx
from knowledge_graph import KnowledgeGraph
import numpy as np
from typing import Dict, List, Tuple

def create_interactive_graph_visualization(kg: KnowledgeGraph, min_weight: float = 1.0):
    """
    Cria uma visualização interativa do grafo de conhecimento usando Plotly
    """
    # Criar grafo NetworkX
    G = kg.create_networkx_graph(min_weight=min_weight)
    
    if len(G.nodes()) == 0:
        st.warning("⚠️ Nenhum conceito encontrado no grafo de conhecimento. Faça algumas pesquisas primeiro!")
        return None
    
    # Layout do grafo
    if len(G.nodes()) > 50:
        # Para grafos grandes, usar layout mais eficiente
        pos = nx.spring_layout(G, k=3, iterations=50)
    else:
        # Para grafos menores, usar layout mais detalhado
        pos = nx.spring_layout(G, k=5, iterations=100)
    
    # Preparar dados para Plotly
    edge_x = []
    edge_y = []
    edge_info = []
    
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        
        # Informações da aresta
        weight = G[edge[0]][edge[1]].get('weight', 1.0)
        edge_info.append(f"{edge[0]} ↔ {edge[1]} (peso: {weight:.1f})")
    
    # Criar trace das arestas
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.8, color='#888'),
        hoverinfo='none',
        mode='lines',
        name='Conexões'
    )
    
    # Preparar dados dos nós
    node_x = []
    node_y = []
    node_text = []
    node_sizes = []
    node_colors = []
    node_info = []
    
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        
        # Tamanho baseado na frequência
        frequency = kg.concept_frequency.get(node, 1)
        node_sizes.append(max(10, min(50, frequency * 8)))  # Tamanho entre 10 e 50
        
        # Cor baseada na centralidade
        centrality = nx.degree_centrality(G).get(node, 0)
        node_colors.append(centrality)
        
        # Texto do nó
        node_text.append(node)
        
        # Informações detalhadas
        connections = len(list(G.neighbors(node)))
        related_concepts = [neighbor for neighbor in G.neighbors(node)][:5]  # Top 5
        
        info = f"""
        <b>{node}</b><br>
        Frequência: {frequency}<br>
        Conexões: {connections}<br>
        Relacionados: {', '.join(related_concepts)}
        """
        node_info.append(info)
    
    # Criar trace dos nós
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=node_text,
        textposition="middle center",
        textfont=dict(size=10, color="white"),
        hoverinfo='text',
        hovertext=node_info,
        marker=dict(
            size=node_sizes,
            color=node_colors,
            colorscale='Viridis',
            colorbar=dict(
                title="Centralidade<br>(Importância)",
                titleside="right",
                tickmode="linear",
                tick0=0,
                dtick=0.1
            ),
            line=dict(width=2, color="white"),
            showscale=True
        ),
        name='Conceitos'
    )
    
    # Criar figura
    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            title={
                'text': "🧠 Mapa de Conhecimento Interativo",
                'x': 0.5,
                'xanchor': 'center'
            },
            titlefont_size=16,
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20,l=5,r=5,t=40),
            annotations=[
                dict(
                    text="Clique em um conceito para ver suas conexões. Tamanho = frequência, Cor = importância",
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.005, y=-0.002,
                    xanchor='left', yanchor='bottom',
                    font=dict(color='gray', size=10)
                )
            ],
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=600
        )
    )
    
    return fig

def display_knowledge_graph_stats(kg: KnowledgeGraph):
    """
    Exibe estatísticas do grafo de conhecimento
    """
    stats = kg.get_graph_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📝 Conceitos",
            value=stats["total_concepts"]
        )
    
    with col2:
        st.metric(
            label="🔗 Conexões",
            value=stats["total_connections"]
        )
    
    with col3:
        st.metric(
            label="📊 Avg. Conexões",
            value=f"{stats['average_connections_per_concept']:.1f}"
        )
    
    with col4:
        # Densidade do grafo
        if stats["total_concepts"] > 1:
            max_possible = stats["total_concepts"] * (stats["total_concepts"] - 1) // 2
            density = stats["total_connections"] / max_possible if max_possible > 0 else 0
            st.metric(
                label="🌐 Densidade",
                value=f"{density:.2%}"
            )
        else:
            st.metric(
                label="🌐 Densidade",
                value="N/A"
            )

def display_top_concepts(kg: KnowledgeGraph):
    """
    Exibe os conceitos mais frequentes
    """
    st.subheader("🔥 Conceitos Mais Frequentes")
    
    top_concepts = kg.concept_frequency.most_common(10)
    
    if top_concepts:
        concepts, frequencies = zip(*top_concepts)
        
        # Criar gráfico de barras
        fig = px.bar(
            x=list(frequencies),
            y=list(concepts),
            orientation='h',
            labels={'x': 'Frequência', 'y': 'Conceitos'},
            title="Top 10 Conceitos por Frequência"
        )
        fig.update_layout(height=400, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Nenhum conceito encontrado ainda. Faça algumas pesquisas!")

def display_suggestions(suggestions: List[str]):
    """
    Exibe sugestões de próximos tópicos
    """
    if suggestions:
        st.subheader("💡 Sugestões de Próximos Tópicos")
        
        # Criar botões para as sugestões
        cols = st.columns(min(len(suggestions), 3))
        
        for i, suggestion in enumerate(suggestions):
            with cols[i % 3]:
                if st.button(f"🔍 {suggestion}", key=f"suggestion_{i}"):
                    # Armazenar sugestão no session state para pesquisa
                    st.session_state['suggested_query'] = suggestion
                    st.rerun()
    else:
        st.info("Faça mais pesquisas para gerar sugestões personalizadas!")

def get_concept_network(kg: KnowledgeGraph, concept: str, depth: int = 2) -> Dict:
    """
    Retorna a rede de conceitos relacionados a um conceito específico
    """
    network = {"nodes": [], "edges": []}
    
    if concept not in kg.adjacency_list:
        return network
    
    visited = set()
    to_visit = [(concept, 0)]
    
    while to_visit:
        current_concept, current_depth = to_visit.pop(0)
        
        if current_concept in visited or current_depth > depth:
            continue
            
        visited.add(current_concept)
        
        # Adicionar nó
        frequency = kg.concept_frequency.get(current_concept, 1)
        network["nodes"].append({
            "id": current_concept,
            "label": current_concept,
            "frequency": frequency,
            "depth": current_depth
        })
        
        # Adicionar conexões
        related = kg.get_related_concepts(current_concept)
        for related_concept, weight in related:
            if current_depth < depth:
                to_visit.append((related_concept, current_depth + 1))
            
            network["edges"].append({
                "source": current_concept,
                "target": related_concept,
                "weight": weight
            })
    
    return network