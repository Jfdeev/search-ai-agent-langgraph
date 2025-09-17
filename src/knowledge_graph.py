from collections import defaultdict, Counter
import json
import re
from typing import Dict, List, Set, Tuple
import networkx as nx
import plotly.graph_objects as go
import plotly.express as px
from dataclasses import dataclass

@dataclass
class ConceptConnection:
    """Representa uma conexão entre conceitos"""
    target: str
    weight: float
    context: str = ""

class KnowledgeGraph:
    """
    Implementação de Mapa de Conhecimento usando Lista de Adjacência
    
    Estrutura de dados principal: dict[conceito] = [ConceptConnection, ...]
    Cada conceito aponta para uma lista de conceitos relacionados com pesos
    """
    
    def __init__(self):
        # Lista de Adjacência - estrutura principal
        self.adjacency_list: Dict[str, List[ConceptConnection]] = defaultdict(list)
        self.concept_frequency: Counter = Counter()
        self.concept_contexts: Dict[str, List[str]] = defaultdict(list)
        
    def extract_concepts(self, text: str, query_context: str = "") -> List[str]:
        """
        Extrai conceitos/entidades importantes do texto
        Usa regex simples para identificar conceitos (palavras capitalizadas, termos técnicos)
        """
        # Limpar texto
        text = re.sub(r'[^\w\s\-]', ' ', text)
        
        # Padrões para identificar conceitos
        patterns = [
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',  # Nomes próprios
            r'\b[A-Z]{2,}\b',                        # Siglas
            r'\b\w*[Gg]raph\w*\b',                   # Termos com "graph"
            r'\b\w*[Aa]rchitect\w*\b',              # Arquiteturas
            r'\b\w*[Ff]ramework\w*\b',              # Frameworks
            r'\b\w*[Ll]ibrar\w*\b',                 # Bibliotecas
            r'\b\w*[Aa]lgorithm\w*\b',              # Algoritmos
            r'\b\w*[Mm]odel\w*\b',                  # Modelos
        ]
        
        concepts = set()
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            concepts.update([match.strip() for match in matches if len(match.strip()) > 2])
        
        # Filtrar conceitos muito comuns
        common_words = {'The', 'This', 'That', 'With', 'From', 'For', 'And', 'But', 'Or'}
        concepts = [c for c in concepts if c not in common_words and len(c) > 2]
        
        # Adicionar contexto
        for concept in concepts:
            self.concept_contexts[concept].append(query_context)
            
        return list(concepts)
    
    def add_concept_connections(self, concepts: List[str], context: str = "", weight: float = 1.0):
        """
        Adiciona conexões entre conceitos na Lista de Adjacência
        Conecta todos os conceitos entre si (grafo completo para os conceitos da mesma fonte)
        """
        # Atualizar frequência
        for concept in concepts:
            self.concept_frequency[concept] += 1
            
        # Criar conexões bidirecionais entre todos os conceitos
        for i, concept1 in enumerate(concepts):
            for j, concept2 in enumerate(concepts):
                if i != j:  # Não conectar conceito consigo mesmo
                    self._add_connection(concept1, concept2, weight, context)
                    
    def _add_connection(self, concept1: str, concept2: str, weight: float, context: str):
        """Adiciona uma conexão na lista de adjacência"""
        # Verificar se conexão já existe
        existing_connections = self.adjacency_list[concept1]
        for conn in existing_connections:
            if conn.target == concept2:
                # Atualizar peso da conexão existente
                conn.weight += weight
                return
                
        # Criar nova conexão
        new_connection = ConceptConnection(
            target=concept2,
            weight=weight,
            context=context
        )
        self.adjacency_list[concept1].append(new_connection)
    
    def get_related_concepts(self, concept: str, min_weight: float = 0.5) -> List[Tuple[str, float]]:
        """
        Retorna conceitos relacionados a partir da Lista de Adjacência
        """
        if concept not in self.adjacency_list:
            return []
            
        related = []
        for connection in self.adjacency_list[concept]:
            if connection.weight >= min_weight:
                related.append((connection.target, connection.weight))
                
        # Ordenar por peso (mais relacionados primeiro)
        return sorted(related, key=lambda x: x[1], reverse=True)
    
    def suggest_next_research(self, current_concepts: List[str], limit: int = 5) -> List[str]:
        """
        Sugere próximos tópicos para pesquisa baseado nos conceitos atuais
        Usa a Lista de Adjacência para encontrar conceitos fortemente conectados
        """
        suggestion_scores = Counter()
        
        for concept in current_concepts:
            related = self.get_related_concepts(concept)
            for related_concept, weight in related:
                suggestion_scores[related_concept] += weight
                
        # Remove conceitos que já estão na pesquisa atual
        for concept in current_concepts:
            suggestion_scores.pop(concept, None)
            
        return [concept for concept, score in suggestion_scores.most_common(limit)]
    
    def get_graph_stats(self) -> Dict:
        """Retorna estatísticas do grafo"""
        total_concepts = len(self.adjacency_list)
        total_connections = sum(len(connections) for connections in self.adjacency_list.values())
        
        return {
            "total_concepts": total_concepts,
            "total_connections": total_connections,
            "most_frequent_concepts": self.concept_frequency.most_common(10),
            "average_connections_per_concept": total_connections / max(total_concepts, 1)
        }
    
    def create_networkx_graph(self, min_weight: float = 1.0) -> nx.Graph:
        """
        Cria um grafo NetworkX a partir da Lista de Adjacência
        Para visualização
        """
        G = nx.Graph()
        
        # Adicionar nós com tamanho baseado na frequência
        for concept, frequency in self.concept_frequency.items():
            G.add_node(concept, frequency=frequency, size=frequency * 10)
            
        # Adicionar arestas da Lista de Adjacência
        for concept, connections in self.adjacency_list.items():
            for connection in connections:
                if connection.weight >= min_weight:
                    G.add_edge(concept, connection.target, weight=connection.weight)
                    
        return G
    
    def save_to_file(self, filename: str):
        """Salva o grafo em arquivo JSON"""
        data = {
            "adjacency_list": {
                concept: [
                    {
                        "target": conn.target,
                        "weight": conn.weight,
                        "context": conn.context
                    }
                    for conn in connections
                ]
                for concept, connections in self.adjacency_list.items()
            },
            "concept_frequency": dict(self.concept_frequency),
            "concept_contexts": dict(self.concept_contexts)
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_from_file(self, filename: str):
        """Carrega o grafo de arquivo JSON"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Reconstruir adjacency_list
            self.adjacency_list = defaultdict(list)
            for concept, connections_data in data.get("adjacency_list", {}).items():
                for conn_data in connections_data:
                    connection = ConceptConnection(
                        target=conn_data["target"],
                        weight=conn_data["weight"],
                        context=conn_data.get("context", "")
                    )
                    self.adjacency_list[concept].append(connection)
            
            # Reconstruir outros dados
            self.concept_frequency = Counter(data.get("concept_frequency", {}))
            self.concept_contexts = defaultdict(list, data.get("concept_contexts", {}))
            
        except FileNotFoundError:
            pass  # Arquivo não existe, começar com grafo vazio