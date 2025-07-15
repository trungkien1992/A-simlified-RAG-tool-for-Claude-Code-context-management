#!/usr/bin/env python3
"""
Claude-Optimized Search Module
Advanced search capabilities specifically designed for Claude Code development context
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import re
import time
import hashlib
from datetime import datetime
from pathlib import Path


@dataclass
class Citation:
    """Grounded citation with source attribution - RAGFlow inspired"""

    source_id: str
    chunk_id: str
    file_path: str
    start_line: int
    end_line: int
    confidence: float
    context_snippet: str
    source_url: Optional[str] = None


@dataclass
class ClaudeSearchResult:
    """Results optimized for Claude Code development context with grounded citations"""

    results: List[Dict[str, Any]]
    total_context_size: int
    query_type: str
    related_files: List[str]
    cross_references: Dict[str, List[str]]
    development_context: Dict[str, Any]
    search_time: float
    citations: List[Citation]  # RAGFlow inspired grounded citations
    confidence_score: float  # Overall confidence in results
    optimization_applied: bool = True


@dataclass
class DevelopmentContext:
    """Development-specific context information"""

    intent: str  # 'debug', 'feature', 'refactor', 'understand', 'test'
    related_components: List[str]
    dependencies: List[str]
    suggested_files: List[str]
    code_patterns: List[str]


class ClaudeOptimizedSearch:
    """Search engine optimized for Claude Code development workflows with RAGFlow features"""

    def __init__(self, rag_system, collection, code_chunker=None):
        self.rag_system = rag_system
        self.collection = collection
        self.code_chunker = code_chunker
        self.file_relationship_map = {}
        self.import_graph = {}
        self.component_map = {}
        self.development_patterns = self._build_development_patterns()
        self.citation_cache = {}  # Cache for grounded citations
        self.quality_threshold = 0.7  # RAGFlow quality threshold

    async def search_for_claude(
        self,
        query: str,
        context_type: str = "development",
        max_context_size: int = 8000,
    ) -> ClaudeSearchResult:
        """Enhanced search that provides larger, more relevant context for Claude"""
        start_time = time.time()

        # Step 1: Analyze query intent and extract keywords
        intent = self._analyze_query_intent(query)
        keywords = self._extract_technical_keywords(query)

        # Step 2: Perform enhanced base search with multiple strategies
        base_results = await self._perform_enhanced_search(query, intent, keywords)

        # Step 3: Expand context based on development intent
        expanded_results = await self._expand_development_context(
            base_results, intent, keywords
        )

        # Step 4: Add related code and documentation
        context_enhanced_results = await self._add_contextual_information(
            expanded_results, intent
        )

        # Step 5: Optimize results for Claude's context window
        optimized_results = self._optimize_for_claude_context(
            context_enhanced_results, max_context_size
        )

        # Step 6: Build development metadata
        development_context = self._build_development_context(
            optimized_results, intent, keywords
        )

        # Step 7: Find cross-references and related files
        related_files = self._find_related_files(optimized_results)
        cross_refs = self._build_cross_references(optimized_results, keywords)

        search_time = time.time() - start_time

        # Step 8: Generate grounded citations (RAGFlow inspired)
        citations = self._generate_grounded_citations(optimized_results, query)

        # Step 9: Calculate overall confidence score
        confidence_score = self._calculate_confidence_score(
            optimized_results, citations
        )

        return ClaudeSearchResult(
            results=optimized_results,
            total_context_size=sum(
                len(r.get("content", "")) for r in optimized_results
            ),
            query_type=intent,
            related_files=related_files,
            cross_references=cross_refs,
            development_context=development_context,
            search_time=search_time,
            citations=citations,
            confidence_score=confidence_score,
            optimization_applied=True,
        )

    def _analyze_query_intent(self, query: str) -> str:
        """Determine Claude's development intent from the query"""
        query_lower = query.lower()

        # Debug/troubleshooting patterns
        debug_patterns = [
            "error",
            "bug",
            "fix",
            "issue",
            "problem",
            "failing",
            "broken",
            "exception",
            "crash",
        ]
        if any(pattern in query_lower for pattern in debug_patterns):
            return "debug"

        # Feature development patterns
        feature_patterns = [
            "add",
            "implement",
            "create",
            "build",
            "develop",
            "new feature",
            "functionality",
        ]
        if any(pattern in query_lower for pattern in feature_patterns):
            return "feature"

        # Refactoring patterns
        refactor_patterns = [
            "refactor",
            "improve",
            "optimize",
            "restructure",
            "clean up",
            "reorganize",
        ]
        if any(pattern in query_lower for pattern in refactor_patterns):
            return "refactor"

        # Testing patterns
        test_patterns = [
            "test",
            "testing",
            "unit test",
            "integration",
            "spec",
            "coverage",
        ]
        if any(pattern in query_lower for pattern in test_patterns):
            return "testing"

        # Configuration patterns
        config_patterns = [
            "config",
            "configuration",
            "setup",
            "environment",
            "settings",
        ]
        if any(pattern in query_lower for pattern in config_patterns):
            return "configuration"

        # API/Integration patterns
        api_patterns = ["api", "endpoint", "integration", "service", "client", "sdk"]
        if any(pattern in query_lower for pattern in api_patterns):
            return "integration"

        # Architecture patterns
        arch_patterns = ["architecture", "design", "pattern", "structure", "organize"]
        if any(pattern in query_lower for pattern in arch_patterns):
            return "architecture"

        return "understand"  # Default intent

    def _extract_technical_keywords(self, query: str) -> List[str]:
        """Extract technical keywords and component names from query"""
        keywords = []

        # Common technical terms - Enhanced for AstraTrade context
        tech_terms = [
            # AstraTrade/Trading terms
            "astratrade",
            "trading",
            "exchange",
            "order",
            "position",
            "portfolio",
            "market",
            "price",
            "volume",
            "liquidity",
            "spread",
            "slippage",
            "execution",
            "fill",
            "partial",
            "cancel",
            "modify",
            "limit",
            "stop",
            "leverage",
            "margin",
            "pnl",
            "profit",
            "loss",
            "risk",
            "exposure",
            # Extended Exchange API terms
            "extended",
            "exchange",
            "api",
            "endpoint",
            "client",
            "service",
            "authentication",
            "authorization",
            "signature",
            "payload",
            "request",
            "response",
            "websocket",
            "streaming",
            "realtime",
            "market_data",
            # X10 Python SDK terms
            "x10",
            "python",
            "sdk",
            "session",
            "account",
            "balance",
            "equity",
            "margin_level",
            "free_margin",
            "used_margin",
            "positions",
            "orders",
            # Blockchain/Starknet terms
            "starknet",
            "cairo",
            "contract",
            "wallet",
            "transaction",
            "signature",
            "paymaster",
            "gasless",
            "nft",
            "token",
            "stark",
            "avnu",
            "felt",
            "call",
            "invoke",
            "deploy",
            "declare",
            "multicall",
            "account_deployment",
            # Flutter/Dart terms
            "provider",
            "riverpod",
            "widget",
            "screen",
            "state",
            "async",
            "future",
            "build",
            "context",
            "scaffold",
            "appbar",
            "column",
            "row",
            "container",
            "stateful",
            "stateless",
            "consumer",
            "ref",
            "watch",
            "read",
            "listen",
            # Backend/API terms
            "fastapi",
            "uvicorn",
            "pydantic",
            "http",
            "cors",
            "middleware",
            "chromadb",
            "embeddings",
            "vector",
            "similarity",
            "search",
            "query",
            "rag",
            "retrieval",
            "augmented",
            "generation",
            "claude",
            "openai",
            # File/Component patterns
            "provider.dart",
            "screen.dart",
            "service.dart",
            "model.dart",
            "test.dart",
            "main.py",
            "cairo",
            "toml",
            "json",
            "yaml",
            "requirements.txt",
            "pubspec.yaml",
            "analysis_options.yaml",
            "docker-compose.yml",
        ]

        query_lower = query.lower()
        for term in tech_terms:
            if term in query_lower:
                keywords.append(term)

        # Extract file patterns
        file_patterns = re.findall(r"(\w+\.\w+)", query)
        keywords.extend(file_patterns)

        # Extract camelCase/snake_case identifiers
        identifier_patterns = re.findall(
            r"([a-z]+(?:[A-Z][a-z]*)*|[a-z]+(?:_[a-z]+)*)", query
        )
        keywords.extend([p for p in identifier_patterns if len(p) > 3])

        return list(set(keywords))  # Remove duplicates

    async def _perform_enhanced_search(
        self, query: str, intent: str, keywords: List[str]
    ) -> List[Dict]:
        """Perform enhanced search with multiple strategies"""
        all_results = []

        # Strategy 1: Direct semantic search
        direct_results = await self._semantic_search(query, max_results=15)
        all_results.extend(direct_results)

        # Strategy 2: Keyword-based search for each keyword
        for keyword in keywords[:5]:  # Limit to top 5 keywords
            keyword_results = await self._semantic_search(keyword, max_results=5)
            all_results.extend(keyword_results)

        # Strategy 3: Intent-specific search
        intent_query = self._build_intent_specific_query(query, intent)
        if intent_query != query:
            intent_results = await self._semantic_search(intent_query, max_results=10)
            all_results.extend(intent_results)

        # Remove duplicates based on content similarity
        unique_results = self._deduplicate_results(all_results)

        return unique_results

    async def _semantic_search(self, query: str, max_results: int = 10) -> List[Dict]:
        """Perform semantic search using the existing RAG system"""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=max_results,
                include=["documents", "metadatas", "distances"],
            )

            processed_results = []
            if results["documents"] and results["documents"][0]:
                for i, doc in enumerate(results["documents"][0]):
                    metadata = (
                        results["metadatas"][0][i] if results["metadatas"] else {}
                    )
                    distance = results["distances"][0][i] if results["distances"] else 0
                    similarity = 1 - distance

                    processed_results.append(
                        {
                            "content": doc,
                            "title": metadata.get("title", "Unknown"),
                            "category": metadata.get("category", "Unknown"),
                            "subcategory": metadata.get("subcategory"),
                            "similarity": similarity,
                            "source_url": metadata.get("source_url"),
                            "metadata": metadata,
                            "file_path": metadata.get("file_path", ""),
                            "language": metadata.get("language", "unknown"),
                            "chunk_type": metadata.get("chunk_type", "generic"),
                        }
                    )

            return processed_results
        except Exception as e:
            print(f"Error in semantic search: {e}")
            return []

    def _build_intent_specific_query(self, original_query: str, intent: str) -> str:
        """Build query enhanced for specific development intent"""
        intent_enhancements = {
            "debug": f"troubleshoot debug fix {original_query} error solution",
            "feature": f"implement create add {original_query} development example",
            "refactor": f"improve optimize {original_query} best practices pattern",
            "testing": f"test unit integration {original_query} example spec",
            "configuration": f"setup configure {original_query} environment config",
            "integration": f"api integrate {original_query} service client example",
            "architecture": f"design pattern structure {original_query} architecture",
        }

        return intent_enhancements.get(intent, original_query)

    async def _expand_development_context(
        self, base_results: List[Dict], intent: str, keywords: List[str]
    ) -> List[Dict]:
        """Expand context based on development patterns and relationships"""
        expanded = base_results.copy()

        # Extract primary code chunks for expansion
        code_chunks = [
            r
            for r in base_results[:5]
            if r.get("chunk_type") in ["function", "class", "component"]
        ]

        # Intent-based context expansion
        if intent in ["feature", "refactor"]:
            # Automatically search for related test files
            for result in code_chunks:
                file_path = result.get("file_path", "")
                if file_path:
                    test_files = await self._find_related_test_files(file_path)
                    expanded.extend(test_files)

        elif intent == "debug":
            # Automatically pull in related documentation on error handling or troubleshooting
            debug_docs = await self._find_debug_documentation(keywords)
            expanded.extend(debug_docs)

        # For each result, find related development context
        for result in base_results[:5]:  # Limit expansion to top results
            file_path = result.get("file_path", "")
            _ = result.get("category", "")  # Fixed F841

            # Add related files based on development patterns
            related_files = self._find_related_development_files(
                file_path, intent, keywords
            )

            for related_file in related_files[
                :3
            ]:  # Limit to 3 related files per result
                related_content = await self._get_file_context(related_file, intent)
                if related_content:
                    expanded.extend(related_content)

        return expanded

    def _find_related_development_files(
        self, file_path: str, intent: str, keywords: List[str]
    ) -> List[str]:
        """Find files related to development context"""
        related_files = []

        if not file_path:
            return related_files

        _ = Path(file_path).name  # Fixed F841
        base_name = Path(file_path).stem

        # Pattern-based relationships
        if file_path.endswith("_provider.dart"):
            # For providers, add related screens and models
            screen_name = base_name.replace("_provider", "_screen")
            model_name = base_name.replace("_provider", "_model")
            related_files.extend(
                [
                    f"lib/screens/{screen_name}.dart",
                    f"lib/models/{model_name}.dart",
                    f"test/unit/{base_name}_test.dart",
                ]
            )

        elif file_path.endswith("_screen.dart"):
            # For screens, add related providers and widgets
            provider_name = base_name.replace("_screen", "_provider")
            related_files.extend(
                [
                    f"lib/providers/{provider_name}.dart",
                    f"lib/widgets/{base_name}_widgets.dart",
                ]
            )

        elif file_path.endswith("_service.dart"):
            # For services, add related providers and tests
            provider_name = base_name.replace("_service", "_provider")
            related_files.extend(
                [
                    f"lib/providers/{provider_name}.dart",
                    f"test/unit/{base_name}_test.dart",
                    f"test/integration/{base_name}_integration_test.dart",
                ]
            )

        # Intent-specific relationships
        if intent == "testing":
            test_file = f"test/unit/{base_name}_test.dart"
            integration_test = f"test/integration/{base_name}_integration_test.dart"
            related_files.extend([test_file, integration_test])

        elif intent == "debug":
            # Add related error handling and logging files
            related_files.extend(
                [
                    "lib/services/logger_service.dart",
                    "lib/errors/app_error.dart",
                    "shared/errors/error_handler.dart",
                ]
            )

        return list(set(related_files))  # Remove duplicates

    async def _find_related_test_files(self, file_path: str) -> List[Dict]:
        """Find test files related to the given file path"""
        test_results = []

        if not file_path:
            return test_results

        # Extract base name and construct potential test file patterns
        base_name = Path(file_path).stem
        _ = str(Path(file_path).parent)  # Fixed F841

        # Common test file patterns
        test_patterns = [
            f"{base_name}_test.py",
            f"{base_name}_test.dart",
            f"test_{base_name}.py",
            f"{base_name}.test.dart",
            f"{base_name}.spec.dart",
        ]

        # Search for test files using multiple strategies
        for pattern in test_patterns:
            # Strategy 1: Direct file pattern search
            test_query = f"file:{pattern} OR title:{pattern}"
            test_search_results = await self._semantic_search(test_query, max_results=3)
            test_results.extend(test_search_results)

            # Strategy 2: Content-based search for tests mentioning the file
            content_query = f"test {base_name} unittest spec"
            content_results = await self._semantic_search(content_query, max_results=2)
            # Filter for actual test files
            test_content = [
                r
                for r in content_results
                if any(
                    test_keyword in r.get("file_path", "").lower()
                    for test_keyword in ["test", "spec"]
                )
            ]
            test_results.extend(test_content)

        return test_results[:5]  # Limit to 5 test files

    async def _find_debug_documentation(self, keywords: List[str]) -> List[Dict]:
        """Find documentation related to debugging and error handling"""
        debug_results = []

        # Build debug-specific query
        _ = [  # Fixed F841
            "error",
            "exception",
            "troubleshoot",
            "debug",
            "logging",
            "validation",
        ]
        keyword_terms = " ".join(keywords[:3])  # Use top 3 keywords

        debug_queries = [
            f"error handling {keyword_terms} troubleshooting",
            f"debugging {keyword_terms} exception",
            f"logging {keyword_terms} validation",
            "error handling best practices",
            "debugging guide troubleshooting",
        ]

        for query in debug_queries:
            results = await self._semantic_search(query, max_results=2)
            # Filter for documentation-type content
            doc_results = [
                r
                for r in results
                if any(
                    doc_indicator in r.get("category", "").lower()
                    or doc_indicator in r.get("title", "").lower()
                    for doc_indicator in ["doc", "guide", "readme", "help", "manual"]
                )
            ]
            debug_results.extend(doc_results)

        return debug_results[:4]  # Limit to 4 debug docs

    async def _get_file_context(self, file_path: str, intent: str) -> List[Dict]:
        """Get context for a specific file"""
        # This would query the collection for chunks from the specific file
        try:
            results = self.collection.query(
                query_texts=[f"file:{file_path}"],
                where={"file_path": {"$eq": file_path}},
                n_results=3,
            )

            if results["documents"] and results["documents"][0]:
                context_results = []
                for i, doc in enumerate(results["documents"][0]):
                    metadata = (
                        results["metadatas"][0][i] if results["metadatas"] else {}
                    )
                    context_results.append(
                        {
                            "content": doc,
                            "title": metadata.get("title", file_path),
                            "category": "related_context",
                            "metadata": metadata,
                            "file_path": file_path,
                            "context_type": "file_reference",
                        }
                    )
                return context_results
        except Exception:  # Fixed E722
            pass

        return []

    async def _add_contextual_information(
        self, results: List[Dict], intent: str
    ) -> List[Dict]:
        """Add contextual information like documentation, examples, and patterns"""
        enhanced_results = results.copy()

        # Add documentation context for understanding/feature intents
        if intent in ["understand", "feature", "architecture"]:
            doc_results = await self._find_documentation_context(results)
            enhanced_results.extend(doc_results)

        # Add example context for feature/integration intents
        if intent in ["feature", "integration"]:
            example_results = await self._find_example_context(results)
            enhanced_results.extend(example_results)

        # Add test context for testing/debug intents
        if intent in ["testing", "debug"]:
            test_results = await self._find_test_context(results)
            enhanced_results.extend(test_results)

        return enhanced_results

    async def _find_documentation_context(self, results: List[Dict]) -> List[Dict]:
        """Find relevant documentation"""
        doc_query = "documentation guide tutorial architecture design"
        return await self._semantic_search(doc_query, max_results=3)

    async def _find_example_context(self, results: List[Dict]) -> List[Dict]:
        """Find relevant examples and patterns"""
        example_query = "example implementation pattern usage how to"
        return await self._semantic_search(example_query, max_results=3)

    async def _find_test_context(self, results: List[Dict]) -> List[Dict]:
        """Find relevant test files and debugging information"""
        test_query = "test debugging error handling validation"
        return await self._semantic_search(test_query, max_results=3)

    def _optimize_for_claude_context(
        self, results: List[Dict], max_context_size: int
    ) -> List[Dict]:
        """Optimize results for Claude's context window"""
        optimized = []
        current_size = 0

        # Sort by relevance and importance
        sorted_results = sorted(
            results,
            key=lambda x: (
                x.get("similarity", 0),
                1 if x.get("chunk_type") == "class" else 0,
                1 if x.get("chunk_type") == "function" else 0,
                len(x.get("content", "")),
            ),
            reverse=True,
        )

        for result in sorted_results:
            content_size = len(result.get("content", ""))

            # Skip if adding this would exceed context window
            if current_size + content_size > max_context_size:
                # Try to truncate if it's a large chunk
                if content_size > max_context_size // 4:
                    truncated_content = (
                        result["content"][: max_context_size // 4]
                        + "\n... (truncated for context)"
                    )
                    result = result.copy()
                    result["content"] = truncated_content
                    result["truncated"] = True
                    content_size = len(truncated_content)

                if current_size + content_size <= max_context_size:
                    optimized.append(result)
                    current_size += content_size
            else:
                optimized.append(result)
                current_size += content_size

        return optimized

    def _build_development_context(
        self, results: List[Dict], intent: str, keywords: List[str]
    ) -> Dict[str, Any]:
        """Build comprehensive development context metadata"""
        file_types = set()
        languages = set()
        components = set()
        patterns = set()

        for result in results:
            if "language" in result:
                languages.add(result["language"])
            if "chunk_type" in result:
                patterns.add(result["chunk_type"])
            if "file_path" in result:
                file_types.add(Path(result["file_path"]).suffix)
                components.add(Path(result["file_path"]).stem)

        return {
            "intent": intent,
            "keywords": keywords,
            "file_types": list(file_types),
            "languages": list(languages),
            "components": list(components)[:10],  # Limit list size
            "patterns": list(patterns),
            "total_files_referenced": len(
                set(r.get("file_path", "") for r in results if r.get("file_path"))
            ),
            "context_optimization": {
                "total_results": len(results),
                "context_size": sum(len(r.get("content", "")) for r in results),
                "truncated_results": len(
                    [r for r in results if r.get("truncated", False)]
                ),
            },
        }

    def _find_related_files(self, results: List[Dict]) -> List[str]:
        """Find files related to the search results"""
        related = set()

        for result in results:
            file_path = result.get("file_path", "")
            if file_path:
                related.add(file_path)

                # Add pattern-based related files
                base_name = Path(file_path).stem
                if base_name.endswith("_provider"):
                    related.add(
                        f"lib/screens/{base_name.replace('_provider', '_screen')}.dart"
                    )
                elif base_name.endswith("_screen"):
                    related.add(
                        f"lib/providers/{base_name.replace('_screen', '_provider')}.dart"
                    )

        return list(related)

    def _build_cross_references(
        self, results: List[Dict], keywords: List[str]
    ) -> Dict[str, List[str]]:
        """Build cross-references between related concepts"""
        cross_refs = {}

        # Group results by type/category
        by_type = {}
        for result in results:
            chunk_type = result.get("chunk_type", "unknown")
            if chunk_type not in by_type:
                by_type[chunk_type] = []
            by_type[chunk_type].append(result)

        # Build cross-references
        for chunk_type, chunks in by_type.items():
            if len(chunks) > 1:
                cross_refs[chunk_type] = [
                    chunk.get("title", chunk.get("file_path", "Unknown"))
                    for chunk in chunks[:5]  # Limit to 5 items
                ]

        return cross_refs

    def _deduplicate_results(self, results: List[Dict]) -> List[Dict]:
        """Remove duplicate results based on content similarity"""
        unique_results = []
        seen_content = set()

        for result in results:
            content = result.get("content", "")
            # Use first 200 characters as fingerprint
            fingerprint = content[:200].strip()

            if fingerprint not in seen_content:
                seen_content.add(fingerprint)
                unique_results.append(result)

        return unique_results

    def _build_development_patterns(self) -> Dict[str, List[str]]:
        """Build patterns for different development scenarios"""
        return {
            "debug": [
                "error handling",
                "exception catching",
                "logging",
                "debugging",
                "validation",
                "error messages",
                "troubleshooting",
            ],
            "feature": [
                "implementation",
                "new functionality",
                "feature development",
                "requirements",
                "user stories",
                "API design",
            ],
            "refactor": [
                "code improvement",
                "optimization",
                "restructuring",
                "best practices",
                "clean code",
                "maintainability",
            ],
            "testing": [
                "unit tests",
                "integration tests",
                "test coverage",
                "mocking",
                "test fixtures",
                "validation",
            ],
            "configuration": [
                "setup",
                "environment",
                "config files",
                "settings",
                "deployment",
                "build configuration",
            ],
            "integration": [
                "API integration",
                "service communication",
                "data flow",
                "external services",
                "SDK usage",
                "webhooks",
            ],
        }

    async def get_file_suggestions(self, query: str, intent: str) -> List[str]:
        """Get file suggestions based on query and intent"""
        _ = []  # Fixed F841

        # Intent-based file suggestions - Enhanced for AstraTrade
        intent_files = {
            "debug": [
                "lib/services/logger_service.dart",
                "shared/errors/error_handler.dart",
                "test/unit/",
                "lib/errors/app_error.dart",
                "knowledge_base/backend/main.py",
                "shared/logging/logger_service.py",
            ],
            "feature": [
                "lib/providers/",
                "lib/screens/",
                "lib/models/",
                "lib/services/",
                "knowledge_base/backend/",
                "shared/services/",
                "shared/api/",
            ],
            "testing": [
                "test/unit/",
                "test/integration/",
                "test/test_config.dart",
                "knowledge_base/backend/test_claude_enhancements.py",
                "knowledge_base/backend/test_rag.py",
            ],
            "configuration": [
                "pubspec.yaml",
                "analysis_options.yaml",
                "lib/services/env_config_service.dart",
                "knowledge_base/backend/requirements.txt",
                "docker-compose.yml",
                "knowledge_base/backend/main.py",
            ],
            "integration": [
                "shared/api/base_api_client.dart",
                "shared/api/base_api_client.py",
                "knowledge_base/backend/claude_search.py",
                "knowledge_base/backend/categorization_system.py",
                "knowledge_base/backend/sdk_enhanced_indexer.py",
            ],
        }

        return intent_files.get(intent, [])

    def _generate_grounded_citations(
        self, results: List[Dict], query: str
    ) -> List[Citation]:
        """Generate grounded citations for search results - RAGFlow inspired"""
        citations = []

        for i, result in enumerate(results):
            metadata = result.get("metadata", {})
            content = result.get("content", "")

            # Extract accurate line information from metadata or content
            start_line = metadata.get("start_line", 0)
            end_line = metadata.get("end_line", 0)

            # If line numbers not in metadata, try to estimate from content
            if start_line == 0 and end_line == 0 and content:
                # Count lines in content for estimated range
                line_count = content.count("\n") + 1
                start_line = metadata.get(
                    "line_start", 1
                )  # Try alternative metadata keys
                end_line = start_line + line_count - 1 if start_line > 0 else line_count

            # Generate unique source ID
            timestamp_hash = hashlib.md5(
                f"{query}_{i}_{metadata.get('file_path', '')}".encode()
            ).hexdigest()[:8]

            # Create citation with accurate source attribution
            citation = Citation(
                source_id=f"cite_{timestamp_hash}",
                chunk_id=metadata.get("chunk_id", metadata.get("id", f"chunk_{i}")),
                file_path=metadata.get("file_path", result.get("file_path", "unknown")),
                start_line=int(start_line) if start_line else 0,
                end_line=int(end_line) if end_line else 0,
                confidence=float(result.get("similarity", 0.0)),
                context_snippet=self._create_context_snippet(content),
                source_url=metadata.get("source_url", metadata.get("url")),
            )

            # Only add citations with meaningful information
            if citation.file_path != "unknown" and citation.confidence >= 0.1:
                citations.append(citation)

        return citations

    def _create_context_snippet(self, content: str) -> str:
        """Create a meaningful context snippet from content"""
        if not content:
            return "..."

        # Clean and truncate content
        cleaned_content = content.strip()

        # If content is short, return as-is
        if len(cleaned_content) <= 200:
            return cleaned_content

        # Find a good breaking point (end of sentence, line, or word)
        snippet = cleaned_content[:200]

        # Try to break at end of line
        last_newline = snippet.rfind("\n")
        if last_newline > 100:
            return snippet[:last_newline] + "..."

        # Try to break at end of sentence
        last_period = snippet.rfind(".")
        if last_period > 100:
            return snippet[: last_period + 1] + "..."

        # Break at last word boundary
        last_space = snippet.rfind(" ")
        if last_space > 100:
            return snippet[:last_space] + "..."

        return snippet + "..."

    def _calculate_confidence_score(
        self, results: List[Dict], citations: List[Citation]
    ) -> float:
        """Calculate overall confidence score for search results"""
        if not results:
            return 0.0

        # Calculate weighted confidence based on similarity scores and citation quality
        total_weight = 0.0
        weighted_confidence = 0.0

        for result in results:
            similarity = result.get("similarity", 0.0)
            # Weight higher similarity results more heavily
            weight = similarity**2
            total_weight += weight
            weighted_confidence += similarity * weight

        if total_weight == 0:
            return 0.0

        base_confidence = weighted_confidence / total_weight

        # Boost confidence if we have multiple high-quality citations
        citation_boost = min(
            0.1,
            len([c for c in citations if c.confidence > self.quality_threshold]) * 0.02,
        )

        return min(1.0, base_confidence + citation_boost)

    def _assess_result_quality(self, result: Dict, query: str) -> float:
        """Assess the quality of a search result - RAGFlow inspired quality assessment"""
        quality_score = 0.0

        # Factor 1: Similarity score (40% weight)
        similarity = result.get("similarity", 0.0)
        quality_score += similarity * 0.4

        # Factor 2: Content length appropriateness (20% weight)
        content_length = len(result.get("content", ""))
        if 200 <= content_length <= 4000:  # Optimal length for Claude
            quality_score += 0.2
        elif content_length > 4000:
            quality_score += 0.1

        # Factor 3: Metadata completeness (20% weight)
        metadata = result.get("metadata", {})
        metadata_completeness = (
            sum(
                [
                    1 if metadata.get("file_path") else 0,
                    1 if metadata.get("title") else 0,
                    1 if metadata.get("chunk_type") else 0,
                    1 if metadata.get("language") else 0,
                ]
            )
            / 4
        )
        quality_score += metadata_completeness * 0.2

        # Factor 4: Code structure preservation (20% weight)
        chunk_type = metadata.get("chunk_type", "generic")
        if chunk_type in ["function", "class", "import_block"]:
            quality_score += 0.2
        elif chunk_type in ["documentation", "config"]:
            quality_score += 0.15
        elif chunk_type == "combined":
            quality_score += 0.1

        return min(1.0, quality_score)

    async def get_citation_context(self, citation: Citation) -> Dict[str, Any]:
        """Get additional context for a citation"""
        try:
            # Get surrounding context from the same file
            file_results = await self._get_file_context(
                citation.file_path, "understand"
            )

            # Find related citations
            related_citations = [
                c
                for c in self.citation_cache.get(citation.file_path, [])
                if c.chunk_id != citation.chunk_id
            ]

            return {
                "file_context": file_results,
                "related_citations": related_citations[:3],
                "confidence_details": {
                    "similarity_score": citation.confidence,
                    "quality_assessment": "high"
                    if citation.confidence > self.quality_threshold
                    else "medium",
                    "source_reliability": "verified"
                    if citation.source_url
                    else "internal",
                },
            }
        except Exception as e:
            return {"error": str(e)}


# Usage analytics integration
class ClaudeSearchAnalytics:
    """Track search patterns for optimization"""

    def __init__(self):
        self.query_log = []
        self.performance_metrics = []

    def log_search(
        self, query: str, intent: str, results_count: int, search_time: float
    ):
        """Log search for analytics"""
        self.query_log.append(
            {
                "timestamp": datetime.now(),
                "query": query,
                "intent": intent,
                "results_count": results_count,
                "search_time": search_time,
            }
        )

    def get_insights(self) -> Dict[str, Any]:
        """Get search analytics insights"""
        if not self.query_log:
            return {}

        intents = [log["intent"] for log in self.query_log]
        avg_time = sum(log["search_time"] for log in self.query_log) / len(
            self.query_log
        )

        return {
            "total_searches": len(self.query_log),
            "average_search_time": avg_time,
            "popular_intents": {
                intent: intents.count(intent) for intent in set(intents)
            },
            "recent_queries": [log["query"] for log in self.query_log[-10:]],
        }
