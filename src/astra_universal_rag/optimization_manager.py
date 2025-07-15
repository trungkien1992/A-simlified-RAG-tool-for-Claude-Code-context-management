#!/usr/bin/env python3
"""
Astra RAG Optimization Manager
Optimizes RAG system performance for trading platform documentation
"""

import asyncio
import time
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict
import statistics
import json

# Vector database optimization
try:
    import chromadb
except ImportError:
    chromadb = None

logger = logging.getLogger(__name__)


@dataclass
class OptimizationMetrics:
    """Metrics for RAG system optimization"""

    query_count: int
    avg_response_time: float
    avg_similarity_score: float
    cache_hit_rate: float
    index_size: int
    memory_usage: float
    disk_usage: float
    error_rate: float
    popular_queries: List[str]
    slow_queries: List[str]
    optimization_suggestions: List[str]


@dataclass
class QueryAnalytics:
    """Analytics for query performance"""

    query: str
    response_time: float
    similarity_score: float
    result_count: int
    timestamp: datetime
    platform: str
    category: str
    error: Optional[str] = None


class RAGOptimizationManager:
    """Manages RAG system optimization for Astra platforms"""

    def __init__(
        self, chroma_client=None, collection_name: str = "astratrade_knowledge_base"
    ):
        self.chroma_client = chroma_client
        self.collection_name = collection_name
        self.query_analytics: List[QueryAnalytics] = []
        self.optimization_history: List[Dict[str, Any]] = []
        self.performance_thresholds = {
            "max_response_time": 2.0,  # seconds
            "min_similarity_score": 0.7,
            "max_error_rate": 0.05,  # 5%
            "min_cache_hit_rate": 0.6,  # 60%
            "max_index_size": 100000,  # documents
            "max_memory_usage": 4.0,  # GB
        }
        self.platform_weights = {
            "extended_exchange": 1.0,
            "x10_python_sdk": 0.9,
            "starknet_dart": 0.8,
            "cairo_lang": 0.7,
            "avnu_paymaster": 0.6,
            "web3auth": 0.5,
            "chipi_pay": 0.4,
        }
        self.feedback_log: List[Dict[str, Any]] = []
        self.feedback_log_file = "context_feedback_log.jsonl"
        self.quality_metrics: List[Dict[str, Any]] = []
        self.quality_metrics_file = "context_quality_metrics.jsonl"

    def log_query_performance(
        self,
        query: str,
        response_time: float,
        similarity_score: float,
        result_count: int,
        platform: str = "unknown",
        category: str = "unknown",
        error: Optional[str] = None,
    ):
        """Log query performance for optimization analysis"""

        analytics = QueryAnalytics(
            query=query,
            response_time=response_time,
            similarity_score=similarity_score,
            result_count=result_count,
            timestamp=datetime.now(),
            platform=platform,
            category=category,
            error=error,
        )

        self.query_analytics.append(analytics)

        # Keep only last 1000 queries to prevent memory issues
        if len(self.query_analytics) > 1000:
            self.query_analytics = self.query_analytics[-1000:]

    def log_feedback(self, feedback):
        """
        Store feedback for a context session, linking it to session_id, developer_id, and task_id.
        Feedback should be a Pydantic/BaseModel or dict with keys: session_id, developer_id, task_id, rating, feedback_notes
        """
        # Convert feedback to dict if it's a Pydantic model
        if hasattr(feedback, "dict"):
            feedback_data = feedback.dict()
        else:
            feedback_data = dict(feedback)
        feedback_data["timestamp"] = datetime.now().isoformat()
        self.feedback_log.append(feedback_data)
        # Optionally, persist to file for durability
        try:
            with open(self.feedback_log_file, "a") as f:
                f.write(json.dumps(feedback_data) + "\n")
        except Exception as e:
            logger.warning(f"Failed to write feedback to file: {e}")

    def analyze_performance(self, timeframe_hours: int = 24) -> OptimizationMetrics:
        """Analyze RAG system performance over specified timeframe"""

        cutoff_time = datetime.now() - timedelta(hours=timeframe_hours)
        recent_queries = [q for q in self.query_analytics if q.timestamp > cutoff_time]

        if not recent_queries:
            return OptimizationMetrics(
                query_count=0,
                avg_response_time=0.0,
                avg_similarity_score=0.0,
                cache_hit_rate=0.0,
                index_size=0,
                memory_usage=0.0,
                disk_usage=0.0,
                error_rate=0.0,
                popular_queries=[],
                slow_queries=[],
                optimization_suggestions=[],
            )

        # Calculate metrics
        query_count = len(recent_queries)
        avg_response_time = statistics.mean([q.response_time for q in recent_queries])
        avg_similarity_score = statistics.mean(
            [q.similarity_score for q in recent_queries]
        )

        # Calculate error rate
        error_count = len([q for q in recent_queries if q.error])
        error_rate = error_count / query_count if query_count > 0 else 0.0

        # Find popular queries
        query_counts = defaultdict(int)
        for q in recent_queries:
            query_counts[q.query] += 1
        popular_queries = sorted(
            query_counts.items(), key=lambda x: x[1], reverse=True
        )[:10]
        popular_queries = [q[0] for q in popular_queries]

        # Find slow queries
        slow_queries = [
            q.query
            for q in recent_queries
            if q.response_time > self.performance_thresholds["max_response_time"]
        ]
        slow_queries = list(set(slow_queries))[:10]

        # Get system metrics
        index_size = self._get_index_size()
        memory_usage = self._get_memory_usage()
        disk_usage = self._get_disk_usage()
        cache_hit_rate = self._calculate_cache_hit_rate(recent_queries)

        # Generate optimization suggestions
        suggestions = self._generate_optimization_suggestions(
            avg_response_time,
            avg_similarity_score,
            error_rate,
            cache_hit_rate,
            index_size,
            memory_usage,
        )

        return OptimizationMetrics(
            query_count=query_count,
            avg_response_time=avg_response_time,
            avg_similarity_score=avg_similarity_score,
            cache_hit_rate=cache_hit_rate,
            index_size=index_size,
            memory_usage=memory_usage,
            disk_usage=disk_usage,
            error_rate=error_rate,
            popular_queries=popular_queries,
            slow_queries=slow_queries,
            optimization_suggestions=suggestions,
        )

    def assess_context_quality(self):
        """
        Analyze logged feedback to identify high- and low-quality context patterns.
        Store results in self.quality_metrics and persist to file.
        """
        high_threshold = 0.8
        low_threshold = 0.4
        results = []
        for feedback in self.feedback_log:
            session_id = feedback.get("session_id")
            rating = feedback.get("rating", 0.0)
            notes = feedback.get("feedback_notes", "")
            # Placeholder: In a real system, fetch context features from session_id (e.g., from proactive_engine logs)
            # Here, we simulate with dummy features
            context_features = self._get_context_features_for_session(session_id)
            assessment = {
                "session_id": session_id,
                "developer_id": feedback.get("developer_id"),
                "task_id": feedback.get("task_id"),
                "rating": rating,
                "feedback_notes": notes,
                "context_features": context_features,
                "timestamp": feedback.get("timestamp"),
                "quality": "high"
                if rating >= high_threshold
                else ("low" if rating <= low_threshold else "medium"),
                "insights": [],
            }
            if assessment["quality"] == "high":
                assessment["insights"].append(
                    f"High quality: features present: {', '.join(context_features) if context_features else 'unknown'}"
                )
            elif assessment["quality"] == "low":
                assessment["insights"].append(
                    f"Low quality: missing or weak features. Notes: {notes}"
                )
            else:
                assessment["insights"].append(
                    "Medium quality: context partially useful."
                )
            results.append(assessment)
        self.quality_metrics = results
        # Persist to file
        try:
            with open(self.quality_metrics_file, "w") as f:
                for metric in results:
                    f.write(json.dumps(metric) + "\n")
        except Exception as e:
            logger.warning(f"Failed to write quality metrics to file: {e}")

    def _get_context_features_for_session(self, session_id):
        """
        Placeholder: In a real system, fetch features from context logs or proactive_engine.
        Here, we simulate with dummy features for demonstration.
        """
        # Simulate: alternate between some feature sets
        if not session_id:
            return []
        if int(hash(session_id)) % 2 == 0:
            return [
                "included 3 recent commits",
                "predicted the correct next file",
                "graph relationship present",
            ]
        else:
            return [
                "no relevant documentation found",
                "graph relationship was incorrect",
            ]

    def _get_index_size(self) -> int:
        """Get current index size"""
        if self.chroma_client:
            try:
                collection = self.chroma_client.get_collection(self.collection_name)
                return collection.count()
            except Exception as e:
                logger.warning(f"Could not get index size: {e}")
        return 0

    def _get_memory_usage(self) -> float:
        """Get current memory usage in GB"""
        try:
            import psutil

            process = psutil.Process()
            memory_info = process.memory_info()
            return memory_info.rss / (1024 * 1024 * 1024)  # Convert to GB
        except ImportError:
            return 0.0

    def _get_disk_usage(self) -> float:
        """Get current disk usage in GB"""
        try:
            import psutil
            import os

            if self.chroma_client and hasattr(self.chroma_client, "_settings"):
                db_path = self.chroma_client._settings.persist_directory
                if db_path and os.path.exists(db_path):
                    return psutil.disk_usage(db_path).used / (1024 * 1024 * 1024)
        except (ImportError, AttributeError):
            pass
        return 0.0

    def _calculate_cache_hit_rate(self, queries: List[QueryAnalytics]) -> float:
        """Calculate cache hit rate (placeholder - would need actual cache implementation)"""
        # This is a placeholder - would need to track actual cache hits
        # For now, estimate based on duplicate queries
        if not queries:
            return 0.0

        unique_queries = set(q.query for q in queries)
        total_queries = len(queries)
        duplicate_rate = 1 - (len(unique_queries) / total_queries)

        # Estimate cache hit rate based on duplicate queries
        return min(duplicate_rate * 2, 1.0)

    def _generate_optimization_suggestions(
        self,
        avg_response_time: float,
        avg_similarity_score: float,
        error_rate: float,
        cache_hit_rate: float,
        index_size: int,
        memory_usage: float,
    ) -> List[str]:
        """Generate optimization suggestions based on metrics"""

        suggestions = []

        # Response time optimization
        if avg_response_time > self.performance_thresholds["max_response_time"]:
            suggestions.append(
                f"Response time ({avg_response_time:.2f}s) exceeds threshold. Consider:"
            )
            suggestions.append("- Implementing query result caching")
            suggestions.append("- Optimizing embedding model")
            suggestions.append("- Reducing chunk size or overlap")
            suggestions.append("- Adding more specific indexing")

        # Similarity score optimization
        if avg_similarity_score < self.performance_thresholds["min_similarity_score"]:
            suggestions.append(
                f"Similarity score ({avg_similarity_score:.2f}) below threshold. Consider:"
            )
            suggestions.append("- Improving document preprocessing")
            suggestions.append("- Using better embedding models")
            suggestions.append("- Implementing query expansion")
            suggestions.append("- Adding more relevant training data")

        # Error rate optimization
        if error_rate > self.performance_thresholds["max_error_rate"]:
            suggestions.append(
                f"Error rate ({error_rate:.2%}) exceeds threshold. Consider:"
            )
            suggestions.append("- Improving error handling")
            suggestions.append("- Adding input validation")
            suggestions.append("- Implementing retry mechanisms")
            suggestions.append("- Monitoring system resources")

        # Cache optimization
        if cache_hit_rate < self.performance_thresholds["min_cache_hit_rate"]:
            suggestions.append(
                f"Cache hit rate ({cache_hit_rate:.2%}) below threshold. Consider:"
            )
            suggestions.append("- Implementing query result caching")
            suggestions.append("- Adding query normalization")
            suggestions.append("- Increasing cache size")
            suggestions.append("- Implementing semantic caching")

        # Index size optimization
        if index_size > self.performance_thresholds["max_index_size"]:
            suggestions.append(
                f"Index size ({index_size:,}) exceeds threshold. Consider:"
            )
            suggestions.append("- Implementing document archival")
            suggestions.append("- Removing duplicate content")
            suggestions.append("- Optimizing chunk sizes")
            suggestions.append("- Using hierarchical indexing")

        # Memory usage optimization
        if memory_usage > self.performance_thresholds["max_memory_usage"]:
            suggestions.append(
                f"Memory usage ({memory_usage:.2f}GB) exceeds threshold. Consider:"
            )
            suggestions.append("- Implementing lazy loading")
            suggestions.append("- Optimizing data structures")
            suggestions.append("- Adding memory pooling")
            suggestions.append("- Implementing garbage collection")

        # Platform-specific suggestions
        platform_analytics = defaultdict(list)
        for q in self.query_analytics:
            platform_analytics[q.platform].append(q)

        for platform, queries in platform_analytics.items():
            if len(queries) > 10:  # Only analyze platforms with sufficient data
                avg_platform_time = statistics.mean([q.response_time for q in queries])
                if avg_platform_time > avg_response_time * 1.5:
                    suggestions.append(
                        f"Platform '{platform}' shows slow performance. Consider:"
                    )
                    suggestions.append(f"- Optimizing {platform}-specific indexing")
                    suggestions.append(f"- Pre-computing common {platform} queries")
                    suggestions.append(f"- Adding {platform}-specific caching")

        return suggestions

    async def optimize_index(self, optimization_type: str = "full") -> Dict[str, Any]:
        """Optimize the vector index"""

        if not self.chroma_client:
            return {"error": "ChromaDB client not available"}

        start_time = time.time()
        optimization_results = {}

        try:
            collection = self.chroma_client.get_collection(self.collection_name)

            if optimization_type == "full":
                # Full optimization
                optimization_results["before_count"] = collection.count()

                # Get all documents
                all_docs = collection.get(
                    include=["documents", "metadatas", "embeddings"]
                )

                # Remove duplicates
                unique_docs = self._remove_duplicate_documents(all_docs)
                optimization_results["duplicates_removed"] = len(
                    all_docs["documents"]
                ) - len(unique_docs["documents"])

                # Optimize embeddings (placeholder - would implement actual optimization)
                optimized_docs = self._optimize_embeddings(unique_docs)
                optimization_results["embeddings_optimized"] = len(
                    optimized_docs["documents"]
                )

                # Rebuild collection
                collection.delete()

                # Re-add optimized documents
                if optimized_docs["documents"]:
                    collection.add(
                        ids=[
                            f"opt_{i}" for i in range(len(optimized_docs["documents"]))
                        ],
                        documents=optimized_docs["documents"],
                        metadatas=optimized_docs["metadatas"],
                        embeddings=optimized_docs["embeddings"],
                    )

                optimization_results["after_count"] = collection.count()

            elif optimization_type == "cleanup":
                # Cleanup optimization
                optimization_results["before_count"] = collection.count()

                # Remove old or low-quality documents
                cleanup_results = await self._cleanup_low_quality_documents(collection)
                optimization_results.update(cleanup_results)

                optimization_results["after_count"] = collection.count()

            elif optimization_type == "reindex":
                # Reindex optimization
                optimization_results["reindex_started"] = True
                # Would implement actual reindexing logic here
                optimization_results["reindex_completed"] = True

            optimization_time = time.time() - start_time
            optimization_results["optimization_time"] = optimization_time
            optimization_results["status"] = "completed"

            # Log optimization
            self.optimization_history.append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "type": optimization_type,
                    "results": optimization_results,
                }
            )

        except Exception as e:
            optimization_results["error"] = str(e)
            optimization_results["status"] = "failed"
            logger.error(f"Optimization failed: {e}")

        return optimization_results

    def _remove_duplicate_documents(self, docs: Dict[str, List]) -> Dict[str, List]:
        """Remove duplicate documents from the collection"""

        seen_content = set()
        unique_docs = {"documents": [], "metadatas": [], "embeddings": []}

        for i, doc in enumerate(docs["documents"]):
            # Create a hash of the document content
            content_hash = hash(doc)

            if content_hash not in seen_content:
                seen_content.add(content_hash)
                unique_docs["documents"].append(doc)
                if docs["metadatas"]:
                    unique_docs["metadatas"].append(docs["metadatas"][i])
                if docs["embeddings"]:
                    unique_docs["embeddings"].append(docs["embeddings"][i])

        return unique_docs

    def _optimize_embeddings(self, docs: Dict[str, List]) -> Dict[str, List]:
        """Optimize embeddings (placeholder for actual optimization)"""
        # This would implement actual embedding optimization
        # For now, just return the input
        return docs

    async def _cleanup_low_quality_documents(self, collection) -> Dict[str, Any]:
        """Remove low-quality documents from the collection"""

        cleanup_results = {"documents_removed": 0, "quality_threshold": 0.5}

        # This would implement actual quality-based cleanup
        # For now, just return placeholder results
        return cleanup_results

    def get_platform_performance(self) -> Dict[str, Dict[str, float]]:
        """Get performance metrics by platform"""

        platform_metrics = defaultdict(lambda: defaultdict(list))

        for query in self.query_analytics:
            platform = query.platform
            platform_metrics[platform]["response_times"].append(query.response_time)
            platform_metrics[platform]["similarity_scores"].append(
                query.similarity_score
            )
            if query.error:
                platform_metrics[platform]["errors"].append(1)
            else:
                platform_metrics[platform]["errors"].append(0)

        # Calculate aggregated metrics
        aggregated_metrics = {}
        for platform, metrics in platform_metrics.items():
            if metrics["response_times"]:  # Only process platforms with data
                aggregated_metrics[platform] = {
                    "avg_response_time": statistics.mean(metrics["response_times"]),
                    "avg_similarity_score": statistics.mean(
                        metrics["similarity_scores"]
                    ),
                    "error_rate": statistics.mean(metrics["errors"]),
                    "query_count": len(metrics["response_times"]),
                    "weight": self.platform_weights.get(platform, 0.5),
                }

        return aggregated_metrics

    def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """Get specific optimization recommendations"""

        recommendations = []

        # Analyze recent performance
        metrics = self.analyze_performance()

        # High-priority recommendations
        if metrics.avg_response_time > 1.0:
            recommendations.append(
                {
                    "priority": "high",
                    "category": "performance",
                    "title": "Slow Query Performance",
                    "description": f"Average response time ({metrics.avg_response_time:.2f}s) needs improvement",
                    "actions": [
                        "Implement query result caching",
                        "Optimize embedding model",
                        "Add query preprocessing",
                        "Consider index partitioning",
                    ],
                }
            )

        if metrics.error_rate > 0.02:
            recommendations.append(
                {
                    "priority": "high",
                    "category": "reliability",
                    "title": "High Error Rate",
                    "description": f"Error rate ({metrics.error_rate:.2%}) exceeds acceptable threshold",
                    "actions": [
                        "Implement better error handling",
                        "Add input validation",
                        "Monitor system resources",
                        "Add circuit breakers",
                    ],
                }
            )

        # Medium-priority recommendations
        if metrics.avg_similarity_score < 0.75:
            recommendations.append(
                {
                    "priority": "medium",
                    "category": "relevance",
                    "title": "Low Similarity Scores",
                    "description": f"Average similarity ({metrics.avg_similarity_score:.2f}) could be improved",
                    "actions": [
                        "Improve document preprocessing",
                        "Use better embedding models",
                        "Implement query expansion",
                        "Add domain-specific training",
                    ],
                }
            )

        if metrics.cache_hit_rate < 0.5:
            recommendations.append(
                {
                    "priority": "medium",
                    "category": "caching",
                    "title": "Low Cache Hit Rate",
                    "description": f"Cache hit rate ({metrics.cache_hit_rate:.2%}) needs improvement",
                    "actions": [
                        "Implement query normalization",
                        "Add semantic caching",
                        "Increase cache size",
                        "Optimize cache eviction policy",
                    ],
                }
            )

        # Low-priority recommendations
        if metrics.index_size > 50000:
            recommendations.append(
                {
                    "priority": "low",
                    "category": "storage",
                    "title": "Large Index Size",
                    "description": f"Index size ({metrics.index_size:,} documents) may impact performance",
                    "actions": [
                        "Implement document archival",
                        "Remove duplicate content",
                        "Optimize chunk sizes",
                        "Use hierarchical indexing",
                    ],
                }
            )

        return recommendations


