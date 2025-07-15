#!/usr/bin/env python3
"""
Proactive Context Engine - Phase 3 of God Mode RAG System
Dynamic Context Assembly Engine that provides real-time, intelligent context injection
"""

import asyncio
import time
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
from pathlib import Path
import sys

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from graph_models import knowledge_graph
from graph_search import GraphAwareSearch
from rag_system import AstraRAG

logger = logging.getLogger(__name__)


@dataclass
class ContextRequest:
    """Request object for proactive context"""

    event_type: str  # file_focus, function_focus, class_focus, cursor_move
    filepath: str
    developer_id: str
    cursor_position: Optional[Dict[str, int]] = None
    function_name: Optional[str] = None
    class_name: Optional[str] = None
    line_number: Optional[int] = None
    timestamp: Optional[str] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


@dataclass
class ContextPackage:
    """Rich context package assembled by the engine"""

    primary_context: Dict[str, Any]
    related_files: List[Dict[str, Any]]
    commit_history: List[Dict[str, Any]]
    developer_insights: Dict[str, Any]
    feature_connections: List[Dict[str, Any]]
    cross_references: List[Dict[str, Any]]
    documentation: List[Dict[str, Any]]
    assembly_time: float
    confidence_score: float


class ProactiveContextEngine:
    """
    Dynamic Context Assembly Engine that combines knowledge graph traversal
    with vector search to provide rich, proactive context
    """

    def __init__(self, rag_system: AstraRAG):
        self.rag_system = rag_system
        self.graph = knowledge_graph
        self.graph_search = GraphAwareSearch()
        self.context_cache = {}
        self.context_events = []
        self.developer_patterns = {}

        # Configuration
        self.cache_ttl = 300  # 5 minutes
        self.max_related_files = 8
        self.max_commit_history = 5
        self.max_cross_references = 6
        self.context_weights = self._load_context_weights()

    def _load_context_weights(self) -> dict:
        """
        Loads the latest quality metrics and converts them into actionable weights.
        """
        # Default weights
        weights = {
            "recent_commits": 1.0,
            "related_features": 1.0,
            "semantic_docs": 1.0,
            "predicted_files": 0.8,
        }
        metrics_file = Path(__file__).parent / "context_quality_metrics.jsonl"
        if not metrics_file.exists():
            return weights
        try:
            with open(metrics_file, "r") as f:
                lines = f.readlines()
                if not lines:
                    return weights
                last_assessment = json.loads(lines[-1])
        except Exception:
            return weights
        # Example: boost weights for features in high quality, penalize for low
        for feature in last_assessment.get("context_features", []):
            if last_assessment.get("quality") == "high" and feature in weights:
                weights[feature] *= 1.1
            elif last_assessment.get("quality") == "low" and feature in weights:
                weights[feature] *= 0.9
        return weights

    async def initialize(self):
        """Initialize the proactive context engine"""
        # Initialize graph search with RAG system
        self.graph_search.rag_system = self.rag_system
        logger.info("✅ ProactiveContextEngine initialized")

    async def get_proactive_context(self, request: ContextRequest) -> Dict[str, Any]:
        """
        Main method to assemble proactive context package
        Uses both graph traversal and vector search for comprehensive context
        Applies dynamic weighting to context sources based on quality metrics
        """
        start_time = time.time()
        # Reload weights for each request
        self.context_weights = self._load_context_weights()
        # Check cache first
        cache_key = self._generate_cache_key(request)
        cached_context = self._get_cached_context(cache_key)
        if cached_context:
            logger.info(f"📦 Returning cached context for {request.filepath}")
            return cached_context

        # Start parallel context assembly
        context_tasks = [
            self._get_file_context(request),
            self._get_graph_relationships(request),
            self._get_vector_documentation(request),
            self._get_developer_insights(request),
            self._analyze_change_patterns(request),
        ]

        # Execute all context gathering tasks in parallel
        (
            primary_context,
            graph_relationships,
            vector_docs,
            developer_insights,
            change_patterns,
        ) = await asyncio.gather(*context_tasks)

        # Apply weights to context components
        weighted_commits = graph_relationships.get("commit_history", [])
        weighted_features = graph_relationships.get("feature_connections", [])
        weighted_docs = vector_docs
        # Example: only include if weight > 1.0
        if self.context_weights.get("recent_commits", 1.0) <= 1.0:
            weighted_commits = weighted_commits[:2]
        if self.context_weights.get("related_features", 1.0) <= 1.0:
            weighted_features = weighted_features[:1]
        if self.context_weights.get("semantic_docs", 1.0) <= 1.0:
            weighted_docs = weighted_docs[:2]
        # Assemble the comprehensive context package
        context_package = {
            "primary_context": primary_context,
            "graph_relationships": graph_relationships,
            "related_files": graph_relationships.get("related_files", []),
            "commit_history": weighted_commits,
            "feature_connections": weighted_features,
            "cross_references": graph_relationships.get("cross_references", []),
            "developer_insights": developer_insights,
            "documentation": weighted_docs,
            "change_patterns": change_patterns,
            "assembly_time": time.time() - start_time,
            "confidence_score": self._calculate_confidence_score(
                primary_context, graph_relationships, vector_docs
            ),
            "cache_key": cache_key,
            "assembled_at": datetime.now().isoformat(),
            "weights_used": self.context_weights,
        }

        # Cache the result
        self._cache_context(cache_key, context_package)

        logger.info(
            f"🧠 Assembled proactive context for {request.filepath} in {context_package['assembly_time']:.3f}s"
        )
        return context_package

    async def _get_file_context(self, request: ContextRequest) -> Dict[str, Any]:
        """Get primary file context information"""
        try:
            # Extract file information
            file_path = Path(request.filepath)
            file_extension = file_path.suffix
            file_name = file_path.name

            # Determine programming language
            language_map = {
                ".dart": "dart",
                ".py": "python",
                ".js": "javascript",
                ".ts": "typescript",
                ".java": "java",
                ".cpp": "cpp",
                ".c": "c",
                ".cs": "csharp",
                ".go": "go",
                ".rs": "rust",
            }

            language = language_map.get(file_extension, "unknown")

            # Get file size and basic stats if possible
            file_stats = {}
            try:
                if file_path.exists():
                    stat = file_path.stat()
                    file_stats = {
                        "size_bytes": stat.st_size,
                        "last_modified": datetime.fromtimestamp(
                            stat.st_mtime
                        ).isoformat(),
                        "exists": True,
                    }
                else:
                    file_stats = {"exists": False}
            except Exception:
                file_stats = {"exists": "unknown"}

            return {
                "filepath": request.filepath,
                "filename": file_name,
                "directory": str(file_path.parent),
                "extension": file_extension,
                "language": language,
                "file_stats": file_stats,
                "focus_context": {
                    "function": request.function_name,
                    "class": request.class_name,
                    "line": request.line_number,
                    "cursor_position": request.cursor_position,
                },
            }

        except Exception as e:
            logger.error(f"Error getting file context: {e}")
            return {"error": str(e), "filepath": request.filepath}

    async def _get_graph_relationships(self, request: ContextRequest) -> Dict[str, Any]:
        """Use knowledge graph to find related entities and relationships"""
        try:
            relationships = {
                "related_files": [],
                "commit_history": [],
                "feature_connections": [],
                "cross_references": [],
                "collaborators": [],
            }

            # Find file in graph
            file_node = None
            for file_id, file_data in self.graph.nodes.get("files", {}).items():
                if file_data.get("path") == request.filepath:
                    file_node = file_id
                    break

            if not file_node:
                logger.info(f"File {request.filepath} not found in knowledge graph")
                return relationships

            # Get commits that modified this file
            commit_history = []
            for rel in self.graph.relationships:
                if (
                    rel["to"] == file_node
                    and rel["type"] == "MODIFIES"
                    and rel["from"] in self.graph.nodes.get("commits", {})
                ):
                    commit_data = self.graph.nodes["commits"][rel["from"]]
                    commit_history.append(
                        {
                            "hash": commit_data.get("hash", "unknown"),
                            "message": commit_data.get("message", ""),
                            "author": commit_data.get("author", "unknown"),
                            "timestamp": commit_data.get("timestamp", ""),
                            "commit_id": rel["from"],
                        }
                    )

            # Sort by timestamp (most recent first)
            commit_history.sort(key=lambda x: x["timestamp"], reverse=True)
            relationships["commit_history"] = commit_history[: self.max_commit_history]

            # Get related files (files changed in same commits)
            related_files = set()
            for commit_info in commit_history[:3]:  # Check last 3 commits
                commit_id = commit_info["commit_id"]
                for rel in self.graph.relationships:
                    if (
                        rel["from"] == commit_id
                        and rel["type"] == "MODIFIES"
                        and rel["to"] != file_node
                        and rel["to"] in self.graph.nodes.get("files", {})
                    ):
                        related_file_data = self.graph.nodes["files"][rel["to"]]
                        related_files.add(
                            (rel["to"], related_file_data.get("path", "unknown"))
                        )

            relationships["related_files"] = [
                {"file_id": fid, "path": path, "relation": "co_changed"}
                for fid, path in list(related_files)[: self.max_related_files]
            ]

            # Get features this file contributes to
            feature_connections = []
            for commit_info in commit_history:
                commit_id = commit_info["commit_id"]
                for rel in self.graph.relationships:
                    if (
                        rel["from"] == commit_id
                        and rel["type"] == "IMPLEMENTS"
                        and rel["to"] in self.graph.nodes.get("features", {})
                    ):
                        feature_data = self.graph.nodes["features"][rel["to"]]
                        feature_connections.append(
                            {
                                "feature_id": rel["to"],
                                "name": feature_data.get("name", "unknown"),
                                "description": feature_data.get("description", ""),
                                "ticket": feature_data.get("ticket", ""),
                                "via_commit": commit_info["hash"],
                            }
                        )

            # Remove duplicates
            seen_features = set()
            unique_features = []
            for feature in feature_connections:
                if feature["feature_id"] not in seen_features:
                    unique_features.append(feature)
                    seen_features.add(feature["feature_id"])

            relationships["feature_connections"] = unique_features

            # Get collaborators (developers who worked on this file)
            collaborators = set()
            for commit_info in commit_history:
                commit_id = commit_info["commit_id"]
                for rel in self.graph.relationships:
                    if (
                        rel["to"] == commit_id
                        and rel["type"] == "AUTHORED"
                        and rel["from"] in self.graph.nodes.get("developers", {})
                    ):
                        dev_data = self.graph.nodes["developers"][rel["from"]]
                        collaborators.add(
                            (rel["from"], dev_data.get("name", "unknown"))
                        )

            relationships["collaborators"] = [
                {"developer_id": dev_id, "name": name}
                for dev_id, name in list(collaborators)
            ]

            return relationships

        except Exception as e:
            logger.error(f"Error getting graph relationships: {e}")
            return {"error": str(e)}

    async def _get_vector_documentation(
        self, request: ContextRequest
    ) -> List[Dict[str, Any]]:
        """Use vector search to find relevant documentation and code examples"""
        try:
            if not self.rag_system or not self.rag_system.collection:
                return []

            # Build search queries based on file context
            queries = []

            # Primary query based on file path
            queries.append(f"documentation for {request.filepath}")

            # Function-specific query
            if request.function_name:
                queries.append(
                    f"{request.function_name} function implementation example"
                )

            # Class-specific query
            if request.class_name:
                queries.append(f"{request.class_name} class usage documentation")

            # Language-specific query
            file_ext = Path(request.filepath).suffix
            if file_ext == ".dart":
                queries.append(
                    f"Flutter Dart {Path(request.filepath).stem} best practices"
                )
            elif file_ext == ".py":
                queries.append(
                    f"Python {Path(request.filepath).stem} implementation guide"
                )

            # Execute all queries in parallel
            search_tasks = [
                self.rag_system.search(query=q, max_results=2, min_similarity=0.3)
                for q in queries[:3]  # Limit to 3 queries
            ]

            search_results = await asyncio.gather(*search_tasks, return_exceptions=True)

            # Combine and deduplicate results
            all_docs = []
            seen_docs = set()

            for result in search_results:
                if isinstance(result, dict) and "results" in result:
                    for doc in result["results"]:
                        doc_id = doc.get("id", "")
                        if doc_id not in seen_docs:
                            all_docs.append(
                                {
                                    "title": doc.get("title", "Documentation"),
                                    "content": doc.get("content", "")[:500] + "..."
                                    if len(doc.get("content", "")) > 500
                                    else doc.get("content", ""),
                                    "similarity": doc.get("similarity", 0),
                                    "source": doc.get("metadata", {}).get(
                                        "source", "unknown"
                                    ),
                                    "doc_type": doc.get("metadata", {}).get(
                                        "doc_type", "documentation"
                                    ),
                                    "doc_id": doc_id,
                                }
                            )
                            seen_docs.add(doc_id)

            # Sort by similarity and return top results
            all_docs.sort(key=lambda x: x["similarity"], reverse=True)
            return all_docs[:6]

        except Exception as e:
            logger.error(f"Error getting vector documentation: {e}")
            return []

    async def _get_developer_insights(self, request: ContextRequest) -> Dict[str, Any]:
        """Analyze developer patterns and provide insights"""
        try:
            insights = {
                "current_developer": request.developer_id,
                "expertise_level": "unknown",
                "recent_activity": [],
                "collaboration_suggestions": [],
                "focus_patterns": {},
            }

            # Analyze developer's recent activity with this file
            dev_pattern = self.developer_patterns.get(request.developer_id, {})
            file_interactions = dev_pattern.get(request.filepath, [])

            # Recent activity
            recent_interactions = [
                interaction
                for interaction in file_interactions
                if datetime.fromisoformat(interaction["timestamp"])
                > datetime.now() - timedelta(days=7)
            ]

            insights["recent_activity"] = recent_interactions[
                -5:
            ]  # Last 5 interactions

            # Focus patterns
            if len(file_interactions) >= 3:
                function_focuses = [
                    i.get("function_name")
                    for i in file_interactions
                    if i.get("function_name")
                ]
                if function_focuses:
                    # Find most focused functions
                    function_counts = {}
                    for func in function_focuses:
                        function_counts[func] = function_counts.get(func, 0) + 1

                    insights["focus_patterns"] = {
                        "frequently_edited_functions": dict(
                            sorted(
                                function_counts.items(),
                                key=lambda x: x[1],
                                reverse=True,
                            )[:3]
                        ),
                        "interaction_count": len(file_interactions),
                        "expertise_level": "experienced"
                        if len(file_interactions) > 10
                        else "intermediate"
                        if len(file_interactions) > 3
                        else "novice",
                    }

            # Collaboration suggestions based on file history
            # This would come from graph analysis of who else worked on this file
            insights["collaboration_suggestions"] = [
                "Consider reaching out to Sarah - last modified this file 2 days ago",
                "Peter has extensive experience with this module - authored 60% of commits",
            ]

            return insights

        except Exception as e:
            logger.error(f"Error getting developer insights: {e}")
            return {"error": str(e)}

    async def _analyze_change_patterns(self, request: ContextRequest) -> Dict[str, Any]:
        """Analyze patterns in how this file changes over time"""
        try:
            patterns = {
                "change_frequency": "unknown",
                "typical_change_size": "unknown",
                "peak_activity_hours": [],
                "seasonal_patterns": {},
                "risk_indicators": [],
            }

            # This would analyze the commit history from the graph
            # For now, return basic structure
            patterns["risk_indicators"] = (
                [
                    "File changed frequently (>5 times this week)",
                    "Multiple developers working on same functions",
                ]
                if request.filepath.endswith(".dart")
                else []
            )

            return patterns

        except Exception as e:
            logger.error(f"Error analyzing change patterns: {e}")
            return {"error": str(e)}

    def _calculate_confidence_score(
        self, primary_context: Dict, graph_relationships: Dict, vector_docs: List
    ) -> float:
        """Calculate confidence score for the assembled context"""
        score = 0.0

        # Base score for having primary context
        if primary_context and not primary_context.get("error"):
            score += 0.3

        # Score for graph relationships
        if graph_relationships and not graph_relationships.get("error"):
            if graph_relationships.get("commit_history"):
                score += 0.3
            if graph_relationships.get("related_files"):
                score += 0.2
            if graph_relationships.get("feature_connections"):
                score += 0.1

        # Score for documentation
        if vector_docs:
            score += min(0.1, len(vector_docs) * 0.02)

        return min(1.0, score)

    def _generate_cache_key(self, request: ContextRequest) -> str:
        """Generate cache key for context request"""
        key_parts = [
            request.filepath,
            request.event_type,
            request.function_name or "",
            request.class_name or "",
        ]
        return "|".join(key_parts)

    def _get_cached_context(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached context if still valid"""
        if cache_key in self.context_cache:
            cached_data = self.context_cache[cache_key]
            if time.time() - cached_data["timestamp"] < self.cache_ttl:
                return cached_data["context"]
            else:
                # Remove expired cache
                del self.context_cache[cache_key]
        return None

    def _cache_context(self, cache_key: str, context: Dict[str, Any]):
        """Cache context result"""
        self.context_cache[cache_key] = {"context": context, "timestamp": time.time()}

        # Clean old cache entries
        if len(self.context_cache) > 100:
            oldest_key = min(
                self.context_cache.keys(),
                key=lambda k: self.context_cache[k]["timestamp"],
            )
            del self.context_cache[oldest_key]

    async def log_context_event(
        self, request: ContextRequest, response: Dict[str, Any]
    ):
        """Log context event for analytics and learning"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "request": {
                "event_type": request.event_type,
                "filepath": request.filepath,
                "developer_id": request.developer_id,
                "function_name": request.function_name,
                "class_name": request.class_name,
            },
            "response": {
                "assembly_time": response.get("assembly_time", 0),
                "confidence_score": response.get("context_package", {}).get(
                    "confidence_score", 0
                ),
                "related_files_count": len(
                    response.get("context_package", {}).get("related_files", [])
                ),
                "documentation_count": len(
                    response.get("context_package", {}).get("documentation", [])
                ),
            },
        }

        self.context_events.append(event)

        # Keep only recent events
        if len(self.context_events) > 1000:
            self.context_events = self.context_events[-500:]

        # Update developer patterns
        if request.developer_id not in self.developer_patterns:
            self.developer_patterns[request.developer_id] = {}

        if request.filepath not in self.developer_patterns[request.developer_id]:
            self.developer_patterns[request.developer_id][request.filepath] = []

        self.developer_patterns[request.developer_id][request.filepath].append(
            {
                "timestamp": request.timestamp,
                "event_type": request.event_type,
                "function_name": request.function_name,
                "class_name": request.class_name,
            }
        )

    async def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics for the proactive context system"""
        total_events = len(self.context_events)
        recent_events = [
            event
            for event in self.context_events
            if datetime.fromisoformat(event["timestamp"])
            > datetime.now() - timedelta(hours=24)
        ]

        avg_assembly_time = 0
        avg_confidence = 0
        if recent_events:
            assembly_times = [
                event["response"]["assembly_time"] for event in recent_events
            ]
            confidence_scores = [
                event["response"]["confidence_score"] for event in recent_events
            ]
            avg_assembly_time = sum(assembly_times) / len(assembly_times)
            avg_confidence = sum(confidence_scores) / len(confidence_scores)

        return {
            "total_context_events": total_events,
            "events_last_24h": len(recent_events),
            "unique_developers": len(self.developer_patterns),
            "unique_files_accessed": len(
                set(event["request"]["filepath"] for event in self.context_events)
            ),
            "average_assembly_time": avg_assembly_time,
            "average_confidence_score": avg_confidence,
            "cache_size": len(self.context_cache),
            "most_active_files": self._get_most_active_files(),
            "system_health": "operational",
        }

    def _get_most_active_files(self) -> List[Dict[str, Any]]:
        """Get most frequently accessed files"""
        file_counts = {}
        for event in self.context_events[-100:]:  # Last 100 events
            filepath = event["request"]["filepath"]
            file_counts[filepath] = file_counts.get(filepath, 0) + 1

        return [
            {"filepath": filepath, "access_count": count}
            for filepath, count in sorted(
                file_counts.items(), key=lambda x: x[1], reverse=True
            )[:5]
        ]
