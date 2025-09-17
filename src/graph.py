from typing import List
from pydantic import BaseModel, Field
from langchain_ollama import ChatOllama
from langgraph.graph import START, END, StateGraph
from langgraph.types import Send
from tavily import TavilyClient

from schemas import *
from prompts import *
from knowledge_graph import KnowledgeGraph

from dotenv import load_dotenv

from src.schemas import QueryResult, ReportState
load_dotenv()

llm = ChatOllama(model="gemma3:1b")
reasoning_llm = ChatOllama(model="gemma2:2b")

# Instância global do grafo de conhecimento
knowledge_graph = KnowledgeGraph()
# Carregar grafo existente se houver
knowledge_graph.load_from_file("knowledge_graph.json")


# Nós

def build_first_queries(state: ReportState):
    class QueryList(BaseModel):
        queries: List[str] = Field(default_factory=list, max_items=3)
    
    user_input = state.user_input

    prompt = build_queries.format(user_input=user_input)
    query_llm = llm.with_structured_output(QueryList)
    result = query_llm.invoke(prompt)

    return {"queries": result.queries}

# Para rodar todos os workers de forma assincrona e paralela
def spawn_researches(state: ReportState):
    return [Send("single_search", query) for query in state.queries]


def single_search(query: str):
    try:
        tavily = TavilyClient()
        results = tavily.search(query, max_results=3, include_raw_content=False)
        
        if not results.get("results") or len(results["results"]) == 0:
            return {"query_result": QueryResult(
                title="Nenhum resultado encontrado",
                url="",
                resume="Não foi possível encontrar informações relevantes para esta consulta.",
                concepts=[]
            )}
        
        url = results["results"][0]["url"]
        url_etraction = tavily.extract(url)

        if len(url_etraction["results"]) > 0:
            raw_content = url_etraction["results"][0]["raw_content"]
            prompt = resume_search.format(user_input=query, search_results=raw_content)
            llm_result = llm.invoke(prompt)

            # Extrair conceitos do conteúdo e do resumo
            content_text = raw_content + " " + llm_result.content
            extracted_concepts = knowledge_graph.extract_concepts(content_text, query)
            
            # Adicionar conexões no grafo de conhecimento
            if extracted_concepts:
                knowledge_graph.add_concept_connections(extracted_concepts, f"Query: {query}", 1.0)

            query_result = QueryResult(
                title=results["results"][0]["title"],
                url=url,
                resume=llm_result.content,
                concepts=extracted_concepts
            )
        else:
            # Extrair conceitos apenas do título se não há conteúdo
            extracted_concepts = knowledge_graph.extract_concepts(results["results"][0]["title"], query)
            
            query_result = QueryResult(
                title=results["results"][0]["title"],
                url=url,
                resume="Conteúdo não disponível para extração.",
                concepts=extracted_concepts
            )
            
        return {"query_result": query_result}
    
    except Exception as e:
        return {"query_result": QueryResult(
            title="Erro na pesquisa",
            url="",
            resume=f"Erro ao processar a consulta: {str(e)}",
            concepts=[]
        )}


def final_writer(state: ReportState):
    search_results = ""
    references = ""
    all_concepts = []
    
    for i, result in enumerate(state.query_results):
        search_results += f"[{i+1}]\n\n"
        search_results += f"Title: {result.title}\n"
        search_results += f"URL: {result.url}\n"
        search_results += f"Content: {result.resume}\n\n"
        search_results += f"---------------------------------------\n\n"

        references += f"[{i+1}] - {result.title}({result.url})\n"
        
        # Coletar todos os conceitos
        if hasattr(result, 'concepts') and result.concepts:
            all_concepts.extend(result.concepts)

    prompt = build_final_response.format(user_input=state.user_input, search_results=search_results)

    llm_result = reasoning_llm.invoke(prompt)
    final_response = llm_result.content + "\n\nReferences:\n" + references
    
    # Salvar o grafo de conhecimento
    knowledge_graph.save_to_file("knowledge_graph.json")
    
    # Gerar sugestões de tópicos relacionados
    suggestions = knowledge_graph.suggest_next_research(all_concepts, limit=5)
    
    # Preparar dados do grafo para o frontend
    graph_stats = knowledge_graph.get_graph_stats()
    
    return {
        "final_response": final_response,
        "knowledge_graph_data": {
            "concepts": all_concepts,
            "suggestions": suggestions,
            "stats": graph_stats
        }
    }


def run_research(user_input: str):
    """
    Executa o processo completo de pesquisa para um input do usuário
    """
    try:
        initial_state = ReportState(user_input=user_input)
        final_state = graph.invoke(initial_state)
        return final_state.get('final_response', 'Erro: resposta não encontrada')
    except Exception as e:
        return f"Erro durante a pesquisa: {str(e)}"

# Edges (arestas)
builder = StateGraph(ReportState)

builder.add_node("build_first_queries", build_first_queries)
builder.add_node("single_search", single_search)
builder.add_node("final_writer", final_writer)

builder.add_edge(START, "build_first_queries")
builder.add_conditional_edges("build_first_queries", spawn_researches, ["single_search"])
builder.add_edge("single_search", "final_writer")
builder.add_edge("final_writer", END)

graph = builder.compile()



if __name__ == "__main__":
    from IPython.display import display, Image
    display(Image(graph.get_graph().draw_mermaid_png()))