# Convenience functions for backward compatibility
async def optimize_rag_system(chroma_client, collection_name: str) -> Dict[str, Any]:
    """Optimize RAG system - convenience function"""

    optimizer = RAGOptimizationManager(chroma_client, collection_name)
    return await optimizer.optimize_index("full")


async def get_rag_health(chroma_client, collection_name: str) -> Dict[str, Any]:
    """Get RAG system health report"""

    optimizer = RAGOptimizationManager(chroma_client, collection_name)
    metrics = optimizer.analyze_performance()
    recommendations = optimizer.get_optimization_recommendations()

    # Determine overall health
    health_score = 100
    if metrics.avg_response_time > 2.0:
        health_score -= 20
    if metrics.error_rate > 0.05:
        health_score -= 25
    if metrics.avg_similarity_score < 0.7:
        health_score -= 15
    if metrics.cache_hit_rate < 0.6:
        health_score -= 10

    health_status = (
        "excellent"
        if health_score >= 90
        else "good"
        if health_score >= 70
        else "fair"
        if health_score >= 50
        else "poor"
    )

    return {
        "health_score": health_score,
        "health_status": health_status,
        "metrics": {
            "query_count": metrics.query_count,
            "avg_response_time": metrics.avg_response_time,
            "avg_similarity_score": metrics.avg_similarity_score,
            "error_rate": metrics.error_rate,
            "cache_hit_rate": metrics.cache_hit_rate,
            "index_size": metrics.index_size,
            "memory_usage": metrics.memory_usage,
        },
        "recommendations": recommendations,
        "popular_queries": metrics.popular_queries[:5],
        "slow_queries": metrics.slow_queries[:3],
    }


