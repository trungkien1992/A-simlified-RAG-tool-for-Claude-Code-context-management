#!/usr/bin/env python3
"""
Platform-specific indexers for Astra RAG system
"""

import logging
from pathlib import Path
from models import ProcessedDocument

# Logging configuration
logger = logging.getLogger(__name__)


class PlatformIndexer:
    """Base class for platform-specific indexers"""

    def __init__(self, platform_name: str):
        self.platform_name = platform_name

    async def index_platform_docs(self, rag_system) -> int:
        """Index documentation for this platform"""
        return 0


class ExtendedExchangeIndexer(PlatformIndexer):
    """Indexer for Extended Exchange API documentation"""

    def __init__(self):
        super().__init__("extended_exchange")

    async def index_platform_docs(self, rag_system) -> int:
        # Implementation for Extended Exchange API docs
        return await self._index_extended_exchange_docs(rag_system)

    async def _index_extended_exchange_docs(self, rag_system) -> int:
        """Index Extended Exchange API documentation from files"""
        docs_count = 0
        try:
            # Load from actual documentation files
            docs_dir = Path("../docs/manual_docs")

            # Extended Exchange files
            extended_files = ["Extended_API_exchange.md", "Extended_API_Python_sdk.md"]

            for filename in extended_files:
                file_path = docs_dir / filename
                if file_path.exists():
                    content = file_path.read_text(encoding="utf-8")
                    if content.strip():  # Only process non-empty files
                        doc = ProcessedDocument(
                            content=content,
                            title=filename.replace("_", " ").replace(".md", ""),
                            category="api_documentation",
                            subcategory="extended_exchange",
                            metadata={
                                "platform": "extended_exchange",
                                "doc_type": "api_reference",
                                "importance": "critical",
                                "source": "extended_exchange_indexer",
                                "file_path": str(file_path),
                            },
                        )

                        chunks = rag_system._chunk_document(doc)
                        await rag_system._add_chunks_to_collection(chunks)
                        docs_count += len(chunks)
                        logger.info(f"Indexed {len(chunks)} chunks from {filename}")
                    else:
                        logger.warning(f"Skipped empty file: {filename}")
                else:
                    logger.warning(f"File not found: {filename}")

        except Exception as e:
            logger.error(f"Failed to index Extended Exchange docs: {str(e)}")

        return docs_count


class X10PythonSDKIndexer(PlatformIndexer):
    """Indexer for X10 Python SDK documentation"""

    def __init__(self):
        super().__init__("x10_python_sdk")

    async def index_platform_docs(self, rag_system) -> int:
        return await self._index_x10_python_docs(rag_system)

    async def _index_x10_python_docs(self, rag_system) -> int:
        """Index X10 Python SDK documentation from files"""
        docs_count = 0
        try:
            # Load from actual documentation files
            docs_dir = Path("../docs/manual_docs")

            # X10 Python SDK files
            x10_files = ["Extended_API_Python_sdk.md"]

            for filename in x10_files:
                file_path = docs_dir / filename
                if file_path.exists():
                    content = file_path.read_text(encoding="utf-8")
                    if content.strip():  # Only process non-empty files
                        doc = ProcessedDocument(
                            content=content,
                            title=filename.replace("_", " ").replace(".md", ""),
                            category="sdk_documentation",
                            subcategory="x10_python",
                            metadata={
                                "platform": "x10_python_sdk",
                                "doc_type": "sdk_reference",
                                "importance": "high",
                                "source": "x10_python_indexer",
                                "file_path": str(file_path),
                            },
                        )

                        chunks = rag_system._chunk_document(doc)
                        await rag_system._add_chunks_to_collection(chunks)
                        docs_count += len(chunks)
                        logger.info(f"Indexed {len(chunks)} chunks from {filename}")
                    else:
                        logger.warning(f"Skipped empty file: {filename}")
                else:
                    logger.warning(f"File not found: {filename}")

        except Exception as e:
            logger.error(f"Failed to index X10 Python SDK docs: {str(e)}")

        return docs_count


class StarknetDartIndexer(PlatformIndexer):
    """Indexer for Starknet.dart SDK documentation"""

    def __init__(self):
        super().__init__("starknet_dart")

    async def index_platform_docs(self, rag_system) -> int:
        return await self._index_starknet_dart_docs(rag_system)

    async def _index_starknet_dart_docs(self, rag_system) -> int:
        """Index Starknet.dart SDK documentation from files"""
        docs_count = 0
        try:
            # Load from actual documentation files
            docs_dir = Path("../docs/manual_docs")

            # Starknet.dart SDK files
            starknet_files = ["starket_dart_sdk.md"]

            for filename in starknet_files:
                file_path = docs_dir / filename
                if file_path.exists():
                    content = file_path.read_text(encoding="utf-8")
                    if content.strip():  # Only process non-empty files
                        doc = ProcessedDocument(
                            content=content,
                            title=filename.replace("_", " ").replace(".md", ""),
                            category="sdk_documentation",
                            subcategory="starknet_dart",
                            metadata={
                                "platform": "starknet_dart",
                                "doc_type": "sdk_reference",
                                "importance": "high",
                                "source": "starknet_dart_indexer",
                                "file_path": str(file_path),
                            },
                        )

                        chunks = rag_system._chunk_document(doc)
                        await rag_system._add_chunks_to_collection(chunks)
                        docs_count += len(chunks)
                        logger.info(f"Indexed {len(chunks)} chunks from {filename}")
                    else:
                        logger.warning(f"Skipped empty file: {filename}")
                else:
                    logger.warning(f"File not found: {filename}")

        except Exception as e:
            logger.error(f"Failed to index Starknet.dart SDK docs: {str(e)}")

        return docs_count


