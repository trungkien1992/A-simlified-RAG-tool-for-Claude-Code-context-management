#!/usr/bin/env python3
"""
Core RAG system implementation for multi-platform knowledge bases
"""

import logging
from typing import List, Dict, Any
from datetime import datetime
from pathlib import Path
import json

# Vector database and embeddings
import chromadb
from sentence_transformers import SentenceTransformer
from chromadb.utils import embedding_functions

# Document processing
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Local imports
from .config import RAG_CONFIG, settings
from .models import ProcessedDocument

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentQualityAssessor:
    """RAGFlow-inspired document quality assessment"""

    def __init__(self, threshold: float = 0.7, platforms: List[str] = None):
        self.threshold = threshold
        self.platforms = platforms or []

    def assess_document_quality(self, content: str, metadata: Dict[str, Any]) -> float:
        """Assess the quality of a document"""
        score = 0.0

        # Content length (25%)
        content_length = len(content)
        if 100 <= content_length <= 8000:
            score += 0.25
        elif content_length > 8000:
            score += 0.15
        elif content_length > 50:
            score += 0.1

        # Platform relevance (25%)
        platform = metadata.get("platform", "unknown")
        if platform in self.platforms:
            score += 0.25
        elif platform != "unknown":
            score += 0.15

        # Metadata completeness (25%)
        required_fields = ["title", "category", "doc_type", "importance"]
        completeness = sum(1 for field in required_fields if metadata.get(field)) / len(
            required_fields
        )
        score += completeness * 0.25

        # Content structure (25%)
        structure_indicators = ["#", "##", "```", "*", "-", "1."]
        structure_score = min(
            1.0,
            sum(1 for indicator in structure_indicators if indicator in content)
            / len(structure_indicators),
        )
        score += structure_score * 0.25

        return min(1.0, score)


