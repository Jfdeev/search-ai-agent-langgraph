from pydantic import BaseModel
from typing import List, Dict, Any
import operator
from typing_extensions import Annotated

class QueryResult(BaseModel):
    title: str = None
    url: str = None
    resume: str = None
    concepts: List[str] = []  # Conceitos extraídos desta pesquisa
    
class ReportState(BaseModel):
    user_input: str = None
    final_response: str = None
    queries: List[str] = []
    query_results: Annotated[List[QueryResult], operator.add] = []
    knowledge_graph_data: Dict[str, Any] = {}  # Dados do grafo de conhecimento