class CairoLangIndexer(PlatformIndexer):
    """Indexer for Cairo language documentation"""

    def __init__(self):
        super().__init__("cairo_lang")

    async def index_platform_docs(self, rag_system) -> int:
        return await self._index_cairo_docs(rag_system)

    async def _index_cairo_docs(self, rag_system) -> int:
        """Index Cairo language documentation from files"""
        docs_count = 0
        try:
            # Load from actual documentation files
            docs_dir = Path("../docs/manual_docs")

            # Cairo language files
            cairo_files = ["Cairo_lang.md"]

            for filename in cairo_files:
                file_path = docs_dir / filename
                if file_path.exists():
                    content = file_path.read_text(encoding="utf-8")
                    if content.strip():  # Only process non-empty files
                        doc = ProcessedDocument(
                            content=content,
                            title=filename.replace("_", " ").replace(".md", ""),
                            category="language_documentation",
                            subcategory="cairo_lang",
                            metadata={
                                "platform": "cairo_lang",
                                "doc_type": "language_reference",
                                "importance": "high",
                                "source": "cairo_lang_indexer",
                                "file_path": str(file_path),
                            },
                        )

                        chunks = rag_system._chunk_document(doc)
                        await rag_system._add_chunks_to_collection(chunks)
                        docs_count += len(chunks)
                        logger.info(f"Indexed {len(chunks)} chunks from {filename}")
                    else:
                        logger.warning(f"Skipped empty file: {filename}")
                else:
                    logger.warning(f"File not found: {filename}")

        except Exception as e:
            logger.error(f"Failed to index Cairo language docs: {str(e)}")

        return docs_count


class AVNUPaymasterIndexer(PlatformIndexer):
    """Indexer for AVNU Paymaster documentation"""

    def __init__(self):
        super().__init__("avnu_paymaster")

    async def index_platform_docs(self, rag_system) -> int:
        return await self._index_avnu_paymaster_docs(rag_system)

    async def _index_avnu_paymaster_docs(self, rag_system) -> int:
        """Index AVNU Paymaster documentation from files"""
        docs_count = 0
        try:
            # Load from actual documentation files
            docs_dir = Path("../docs/manual_docs")

            # AVNU Paymaster files
            avnu_files = [
                "ANVU_paymaster_Git_SDK.md",
                "AVNU_API_INTEGRATION.md",
                "AVNU_PAYMASTER_INTEGRATION.md",
                "Starknet_paymaster.md",
            ]

            for filename in avnu_files:
                file_path = docs_dir / filename
                if file_path.exists():
                    content = file_path.read_text(encoding="utf-8")
                    if content.strip():  # Only process non-empty files
                        doc = ProcessedDocument(
                            content=content,
                            title=filename.replace("_", " ").replace(".md", ""),
                            category="integration_documentation",
                            subcategory="avnu_paymaster",
                            metadata={
                                "platform": "avnu_paymaster",
                                "doc_type": "integration_guide",
                                "importance": "high",
                                "source": "avnu_paymaster_indexer",
                                "file_path": str(file_path),
                            },
                        )

                        chunks = rag_system._chunk_document(doc)
                        await rag_system._add_chunks_to_collection(chunks)
                        docs_count += len(chunks)
                        logger.info(f"Indexed {len(chunks)} chunks from {filename}")
                    else:
                        logger.warning(f"Skipped empty file: {filename}")
                else:
                    logger.warning(f"File not found: {filename}")

        except Exception as e:
            logger.error(f"Failed to index AVNU Paymaster docs: {str(e)}")

        return docs_count


