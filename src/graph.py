from pydantic import BaseModel, Field
from langchain_ollama import ChatOllama
from langgraph.graph import START, END, StateGraph
from langgraph.types import Send
from tavily import TavilyClient

from schemas import *
from prompts import *

from dotenv import load_dotenv
load_dotenv()

llm = ChatOllama(model="gemma3:1b")
reasoning_llm = ChatOllama(model="gemma2:2b")


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
                resume="Não foi possível encontrar informações relevantes para esta consulta."
            )}
        
        url = results["results"][0]["url"]
        url_etraction = tavily.extract(url)

        if len(url_etraction["results"]) > 0:
            raw_content = url_etraction["results"][0]["raw_content"]
            prompt = resume_search.format(user_input=query, search_results=raw_content)
            llm_result = llm.invoke(prompt)

            query_result = QueryResult(
                title=results["results"][0]["title"],
                url=url,
                resume=llm_result.content
            )
        else:
            query_result = QueryResult(
                title=results["results"][0]["title"],
                url=url,
                resume="Conteúdo não disponível para extração."
            )
            
        return {"query_result": query_result}
    
    except Exception as e:
        return {"query_result": QueryResult(
            title="Erro na pesquisa",
            url="",
            resume=f"Erro ao processar a consulta: {str(e)}"
        )}


def final_writer(state: ReportState):
    search_results = ""
    references = ""
    for i, result in enumerate(state.query_results):
        search_results += f"[{i+1}]\n\n"
        search_results += f"Title: {result.title}\n"
        search_results += f"URL: {result.url}\n"
        search_results += f"Content: {result.resume}\n\n"
        search_results += f"---------------------------------------\n\n"

        references += f"[{i+1}] - {result.title}({result.url})\n"

    prompt = build_final_response.format(user_input=state.user_input, search_results=search_results)

    llm_result = reasoning_llm.invoke(prompt)
    final_response = llm_result.content + "\n\nReferences:\n" + references

    return {"final_response": final_response}


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