if __name__ == "__main__":
    # Test the optimization manager
    import asyncio

    async def test_optimization():
        optimizer = RAGOptimizationManager()

        # Simulate some query analytics
        optimizer.log_query_performance(
            "trading api", 1.5, 0.8, 5, "extended_exchange", "trading_api"
        )
        optimizer.log_query_performance(
            "starknet dart", 0.8, 0.9, 3, "starknet_dart", "sdk"
        )
        optimizer.log_query_performance(
            "cairo contract", 2.1, 0.7, 7, "cairo_lang", "smart_contract"
        )

        # Analyze performance
        metrics = optimizer.analyze_performance()
        print("Performance Metrics:")
        print(f"Query Count: {metrics.query_count}")
        print(f"Avg Response Time: {metrics.avg_response_time:.2f}s")
        print(f"Avg Similarity Score: {metrics.avg_similarity_score:.2f}")
        print(f"Error Rate: {metrics.error_rate:.2%}")
        print(f"Popular Queries: {metrics.popular_queries}")
        print(f"Optimization Suggestions: {len(metrics.optimization_suggestions)}")

        # Get recommendations
        recommendations = optimizer.get_optimization_recommendations()
        print(f"\nRecommendations: {len(recommendations)}")
        for rec in recommendations:
            print(f"- {rec['title']} ({rec['priority']})")

    asyncio.run(test_optimization())