class AstraRAG:
    """High-performance RAG system for multi-platform knowledge bases with RAGFlow features"""

    def __init__(self):
        self.chroma_client = None
        self.collection = None
        self.embedding_model = None
        self.text_splitter = None
        self.documents_indexed = 0
        self.last_updated = None
        self.document_cache = {}  # Cache for processed documents
        self.quality_assessor = None  # RAGFlow-inspired quality assessment
        self.citation_tracker = {}  # Track citations for grounded answers
        self.platform_indexers = {}  # Platform-specific indexers

    async def initialize(self):
        """Initialize the RAG system with RAGFlow-inspired features"""
        logger.info("🚀 Initializing RAG system with advanced features...")

        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(
            path=RAG_CONFIG["chroma_db_path"]
        )

        # Initialize embedding model
        self.embedding_model = SentenceTransformer(RAG_CONFIG["embedding_model"])

        # Create embedding function for ChromaDB
        embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=RAG_CONFIG["embedding_model"]
        )

        # Get or create collection
        try:
            self.collection = self.chroma_client.get_collection(
                name=RAG_CONFIG["collection_name"],
                embedding_function=embedding_function,
            )
            logger.info(
                f"✅ Loaded existing collection: {RAG_CONFIG['collection_name']}"
            )
        except Exception:
            self.collection = self.chroma_client.create_collection(
                name=RAG_CONFIG["collection_name"],
                embedding_function=embedding_function,
                metadata={
                    "description": "Astra multi-platform trading knowledge base",
                    "platforms_count": str(len(RAG_CONFIG["platforms"])),
                    "template_chunking": str(RAG_CONFIG["template_chunking"]),
                    "grounded_citations": str(RAG_CONFIG["grounded_citations"]),
                    "deep_doc_understanding": str(RAG_CONFIG["deep_doc_understanding"]),
                },
            )
            logger.info(f"✅ Created new collection: {RAG_CONFIG['collection_name']}")

        # Initialize text splitter with RAGFlow-inspired improvements
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=RAG_CONFIG["chunk_size"],
            chunk_overlap=RAG_CONFIG["chunk_overlap"],
            separators=["\n\n", "\n", ". ", " ", ""],
            length_function=len,
            is_separator_regex=False,
        )

        # Initialize platform-specific indexers
        self._initialize_platform_indexers()

        # Initialize quality assessor
        self._initialize_quality_assessor()

        # Get current stats
        count = self.collection.count()
        self.documents_indexed = count
        logger.info(f"📊 Current documents in collection: {count}")
        logger.info(f"🔧 RAGFlow features enabled: {list(RAG_CONFIG.keys())}")

    def _initialize_platform_indexers(self):
        """Initialize platform-specific indexers for Astra"""
        # Import here to avoid circular imports
        from .indexers import (
            ExtendedExchangeIndexer,
            X10PythonSDKIndexer,
            StarknetDartIndexer,
            CairoLangIndexer,
            AVNUPaymasterIndexer,
            Web3AuthIndexer,
            ChipiPayIndexer,
            ProductDesignIndexer,
        )

        self.platform_indexers = {
            "extended_exchange": ExtendedExchangeIndexer(),
            "x10_python_sdk": X10PythonSDKIndexer(),
            "starknet_dart": StarknetDartIndexer(),
            "cairo_lang": CairoLangIndexer(),
            "avnu_paymaster": AVNUPaymasterIndexer(),
            "web3auth": Web3AuthIndexer(),
            "chipi_pay": ChipiPayIndexer(),
            "product_design": ProductDesignIndexer(),
        }

    def _initialize_quality_assessor(self):
        """Initialize RAGFlow-inspired quality assessment"""
        self.quality_assessor = DocumentQualityAssessor(
            threshold=RAG_CONFIG["quality_threshold"], platforms=RAG_CONFIG["platforms"]
        )

    async def _index_commit_history(self) -> int:
        """
        Scans the .rag_commits directory and indexes each commit as a document.
        """
        logger.info("🔍 Indexing commit history...")
        commit_dir = settings.commit_cache_dir
        if not commit_dir.exists():
            logger.warning(f"Commit directory not found: {commit_dir}")
            return 0

        commit_files = list(commit_dir.glob("commit_*.json"))
        if not commit_files:
            logger.info("No new commits to index.")
            return 0

        ids = []
        documents = []
        metadatas = []

        for commit_file in commit_files:
            try:
                with open(commit_file, "r", encoding="utf-8") as f:
                    card = json.load(f)

                # Check required fields
                if "what_changed" not in card:
                    logger.warning(
                        f"Skipping {commit_file.name}: missing 'what_changed' field"
                    )
                    continue
                if "code_changes" not in card:
                    logger.warning(
                        f"Skipping {commit_file.name}: missing 'code_changes' field"
                    )
                    continue
                if "metadata" not in card or "special_code" not in card["metadata"]:
                    logger.warning(
                        f"Skipping {commit_file.name}: missing metadata.special_code"
                    )
                    continue

                # Combine message and diff for a rich semantic embedding
                full_content = (
                    f"Commit Message: {card['what_changed']}\n\n"
                    f"Code Changes:\n{card['code_changes']}"
                )
                # Use the commit hash as the unique ID to prevent duplicates
                commit_hash = card["metadata"]["special_code"]

                # Enhance metadata for proper categorization and search
                enhanced_metadata = {
                    **card["metadata"],
                    "category": "commit_history",
                    "subcategory": "commit",
                    "platform": "commits",
                    "doc_type": "commit_record",
                    "importance": "high",
                    "source": "commit_indexer",
                    "title": f"Commit: {card['what_changed'][:50]}...",
                    "commit_message": card["what_changed"],
                }

                ids.append(commit_hash)
                documents.append(full_content)
                metadatas.append(enhanced_metadata)

            except Exception as e:
                logger.error(
                    f"Error processing commit file {commit_file.name}: {str(e)}"
                )
                continue

        if ids:
            self.collection.add(ids=ids, documents=documents, metadatas=metadatas)
            logger.info(f"✅ Indexed {len(ids)} commits into the RAG system.")
            return len(ids)
        return 0

    async def _index_pull_requests(self) -> int:
        """Scans the .rag_pull_requests directory and indexes each pull request memory card."""
        logger.info("🔍 Indexing pull request history...")
        pr_dir = (
            Path(RAG_CONFIG["chroma_db_path"]).resolve().parent / ".rag_pull_requests"
        )
        if not pr_dir.exists():
            logger.warning(f"Pull request directory not found: {pr_dir}")
            return 0

        pr_files = list(pr_dir.glob("pr_*.json"))
        if not pr_files:
            logger.info("No new pull request memory cards to index.")
            return 0

        ids_to_add = []
        documents_to_add = []
        metadatas_to_add = []

        for pr_file in pr_files:
            with open(pr_file, "r", encoding="utf-8") as f:
                card = json.load(f)
            pr_number = card["metadata"]["pr_number"]
            ids_to_add.append(f"pr_{pr_number}")
            documents_to_add.append(card["content"])
            metadatas_to_add.append(card["metadata"])

        if ids_to_add:
            self.collection.add(
                ids=ids_to_add, documents=documents_to_add, metadatas=metadatas_to_add
            )
            logger.info(
                f"✅ Indexed {len(ids_to_add)} pull requests into the RAG system."
            )
            return len(ids_to_add)
        return 0

    async def index_documentation(
        self, project_name: str, force_reindex: bool = False
    ) -> Dict[str, Any]:
        """Index all documentation for a specific project with RAGFlow-inspired features"""
        start_time = datetime.now()

        if force_reindex:
            logger.info(
                f"🔄 Force reindexing - clearing existing collection for {project_name}..."
            )
            # Delete all documents in the collection
            try:
                existing_docs = self.collection.get()
                if existing_docs["ids"]:
                    self.collection.delete(ids=existing_docs["ids"])
            except Exception as e:
                logger.warning(
                    f"Could not clear existing collection for {project_name}: {e}"
                )
                # If we can't clear, let's delete and recreate the collection
                try:
                    self.chroma_client.delete_collection(
                        name=RAG_CONFIG["collection_name"]
                    )
                    embedding_function = (
                        embedding_functions.SentenceTransformerEmbeddingFunction(
                            model_name=RAG_CONFIG["embedding_model"]
                        )
                    )
                    self.collection = self.chroma_client.create_collection(
                        name=RAG_CONFIG["collection_name"],
                        embedding_function=embedding_function,
                        metadata={
                            "description": "Astra multi-platform trading knowledge base",
                            "platforms_count": str(len(RAG_CONFIG["platforms"])),
                            "template_chunking": str(RAG_CONFIG["template_chunking"]),
                            "grounded_citations": str(RAG_CONFIG["grounded_citations"]),
                            "deep_doc_understanding": str(
                                RAG_CONFIG["deep_doc_understanding"]
                            ),
                        },
                    )
                except Exception as e2:
                    logger.error(
                        f"Could not recreate collection for {project_name}: {e2}"
                    )
                    return {
                        "status": "error",
                        "message": f"Failed to reset collection for {project_name}: {e2}",
                    }

        # Collect documents from all platforms
        platform_results = await self._index_all_platforms(project_name)
        total_docs = sum(platform_results.values())
        commit_docs_count = await self._index_commit_history()
        pr_docs_count = await self._index_pull_requests()
        total_docs += commit_docs_count + pr_docs_count
        platform_results["commits"] = commit_docs_count
        platform_results["pull_requests"] = pr_docs_count

        # Apply RAGFlow-inspired quality assessment
        quality_report = await self._assess_collection_quality()

        # Update stats
        self.documents_indexed = total_docs
        self.last_updated = datetime.now().isoformat()

        time_taken = (datetime.now() - start_time).total_seconds()

        return {
            "status": "completed",
            "documents_indexed": total_docs,
            "platform_breakdown": platform_results,
            "quality_report": quality_report,
            "ragflow_features": {
                "template_chunking_applied": RAG_CONFIG["template_chunking"],
                "grounded_citations_enabled": RAG_CONFIG["grounded_citations"],
                "deep_doc_understanding": RAG_CONFIG["deep_doc_understanding"],
            },
            "time_taken": time_taken,
        }

    async def _index_all_platforms(self, project_name: str) -> Dict[str, int]:
        """Index documentation from all platforms for a specific project"""
        platform_results = {}

        for platform_name, indexer in self.platform_indexers.items():
            try:
                logger.info(
                    f"🔍 Indexing {platform_name} documentation for {project_name}..."
                )
                docs_count = await indexer.index_platform_docs(self, project_name)
                platform_results[platform_name] = docs_count
                logger.info(
                    f"✅ Indexed {docs_count} documents from {platform_name} for {project_name}"
                )
            except Exception as e:
                logger.error(
                    f"❌ Failed to index {platform_name} for {project_name}: {str(e)}"
                )
                platform_results[platform_name] = 0

        return platform_results

    async def _assess_collection_quality(self) -> Dict[str, Any]:
        """Assess the quality of the indexed collection - RAGFlow inspired"""
        if not self.quality_assessor:
            return {"status": "quality_assessor_not_initialized"}

        try:
            # Get sample of documents for quality assessment
            sample_results = self.collection.get(
                limit=100, include=["documents", "metadatas"]
            )

            quality_metrics = {
                "total_documents": len(sample_results["documents"]),
                "platform_coverage": {},
                "chunk_quality_distribution": {},
                "citation_completeness": 0.0,
                "template_coverage": 0.0,
            }

            # Analyze platform coverage
            for metadata in sample_results["metadatas"]:
                platform = metadata.get("platform", "unknown")
                quality_metrics["platform_coverage"][platform] = (
                    quality_metrics["platform_coverage"].get(platform, 0) + 1
                )

            # Analyze chunk quality
            quality_scores = []
            for doc, metadata in zip(
                sample_results["documents"], sample_results["metadatas"]
            ):
                quality_score = self.quality_assessor.assess_document_quality(
                    doc, metadata
                )
                quality_scores.append(quality_score)

            if quality_scores:
                quality_metrics["average_quality_score"] = sum(quality_scores) / len(
                    quality_scores
                )
                quality_metrics["high_quality_percentage"] = (
                    len([s for s in quality_scores if s > 0.8])
                    / len(quality_scores)
                    * 100
                )

            return quality_metrics

        except Exception as e:
            logger.error(f"Quality assessment failed: {str(e)}")
            return {"status": "assessment_failed", "error": str(e)}

    async def _collect_documentation(
        self, project_name: str
    ) -> List[ProcessedDocument]:
        """Collect all documentation for a specific project with RAGFlow-inspired deep understanding"""
        documents = []

        # Manual documentation files
        documents.extend(await self._fetch_manual_docs(project_name))

        # Extended Exchange API documentation
        documents.extend(await self._fetch_extended_exchange_docs(project_name))

        # X10 Python SDK documentation
        documents.extend(await self._fetch_x10_python_docs(project_name))

        # Starknet.dart SDK documentation
        documents.extend(await self._fetch_starknet_dart_docs(project_name))

        # Cairo language documentation
        documents.extend(await self._fetch_cairo_docs(project_name))

        # AVNU Paymaster documentation
        documents.extend(await self._fetch_avnu_paymaster_docs(project_name))

        # Web3Auth documentation
        documents.extend(await self._fetch_web3auth_docs(project_name))

        # ChipiPay SDK documentation
        documents.extend(await self._fetch_chipi_pay_docs(project_name))

        return documents

    async def _fetch_manual_docs(self, project_name: str) -> List[ProcessedDocument]:
        """Fetch manual documentation files from the docs folder"""
        documents = []
        docs_path = Path("../docs/manual_docs")

        if docs_path.exists():
            for doc_file in docs_path.glob("*.md"):
                try:
                    content = doc_file.read_text(encoding="utf-8")

                    # Apply deep document understanding
                    doc_type = self._detect_document_type(content, doc_file.name)
                    importance = self._assess_document_importance(
                        content, doc_file.name
                    )

                    documents.append(
                        ProcessedDocument(
                            content=content,
                            title=doc_file.stem.replace("_", " ").title(),
                            category=doc_type["category"],
                            subcategory=doc_type["subcategory"],
                            metadata={
                                "source": "manual_docs",
                                "file_path": str(doc_file),
                                "importance": importance,
                                "doc_type": doc_type["type"],
                                "platform": doc_type["platform"],
                                "last_modified": doc_file.stat().st_mtime,
                            },
                        )
                    )

                except Exception as e:
                    logger.error(f"Failed to process {doc_file}: {str(e)}")

        return documents

    def _detect_document_type(self, content: str, filename: str) -> Dict[str, str]:
        """Detect document type using RAGFlow-inspired analysis"""
        _ = content.lower()  # Fixed F841
        filename_lower = filename.lower()

        # Platform detection
        if "extended" in filename_lower and "api" in filename_lower:
            return {
                "category": "api_documentation",
                "subcategory": "extended_exchange",
                "type": "api_reference",
                "platform": "extended_exchange",
            }
        elif "x10" in filename_lower or "python" in filename_lower:
            return {
                "category": "sdk_documentation",
                "subcategory": "x10_python",
                "type": "sdk_reference",
                "platform": "x10_python_sdk",
            }
        elif "starknet" in filename_lower or "dart" in filename_lower:
            return {
                "category": "sdk_documentation",
                "subcategory": "starknet_dart",
                "type": "sdk_reference",
                "platform": "starknet_dart",
            }
        elif "cairo" in filename_lower:
            return {
                "category": "language_documentation",
                "subcategory": "cairo_lang",
                "type": "language_reference",
                "platform": "cairo_lang",
            }
        elif "avnu" in filename_lower or "paymaster" in filename_lower:
            return {
                "category": "integration_documentation",
                "subcategory": "avnu_paymaster",
                "type": "integration_guide",
                "platform": "avnu_paymaster",
            }
        elif "web3auth" in filename_lower:
            return {
                "category": "authentication_documentation",
                "subcategory": "web3auth",
                "type": "auth_reference",
                "platform": "web3auth",
            }
        elif "chipi" in filename_lower:
            return {
                "category": "payment_documentation",
                "subcategory": "chipi_pay",
                "type": "payment_reference",
                "platform": "chipi_pay",
            }
        else:
            return {
                "category": "general_documentation",
                "subcategory": "general",
                "type": "general_reference",
                "platform": "general",
            }

    def _assess_document_importance(self, content: str, filename: str) -> str:
        """Assess document importance using RAGFlow-inspired analysis"""
        content_lower = content.lower()

        # Critical indicators
        critical_indicators = [
            "api reference",
            "getting started",
            "authentication",
            "security",
            "deployment",
        ]
        if any(indicator in content_lower for indicator in critical_indicators):
            return "critical"

        # High importance indicators
        high_indicators = [
            "integration",
            "configuration",
            "examples",
            "tutorial",
            "guide",
        ]
        if any(indicator in content_lower for indicator in high_indicators):
            return "high"

        # Medium importance indicators
        medium_indicators = ["reference", "documentation", "sdk", "api"]
        if any(indicator in content_lower for indicator in medium_indicators):
            return "medium"

        return "low"

    def _chunk_document(self, doc: ProcessedDocument) -> List[Dict[str, Any]]:
        """Chunk a document into smaller pieces using code-aware chunking"""
        chunked_docs = []

        # Check if code-aware chunking is enabled and we have a file path
        if (
            RAG_CONFIG.get("code_aware_chunking", False)
            and hasattr(doc, "file_path")
            and doc.file_path
        ):
            # Use CodeAwareChunker for supported file types
            try:
                from .code_aware_chunker import CodeAwareChunker

                code_chunker = CodeAwareChunker(RAG_CONFIG)
                code_chunks = code_chunker.chunk_file(doc.file_path, doc.content)

                # Convert CodeChunk objects to our format
                for i, code_chunk in enumerate(code_chunks):
                    chunk_id = (
                        f"{doc.category}_{doc.subcategory}_{i}"
                        if doc.subcategory
                        else f"{doc.category}_{i}"
                    )

                    # Clean metadata - ensure all values are strings, numbers, or booleans
                    clean_metadata = {
                        "title": str(doc.title) if doc.title else "Unknown",
                        "category": str(doc.category) if doc.category else "general",
                        "subcategory": str(doc.subcategory)
                        if doc.subcategory
                        else "general",
                        "chunk_index": i,
                        "total_chunks": len(code_chunks),
                        "source_url": str(doc.source_url)
                        if doc.source_url
                        else "unknown",
                        "chunk_type": str(code_chunk.chunk_type.value),
                        "language": str(code_chunk.language),
                        "importance": str(code_chunk.importance),
                        "start_line": code_chunk.start_line,
                        "end_line": code_chunk.end_line,
                        "code_aware": True,
                    }

                    # Add metadata from code chunk
                    for key, value in code_chunk.metadata.items():
                        if value is None:
                            clean_metadata[key] = "unknown"
                        elif isinstance(value, (str, int, float, bool)):
                            clean_metadata[key] = value
                        else:
                            clean_metadata[key] = str(value)

                    # Add other metadata from doc, ensuring all values are properly converted
                    for key, value in doc.metadata.items():
                        if key not in clean_metadata:
                            if value is None:
                                clean_metadata[key] = "unknown"
                            elif isinstance(value, (str, int, float, bool)):
                                clean_metadata[key] = value
                            else:
                                clean_metadata[key] = str(value)

                    chunked_docs.append(
                        {
                            "id": chunk_id,
                            "content": code_chunk.content,
                            "metadata": clean_metadata,
                        }
                    )

                logger.info(
                    f"📝 Code-aware chunking: {len(code_chunks)} chunks from {doc.file_path}"
                )
                return chunked_docs

            except Exception as e:
                logger.warning(f"Code-aware chunking failed for {doc.file_path}: {e}")
                # Fall back to regular chunking

        # Fallback to regular text splitting
        chunks = self.text_splitter.split_text(doc.content)

        for i, chunk in enumerate(chunks):
            chunk_id = (
                f"{doc.category}_{doc.subcategory}_{i}"
                if doc.subcategory
                else f"{doc.category}_{i}"
            )

            # Clean metadata - ensure all values are strings, numbers, or booleans
            clean_metadata = {
                "title": str(doc.title) if doc.title else "Unknown",
                "category": str(doc.category) if doc.category else "general",
                "subcategory": str(doc.subcategory) if doc.subcategory else "general",
                "chunk_index": i,
                "total_chunks": len(chunks),
                "source_url": str(doc.source_url) if doc.source_url else "unknown",
                "code_aware": False,
            }

            # Add other metadata, ensuring all values are properly converted
            for key, value in doc.metadata.items():
                if value is None:
                    clean_metadata[key] = "unknown"
                elif isinstance(value, (str, int, float, bool)):
                    clean_metadata[key] = value
                else:
                    clean_metadata[key] = str(value)

            chunked_docs.append(
                {"id": chunk_id, "content": chunk, "metadata": clean_metadata}
            )

        return chunked_docs

    async def _add_chunks_to_collection(self, chunks: List[Dict[str, Any]]):
        """Add document chunks to ChromaDB collection"""
        batch_size = 100

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]

            ids = [chunk["id"] for chunk in batch]
            documents = [chunk["content"] for chunk in batch]
            metadatas = [chunk["metadata"] for chunk in batch]

            self.collection.add(ids=ids, documents=documents, metadatas=metadatas)

            print(
                f"✅ Added batch {i // batch_size + 1}/{(len(chunks) + batch_size - 1) // batch_size}"
            )

    async def search(
        self,
        query: str,
        max_results: int = 5,
        category: str = None,
        min_similarity: float = 0.6,
    ) -> Dict[str, Any]:
        """Search the knowledge base"""
        start_time = datetime.now()

        # Prepare query filters
        where_filter = {}
        if category:
            where_filter["category"] = category

        # Perform vector search
        results = self.collection.query(
            query_texts=[query],
            n_results=max_results,
            where=where_filter if where_filter else None,
        )

        # Process results
        processed_results = []
        if results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                distance = results["distances"][0][i] if results["distances"] else 0
                # Better similarity calculation for cosine distance that can be > 1.0
                similarity = max(0, 1 - (distance / 2.0))  # Normalized to 0-1 range

                if similarity >= min_similarity:
                    processed_results.append(
                        {
                            "content": doc,
                            "title": metadata.get("title", "Unknown"),
                            "category": metadata.get("category", "Unknown"),
                            "subcategory": metadata.get("subcategory"),
                            "similarity": similarity,
                            "source_url": metadata.get("source_url"),
                            "metadata": metadata,
                        }
                    )

        query_time = (datetime.now() - start_time).total_seconds()

        return {
            "results": processed_results,
            "query_time": query_time,
            "total_results": len(processed_results),
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        total_docs = self.collection.count()

        # Get categories
        all_metadata = self.collection.get()["metadatas"]
        categories = {}
        for metadata in all_metadata:
            category = metadata.get("category", "unknown")
            categories[category] = categories.get(category, 0) + 1

        return {
            "total_documents": total_docs,
            "categories": categories,
            "last_updated": self.last_updated or "Never",
            "embedding_model": RAG_CONFIG["embedding_model"],
        }
