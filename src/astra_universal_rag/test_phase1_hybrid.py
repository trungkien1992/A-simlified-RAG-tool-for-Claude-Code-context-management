#!/usr/bin/env python3
"""
Phase 1 Integration Test - Hybrid RAG System
Tests the integration of Neo4j graph database with ChromaDB vector store
"""

import asyncio
import logging
from pathlib import Path
from .hybrid.hybrid_rag import HybridRAG
from .graph.neo4j_adapter import Neo4jAdapter
from .config_phase1 import phase1_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_hybrid_system():
    """Test the Phase 1 hybrid RAG system"""
    
    # Initialize hybrid RAG
    rag = HybridRAG()
    rag.initialize_graph(
        uri=phase1_settings.neo4j_uri,
        username=phase1_settings.neo4j_username,
        password=phase1_settings.neo4j_password
    )
    
    # Test repository ingestion
    logger.info("Testing dual pipeline ingestion...")
    result = await rag.ingest_repository(
        repo_path=".",
        repo_url="https://github.com/astra/universal-rag"
    )
    logger.info(f"Ingestion result: {result}")
    
    # Test hybrid search
    logger.info("Testing hybrid search...")
    queries = [
        "Show me commits that fix authentication bugs",
        "Find all functions that handle payment processing",
        "What files were modified by the developer John Doe?",
        "Show me the relationship between API endpoints and their tests"
    ]
    
    for query in queries:
        logger.info(f"\nQuery: {query}")
        result = await rag.hybrid_search(query)
        logger.info(f"Vector results: {len(result.vector_results)}")
        logger.info(f"Graph context nodes: {len(result.graph_context)}")
        logger.info(f"Combined score: {result.combined_score:.3f}")
        logger.info(f"Reasoning path: {result.reasoning_path}")
        
    # Test graph traversal
    logger.info("\nTesting direct graph queries...")
    
    # Find all files modified in the last 10 commits
    cypher_query = """
    MATCH (c:Commit)-[:MODIFIES]->(f:File)
    RETURN f.path as file, COUNT(c) as modifications
    ORDER BY modifications DESC
    LIMIT 10
    """
    
    results = rag.graph_adapter.execute_cypher(cypher_query)
    logger.info(f"Most modified files: {results}")
    
    logger.info("\n✅ Phase 1 hybrid system test completed")


if __name__ == "__main__":
    asyncio.run(test_hybrid_system())