class Web3AuthIndexer(PlatformIndexer):
    """Indexer for Web3Auth documentation"""

    def __init__(self):
        super().__init__("web3auth")

    async def index_platform_docs(self, rag_system) -> int:
        return await self._index_web3auth_docs(rag_system)

    async def _index_web3auth_docs(self, rag_system) -> int:
        """Index Web3Auth documentation from files"""
        docs_count = 0
        try:
            # Load from actual documentation files
            docs_dir = Path("../docs/manual_docs")

            # Web3Auth files
            web3auth_files = ["WEB3AUTH_FLUTTER_SDK.MD", "WEB3_AUTH.MD"]

            for filename in web3auth_files:
                file_path = docs_dir / filename
                if file_path.exists():
                    content = file_path.read_text(encoding="utf-8")
                    if content.strip():  # Only process non-empty files
                        doc = ProcessedDocument(
                            content=content,
                            title=filename.replace("_", " ")
                            .replace(".md", "")
                            .replace(".MD", ""),
                            category="authentication_documentation",
                            subcategory="web3auth",
                            metadata={
                                "platform": "web3auth",
                                "doc_type": "auth_reference",
                                "importance": "high",
                                "source": "web3auth_indexer",
                                "file_path": str(file_path),
                            },
                        )

                        chunks = rag_system._chunk_document(doc)
                        await rag_system._add_chunks_to_collection(chunks)
                        docs_count += len(chunks)
                        logger.info(f"Indexed {len(chunks)} chunks from {filename}")
                    else:
                        logger.warning(f"Skipped empty file: {filename}")
                else:
                    logger.warning(f"File not found: {filename}")

        except Exception as e:
            logger.error(f"Failed to index Web3Auth docs: {str(e)}")

        return docs_count


class ChipiPayIndexer(PlatformIndexer):
    """Indexer for ChipiPay SDK documentation"""

    def __init__(self):
        super().__init__("chipi_pay")

    async def index_platform_docs(self, rag_system) -> int:
        return await self._index_chipi_pay_docs(rag_system)

    async def _index_chipi_pay_docs(self, rag_system) -> int:
        """Index ChipiPay SDK documentation from files"""
        docs_count = 0
        try:
            # Load from actual documentation files
            docs_dir = Path("../docs/manual_docs")

            # ChipiPay files
            chipi_files = ["chipi_pay_sdk.md"]

            for filename in chipi_files:
                file_path = docs_dir / filename
                if file_path.exists():
                    content = file_path.read_text(encoding="utf-8")
                    if content.strip():  # Only process non-empty files
                        doc = ProcessedDocument(
                            content=content,
                            title=filename.replace("_", " ").replace(".md", ""),
                            category="payment_documentation",
                            subcategory="chipi_pay",
                            metadata={
                                "platform": "chipi_pay",
                                "doc_type": "payment_reference",
                                "importance": "high",
                                "source": "chipi_pay_indexer",
                                "file_path": str(file_path),
                            },
                        )

                        chunks = rag_system._chunk_document(doc)
                        await rag_system._add_chunks_to_collection(chunks)
                        docs_count += len(chunks)
                        logger.info(f"Indexed {len(chunks)} chunks from {filename}")
                    else:
                        logger.warning(f"Skipped empty file: {filename}")
                else:
                    logger.warning(f"File not found: {filename}")

        except Exception as e:
            logger.error(f"Failed to index ChipiPay docs: {str(e)}")

        return docs_count


class ProductDesignIndexer(PlatformIndexer):
    """Indexer for product design documentation"""

    def __init__(self):
        super().__init__("product_design")

    async def index_platform_docs(self, rag_system) -> int:
        return await self._index_product_design_docs(rag_system)

    async def _index_product_design_docs(self, rag_system) -> int:
        """Index product design documentation from files"""
        docs_count = 0
        try:
            # Load from actual documentation files
            docs_dir = Path("../docs/project_design")

            if not docs_dir.exists():
                logger.warning(f"Project design directory not found: {docs_dir}")
                return docs_count

            # Get all .md files from the project_design directory
            design_files = list(docs_dir.glob("*.md"))

            if not design_files:
                logger.warning("No .md files found in project_design directory")
                return docs_count

            for file_path in design_files:
                try:
                    content = file_path.read_text(encoding="utf-8")
                    if content.strip():  # Only process non-empty files
                        # Categorize based on filename
                        filename = file_path.name
                        if "game" in filename.lower():
                            category = "game_design"
                            subcategory = "game_mechanics"
                        elif "bounty" in filename.lower():
                            category = "project_requirements"
                            subcategory = "bounty_specs"
                        elif "frontend" in filename.lower():
                            category = "frontend_design"
                            subcategory = "ui_ux"
                        elif "user" in filename.lower():
                            category = "user_research"
                            subcategory = "user_archetypes"
                        elif "spec" in filename.lower():
                            category = "technical_specs"
                            subcategory = "specifications"
                        else:
                            category = "product_design"
                            subcategory = "general"

                        doc = ProcessedDocument(
                            content=content,
                            title=filename.replace("_", " ").replace(".md", ""),
                            category=category,
                            subcategory=subcategory,
                            metadata={
                                "platform": "product_design",
                                "doc_type": "design_document",
                                "importance": "critical",
                                "source": "product_design_indexer",
                                "file_path": str(file_path),
                            },
                        )

                        chunks = rag_system._chunk_document(doc)
                        await rag_system._add_chunks_to_collection(chunks)
                        docs_count += len(chunks)
                        logger.info(f"Indexed {len(chunks)} chunks from {filename}")
                    else:
                        logger.warning(f"Skipped empty file: {file_path.name}")
                except Exception as e:
                    logger.error(f"Failed to process file {file_path}: {str(e)}")

        except Exception as e:
            logger.error(f"Failed to index product design docs: {str(e)}")

        return docs_count
