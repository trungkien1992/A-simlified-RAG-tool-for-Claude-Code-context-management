#!/usr/bin/env python3
"""
Hybrid RAG System - Phase 1
Combines vector search (ChromaDB) with graph traversal (Neo4j) for enhanced retrieval
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from ..rag_system import AstraRAG
from ..graph.neo4j_adapter import Neo4jAdapter
from ..schemas.universal_schema import EntityType, RelationType

logger = logging.getLogger(__name__)


@dataclass
class HybridSearchResult:
    """Result from hybrid search combining vector and graph results"""
    vector_results: List[Dict[str, Any]]
    graph_context: Dict[str, Any]
    combined_score: float
    reasoning_path: List[str]


class HybridRAG(AstraRAG):
    """
    Enhanced RAG system that combines vector similarity search
    with graph-based relationship traversal
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.graph_adapter: Optional[Neo4jAdapter] = None
        
    def initialize_graph(self, uri: str, username: str, password: str):
        """Initialize the graph database connection"""
        self.graph_adapter = Neo4jAdapter(uri, username, password)
        logger.info("Initialized graph adapter for hybrid RAG")
        
    async def hybrid_search(
        self,
        query: str,
        intent: Optional[str] = None,
        max_vector_results: int = 10,
        max_graph_depth: int = 2
    ) -> HybridSearchResult:
        """
        Perform hybrid search combining vector and graph retrieval
        
        1. Start with semantic search in vector store
        2. Use top results to find entry points in graph
        3. Traverse graph for additional context
        4. Combine and rank results
        """
        # Step 1: Vector search for semantic similarity
        vector_results = await self.search_with_intent(
            query=query,
            intent=intent or "general",
            top_k=max_vector_results
        )
        
        # Step 2: Extract graph node IDs from vector results
        graph_entry_points = []
        for result in vector_results.results[:3]:  # Top 3 as entry points
            if result.metadata.get("graph_node_id"):
                graph_entry_points.append(result.metadata["graph_node_id"])
                
        # Step 3: Graph traversal from entry points
        graph_context = {}
        reasoning_path = []
        
        if self.graph_adapter and graph_entry_points:
            for node_id in graph_entry_points:
                # Find related commits, files, and developers
                related = self.graph_adapter.find_related_nodes(
                    node_id=node_id,
                    relationship_types=[
                        RelationType.MODIFIES,
                        RelationType.AUTHORED_BY,
                        RelationType.FIXES,
                        RelationType.TESTS
                    ],
                    max_depth=max_graph_depth
                )
                
                graph_context[node_id] = related
                reasoning_path.append(
                    f"Found {len(related)} related nodes from {node_id}"
                )
                
        # Step 4: Combine and score results
        combined_score = self._calculate_combined_score(
            vector_results, graph_context
        )
        
        return HybridSearchResult(
            vector_results=[r.to_dict() for r in vector_results.results],
            graph_context=graph_context,
            combined_score=combined_score,
            reasoning_path=reasoning_path
        )
        
    def _calculate_combined_score(
        self,
        vector_results: Any,
        graph_context: Dict[str, Any]
    ) -> float:
        """Calculate combined relevance score"""
        # Simple weighted combination for now
        vector_score = vector_results.confidence_score if hasattr(vector_results, 'confidence_score') else 0.5
        graph_score = min(1.0, len(graph_context) / 10.0) if graph_context else 0.0
        
        # 70% vector, 30% graph
        return 0.7 * vector_score + 0.3 * graph_score
