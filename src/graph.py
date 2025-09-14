from pydantic import BaseModel
from langchain_ollama import ChatOllama
from langgraph.graph import START, END, StateGraph
from langgraph.types import Send
from tavily import TavilyClient

from schemas import *
from prompts import *

from dotenv import load_dotenv
load_dotenv()

llm = ChatOllama(model="gemma3:1b")
reasoning_llm = ChatOllama(model="deepseek-r1:1.5b")


# Nós

def build_first_queries(state: ReportState):
    class QueryList(BaseModel):
        queries: List[str]
    
    user_input = state.user_input

    prompt = build_queries.format(user_input=user_input)
    query_llm = llm.with_structured_output(QueryList)
    result = query_llm.invoke(prompt)

    return {"queries": result.queries}

# Para rodar todos os workers de forma assincrona e paralela
def spawn_researches(state: ReportState):
    return [Send("single_search", query) for query in state.queries]


def single_search(query: str):
    tavily = TavilyClient()
    results = tavily.search(query, max_results=3, include_raw_content=False)
    url = results["results"][0]["url"]
    url_etraction = tavily.extract(url)

    if len(url_etraction["results"]) > 0:
        raw_content = url_etraction["results"][0]["raw_content"]
        prompt = resume_search.format(user_input=user_input,search_results=raw_content)
        llm_result = llm.invoke(prompt)

        query_result = QueryResult(
            title=results["results"][0]["title"],
            url=url,
            resume=llm_result
        )
    return {"query_result": query_result}


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
    final_response = llm_result + "\n\nReferences:\n" + references

    return {"final_response": final_response}

# Edges (arestas)
builder = StateGraph(ReportState)

#TODO

graph = builder.compile()



if __name__ == "__main__":
    user_input = """Can you explain to me how is the full process of bulding an LLM? From scratch"""
    graph.invoke({"user_input": user_input})