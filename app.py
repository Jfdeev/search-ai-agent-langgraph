import streamlit as st
import sys
import os
from pathlib import Path

# Adiciona o diretório src ao path para importar os módulos
sys.path.append('src')

from graph import run_research

# Configuração da página
st.set_page_config(
    page_title="AI Research Agent",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("🔍 AI Research Agent")
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
    """)
    
    st.header("🛠️ Tecnologias")
    st.markdown("""
    - **LangGraph**: Orquestração de agentes
    - **Ollama**: Modelos de linguagem locais
    - **Tavily**: API de busca web
    - **Streamlit**: Interface de usuário
    """)

# Interface principal
st.header("📝 Faça sua pergunta")

# Input do usuário
user_query = st.text_area(
    "Digite sua pergunta ou tópico de pesquisa:",
    height=100,
    placeholder="Ex: Quais são as últimas tendências em inteligência artificial para 2024?"
)

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
        Desenvolvido com ❤️ usando Streamlit e LangGraph
    </div>
    """,
    unsafe_allow_html=True
)
