#!/usr/bin/env python3
"""
Graph-Aware Search System for Astra Knowledge Base
Combines knowledge graph queries with semantic vector search for intelligent answers
"""

import logging
import re
from typing import List, Dict, Any, Tuple
from datetime import datetime
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from graph_models import knowledge_graph
from rag_system import AstraRAG

logger = logging.getLogger(__name__)


class GraphAwareSearch:
    """Advanced search system that combines knowledge graph queries with vector search for contextually aware and precise answers"""

    def __init__(self):
        self.rag_system = None
        self.graph = knowledge_graph
        self.query_patterns = self._initialize_query_patterns()

    def _initialize_query_patterns(self) -> Dict[str, Dict]:
        """Initialize query patterns for different types of questions"""
        return {
            "developer_work": {
                "patterns": [
                    r"what has (\w+) worked on.*?(\w+)",
                    r"show me (\w+)\'s work.*?(\w+)",
                    r"(\w+).*?contributed.*?(\w+)",
                    r"(\w+).*?implemented.*?(\w+)",
                ],
                "description": "Find work done by a specific developer on a feature",
            },
            "file_history": {
                "patterns": [
                    r"who.*?last.*?changed.*?([^\s]+\.[^\s]+)",
                    r"history.*?([^\s]+\.[^\s]+)",
                    r"who.*?modified.*?([^\s]+\.[^\s]+)",
                    r"changes.*?([^\s]+\.[^\s]+)",
                ],
                "description": "Find who changed a file and when",
            },
            "feature_contributors": {
                "patterns": [
                    r"who.*?worked.*?(\w+)",
                    r"contributors.*?(\w+)",
                    r"who.*?implemented.*?(\w+)",
                    r"team.*?(\w+)",
                ],
                "description": "Find all people who worked on a feature",
            },
            "commit_details": {
                "patterns": [
                    r"show.*?commit.*?(\w+)",
                    r"details.*?commit.*?(\w+)",
                    r"changes.*?commit.*?(\w+)",
                ],
                "description": "Get details about a specific commit",
            },
            "recent_work": {
                "patterns": [
                    r"recent.*?work.*?(\w+)",
                    r"latest.*?(\w+)",
                    r"what.*?(\w+).*?recently",
                ],
                "description": "Find recent work by a developer",
            },
        }

    async def initialize(self):
        """Initialize both RAG system and knowledge graph"""
        logger.info("🚀 Initializing Graph-Aware Search System...")

        # Initialize RAG system
        self.rag_system = AstraRAG()
        await self.rag_system.initialize()

        # Initialize knowledge graph
        if not await self.graph.connect():
            logger.error("❌ Failed to initialize knowledge graph")
            return False

        logger.info("✅ Graph-Aware Search System initialized successfully")
        return True

    def _classify_query(self, query: str) -> Tuple[str, List[str]]:
        """Classify the query and extract key parameters"""
        query_lower = query.lower()

        for query_type, config in self.query_patterns.items():
            for pattern in config["patterns"]:
                match = re.search(pattern, query_lower)
                if match:
                    return query_type, list(match.groups())

        return "general", []

    async def search(
        self,
        query: str,
        max_results: int = 5,
        use_graph: bool = True,
        use_vector: bool = True,
    ) -> Dict[str, Any]:
        """
        Perform intelligent search combining graph queries and vector search
        """
        start_time = datetime.now()

        logger.info(f"🔍 Processing query: '{query}'")

        # Classify the query
        query_type, parameters = self._classify_query(query)
        logger.info(f"📊 Query type: {query_type}, Parameters: {parameters}")

        results = {
            "query": query,
            "query_type": query_type,
            "parameters": parameters,
            "graph_results": [],
            "vector_results": [],
            "combined_results": [],
            "execution_time": 0,
            "sources": [],
        }

        # Execute graph-based search if enabled
        if use_graph and query_type != "general":
            try:
                graph_results = await self._execute_graph_query(query_type, parameters)
                results["graph_results"] = graph_results
                logger.info(f"📊 Graph query returned {len(graph_results)} results")
            except Exception as e:
                logger.error(f"❌ Graph query failed: {e}")
                results["graph_results"] = []

        # Execute vector search if enabled
        if use_vector and self.rag_system:
            try:
                vector_results = await self.rag_system.search(
                    query=query, max_results=max_results, min_similarity=0.3
                )
                results["vector_results"] = vector_results["results"]
                logger.info(
                    f"📊 Vector search returned {len(vector_results['results'])} results"
                )
            except Exception as e:
                logger.error(f"❌ Vector search failed: {e}")
                results["vector_results"] = []

        # Combine and enhance results
        if results["graph_results"] and results["vector_results"]:
            results["combined_results"] = await self._combine_graph_and_vector_results(
                results["graph_results"], results["vector_results"], query_type
            )
        elif results["graph_results"]:
            results["combined_results"] = await self._format_graph_results(
                results["graph_results"]
            )
        elif results["vector_results"]:
            results["combined_results"] = results["vector_results"]

        # Calculate execution time
        execution_time = (datetime.now() - start_time).total_seconds()
        results["execution_time"] = execution_time

        logger.info(f"✅ Search completed in {execution_time:.3f}s")
        return results

    async def _execute_graph_query(
        self, query_type: str, parameters: List[str]
    ) -> List[Dict[str, Any]]:
        """Execute graph-specific queries based on query type"""

        if query_type == "developer_work" and len(parameters) >= 2:
            developer_name = parameters[0]
            feature_keyword = parameters[1]
            return await self.graph.find_developer_work(developer_name, feature_keyword)

        elif query_type == "file_history" and len(parameters) >= 1:
            file_path = parameters[0]
            return await self.graph.find_file_history(file_path)

        elif query_type == "feature_contributors" and len(parameters) >= 1:
            feature_name = parameters[0]
            return await self.graph.find_feature_contributors(feature_name)

        elif query_type == "recent_work" and len(parameters) >= 1:
            developer_name = parameters[0]
            # Get recent work (last 10 commits)
            work_results = await self.graph.find_developer_work(developer_name)
            # Sort by timestamp and return recent ones
            sorted_results = sorted(
                work_results, key=lambda x: x["commit"]["timestamp"], reverse=True
            )
            return sorted_results[:10]

        return []

    async def _combine_graph_and_vector_results(
        self, graph_results: List[Dict], vector_results: List[Dict], query_type: str
    ) -> List[Dict[str, Any]]:
        """Intelligently combine graph and vector search results"""
        combined = []

        # For developer work queries, enhance graph results with vector search context
        if query_type == "developer_work":
            for graph_result in graph_results:
                commit = graph_result["commit"]

                # Find related vector results based on commit hash
                related_vectors = []
                for vector_result in vector_results:
                    if commit["hash"] in vector_result.get("content", "") or commit[
                        "hash"
                    ][:8] in vector_result.get("content", ""):
                        related_vectors.append(vector_result)

                combined.append(
                    {
                        "type": "enhanced_commit",
                        "commit": commit,
                        "files": graph_result["files"],
                        "vector_context": related_vectors[:2],  # Top 2 related results
                        "source": "graph + vector",
                    }
                )

        # For file history, combine chronological graph data with content context
        elif query_type == "file_history":
            for graph_result in graph_results:
                commit = graph_result["commit"]
                author = graph_result["author"]

                # Find vector results that mention this file
                related_vectors = []
                for vector_result in vector_results:
                    if any(
                        file_path in vector_result.get("content", "")
                        for file_path in [
                            r["path"] for r in graph_result.get("files", [])
                        ]
                    ):
                        related_vectors.append(vector_result)

                combined.append(
                    {
                        "type": "file_change",
                        "commit": commit,
                        "author": author,
                        "vector_context": related_vectors[:1],
                        "source": "graph + vector",
                    }
                )

        # For feature contributors, group by developer
        elif query_type == "feature_contributors":
            for graph_result in graph_results:
                developer = graph_result["developer"]
                commits = graph_result["commits"]

                # Find vector results related to this developer's work
                related_vectors = []
                for vector_result in vector_results:
                    if (
                        developer["name"].lower()
                        in vector_result.get("content", "").lower()
                    ):
                        related_vectors.append(vector_result)

                combined.append(
                    {
                        "type": "contributor_summary",
                        "developer": developer,
                        "commits": commits,
                        "contribution_count": len(commits),
                        "vector_context": related_vectors[:2],
                        "source": "graph + vector",
                    }
                )

        # If no specific combination logic, interleave results
        else:
            # Add top graph results
            for result in graph_results[:3]:
                combined.append(
                    {"type": "graph_result", "data": result, "source": "graph"}
                )

            # Add top vector results
            for result in vector_results[:2]:
                combined.append(
                    {
                        "type": "vector_result",
                        "title": result.get("title", "Unknown"),
                        "content": result.get("content", "")[:200] + "...",
                        "similarity": result.get("similarity", 0),
                        "source": "vector",
                    }
                )

        return combined

    async def _format_graph_results(
        self, graph_results: List[Dict]
    ) -> List[Dict[str, Any]]:
        """Format graph-only results for consistent output"""
        formatted = []

        for result in graph_results:
            formatted.append({"type": "graph_only", "data": result, "source": "graph"})

        return formatted

    async def get_sample_queries(self) -> List[Dict[str, str]]:
        """Get sample queries that demonstrate graph-aware search capabilities"""
        return [
            {
                "query": "What has Peter worked on related to leaderboard?",
                "type": "developer_work",
                "description": "Find specific developer work on a feature",
            },
            {
                "query": "Who was the last person to change leaderboard_service.dart and when?",
                "type": "file_history",
                "description": "Get file modification history",
            },
            {
                "query": "Show me all contributors to the authentication feature",
                "type": "feature_contributors",
                "description": "Find everyone who worked on a feature",
            },
            {
                "query": "What has John worked on recently?",
                "type": "recent_work",
                "description": "Get recent activity for a developer",
            },
            {
                "query": "How does the XP system work?",
                "type": "general",
                "description": "General knowledge search using vector similarity",
            },
        ]

    async def explain_query_processing(self, query: str) -> Dict[str, Any]:
        """Explain how a query would be processed (for debugging/demonstration)"""
        query_type, parameters = self._classify_query(query)

        explanation = {
            "original_query": query,
            "detected_type": query_type,
            "extracted_parameters": parameters,
            "graph_query_available": query_type != "general",
            "processing_strategy": {},
            "example_graph_query": None,
        }

        if query_type == "developer_work":
            explanation["processing_strategy"] = {
                "step_1": "Query knowledge graph for developer commits",
                "step_2": "Filter by feature keyword if provided",
                "step_3": "Find related files and relationships",
                "step_4": "Enhance with vector search for detailed content",
            }
            if len(parameters) >= 2:
                explanation["example_graph_query"] = (
                    f"MATCH (d:Developer {{name: '{parameters[0]}'}})-[:AUTHORED]->(c:Commit)-[:MODIFIED]->(f:File) WHERE f.path CONTAINS '{parameters[1]}' RETURN c, f"
                )

        elif query_type == "file_history":
            explanation["processing_strategy"] = {
                "step_1": "Find file node in knowledge graph",
                "step_2": "Get all commits that modified this file",
                "step_3": "Find authors and timestamps",
                "step_4": "Sort by recency and enhance with content",
            }
            if len(parameters) >= 1:
                explanation["example_graph_query"] = (
                    f"MATCH (f:File {{path: '{parameters[0]}'}})<-[:MODIFIED]-(c:Commit)<-[:AUTHORED]-(d:Developer) RETURN d, c ORDER BY c.timestamp DESC"
                )

        return explanation


# Global instance
graph_search = GraphAwareSearch()
