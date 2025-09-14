from pydantic import BaseModel
from langchain_ollama import ChatOllama
from langgraph.graph import START, END, StateGraph
from langgraph.types import Send

from schemas import *
from prompts import *

from dotenv import load_dotenv
load_dotenv()

llm = ChatOllama(model="gemma3:1b")
reasoning_llm = ChatOllama(model="deepseek-r1:1.5b")


# Nós

def build_first_queries(state: ReportState):


    return {""}


# Edges (arestas)
builder = StateGraph(ReportState)

#TODO

graph = builder.compile()



if __name__ == "__main__":
    user_input = """Can you explain to me how is the full process of bulding an LLM? From scratch"""
    graph.invoke({"user_input": user_input})