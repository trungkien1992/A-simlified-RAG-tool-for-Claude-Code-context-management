#!/usr/bin/env python3
"""
Astra SDK Enhanced Indexer
Specialized indexing for multiple trading platform SDKs and documentation
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

# Import categorization system
from categorization_system import AstraCategorizer

logger = logging.getLogger(__name__)


@dataclass
class ProcessedDocument:
    """Processed document with enhanced metadata"""

    content: str
    title: str
    category: str
    subcategory: Optional[str]
    platform: str
    metadata: Dict[str, Any]
    source_url: Optional[str] = None
    quality_score: float = 0.0
    importance: str = "medium"
    doc_type: str = "general"
    tags: List[str] = None


class EnhancedSDKIndexer:
    """Enhanced indexer for Astra multi-platform SDK documentation"""

    def __init__(self, rag_system):
        self.rag_system = rag_system
        self.categorizer = AstraCategorizer()
        self.platform_indexers = {
            "extended_exchange": self._index_extended_exchange,
            "x10_python_sdk": self._index_x10_python_sdk,
            "starknet_dart": self._index_starknet_dart,
            "cairo_lang": self._index_cairo_lang,
            "avnu_paymaster": self._index_avnu_paymaster,
            "web3auth": self._index_web3auth,
            "chipi_pay": self._index_chipi_pay,
            "Starknet_paymaster": self._index_starknet_paymaster,
            "SNIP_29": self._index_snip_29,
            "Web3Auth_flutter": self._index_web3auth_flutter,
        }
        self.api_endpoints = {
            "extended_exchange": "https://api.extended-exchange.com/docs",
            "x10_python_sdk": "https://pypi.org/project/x10-python-sdk/",
            "starknet_dart": "https://pub.dev/packages/starknet",
            "cairo_lang": "https://github.com/starkware-libs/cairo",
            "avnu_paymaster": "https://github.com/avnu-labs/paymaster",
            "Starknet_paymaster": "https://starknetjs.com/docs/next/guides/paymaster/",
            "web3auth": "https://web3auth.io/docs",
            "chipi_pay": "https://docs.chipi.com",
            "SNIP_29": "https://github.com/starkware-libs/cairo/blob/main/snippets/snip29.cairo",
            "Web3Auth_flutter": "https://web3auth.io/docs/flutter/sdk-integration/overview",
        }

    async def index_all_sdks(self) -> Dict[str, int]:
        """Index all supported SDKs and platforms"""

        platform_results = {}

        # Index each platform
        for platform, indexer_func in self.platform_indexers.items():
            try:
                logger.info(f"Indexing platform: {platform}")
                document_count = await indexer_func()
                platform_results[platform] = document_count
                logger.info(f"Indexed {document_count} documents for {platform}")
            except Exception as e:
                logger.error(f"Failed to index {platform}: {e}")
                platform_results[platform] = 0

        # Index manual documentation
        try:
            manual_docs_count = await self._index_manual_docs()
            platform_results["manual_docs"] = manual_docs_count
            logger.info(f"Indexed {manual_docs_count} manual documents")
        except Exception as e:
            logger.error(f"Failed to index manual docs: {e}")
            platform_results["manual_docs"] = 0

        return platform_results

    async def _index_extended_exchange(self) -> int:
        """Index Extended Exchange API documentation"""

        documents = []

        # Extended Exchange API documentation
        extended_exchange_docs = [
            {
                "title": "Extended Exchange Trading API",
                "content": self._get_extended_exchange_api_content(),
                "category": "trading_api",
                "subcategory": "rest_api",
                "importance": "critical",
                "doc_type": "api",
            },
            {
                "title": "Extended Exchange Market Data",
                "content": self._get_extended_exchange_market_data_content(),
                "category": "market_data",
                "subcategory": "real_time",
                "importance": "high",
                "doc_type": "api",
            },
            {
                "title": "Extended Exchange Order Management",
                "content": self._get_extended_exchange_order_content(),
                "category": "order_management",
                "subcategory": "order_lifecycle",
                "importance": "critical",
                "doc_type": "api",
            },
            {
                "title": "Extended Exchange Authentication",
                "content": self._get_extended_exchange_auth_content(),
                "category": "authentication",
                "subcategory": "api_key",
                "importance": "critical",
                "doc_type": "security",
            },
        ]

        # Process and add documents
        for doc_data in extended_exchange_docs:
            doc = ProcessedDocument(
                content=doc_data["content"],
                title=doc_data["title"],
                category=doc_data["category"],
                subcategory=doc_data["subcategory"],
                platform="extended_exchange",
                metadata={
                    "source": "extended_exchange",
                    "importance": doc_data["importance"],
                    "doc_type": doc_data["doc_type"],
                    "indexed_at": datetime.now().isoformat(),
                },
                source_url=self.api_endpoints["extended_exchange"],
                quality_score=0.9,
                importance=doc_data["importance"],
                doc_type=doc_data["doc_type"],
                tags=["trading", "api", "rest", "extended_exchange"],
            )
            documents.append(doc)

        # Add documents to RAG system
        await self._add_documents_to_rag(documents)

        return len(documents)

    async def _index_x10_python_sdk(self) -> int:
        """Index X10 Python SDK documentation"""

        documents = []

        # X10 Python SDK documentation
        x10_docs = [
            {
                "title": "X10 Python SDK Overview",
                "content": self._get_x10_python_overview_content(),
                "category": "python_sdk",
                "subcategory": "overview",
                "importance": "high",
                "doc_type": "tutorial",
            },
            {
                "title": "X10 Python SDK Installation",
                "content": self._get_x10_python_installation_content(),
                "category": "python_sdk",
                "subcategory": "installation",
                "importance": "high",
                "doc_type": "tutorial",
            },
            {
                "title": "X10 Python SDK Trading Client",
                "content": self._get_x10_python_trading_content(),
                "category": "python_sdk",
                "subcategory": "trading_client",
                "importance": "critical",
                "doc_type": "api",
            },
            {
                "title": "X10 Python SDK Examples",
                "content": self._get_x10_python_examples_content(),
                "category": "python_sdk",
                "subcategory": "examples",
                "importance": "medium",
                "doc_type": "example",
            },
        ]

        # Process and add documents
        for doc_data in x10_docs:
            doc = ProcessedDocument(
                content=doc_data["content"],
                title=doc_data["title"],
                category=doc_data["category"],
                subcategory=doc_data["subcategory"],
                platform="x10_python_sdk",
                metadata={
                    "source": "x10_python_sdk",
                    "importance": doc_data["importance"],
                    "doc_type": doc_data["doc_type"],
                    "indexed_at": datetime.now().isoformat(),
                },
                source_url=self.api_endpoints["x10_python_sdk"],
                quality_score=0.85,
                importance=doc_data["importance"],
                doc_type=doc_data["doc_type"],
                tags=["python", "sdk", "trading", "x10"],
            )
            documents.append(doc)

        await self._add_documents_to_rag(documents)
        return len(documents)

    async def _index_starknet_dart(self) -> int:
        """Index Starknet.dart SDK documentation"""

        documents = []

        # Starknet.dart SDK documentation
        starknet_docs = [
            {
                "title": "Starknet.dart SDK Overview",
                "content": self._get_starknet_dart_overview_content(),
                "category": "dart_sdk",
                "subcategory": "overview",
                "importance": "high",
                "doc_type": "tutorial",
            },
            {
                "title": "Starknet.dart Provider",
                "content": self._get_starknet_dart_provider_content(),
                "category": "dart_sdk",
                "subcategory": "provider",
                "importance": "critical",
                "doc_type": "api",
            },
            {
                "title": "Starknet.dart Account Management",
                "content": self._get_starknet_dart_account_content(),
                "category": "dart_sdk",
                "subcategory": "account",
                "importance": "critical",
                "doc_type": "api",
            },
            {
                "title": "Starknet.dart Contract Interaction",
                "content": self._get_starknet_dart_contract_content(),
                "category": "dart_sdk",
                "subcategory": "contract",
                "importance": "high",
                "doc_type": "api",
            },
        ]

        # Process and add documents
        for doc_data in starknet_docs:
            doc = ProcessedDocument(
                content=doc_data["content"],
                title=doc_data["title"],
                category=doc_data["category"],
                subcategory=doc_data["subcategory"],
                platform="starknet_dart",
                metadata={
                    "source": "starknet_dart",
                    "importance": doc_data["importance"],
                    "doc_type": doc_data["doc_type"],
                    "indexed_at": datetime.now().isoformat(),
                },
                source_url=self.api_endpoints["starknet_dart"],
                quality_score=0.88,
                importance=doc_data["importance"],
                doc_type=doc_data["doc_type"],
                tags=["dart", "flutter", "starknet", "blockchain", "mobile"],
            )
            documents.append(doc)

        await self._add_documents_to_rag(documents)
        return len(documents)

    async def _index_cairo_lang(self) -> int:
        """Index Cairo language documentation"""

        documents = []

        # Cairo language documentation
        cairo_docs = [
            {
                "title": "Cairo Language Overview",
                "content": self._get_cairo_lang_overview_content(),
                "category": "cairo_lang",
                "subcategory": "overview",
                "importance": "high",
                "doc_type": "tutorial",
            },
            {
                "title": "Cairo Smart Contract Development",
                "content": self._get_cairo_contract_dev_content(),
                "category": "cairo_lang",
                "subcategory": "smart_contract",
                "importance": "critical",
                "doc_type": "tutorial",
            },
            {
                "title": "Cairo Language Syntax",
                "content": self._get_cairo_syntax_content(),
                "category": "cairo_lang",
                "subcategory": "syntax",
                "importance": "high",
                "doc_type": "reference",
            },
            {
                "title": "Cairo Examples",
                "content": self._get_cairo_examples_content(),
                "category": "cairo_lang",
                "subcategory": "examples",
                "importance": "medium",
                "doc_type": "example",
            },
        ]

        # Process and add documents
        for doc_data in cairo_docs:
            doc = ProcessedDocument(
                content=doc_data["content"],
                title=doc_data["title"],
                category=doc_data["category"],
                subcategory=doc_data["subcategory"],
                platform="cairo_lang",
                metadata={
                    "source": "cairo_lang",
                    "importance": doc_data["importance"],
                    "doc_type": doc_data["doc_type"],
                    "indexed_at": datetime.now().isoformat(),
                },
                source_url=self.api_endpoints["cairo_lang"],
                quality_score=0.9,
                importance=doc_data["importance"],
                doc_type=doc_data["doc_type"],
                tags=["cairo", "smart_contract", "starknet", "blockchain"],
            )
            documents.append(doc)

        await self._add_documents_to_rag(documents)
        return len(documents)

    async def _index_avnu_paymaster(self) -> int:
        """Index AVNU Paymaster documentation"""

        documents = []

        # AVNU Paymaster documentation
        avnu_docs = [
            {
                "title": "AVNU Paymaster Overview",
                "content": self._get_avnu_paymaster_overview_content(),
                "category": "paymaster",
                "subcategory": "overview",
                "importance": "high",
                "doc_type": "tutorial",
            },
            {
                "title": "AVNU Paymaster Integration",
                "content": self._get_avnu_paymaster_integration_content(),
                "category": "paymaster",
                "subcategory": "integration",
                "importance": "critical",
                "doc_type": "api",
            },
            {
                "title": "AVNU Paymaster Gas Sponsorship",
                "content": self._get_avnu_paymaster_gas_content(),
                "category": "paymaster",
                "subcategory": "gas_sponsorship",
                "importance": "high",
                "doc_type": "api",
            },
        ]

        # Process and add documents
        for doc_data in avnu_docs:
            doc = ProcessedDocument(
                content=doc_data["content"],
                title=doc_data["title"],
                category=doc_data["category"],
                subcategory=doc_data["subcategory"],
                platform="avnu_paymaster",
                metadata={
                    "source": "avnu_paymaster",
                    "importance": doc_data["importance"],
                    "doc_type": doc_data["doc_type"],
                    "indexed_at": datetime.now().isoformat(),
                },
                source_url=self.api_endpoints["avnu_paymaster"],
                quality_score=0.85,
                importance=doc_data["importance"],
                doc_type=doc_data["doc_type"],
                tags=["paymaster", "gas", "starknet", "sponsored_tx"],
            )
            documents.append(doc)

        await self._add_documents_to_rag(documents)
        return len(documents)

    async def _index_web3auth(self) -> int:
        """Index Web3Auth documentation"""

        documents = []

        # Web3Auth documentation
        web3auth_docs = [
            {
                "title": "Web3Auth Overview",
                "content": self._get_web3auth_overview_content(),
                "category": "authentication",
                "subcategory": "web3auth",
                "importance": "high",
                "doc_type": "tutorial",
            },
            {
                "title": "Web3Auth Flutter Integration",
                "content": self._get_web3auth_flutter_content(),
                "category": "authentication",
                "subcategory": "flutter",
                "importance": "critical",
                "doc_type": "api",
            },
            {
                "title": "Web3Auth Key Management",
                "content": self._get_web3auth_key_management_content(),
                "category": "authentication",
                "subcategory": "key_management",
                "importance": "critical",
                "doc_type": "security",
            },
        ]

        # Process and add documents
        for doc_data in web3auth_docs:
            doc = ProcessedDocument(
                content=doc_data["content"],
                title=doc_data["title"],
                category=doc_data["category"],
                subcategory=doc_data["subcategory"],
                platform="web3auth",
                metadata={
                    "source": "web3auth",
                    "importance": doc_data["importance"],
                    "doc_type": doc_data["doc_type"],
                    "indexed_at": datetime.now().isoformat(),
                },
                source_url=self.api_endpoints["web3auth"],
                quality_score=0.8,
                importance=doc_data["importance"],
                doc_type=doc_data["doc_type"],
                tags=["web3auth", "authentication", "oauth", "flutter"],
            )
            documents.append(doc)

        await self._add_documents_to_rag(documents)
        return len(documents)

    async def _index_chipi_pay(self) -> int:
        """Index ChipiPay documentation"""

        documents = []

        # ChipiPay documentation
        chipi_docs = [
            {
                "title": "ChipiPay Overview",
                "content": self._get_chipi_pay_overview_content(),
                "category": "payment",
                "subcategory": "overview",
                "importance": "medium",
                "doc_type": "tutorial",
            },
            {
                "title": "ChipiPay Integration",
                "content": self._get_chipi_pay_integration_content(),
                "category": "payment",
                "subcategory": "integration",
                "importance": "high",
                "doc_type": "api",
            },
        ]

        # Process and add documents
        for doc_data in chipi_docs:
            doc = ProcessedDocument(
                content=doc_data["content"],
                title=doc_data["title"],
                category=doc_data["category"],
                subcategory=doc_data["subcategory"],
                platform="chipi_pay",
                metadata={
                    "source": "chipi_pay",
                    "importance": doc_data["importance"],
                    "doc_type": doc_data["doc_type"],
                    "indexed_at": datetime.now().isoformat(),
                },
                source_url=self.api_endpoints["chipi_pay"],
                quality_score=0.75,
                importance=doc_data["importance"],
                doc_type=doc_data["doc_type"],
                tags=["chipi_pay", "payment", "gateway", "crypto"],
            )
            documents.append(doc)

        await self._add_documents_to_rag(documents)
        return len(documents)

    async def _index_manual_docs(self) -> int:
        """Index manual documentation files"""

        documents = []
        manual_docs_path = Path("../docs/manual_docs")

        if not manual_docs_path.exists():
            logger.warning(f"Manual docs path not found: {manual_docs_path}")
            return 0

        # Process each manual document
        for doc_file in manual_docs_path.glob("*.md"):
            try:
                content = doc_file.read_text(encoding="utf-8")

                # Use categorizer to process the document
                categorization_result = self.categorizer.categorize_document(
                    content, str(doc_file)
                )

                doc = ProcessedDocument(
                    content=content,
                    title=doc_file.stem.replace("_", " ").title(),
                    category=categorization_result.category.value,
                    subcategory=categorization_result.subcategory,
                    platform=categorization_result.platform.value,
                    metadata={
                        "source": "manual_docs",
                        "file_path": str(doc_file),
                        "importance": categorization_result.importance,
                        "doc_type": categorization_result.doc_type,
                        "indexed_at": datetime.now().isoformat(),
                        "confidence": categorization_result.confidence,
                        "keywords": categorization_result.keywords,
                    },
                    source_url=f"file://{doc_file.absolute()}",
                    quality_score=categorization_result.confidence,
                    importance=categorization_result.importance,
                    doc_type=categorization_result.doc_type,
                    tags=categorization_result.tags,
                )
                documents.append(doc)

            except Exception as e:
                logger.error(f"Error processing manual doc {doc_file}: {e}")

        await self._add_documents_to_rag(documents)
        return len(documents)

    async def _add_documents_to_rag(self, documents: List[ProcessedDocument]):
        """Add processed documents to the RAG system"""

        if not documents:
            return

        # Process documents into chunks
        for doc in documents:
            try:
                # Create chunks using the RAG system's chunking mechanism
                chunks = self.rag_system._chunk_document(doc)

                # Add chunks to collection
                await self.rag_system._add_chunks_to_collection(chunks)

            except Exception as e:
                logger.error(f"Error adding document to RAG: {e}")

    # Content generation methods (placeholder implementations)

    def _get_extended_exchange_api_content(self) -> str:
        return """
        Extended Exchange Trading API Documentation

        Base URL: https://api.extended-exchange.com

        Authentication:
        All API requests require authentication using API key and signature.

        Headers:
        - X-API-Key: Your API key
        - X-Signature: HMAC-SHA256 signature
        - X-Timestamp: Request timestamp

        Endpoints:

        GET /api/v1/ticker
        Get 24hr ticker price change statistics

        GET /api/v1/depth
        Get order book depth

        POST /api/v1/order
        Place a new order

        DELETE /api/v1/order
        Cancel an order

        GET /api/v1/order
        Get order status

        GET /api/v1/trades
        Get recent trades

        Trading Pairs:
        - BTC/USDT
        - ETH/USDT
        - STRK/USDT
        - AVNU/USDT

        Order Types:
        - MARKET: Market order
        - LIMIT: Limit order
        - STOP_LOSS: Stop loss order
        - STOP_LOSS_LIMIT: Stop loss limit order

        Rate Limits:
        - 1200 requests per minute per IP
        - 100 orders per 10 seconds per account
        """

    def _get_extended_exchange_market_data_content(self) -> str:
        return """
        Extended Exchange Market Data API

        Real-time market data endpoints for Extended Exchange.

        Ticker Information:
        GET /api/v1/ticker/24hr
        - 24hr price change statistics
        - Volume, high, low, open, close prices
        - Available for all trading pairs

        Kline/Candlestick Data:
        GET /api/v1/klines
        - Historical price data
        - Intervals: 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M
        - Up to 1000 data points per request

        Order Book:
        GET /api/v1/depth
        - Current order book depth
        - Bids and asks with price and quantity
        - Limit parameter for depth (5, 10, 20, 50, 100, 500, 1000)

        Recent Trades:
        GET /api/v1/trades
        - Recent trades for a symbol
        - Up to 1000 trades per request
        - Includes price, quantity, time, and side

        WebSocket Streams:
        - Real-time ticker updates
        - Order book depth updates
        - Trade stream
        - User data stream

        Base URL: wss://stream.extended-exchange.com/ws
        """

    def _get_extended_exchange_order_content(self) -> str:
        return """
        Extended Exchange Order Management

        Complete order lifecycle management on Extended Exchange.

        Order Placement:
        POST /api/v1/order

        Parameters:
        - symbol: Trading pair (required)
        - side: BUY or SELL (required)
        - type: ORDER type (required)
        - quantity: Order quantity (required)
        - price: Price (required for LIMIT orders)
        - timeInForce: GTC, IOC, FOK
        - stopPrice: Stop price for stop orders

        Order Types:
        - MARKET: Execute immediately at market price
        - LIMIT: Execute at specified price or better
        - STOP_LOSS: Market order triggered at stop price
        - STOP_LOSS_LIMIT: Limit order triggered at stop price

        Order Status:
        - NEW: Order accepted by engine
        - PARTIALLY_FILLED: Order partially filled
        - FILLED: Order completely filled
        - CANCELED: Order canceled
        - REJECTED: Order rejected

        Order Cancellation:
        DELETE /api/v1/order
        - Cancel specific order by orderId
        - Cancel all orders for a symbol
        - Cancel all open orders

        Order History:
        GET /api/v1/allOrders
        - Get all orders for account
        - Filter by symbol, status, time range
        - Paginated results

        Fill Information:
        GET /api/v1/myTrades
        - Get trade history
        - Commission information
        - Executed price and quantity
        """

    def _get_extended_exchange_auth_content(self) -> str:
        return """
        Extended Exchange Authentication

        API Key Authentication with HMAC-SHA256 signature.

        API Key Management:
        - Generate API key in account settings
        - Set permissions: Read, Trade, Withdraw
        - IP restrictions available
        - Key rotation recommended

        Request Signing:
        1. Create query string from parameters
        2. Calculate HMAC-SHA256 signature
        3. Include signature in request header

        Required Headers:
        - X-API-Key: Your API key
        - X-Signature: HMAC-SHA256 signature
        - X-Timestamp: Request timestamp (milliseconds)
        - Content-Type: application/json

        Signature Calculation:
        signature = hmac.new(
            secret_key.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        Python Example:
        import hmac
        import hashlib
        import time
        import requests

        api_key = "your_api_key"
        secret_key = "your_secret_key"

        timestamp = int(time.time() * 1000)
        query_string = f"timestamp={timestamp}&symbol=BTCUSDT"

        signature = hmac.new(
            secret_key.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        headers = {
            'X-API-Key': api_key,
            'X-Signature': signature,
            'X-Timestamp': str(timestamp)
        }

        Security Best Practices:
        - Never share API keys
        - Use IP restrictions
        - Rotate keys regularly
        - Store keys securely
        - Monitor API usage
        """

    def _get_x10_python_overview_content(self) -> str:
        return """
        X10 Python SDK Overview

        Python SDK for X10 trading platform integration.

        Features:
        - REST API client
        - WebSocket client
        - Account management
        - Order management
        - Market data access
        - Risk management

        Installation:
        pip install x10-python-sdk

        Quick Start:
        from x10_sdk import X10Client

        client = X10Client(
            api_key="your_api_key",
            secret_key="your_secret_key",
            testnet=True
        )

        # Get account info
        account = client.get_account()

        # Place order
        order = client.place_order(
            symbol="BTC/USDT",
            side="buy",
            type="limit",
            quantity=0.1,
            price=50000
        )

        Supported Exchanges:
        - X10 Exchange
        - Extended Exchange
        - Partner exchanges

        Python Version Support:
        - Python 3.7+
        - Async/await support
        - Type hints included
        """

    def _get_x10_python_installation_content(self) -> str:
        return """
        X10 Python SDK Installation Guide

        System Requirements:
        - Python 3.7 or higher
        - pip package manager
        - Internet connection

        Installation Methods:

        1. PyPI Installation (Recommended):
        pip install x10-python-sdk

        2. Development Installation:
        git clone https://github.com/x10-exchange/python-sdk.git
        cd python-sdk
        pip install -e .

        3. Requirements Installation:
        pip install -r requirements.txt

        Dependencies:
        - requests>=2.25.1
        - websocket-client>=1.0.0
        - cryptography>=3.4.8
        - pandas>=1.3.0
        - numpy>=1.21.0

        Verification:
        import x10_sdk
        print(x10_sdk.__version__)

        Configuration:
        export X10_API_KEY="your_api_key"
        export X10_SECRET_KEY="your_secret_key"
        export X10_TESTNET="true"

        Common Issues:
        - SSL certificate errors: Update certificates
        - Permission errors: Use virtual environment
        - Network timeouts: Check firewall settings
        """

    def _get_x10_python_trading_content(self) -> str:
        return """
        X10 Python SDK Trading Client

        Complete trading functionality for X10 Exchange.

        Client Initialization:
        from x10_sdk import X10TradingClient

        client = X10TradingClient(
            api_key="your_api_key",
            secret_key="your_secret_key",
            base_url="https://api.x10.exchange",
            testnet=False
        )

        Account Management:
        # Get account information
        account = client.get_account()
        print(f"Balance: {account.balance}")

        # Get positions
        positions = client.get_positions()

        # Get trade history
        trades = client.get_trades(symbol="BTC/USDT")

        Order Management:
        # Place market order
        market_order = client.place_market_order(
            symbol="BTC/USDT",
            side="buy",
            quantity=0.1
        )

        # Place limit order
        limit_order = client.place_limit_order(
            symbol="BTC/USDT",
            side="buy",
            quantity=0.1,
            price=50000
        )

        # Cancel order
        client.cancel_order(order_id=market_order.order_id)

        # Get order status
        order_status = client.get_order(order_id=limit_order.order_id)

        Market Data:
        # Get ticker
        ticker = client.get_ticker("BTC/USDT")

        # Get order book
        orderbook = client.get_orderbook("BTC/USDT", depth=20)

        # Get recent trades
        trades = client.get_recent_trades("BTC/USDT")

        WebSocket Support:
        # Real-time data
        ws_client = client.get_websocket_client()

        ws_client.subscribe_ticker("BTC/USDT")
        ws_client.subscribe_orderbook("BTC/USDT")
        ws_client.subscribe_trades("BTC/USDT")
        """

    def _get_x10_python_examples_content(self) -> str:
        return """
        X10 Python SDK Examples

        Comprehensive examples for X10 Python SDK usage.

        Basic Trading Bot:
        import time
        from x10_sdk import X10TradingClient

        client = X10TradingClient(
            api_key="your_api_key",
            secret_key="your_secret_key"
        )

        def simple_trading_bot():
            while True:
                # Get current price
                ticker = client.get_ticker("BTC/USDT")
                current_price = ticker.price

                # Simple strategy: buy if price drops 1%
                if current_price < previous_price * 0.99:
                    client.place_market_order(
                        symbol="BTC/USDT",
                        side="buy",
                        quantity=0.01
                    )

                time.sleep(60)  # Check every minute

        Portfolio Manager:
        class PortfolioManager:
            def __init__(self, client):
                self.client = client

            def get_portfolio_value(self):
                account = self.client.get_account()
                total_value = 0

                for balance in account.balances:
                    if balance.free > 0:
                        ticker = self.client.get_ticker(f"{balance.asset}/USDT")
                        total_value += balance.free * ticker.price

                return total_value

            def rebalance_portfolio(self, target_weights):
                current_value = self.get_portfolio_value()

                for asset, weight in target_weights.items():
                    target_value = current_value * weight
                    # Implement rebalancing logic
                    pass

        Risk Management:
        class RiskManager:
            def __init__(self, client, max_position_size=0.1):
                self.client = client
                self.max_position_size = max_position_size

            def check_position_size(self, symbol, quantity):
                account = self.client.get_account()
                current_position = self.get_position_size(symbol)

                if current_position + quantity > self.max_position_size:
                    raise ValueError("Position size exceeds limit")

                return True

            def set_stop_loss(self, symbol, position_size, stop_percentage=0.05):
                current_price = self.client.get_ticker(symbol).price
                stop_price = current_price * (1 - stop_percentage)

                self.client.place_stop_order(
                    symbol=symbol,
                    side="sell",
                    quantity=position_size,
                    stop_price=stop_price
                )

        Market Data Analysis:
        import pandas as pd

        def analyze_market_data():
            # Get historical data
            klines = client.get_klines("BTC/USDT", interval="1h", limit=100)

            # Convert to DataFrame
            df = pd.DataFrame(klines)
            df['close'] = df['close'].astype(float)

            # Calculate moving averages
            df['ma_20'] = df['close'].rolling(20).mean()
            df['ma_50'] = df['close'].rolling(50).mean()

            # Generate signals
            df['signal'] = 0
            df.loc[df['ma_20'] > df['ma_50'], 'signal'] = 1
            df.loc[df['ma_20'] < df['ma_50'], 'signal'] = -1

            return df
        """

    def _get_starknet_dart_overview_content(self) -> str:
        return """
        Starknet.dart SDK Overview

        Dart SDK for Starknet blockchain integration in Flutter applications.

        Features:
        - Starknet network connectivity
        - Account management
        - Contract interaction
        - Transaction handling
        - Mobile-first design

        Installation:
        dependencies:
          starknet: ^1.0.0

        Quick Start:
        import 'package:starknet/starknet.dart';

        // Initialize provider
        final provider = JsonRpcProvider(
          nodeUrl: 'https://starknet-mainnet.infura.io/v3/YOUR_KEY'
        );

        // Create account
        final account = Account(
          provider: provider,
          address: '0x123...',
          keyPair: KeyPair.fromPrivateKey('0xabc...')
        );

        // Call contract
        final result = await account.call(
          contractAddress: '0x456...',
          selector: 'get_balance',
          calldata: []
        );

        Supported Networks:
        - Starknet Mainnet
        - Starknet Testnet
        - Local development networks

        Platform Support:
        - Flutter (iOS/Android)
        - Dart VM
        - Web (with limitations)
        """

    def _get_starknet_dart_provider_content(self) -> str:
        return """
        Starknet.dart Provider

        Network provider for Starknet blockchain connectivity.

        Provider Types:

        1. JsonRpcProvider:
        final provider = JsonRpcProvider(
          nodeUrl: 'https://starknet-mainnet.infura.io/v3/YOUR_KEY'
        );

        2. SequencerProvider:
        final provider = SequencerProvider(
          baseUrl: 'https://alpha-mainnet.starknet.io',
          feederGatewayUrl: 'feeder_gateway',
          gatewayUrl: 'gateway'
        );

        Provider Methods:

        // Get block information
        final block = await provider.getBlock(blockNumber: 12345);

        // Get transaction
        final tx = await provider.getTransaction(txHash: '0x123...');

        // Get contract class
        final contractClass = await provider.getClassAt(
          contractAddress: '0x456...'
        );

        // Call contract view function
        final result = await provider.call(
          contractAddress: '0x789...',
          selector: 'get_balance',
          calldata: []
        );

        // Estimate fee
        final fee = await provider.estimateFee(
          contractAddress: '0xabc...',
          selector: 'transfer',
          calldata: ['0xdef...', '1000000000000000000']
        );

        Network Configuration:
        // Mainnet
        const mainnetProvider = JsonRpcProvider(
          nodeUrl: 'https://starknet-mainnet.infura.io/v3/YOUR_KEY'
        );

        // Testnet
        const testnetProvider = JsonRpcProvider(
          nodeUrl: 'https://starknet-goerli.infura.io/v3/YOUR_KEY'
        );

        Error Handling:
        try {
          final result = await provider.call(/* ... */);
        } on StarknetException catch (e) {
          print('Starknet error: ${e.message}');
        } on NetworkException catch (e) {
          print('Network error: ${e.message}');
        }
        """

    def _get_starknet_dart_account_content(self) -> str:
        return """
        Starknet.dart Account Management

        Account management for Starknet transactions.

        Account Creation:

        1. From Private Key:
        final keyPair = KeyPair.fromPrivateKey('0xabc123...');
        final account = Account(
          provider: provider,
          address: '0x123...',
          keyPair: keyPair
        );

        2. From Mnemonic:
        final keyPair = KeyPair.fromMnemonic('word1 word2 ...');
        final account = Account(
          provider: provider,
          address: computeAddress(keyPair.publicKey),
          keyPair: keyPair
        );

        Account Operations:

        // Get account balance
        final balance = await account.getBalance();

        // Get nonce
        final nonce = await account.getNonce();

        // Execute transaction
        final result = await account.execute(
          contractAddress: '0x456...',
          selector: 'transfer',
          calldata: ['0x789...', '1000000000000000000']
        );

        // Deploy contract
        final deployResult = await account.deploy(
          classHash: '0xabc...',
          constructorCalldata: ['param1', 'param2']
        );

        Account Abstraction:

        // Custom account contract
        class CustomAccount extends Account {
          @override
          Future<List<String>> signTransaction(
            List<String> txnHash
          ) async {
            // Custom signing logic
            return customSign(txnHash);
          }
        }

        Multi-signature Account:
        final multiSigAccount = MultiSigAccount(
          provider: provider,
          address: '0x123...',
          signers: [keyPair1, keyPair2, keyPair3],
          threshold: 2
        );

        Account Recovery:
        // Recover from social recovery
        final recoveryAccount = await SocialRecovery.recover(
          guardians: ['0x111...', '0x222...'],
          newOwner: newKeyPair.publicKey
        );

        Security Best Practices:
        - Store private keys securely
        - Use hardware wallets when possible
        - Implement proper key rotation
        - Monitor account activity
        - Use multi-signature for high-value accounts
        """

    def _get_starknet_dart_contract_content(self) -> str:
        return """
        Starknet.dart Contract Interaction

        Smart contract interaction on Starknet.

        Contract Instance:
        final contract = Contract(
          provider: provider,
          address: '0x123...',
          abi: contractAbi
        );

        Reading Contract State:

        // Call view function
        final balance = await contract.call('get_balance', []);

        // Call with parameters
        final allowance = await contract.call(
          'allowance',
          ['0x456...', '0x789...']
        );

        Writing to Contract:

        // Execute function
        final result = await account.execute(
          contractAddress: contract.address,
          selector: 'transfer',
          calldata: ['0x456...', '1000000000000000000']
        );

        // Multiple calls in single transaction
        final multiResult = await account.execute([
          Call(
            contractAddress: '0x123...',
            selector: 'approve',
            calldata: ['0x456...', '1000000000000000000']
          ),
          Call(
            contractAddress: '0x789...',
            selector: 'swap',
            calldata: ['0x123...', '500000000000000000']
          )
        ]);

        Contract Deployment:

        // Deploy new contract
        final deployResult = await account.deploy(
          classHash: '0xabc...',
          constructorCalldata: ['param1', 'param2'],
          salt: '0x123...'
        );

        // Get deployed contract address
        final deployedAddress = deployResult.contractAddress;

        Event Handling:

        // Listen to contract events
        final eventFilter = EventFilter(
          contractAddress: contract.address,
          eventName: 'Transfer'
        );

        final events = await provider.getEvents(eventFilter);

        for (final event in events) {
          print('Transfer: ${event.data}');
        }

        Contract ABI:
        const contractAbi = [
          {
            "name": "transfer",
            "type": "function",
            "inputs": [
              {"name": "recipient", "type": "felt"},
              {"name": "amount", "type": "Uint256"}
            ],
            "outputs": [
              {"name": "success", "type": "felt"}
            ]
          }
        ];

        Error Handling:
        try {
          final result = await contract.call('get_balance', []);
        } on ContractException catch (e) {
          print('Contract error: ${e.message}');
        } on TransactionException catch (e) {
          print('Transaction failed: ${e.message}');
        }
        """

    def _get_cairo_lang_overview_content(self) -> str:
        return """
        Cairo Language Overview

        Cairo is a programming language for writing provable programs on Starknet.

        Key Features:
        - Proven computation
        - Zero-knowledge proofs
        - Efficient execution
        - Type safety
        - Memory safety

        Installation:
        curl -L https://github.com/starkware-libs/cairo/releases/download/v2.0.0/cairo-lang-2.0.0.tar.gz | tar -xz
        cd cairo-lang-2.0.0
        pip install .

        Basic Syntax:
        // Hello World
        #[contract]
        mod HelloWorld {
            #[storage]
            struct Storage {
                message: felt252
            }

            #[constructor]
            fn constructor(ref self: ContractState, initial_message: felt252) {
                self.message.write(initial_message);
            }

            #[external(v0)]
            fn get_message(self: @ContractState) -> felt252 {
                self.message.read()
            }

            #[external(v0)]
            fn set_message(ref self: ContractState, new_message: felt252) {
                self.message.write(new_message);
            }
        }

        Data Types:
        - felt252: Field element (252 bits)
        - u8, u16, u32, u64, u128, u256: Unsigned integers
        - Array<T>: Dynamic arrays
        - Option<T>: Optional values
        - Result<T, E>: Error handling

        Control Flow:
        if condition {
            // true branch
        } else {
            // false branch
        }

        loop {
            // infinite loop
            break;
        }

        Functions:
        fn add(x: felt252, y: felt252) -> felt252 {
            x + y
        }

        Structs:
        #[derive(Copy, Drop)]
        struct Point {
            x: felt252,
            y: felt252
        }

        Enums:
        enum Direction {
            North,
            South,
            East,
            West
        }

        Traits:
        trait Drawable {
            fn draw(self: @Self);
        }

        impl DrawablePoint of Drawable<Point> {
            fn draw(self: @Point) {
                // drawing logic
            }
        }
        """

    def _get_cairo_contract_dev_content(self) -> str:
        return """
        Cairo Smart Contract Development

        Complete guide to developing smart contracts in Cairo.

        Contract Structure:
        #[contract]
        mod MyContract {
            use starknet::storage_access::StorageAccess;

            #[storage]
            struct Storage {
                balance: LegacyMap<ContractAddress, u256>,
                total_supply: u256,
                owner: ContractAddress
            }

            #[event]
            #[derive(Drop, starknet::Event)]
            enum Event {
                Transfer: Transfer,
                Approval: Approval
            }

            #[derive(Drop, starknet::Event)]
            struct Transfer {
                from: ContractAddress,
                to: ContractAddress,
                value: u256
            }

            #[constructor]
            fn constructor(ref self: ContractState, owner: ContractAddress) {
                self.owner.write(owner);
                self.total_supply.write(1000000_u256);
                self.balance.write(owner, 1000000_u256);
            }

            #[external(v0)]
            fn transfer(ref self: ContractState, to: ContractAddress, amount: u256) -> bool {
                let caller = get_caller_address();
                self._transfer(caller, to, amount);
                true
            }

            #[external(v0)]
            fn balance_of(self: @ContractState, account: ContractAddress) -> u256 {
                self.balance.read(account)
            }

            #[generate_trait]
            impl InternalFunctions of InternalFunctionsTrait {
                fn _transfer(ref self: ContractState, from: ContractAddress, to: ContractAddress, amount: u256) {
                    let from_balance = self.balance.read(from);
                    assert(from_balance >= amount, 'Insufficient balance');

                    self.balance.write(from, from_balance - amount);
                    self.balance.write(to, self.balance.read(to) + amount);

                    self.emit(Transfer { from, to, value: amount });
                }
            }
        }

        Storage:
        - LegacyMap<K, V>: Key-value storage
        - Simple variables: Direct storage
        - Nested structs: Complex storage

        Events:
        - Emit events for important state changes
        - Events are indexed for efficient querying
        - Use #[derive(Drop, starknet::Event)] for event structs

        Access Control:
        fn only_owner(self: @ContractState) {
            let caller = get_caller_address();
            let owner = self.owner.read();
            assert(caller == owner, 'Only owner can call');
        }

        Error Handling:
        - Use assert! for preconditions
        - Use Result<T, E> for fallible operations
        - Custom error types

        Testing:
        #[cfg(test)]
        mod tests {
            use super::*;

            #[test]
            fn test_transfer() {
                let contract = deploy_contract();
                let result = contract.transfer(recipient, 100);
                assert(result == true, 'Transfer failed');
            }
        }

        Deployment:
        starknet-compile src/contract.cairo output.json
        starknet deploy --contract output.json
        """

    def _get_cairo_syntax_content(self) -> str:
        return """
        Cairo Language Syntax Reference

        Complete syntax reference for Cairo programming language.

        Variables:
        let x = 5;  // immutable
        let mut y = 10;  // mutable

        Constants:
        const MAX_SUPPLY: u256 = 1000000;

        Functions:
        fn function_name(param1: felt252, param2: u256) -> felt252 {
            // function body
            param1 + param2
        }

        Structs:
        #[derive(Copy, Drop)]
        struct Person {
            name: felt252,
            age: u8
        }

        let person = Person { name: 'Alice', age: 30 };

        Enums:
        enum Color {
            Red,
            Green,
            Blue,
            RGB: (u8, u8, u8)
        }

        let color = Color::RGB((255, 0, 0));

        Arrays:
        let arr: Array<felt252> = array![1, 2, 3, 4];
        let first = arr[0];

        Tuples:
        let tuple: (felt252, u256) = (1, 100);
        let (a, b) = tuple;

        Options:
        let some_value: Option<felt252> = Option::Some(5);
        let none_value: Option<felt252> = Option::None;

        match some_value {
            Option::Some(value) => value,
            Option::None => 0
        }

        Results:
        fn divide(a: felt252, b: felt252) -> Result<felt252, felt252> {
            if b == 0 {
                Result::Err('Division by zero')
            } else {
                Result::Ok(a / b)
            }
        }

        Pattern Matching:
        match value {
            0 => 'zero',
            1 => 'one',
            _ => 'other'
        }

        Control Flow:
        // If expressions
        let result = if condition {
            value1
        } else {
            value2
        };

        // Loops
        loop {
            // infinite loop
            break;
        }

        let mut i = 0;
        while i < 10 {
            i += 1;
        }

        Traits:
        trait Display {
            fn display(self: @Self) -> felt252;
        }

        impl DisplayU256 of Display<u256> {
            fn display(self: @u256) -> felt252 {
                // implementation
            }
        }

        Generics:
        fn generic_function<T>(value: T) -> T {
            value
        }

        struct GenericStruct<T> {
            value: T
        }

        Comments:
        // Single line comment
        /* Multi-line
           comment */

        Attributes:
        #[derive(Copy, Drop)]
        #[contract]
        #[storage]
        #[event]
        #[external(v0)]
        #[constructor]
        #[generate_trait]
        """

    def _get_cairo_examples_content(self) -> str:
        return """
        Cairo Programming Examples

        Practical examples of Cairo programming patterns.

        ERC-20 Token:
        #[contract]
        mod ERC20 {
            use starknet::{ContractAddress, get_caller_address};

            #[storage]
            struct Storage {
                balances: LegacyMap<ContractAddress, u256>,
                allowances: LegacyMap<(ContractAddress, ContractAddress), u256>,
                total_supply: u256,
                name: felt252,
                symbol: felt252,
                decimals: u8
            }

            #[constructor]
            fn constructor(
                ref self: ContractState,
                name: felt252,
                symbol: felt252,
                decimals: u8,
                initial_supply: u256,
                recipient: ContractAddress
            ) {
                self.name.write(name);
                self.symbol.write(symbol);
                self.decimals.write(decimals);
                self.total_supply.write(initial_supply);
                self.balances.write(recipient, initial_supply);
            }

            #[external(v0)]
            fn transfer(ref self: ContractState, to: ContractAddress, amount: u256) -> bool {
                let caller = get_caller_address();
                self._transfer(caller, to, amount);
                true
            }

            #[external(v0)]
            fn approve(ref self: ContractState, spender: ContractAddress, amount: u256) -> bool {
                let caller = get_caller_address();
                self.allowances.write((caller, spender), amount);
                true
            }

            #[external(v0)]
            fn transfer_from(
                ref self: ContractState,
                from: ContractAddress,
                to: ContractAddress,
                amount: u256
            ) -> bool {
                let caller = get_caller_address();
                let allowance = self.allowances.read((from, caller));
                assert(allowance >= amount, 'Insufficient allowance');

                self.allowances.write((from, caller), allowance - amount);
                self._transfer(from, to, amount);
                true
            }

            #[generate_trait]
            impl InternalFunctions of InternalFunctionsTrait {
                fn _transfer(ref self: ContractState, from: ContractAddress, to: ContractAddress, amount: u256) {
                    let from_balance = self.balances.read(from);
                    assert(from_balance >= amount, 'Insufficient balance');

                    self.balances.write(from, from_balance - amount);
                    self.balances.write(to, self.balances.read(to) + amount);
                }
            }
        }

        Voting Contract:
        #[contract]
        mod Voting {
            #[storage]
            struct Storage {
                proposals: LegacyMap<u256, Proposal>,
                votes: LegacyMap<(u256, ContractAddress), bool>,
                proposal_count: u256,
                owner: ContractAddress
            }

            #[derive(Copy, Drop, Serde)]
            struct Proposal {
                id: u256,
                description: felt252,
                yes_votes: u256,
                no_votes: u256,
                deadline: u64
            }

            #[external(v0)]
            fn create_proposal(ref self: ContractState, description: felt252, duration: u64) {
                let caller = get_caller_address();
                assert(caller == self.owner.read(), 'Only owner can create proposals');

                let proposal_id = self.proposal_count.read() + 1;
                let deadline = get_block_timestamp() + duration;

                let proposal = Proposal {
                    id: proposal_id,
                    description,
                    yes_votes: 0,
                    no_votes: 0,
                    deadline
                };

                self.proposals.write(proposal_id, proposal);
                self.proposal_count.write(proposal_id);
            }

            #[external(v0)]
            fn vote(ref self: ContractState, proposal_id: u256, vote: bool) {
                let caller = get_caller_address();
                let has_voted = self.votes.read((proposal_id, caller));
                assert(!has_voted, 'Already voted');

                let mut proposal = self.proposals.read(proposal_id);
                assert(get_block_timestamp() < proposal.deadline, 'Voting ended');

                if vote {
                    proposal.yes_votes += 1;
                } else {
                    proposal.no_votes += 1;
                }

                self.proposals.write(proposal_id, proposal);
                self.votes.write((proposal_id, caller), true);
            }
        }

        NFT Contract:
        #[contract]
        mod NFT {
            use starknet::{ContractAddress, get_caller_address};

            #[storage]
            struct Storage {
                owners: LegacyMap<u256, ContractAddress>,
                balances: LegacyMap<ContractAddress, u256>,
                token_approvals: LegacyMap<u256, ContractAddress>,
                operator_approvals: LegacyMap<(ContractAddress, ContractAddress), bool>,
                next_token_id: u256
            }

            #[external(v0)]
            fn mint(ref self: ContractState, to: ContractAddress) -> u256 {
                let token_id = self.next_token_id.read();
                self.next_token_id.write(token_id + 1);

                self.owners.write(token_id, to);
                self.balances.write(to, self.balances.read(to) + 1);

                token_id
            }

            #[external(v0)]
            fn transfer_from(
                ref self: ContractState,
                from: ContractAddress,
                to: ContractAddress,
                token_id: u256
            ) {
                let caller = get_caller_address();
                let owner = self.owners.read(token_id);

                assert(
                    caller == owner ||
                    caller == self.token_approvals.read(token_id) ||
                    self.operator_approvals.read((owner, caller)),
                    'Not approved'
                );

                self.owners.write(token_id, to);
                self.balances.write(from, self.balances.read(from) - 1);
                self.balances.write(to, self.balances.read(to) + 1);

                // Clear approval
                self.token_approvals.write(token_id, contract_address_const::<0>());
            }
        }
        """

    def _get_avnu_paymaster_overview_content(self) -> str:
        return """
        AVNU Paymaster Overview

        Gas sponsorship and account abstraction for Starknet.

        What is AVNU Paymaster?
        AVNU Paymaster enables gasless transactions on Starknet by sponsoring gas fees for users.

        Key Features:
        - Gas sponsorship
        - Account abstraction
        - Flexible payment models
        - Developer-friendly API
        - Production-ready infrastructure

        How it Works:
        1. User initiates transaction
        2. Paymaster validates request
        3. Paymaster sponsors gas fee
        4. Transaction executes on Starknet
        5. Paymaster handles fee settlement

        Benefits:
        - Better user experience
        - Lower barrier to entry
        - Flexible fee structures
        - Scalable infrastructure

        Use Cases:
        - Onboarding new users
        - Gaming applications
        - DeFi protocols
        - NFT marketplaces
        - Social applications

        Supported Networks:
        - Starknet Mainnet
        - Starknet Goerli Testnet
        - Starknet Sepolia Testnet

        Integration Options:
        - REST API
        - TypeScript SDK
        - Python SDK
        - Direct contract calls

        Getting Started:
        1. Sign up for AVNU Paymaster
        2. Get API credentials
        3. Configure your application
        4. Test on testnet
        5. Deploy to mainnet

        Documentation:
        - API Reference
        - SDK Documentation
        - Integration Guides
        - Best Practices
        - Troubleshooting
        """

    def _get_avnu_paymaster_integration_content(self) -> str:
        return """
        AVNU Paymaster Integration Guide

        Step-by-step integration guide for AVNU Paymaster.

        Prerequisites:
        - Starknet account
        - AVNU Paymaster API key
        - Development environment

        Installation:

        TypeScript/JavaScript:
        npm install @avnu/paymaster-sdk

        Python:
        pip install avnu-paymaster

        Basic Integration:

        TypeScript:
        import { PaymasterSDK } from '@avnu/paymaster-sdk';

        const paymaster = new PaymasterSDK({
          apiKey: 'your-api-key',
          network: 'mainnet'
        });

        // Sponsor transaction
        const sponsoredTx = await paymaster.sponsorTransaction({
          to: '0x123...',
          calldata: ['0x456...', '1000'],
          maxFee: '1000000000000000'
        });

        Python:
        from avnu_paymaster import PaymasterClient

        client = PaymasterClient(
          api_key='your-api-key',
          network='mainnet'
        )

        # Sponsor transaction
        sponsored_tx = client.sponsor_transaction(
          to='0x123...',
          calldata=['0x456...', '1000'],
          max_fee='1000000000000000'
        )

        Advanced Configuration:

        // Custom validation rules
        const config = {
          apiKey: 'your-api-key',
          network: 'mainnet',
          validation: {
            maxGasPrice: '1000000000',
            allowedContracts: ['0x123...', '0x456...'],
            rateLimit: 100
          }
        };

        const paymaster = new PaymasterSDK(config);

        Error Handling:

        try {
          const result = await paymaster.sponsorTransaction(tx);
          console.log('Transaction sponsored:', result.txHash);
        } catch (error) {
          if (error.code === 'INSUFFICIENT_BALANCE') {
            console.error('Paymaster has insufficient balance');
          } else if (error.code === 'VALIDATION_FAILED') {
            console.error('Transaction validation failed');
          }
        }

        Monitoring:

        // Get paymaster balance
        const balance = await paymaster.getBalance();

        // Get transaction status
        const status = await paymaster.getTransactionStatus(txHash);

        // Get usage statistics
        const stats = await paymaster.getUsageStats();

        Best Practices:
        - Set appropriate gas limits
        - Implement proper error handling
        - Monitor paymaster balance
        - Use rate limiting
        - Validate transactions before sponsoring
        - Test thoroughly on testnet
        """

    def _get_avnu_paymaster_gas_content(self) -> str:
        return """
        AVNU Paymaster Gas Sponsorship

        Comprehensive guide to gas sponsorship with AVNU Paymaster.

        Gas Sponsorship Models:

        1. Full Sponsorship:
        - Paymaster covers all gas costs
        - User pays nothing
        - Best for onboarding

        2. Partial Sponsorship:
        - Paymaster covers percentage of gas
        - User pays remainder
        - Good for premium features

        3. Conditional Sponsorship:
        - Sponsorship based on conditions
        - User type, transaction amount, etc.
        - Flexible business models

        Configuration:

        const sponsorshipConfig = {
          model: 'full',
          maxGasPrice: '1000000000',
          maxTransactionValue: '1000000000000000000',
          allowedContracts: ['0x123...'],
          userWhitelist: ['0x456...']
        };

        Usage Tracking:

        // Track sponsored transactions
        const usage = await paymaster.getUsage({
          startDate: '2024-01-01',
          endDate: '2024-01-31',
          groupBy: 'contract'
        });

        console.log('Total sponsored:', usage.totalSponsored);
        console.log('Gas saved:', usage.totalGasSaved);

        Cost Management:

        // Set daily limits
        await paymaster.setDailyLimit('1000000000000000000');

        // Set per-user limits
        await paymaster.setUserLimit('0x123...', '100000000000000000');

        // Monitor costs
        const costs = await paymaster.getCosts();

        Optimization:

        // Batch transactions
        const batchedTx = await paymaster.sponsorBatch([
          { to: '0x123...', calldata: ['0x456...'] },
          { to: '0x789...', calldata: ['0xabc...'] }
        ]);

        // Optimize gas estimation
        const optimizedGas = await paymaster.estimateOptimalGas(tx);

        Analytics:

        // User behavior analysis
        const userStats = await paymaster.getUserAnalytics('0x123...');

        // Contract usage patterns
        const contractStats = await paymaster.getContractAnalytics('0x456...');

        // ROI calculation
        const roi = await paymaster.calculateROI({
          sponsorshipCost: '1000000000000000000',
          userRetention: 0.8,
          averageUserValue: '5000000000000000000'
        });

        Alerts and Notifications:

        // Set up balance alerts
        await paymaster.setBalanceAlert({
          threshold: '100000000000000000',
          webhook: 'https://your-app.com/webhook'
        });

        // Usage alerts
        await paymaster.setUsageAlert({
          dailyLimit: '1000000000000000000',
          webhook: 'https://your-app.com/webhook'
        });

        Reporting:

        // Generate reports
        const report = await paymaster.generateReport({
          type: 'monthly',
          format: 'pdf',
          includes: ['usage', 'costs', 'analytics']
        });

        // Export data
        const data = await paymaster.exportData({
          format: 'csv',
          fields: ['txHash', 'gasUsed', 'gasSaved', 'timestamp']
        });
        """

    def _get_web3auth_overview_content(self) -> str:
        return """
        Web3Auth Overview

        Non-custodial authentication infrastructure for Web3 applications.

        What is Web3Auth?
        Web3Auth is a pluggable authentication infrastructure that enables Web3 applications to provide seamless onboarding experiences.

        Key Features:
        - Social login integration
        - Multi-factor authentication
        - Non-custodial key management
        - Cross-platform support
        - Enterprise-grade security

        Supported Platforms:
        - Web (JavaScript/TypeScript)
        - Mobile (React Native)
        - Flutter
        - Unity
        - Unreal Engine

        Authentication Options:
        - Google
        - Facebook
        - Twitter
        - Discord
        - Email/Password
        - SMS
        - Custom JWT

        Key Management:
        - Threshold cryptography
        - Multi-party computation (MPC)
        - Hardware security modules
        - Biometric authentication

        Networks Supported:
        - Ethereum
        - Polygon
        - Binance Smart Chain
        - Solana
        - Avalanche
        - Starknet

        Integration Types:
        - Plug and Play
        - Core SDK
        - Custom implementation

        Use Cases:
        - DeFi applications
        - NFT marketplaces
        - Gaming applications
        - Social platforms
        - Enterprise solutions
        """

    def _get_web3auth_flutter_content(self) -> str:
        return """
        Web3Auth Flutter Integration

        Complete guide for integrating Web3Auth with Flutter applications.

        Installation:
        dependencies:
          web3auth_flutter: ^3.0.0

        iOS Setup:
        Add to Info.plist:
        <key>CFBundleURLTypes</key>
        <array>
          <dict>
            <key>CFBundleURLName</key>
            <string>com.example.app</string>
            <key>CFBundleURLSchemes</key>
            <array>
              <string>com.example.app</string>
            </array>
          </dict>
        </array>

        Android Setup:
        Add to AndroidManifest.xml:
        <activity
          android:name="com.web3auth.flutter.Web3AuthActivity"
          android:exported="true"
          android:launchMode="singleTop">
          <intent-filter>
            <action android:name="android.intent.action.VIEW" />
            <category android:name="android.intent.category.DEFAULT" />
            <category android:name="android.intent.category.BROWSABLE" />
            <data android:scheme="com.example.app" />
          </intent-filter>
        </activity>

        Basic Implementation:

        import 'package:web3auth_flutter/web3auth_flutter.dart';

        class Web3AuthService {
          late Web3AuthFlutter _web3AuthFlutter;

          Future<void> initialize() async {
            _web3AuthFlutter = Web3AuthFlutter(
              Web3AuthOptions(
                clientId: 'your-client-id',
                network: Network.testnet,
                redirectUrl: 'com.example.app://auth',
                whiteLabel: WhiteLabel(
                  name: 'Your App',
                  logoLight: 'assets/logo.png',
                  logoDark: 'assets/logo_dark.png',
                  defaultLanguage: Language.en,
                  mode: ThemeModes.light,
                )
              )
            );

            await _web3AuthFlutter.initialize();
          }

          Future<Web3AuthResponse> login(LoginProvider provider) async {
            return await _web3AuthFlutter.login(LoginParams(
              loginProvider: provider,
              mfaLevel: MFALevel.default,
            ));
          }

          Future<void> logout() async {
            await _web3AuthFlutter.logout();
          }

          Future<String?> getPrivateKey() async {
            return await _web3AuthFlutter.getPrivateKey();
          }

          Future<String?> getAddress() async {
            return await _web3AuthFlutter.getEd25519PrivateKey();
          }
        }

        UI Integration:

        class LoginScreen extends StatefulWidget {
          @override
          _LoginScreenState createState() => _LoginScreenState();
        }

        class _LoginScreenState extends State<LoginScreen> {
          final Web3AuthService _web3AuthService = Web3AuthService();
          bool _isLoading = false;

          @override
          void initState() {
            super.initState();
            _initializeWeb3Auth();
          }

          Future<void> _initializeWeb3Auth() async {
            await _web3AuthService.initialize();
          }

          Future<void> _login(LoginProvider provider) async {
            setState(() => _isLoading = true);

            try {
              final result = await _web3AuthService.login(provider);

              if (result.privKey != null) {
                // Login successful
                Navigator.pushReplacementNamed(context, '/dashboard');
              }
            } catch (e) {
              // Handle login error
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text('Login failed: $e'))
              );
            } finally {
              setState(() => _isLoading = false);
            }
          }

          @override
          Widget build(BuildContext context) {
            return Scaffold(
              appBar: AppBar(title: Text('Login')),
              body: Center(
                child: _isLoading
                  ? CircularProgressIndicator()
                  : Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        ElevatedButton(
                          onPressed: () => _login(Provider.google),
                          child: Text('Login with Google'),
                        ),
                        ElevatedButton(
                          onPressed: () => _login(Provider.facebook),
                          child: Text('Login with Facebook'),
                        ),
                        ElevatedButton(
                          onPressed: () => _login(Provider.twitter),
                          child: Text('Login with Twitter'),
                        ),
                      ],
                    ),
              ),
            );
          }
        }

        Advanced Features:

        // Custom authentication
        final customAuth = await _web3AuthFlutter.login(LoginParams(
          loginProvider: Provider.jwt,
          extraLoginOptions: ExtraLoginOptions(
            domain: 'your-domain.com',
            id_token: 'your-jwt-token',
          ),
        ));

        // Multi-factor authentication
        final mfaAuth = await _web3AuthFlutter.login(LoginParams(
          loginProvider: Provider.google,
          mfaLevel: MFALevel.mandatory,
        ));

        // Custom UI
        final customUI = await _web3AuthFlutter.login(LoginParams(
          loginProvider: Provider.google,
          curve: Curve.secp256k1,
          customAuth: CustomAuthArgs(
            verifier: 'your-verifier',
            verifierId: 'user-id',
          ),
        ));

        Error Handling:

        try {
          final result = await _web3AuthService.login(Provider.google);
        } on Web3AuthException catch (e) {
          switch (e.code) {
            case 'user_cancelled':
              print('User cancelled login');
              break;
            case 'network_error':
              print('Network error during login');
              break;
            default:
              print('Login error: ${e.message}');
          }
        }

        State Management:

        class AuthProvider extends ChangeNotifier {
          Web3AuthResponse? _user;
          bool _isLoggedIn = false;

          bool get isLoggedIn => _isLoggedIn;
          Web3AuthResponse? get user => _user;

          Future<void> login(LoginProvider provider) async {
            final result = await _web3AuthService.login(provider);
            _user = result;
            _isLoggedIn = true;
            notifyListeners();
          }

          Future<void> logout() async {
            await _web3AuthService.logout();
            _user = null;
            _isLoggedIn = false;
            notifyListeners();
          }
        }
        """

    def _get_web3auth_key_management_content(self) -> str:
        return """
        Web3Auth Key Management

        Secure key management and cryptographic operations with Web3Auth.

        Key Generation:
        Web3Auth uses threshold cryptography to generate and manage private keys across multiple parties.

        Architecture:
        - Threshold Secret Sharing (TSS)
        - Multi-Party Computation (MPC)
        - Hardware Security Modules (HSM)
        - Secure enclaves

        Key Recovery:
        Multiple recovery mechanisms available:
        - Social recovery
        - Device-based recovery
        - Backup phrase recovery
        - Biometric recovery

        Security Features:

        // Key encryption
        const encryptedKey = await web3auth.encrypt(
          privateKey,
          'user-password'
        );

        // Key decryption
        const decryptedKey = await web3auth.decrypt(
          encryptedKey,
          'user-password'
        );

        // Secure key storage
        await web3auth.secureStore(
          'user-private-key',
          privateKey,
          {
            requireBiometric: true,
            requirePin: true
          }
        );

        Multi-Device Support:

        // Sync keys across devices
        await web3auth.syncKeys({
          devices: ['mobile', 'desktop'],
          method: 'cloud-backup'
        });

        // Device registration
        await web3auth.registerDevice({
          deviceId: 'device-unique-id',
          publicKey: devicePublicKey,
          attestation: deviceAttestation
        });

        Backup and Recovery:

        // Create backup
        const backup = await web3auth.createBackup({
          method: 'mnemonic',
          encryptionKey: 'user-password'
        });

        // Restore from backup
        const restored = await web3auth.restoreFromBackup({
          backup: backup,
          decryptionKey: 'user-password'
        });

        Social Recovery:

        // Set recovery guardians
        await web3auth.setRecoveryGuardians([
          'guardian1@example.com',
          'guardian2@example.com',
          'guardian3@example.com'
        ]);

        // Initiate recovery
        const recovery = await web3auth.initiateRecovery({
          userEmail: 'user@example.com',
          guardians: ['guardian1@example.com', 'guardian2@example.com']
        });

        // Complete recovery
        const newKey = await web3auth.completeRecovery({
          recoveryId: recovery.id,
          guardianSignatures: [signature1, signature2]
        });

        Hardware Security:

        // Hardware wallet integration
        const hwWallet = await web3auth.connectHardwareWallet({
          type: 'ledger',
          transport: 'usb'
        });

        // Sign with hardware wallet
        const signature = await hwWallet.sign(transactionHash);

        // Biometric authentication
        const biometricAuth = await web3auth.authenticateBiometric({
          type: 'fingerprint',
          challenge: 'transaction-hash'
        });

        Key Rotation:

        // Rotate keys
        const newKeyPair = await web3auth.rotateKeys({
          oldPrivateKey: currentPrivateKey,
          reason: 'security-update'
        });

        // Update key references
        await web3auth.updateKeyReferences({
          oldPublicKey: oldPublicKey,
          newPublicKey: newKeyPair.publicKey
        });

        Audit and Monitoring:

        // Key usage audit
        const auditLog = await web3auth.getKeyUsageAudit({
          keyId: 'key-id',
          startDate: '2024-01-01',
          endDate: '2024-01-31'
        });

        // Security alerts
        await web3auth.setSecurityAlerts({
          unusualActivity: true,
          multipleFailedAttempts: true,
          newDeviceAccess: true
        });

        Best Practices:

        1. Regular key rotation
        2. Multi-device backup
        3. Guardian setup
        4. Biometric authentication
        5. Hardware wallet integration
        6. Audit logging
        7. Security monitoring
        8. User education

        Compliance:
        - SOC 2 Type II
        - ISO 27001
        - GDPR compliance
        - CCPA compliance
        - Industry-specific regulations
        """

    def _get_chipi_pay_overview_content(self) -> str:
        return """
        ChipiPay Overview

        Cryptocurrency payment gateway for seamless crypto transactions.

        What is ChipiPay?
        ChipiPay is a comprehensive payment gateway that enables businesses to accept cryptocurrency payments easily.

        Key Features:
        - Multi-currency support
        - Instant settlement
        - Low transaction fees
        - Secure infrastructure
        - Easy integration

        Supported Cryptocurrencies:
        - Bitcoin (BTC)
        - Ethereum (ETH)
        - Starknet (STRK)
        - USDC
        - USDT
        - Custom tokens

        Integration Options:
        - REST API
        - JavaScript SDK
        - WordPress Plugin
        - WooCommerce Extension
        - Shopify App

        Payment Flow:
        1. Customer initiates payment
        2. ChipiPay generates payment address
        3. Customer sends cryptocurrency
        4. ChipiPay confirms transaction
        5. Merchant receives notification
        6. Funds settled to merchant account

        Benefits:
        - Global reach
        - 24/7 availability
        - No chargebacks
        - Fast settlement
        - Low fees

        Use Cases:
        - E-commerce
        - Subscription services
        - Digital goods
        - Service payments
        - Donations

        Security:
        - End-to-end encryption
        - Multi-signature wallets
        - Real-time monitoring
        - Fraud detection
        - Compliance tools
        """

    def _get_chipi_pay_integration_content(self) -> str:
        return """
        ChipiPay Integration Guide

        Step-by-step integration guide for ChipiPay payment gateway.

        Prerequisites:
        - ChipiPay merchant account
        - API credentials
        - HTTPS-enabled website

        Quick Start:

        1. Get API Credentials:
        - Login to ChipiPay dashboard
        - Navigate to API settings
        - Generate API key and secret

        2. Install SDK:

        JavaScript:
        npm install @chipi/pay-js

        PHP:
        composer require chipi/pay-php

        Python:
        pip install chipi-pay

        3. Basic Integration:

        JavaScript:
        import ChipiPay from '@chipi/pay-js';

        const chipiPay = new ChipiPay({
          apiKey: 'your-api-key',
          apiSecret: 'your-api-secret',
          testMode: true
        });

        // Create payment
        const payment = await chipiPay.createPayment({
          amount: 100.00,
          currency: 'USD',
          acceptedCurrencies: ['BTC', 'ETH', 'STRK'],
          orderId: 'order-123',
          redirectUrl: 'https://yoursite.com/success',
          webhookUrl: 'https://yoursite.com/webhook'
        });

        // Redirect to payment page
        window.location.href = payment.paymentUrl;

        PHP:
        <?php
        require_once 'vendor/autoload.php';

        $chipiPay = new ChipiPay\\Client([
          'api_key' => 'your-api-key',
          'api_secret' => 'your-api-secret',
          'test_mode' => true
        ]);

        $payment = $chipiPay->createPayment([
          'amount' => 100.00,
          'currency' => 'USD',
          'accepted_currencies' => ['BTC', 'ETH', 'STRK'],
          'order_id' => 'order-123',
          'redirect_url' => 'https://yoursite.com/success',
          'webhook_url' => 'https://yoursite.com/webhook'
        ]);

        header('Location: ' . $payment['payment_url']);
        ?>

        Python:
        from chipi_pay import ChipiPayClient

        client = ChipiPayClient(
          api_key='your-api-key',
          api_secret='your-api-secret',
          test_mode=True
        )

        payment = client.create_payment(
          amount=100.00,
          currency='USD',
          accepted_currencies=['BTC', 'ETH', 'STRK'],
          order_id='order-123',
          redirect_url='https://yoursite.com/success',
          webhook_url='https://yoursite.com/webhook'
        )

        # Redirect to payment URL
        return redirect(payment['payment_url'])

        Webhook Handling:

        // Verify webhook signature
        const crypto = require('crypto');

        function verifyWebhook(payload, signature, secret) {
          const hmac = crypto.createHmac('sha256', secret);
          hmac.update(payload);
          const expectedSignature = hmac.digest('hex');

          return crypto.timingSafeEqual(
            Buffer.from(signature),
            Buffer.from(expectedSignature)
          );
        }

        // Handle webhook
        app.post('/webhook', (req, res) => {
          const signature = req.headers['x-chipi-signature'];
          const payload = JSON.stringify(req.body);

          if (!verifyWebhook(payload, signature, 'your-webhook-secret')) {
            return res.status(401).send('Invalid signature');
          }

          const event = req.body;

          switch (event.type) {
            case 'payment.completed':
              // Handle successful payment
              updateOrderStatus(event.data.order_id, 'paid');
              break;
            case 'payment.failed':
              // Handle failed payment
              updateOrderStatus(event.data.order_id, 'failed');
              break;
            case 'payment.refunded':
              // Handle refund
              updateOrderStatus(event.data.order_id, 'refunded');
              break;
          }

          res.status(200).send('OK');
        });

        Advanced Features:

        // Subscription payments
        const subscription = await chipiPay.createSubscription({
          amount: 29.99,
          currency: 'USD',
          interval: 'monthly',
          acceptedCurrencies: ['BTC', 'ETH'],
          customerId: 'customer-123'
        });

        // Refund payment
        const refund = await chipiPay.refundPayment({
          paymentId: 'payment-123',
          amount: 50.00,
          reason: 'Customer request'
        });

        // Get payment status
        const status = await chipiPay.getPaymentStatus('payment-123');

        Error Handling:

        try {
          const payment = await chipiPay.createPayment(paymentData);
        } catch (error) {
          if (error.code === 'INVALID_AMOUNT') {
            console.error('Invalid payment amount');
          } else if (error.code === 'INSUFFICIENT_FUNDS') {
            console.error('Insufficient funds');
          } else {
            console.error('Payment error:', error.message);
          }
        }

        Testing:

        // Test mode configuration
        const testChipiPay = new ChipiPay({
          apiKey: 'test-api-key',
          apiSecret: 'test-api-secret',
          testMode: true
        });

        // Test payment
        const testPayment = await testChipiPay.createPayment({
          amount: 0.01,
          currency: 'USD',
          acceptedCurrencies: ['BTC-TEST'],
          orderId: 'test-order-123'
        });

        Production Checklist:
        - Switch to production API keys
        - Set testMode to false
        - Configure webhook URL
        - Test payment flow
        - Monitor transactions
        - Set up alerts
        """


if __name__ == "__main__":
    # Test the enhanced indexer
    import asyncio

    async def test_indexer():
        # Mock RAG system for testing
        class MockRAGSystem:
            def _chunk_document(self, doc):
                return [
                    {"id": "test", "content": doc.content, "metadata": doc.metadata}
                ]

            async def _add_chunks_to_collection(self, chunks):
                print(f"Added {len(chunks)} chunks to collection")

        mock_rag = MockRAGSystem()
        indexer = EnhancedSDKIndexer(mock_rag)

        # Test indexing
        results = await indexer.index_all_sdks()
        print("Indexing Results:")
        for platform, count in results.items():
            print(f"  {platform}: {count} documents")

        total_docs = sum(results.values())
        print(f"\nTotal documents indexed: {total_docs}")

    asyncio.run(test_indexer())
