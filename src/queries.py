"""
Job search queries organized by category.
This module contains predefined search queries for different types of AI/ML positions.
"""

from dataclasses import dataclass
from typing import List, Dict, Any
import random


@dataclass
class QuerySet:
    """A set of related job search queries."""
    name: str
    description: str
    queries: List[str]
    
    def get_random_query(self) -> str:
        """Get a random query from this set."""
        return random.choice(self.queries)
    
    def get_all_queries(self) -> List[str]:
        """Get all queries in this set."""
        return self.queries.copy()


# Define all query sets
CORE_LLM_QUERIES = QuerySet(
    name="Core LLM / Generative AI",
    description="Core large language model and generative AI positions",
    queries=[
        "LLM engineer",
        "large language model engineer",
        "Generative AI engineer", 
        "LLM developer",
        "Applied AI engineer",
        "LLM scientist"
    ]
)

AGENTIC_AI_QUERIES = QuerySet(
    name="Agentic AI / AI Agents",
    description="AI agents and autonomous systems positions",
    queries=[
        "Agentic AI engineer",
        "AI agent developer",
        "autonomous AI agents",
        "multi-agent systems engineer",
        "AI orchestration engineer",
        "AI automation engineer"
    ]
)

PYTHON_ML_QUERIES = QuerySet(
    name="Python + ML",
    description="Python-focused machine learning positions",
    queries=[
        "Python AI engineer",
        "Python machine learning engineer",
        "ML engineer Python",
        "Deep learning engineer",
        "Applied ML engineer",
        "AI/ML engineer"
    ]
)

RAG_VECTOR_QUERIES = QuerySet(
    name="RAG / Vector DB / LangChain", 
    description="RAG, vector databases, and AI framework positions",
    queries=[
        "RAG engineer",
        "retrieval augmented generation",
        "Vector database AI",
        "LangChain engineer", 
        "LlamaIndex engineer",
        "Embedding engineer"
    ]
)

STARTUP_CATCHALL_QUERIES = QuerySet(
    name="Catch-All / Startup Variants",
    description="Startup and specialized AI positions",
    queries=[
        "Founding AI engineer",
        "AI researcher engineer",
        "NLP engineer",
        "natural language processing",
        "Prompt engineer LLM",
        "AI systems developer",
        "AI infrastructure engineer"
    ]
)

# All query sets grouped
ALL_QUERY_SETS = [
    CORE_LLM_QUERIES,
    AGENTIC_AI_QUERIES,
    PYTHON_ML_QUERIES,
    RAG_VECTOR_QUERIES,
    STARTUP_CATCHALL_QUERIES
]

# Convenience dictionaries for easy access
QUERY_SETS_BY_NAME = {qs.name: qs for qs in ALL_QUERY_SETS}


def get_all_queries() -> List[str]:
    """Get all queries from all sets as a flat list."""
    all_queries = []
    for query_set in ALL_QUERY_SETS:
        all_queries.extend(query_set.queries)
    return all_queries


def get_random_query() -> str:
    """Get a random query from any set."""
    return random.choice(get_all_queries())


def get_random_query_from_set(set_name: str) -> str:
    """Get a random query from a specific set."""
    if set_name not in QUERY_SETS_BY_NAME:
        raise ValueError(f"Unknown query set: {set_name}. Available: {list(QUERY_SETS_BY_NAME.keys())}")
    return QUERY_SETS_BY_NAME[set_name].get_random_query()


def list_query_sets() -> List[str]:
    """List all available query set names."""
    return list(QUERY_SETS_BY_NAME.keys())


def search_queries(keyword: str) -> List[str]:
    """Search for queries containing a specific keyword."""
    keyword_lower = keyword.lower()
    matching_queries = []
    
    for query in get_all_queries():
        if keyword_lower in query.lower():
            matching_queries.append(query)
    
    return matching_queries


# Quick access functions for each category
def get_core_llm_queries() -> List[str]:
    """Get all core LLM queries."""
    return CORE_LLM_QUERIES.get_all_queries()


def get_agentic_ai_queries() -> List[str]:
    """Get all agentic AI queries."""
    return AGENTIC_AI_QUERIES.get_all_queries()


def get_python_ml_queries() -> List[str]:
    """Get all Python ML queries."""
    return PYTHON_ML_QUERIES.get_all_queries()


def get_rag_vector_queries() -> List[str]:
    """Get all RAG/Vector queries."""
    return RAG_VECTOR_QUERIES.get_all_queries()


def get_startup_queries() -> List[str]:
    """Get all startup/catch-all queries."""
    return STARTUP_CATCHALL_QUERIES.get_all_queries()


def main():
    """Main function for the queries module."""
    # Demo usage
    print("🔍 Job Search Queries Demo\n")
    
    print("📋 Available Query Sets:")
    for query_set in ALL_QUERY_SETS:
        print(f"  • {query_set.name}: {len(query_set.queries)} queries")
        print(f"    {query_set.description}")
    
    print(f"\n📊 Total queries: {len(get_all_queries())}")
    for query in get_all_queries():
        print(f"\t{query}")
    
    print(f"\n🎲 Random query: '{get_random_query()}'")
    print(f"🎲 Random LLM query: '{get_random_query_from_set('Core LLM / Generative AI')}'")


if __name__ == "__main__":
    main()
