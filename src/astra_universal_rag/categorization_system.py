#!/usr/bin/env python3
"""
Enhanced Categorization System
Multi-platform categorization for trading platforms and blockchain documentation
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class DocumentCategory(Enum):
    """Document categories for any project"""

    # Trading Platform Categories
    TRADING_API = "trading_api"
    MARKET_DATA = "market_data"
    ORDER_MANAGEMENT = "order_management"
    ACCOUNT_MANAGEMENT = "account_management"
    AUTHENTICATION = "authentication"

    # Blockchain Categories
    SMART_CONTRACT = "smart_contract"
    CAIRO_LANG = "cairo_lang"
    STARKNET = "starknet"
    PAYMASTER = "paymaster"
    WALLET_INTEGRATION = "wallet_integration"

    # SDK Categories
    PYTHON_SDK = "python_sdk"
    DART_SDK = "dart_sdk"
    FLUTTER_SDK = "flutter_sdk"
    WEB3_SDK = "web3_sdk"

    # Documentation Categories
    API_REFERENCE = "api_reference"
    TUTORIAL = "tutorial"
    EXAMPLE_CODE = "example_code"
    CONFIGURATION = "configuration"
    TROUBLESHOOTING = "troubleshooting"

    # General Categories
    OVERVIEW = "overview"
    GETTING_STARTED = "getting_started"
    BEST_PRACTICES = "best_practices"
    SECURITY = "security"
    GENERAL = "general"


class PlatformType(Enum):
    """Supported platforms in any project"""

    EXTENDED_EXCHANGE = "extended_exchange"
    X10_PYTHON_SDK = "x10_python_sdk"
    STARKNET_DART = "starknet_dart"
    CAIRO_LANG = "cairo_lang"
    AVNU_PAYMASTER = "avnu_paymaster"
    WEB3AUTH = "web3auth"
    CHIPI_PAY = "chipi_pay"
    UNKNOWN = "unknown"


@dataclass
class CategoryResult:
    """Result of document categorization"""

    category: DocumentCategory
    subcategory: Optional[str]
    platform: PlatformType
    confidence: float
    keywords: List[str]
    importance: str  # 'critical', 'high', 'medium', 'low'
    doc_type: str  # 'api', 'tutorial', 'reference', 'example'
    tags: List[str]


class DocumentCategorizer:
    """Enhanced categorization system for multi-platform documentation"""

    def __init__(self):
        self.platform_keywords = self._build_platform_keywords()
        self.category_patterns = self._build_category_patterns()
        self.technical_keywords = self._build_technical_keywords()
        self.importance_indicators = self._build_importance_indicators()

    def _build_platform_keywords(self) -> Dict[PlatformType, List[str]]:
        """Build platform-specific keywords for identification"""
        return {
            PlatformType.EXTENDED_EXCHANGE: [
                "extended exchange",
                "trading api",
                "market data",
                "order book",
                "spot trading",
                "futures",
                "perpetual",
                "derivatives",
                "trading pairs",
                "klines",
                "candlestick",
                "ticker",
                "depth",
                "trades",
                "order history",
            ],
            PlatformType.X10_PYTHON_SDK: [
                "x10 python",
                "python sdk",
                "trading client",
                "api client",
                "python trading",
                "rest api",
                "websocket",
                "authentication",
                "order placement",
                "account info",
                "balance",
                "positions",
            ],
            PlatformType.STARKNET_DART: [
                "starknet dart",
                "dart sdk",
                "flutter",
                "mobile",
                "wallet",
                "cairo contract",
                "felt",
                "account",
                "provider",
                "signer",
                "invoke",
                "declare",
                "deploy",
                "transaction",
                "calldata",
            ],
            PlatformType.CAIRO_LANG: [
                "cairo",
                "cairo lang",
                "smart contract",
                "felt252",
                "starknet",
                "contract",
                "storage",
                "event",
                "interface",
                "trait",
                "impl",
                "constructor",
                "external",
                "view",
                "scarb",
                "sierra",
            ],
            PlatformType.AVNU_PAYMASTER: [
                "avnu",
                "paymaster",
                "gas",
                "fee",
                "sponsored",
                "transaction",
                "starknet paymaster",
                "account abstraction",
                "user operations",
                "gasless",
                "meta transaction",
                "fee sponsorship",
            ],
            PlatformType.WEB3AUTH: [
                "web3auth",
                "authentication",
                "oauth",
                "social login",
                "wallet",
                "private key",
                "mpc",
                "tss",
                "custody",
                "key management",
                "multi factor",
                "biometric",
                "social recovery",
            ],
            PlatformType.CHIPI_PAY: [
                "chipi pay",
                "payment",
                "gateway",
                "checkout",
                "crypto payment",
                "fiat",
                "conversion",
                "settlement",
                "merchant",
                "invoice",
                "payment processing",
                "transaction fee",
                "payout",
            ],
        }

    def _build_category_patterns(self) -> Dict[DocumentCategory, List[str]]:
        """Build category-specific patterns"""
        return {
            DocumentCategory.TRADING_API: [
                "trading api",
                "place order",
                "cancel order",
                "order status",
                "market order",
                "limit order",
                "stop order",
                "trading endpoint",
                "order book",
                "trade history",
                "execution report",
            ],
            DocumentCategory.MARKET_DATA: [
                "market data",
                "price feed",
                "ticker",
                "kline",
                "candlestick",
                "depth",
                "order book",
                "trade stream",
                "price history",
                "ohlcv",
                "volume",
                "market stats",
                "24hr ticker",
            ],
            DocumentCategory.ORDER_MANAGEMENT: [
                "order management",
                "order lifecycle",
                "order types",
                "order routing",
                "order execution",
                "fill",
                "partial fill",
                "order book management",
                "order matching",
                "order priority",
                "order validation",
            ],
            DocumentCategory.ACCOUNT_MANAGEMENT: [
                "account",
                "balance",
                "portfolio",
                "positions",
                "margin",
                "account info",
                "account history",
                "asset management",
                "account settings",
                "profile",
                "kyc",
                "verification",
            ],
            DocumentCategory.AUTHENTICATION: [
                "authentication",
                "api key",
                "signature",
                "hmac",
                "oauth",
                "jwt",
                "token",
                "login",
                "logout",
                "session",
                "security",
                "authorization",
                "access control",
                "credentials",
            ],
            DocumentCategory.SMART_CONTRACT: [
                "smart contract",
                "contract",
                "cairo contract",
                "erc20",
                "erc721",
                "nft",
                "defi",
                "dapp",
                "blockchain",
                "deploy",
                "invoke",
                "call",
                "transaction",
                "event",
                "storage",
            ],
            DocumentCategory.CAIRO_LANG: [
                "cairo",
                "cairo language",
                "felt252",
                "array",
                "struct",
                "enum",
                "trait",
                "impl",
                "constructor",
                "external",
                "view",
                "storage",
                "event",
                "interface",
                "sierra",
                "scarb",
            ],
            DocumentCategory.STARKNET: [
                "starknet",
                "layer 2",
                "zk rollup",
                "cairo vm",
                "sequencer",
                "prover",
                "merkle tree",
                "commitment",
                "state",
                "block",
                "transaction hash",
                "class hash",
                "contract address",
            ],
            DocumentCategory.PAYMASTER: [
                "paymaster",
                "gas",
                "fee",
                "sponsored transaction",
                "gasless",
                "account abstraction",
                "user operation",
                "meta transaction",
                "fee sponsorship",
                "gas optimization",
                "transaction cost",
            ],
            DocumentCategory.WALLET_INTEGRATION: [
                "wallet",
                "wallet connect",
                "metamask",
                "argent",
                "braavos",
                "wallet integration",
                "connect wallet",
                "sign transaction",
                "wallet adapter",
                "web3 wallet",
                "mobile wallet",
            ],
            DocumentCategory.PYTHON_SDK: [
                "python sdk",
                "python client",
                "python api",
                "pip install",
                "import",
                "class",
                "method",
                "function",
                "python example",
                "async",
                "await",
                "requests",
                "httpx",
                "aiohttp",
            ],
            DocumentCategory.DART_SDK: [
                "dart sdk",
                "flutter",
                "dart",
                "pubspec",
                "package",
                "import",
                "class",
                "method",
                "async",
                "await",
                "future",
                "stream",
                "widget",
                "stateful",
                "stateless",
            ],
            DocumentCategory.FLUTTER_SDK: [
                "flutter",
                "flutter sdk",
                "widget",
                "stateful widget",
                "stateless widget",
                "build context",
                "state management",
                "provider",
                "riverpod",
                "bloc",
                "cubit",
                "navigator",
            ],
            DocumentCategory.WEB3_SDK: [
                "web3",
                "web3 sdk",
                "ethereum",
                "blockchain",
                "dapp",
                "smart contract",
                "abi",
                "bytecode",
                "gas",
                "gwei",
                "transaction",
                "block",
                "event",
                "filter",
                "provider",
            ],
            DocumentCategory.API_REFERENCE: [
                "api reference",
                "endpoint",
                "parameter",
                "response",
                "request",
                "method",
                "header",
                "status code",
                "error code",
                "schema",
                "swagger",
                "openapi",
                "postman",
                "curl",
            ],
            DocumentCategory.TUTORIAL: [
                "tutorial",
                "guide",
                "walkthrough",
                "step by step",
                "how to",
                "getting started",
                "quickstart",
                "beginner",
                "example",
                "sample",
                "demo",
                "hands on",
                "learn",
            ],
            DocumentCategory.EXAMPLE_CODE: [
                "example",
                "sample",
                "demo",
                "code example",
                "snippet",
                "implementation",
                "use case",
                "scenario",
                "practical",
                "working example",
                "template",
                "boilerplate",
            ],
            DocumentCategory.CONFIGURATION: [
                "configuration",
                "config",
                "settings",
                "environment",
                "env",
                "setup",
                "installation",
                "deployment",
                "build",
                "compile",
                "package",
                "dependency",
                "requirement",
                "version",
            ],
            DocumentCategory.TROUBLESHOOTING: [
                "troubleshooting",
                "error",
                "issue",
                "problem",
                "bug",
                "fix",
                "solution",
                "debug",
                "diagnostic",
                "common issues",
                "faq",
                "known issues",
                "workaround",
                "resolution",
            ],
        }

    def _build_technical_keywords(self) -> Dict[str, List[str]]:
        """Build technical keywords for better categorization"""
        return {
            "trading": [
                "order",
                "trade",
                "price",
                "volume",
                "market",
                "exchange",
                "buy",
                "sell",
                "bid",
                "ask",
                "spread",
                "liquidity",
                "slippage",
            ],
            "blockchain": [
                "block",
                "hash",
                "transaction",
                "address",
                "signature",
                "gas",
                "fee",
                "consensus",
                "mining",
                "validator",
                "node",
                "peer",
            ],
            "api": [
                "endpoint",
                "request",
                "response",
                "header",
                "body",
                "parameter",
                "query",
                "path",
                "method",
                "status",
                "error",
                "authentication",
            ],
            "sdk": [
                "library",
                "package",
                "module",
                "class",
                "method",
                "function",
                "import",
                "export",
                "interface",
                "type",
                "generic",
                "async",
            ],
            "security": [
                "encryption",
                "decryption",
                "key",
                "certificate",
                "ssl",
                "tls",
                "hash",
                "signature",
                "verification",
                "authorization",
                "permission",
            ],
        }

    def _build_importance_indicators(self) -> Dict[str, List[str]]:
        """Build importance indicators for content priority"""
        return {
            "critical": [
                "breaking change",
                "security",
                "vulnerability",
                "critical",
                "urgent",
                "important",
                "deprecated",
                "migration",
                "upgrade",
            ],
            "high": [
                "new feature",
                "enhancement",
                "improvement",
                "optimization",
                "performance",
                "best practice",
                "recommended",
                "important",
            ],
            "medium": [
                "example",
                "tutorial",
                "guide",
                "reference",
                "documentation",
                "sample",
                "demo",
                "walkthrough",
                "how to",
            ],
            "low": [
                "note",
                "tip",
                "info",
                "additional",
                "optional",
                "advanced",
                "experimental",
                "beta",
                "preview",
                "draft",
            ],
        }

    def categorize_document(
        self, content: str, file_path: str = "", metadata: Dict[str, Any] = None
    ) -> CategoryResult:
        """Categorize a document based on content and metadata"""

        content_lower = content.lower()
        file_path_lower = file_path.lower()

        # Detect platform
        platform = self._detect_platform(content_lower, file_path_lower)

        # Detect category
        category = self._detect_category(content_lower, file_path_lower)

        # Detect subcategory
        subcategory = self._detect_subcategory(content_lower, category, platform)

        # Calculate confidence
        confidence = self._calculate_confidence(content_lower, category, platform)

        # Extract keywords
        keywords = self._extract_keywords(content_lower, category, platform)

        # Determine importance
        importance = self._determine_importance(content_lower, file_path_lower)

        # Determine document type
        doc_type = self._determine_doc_type(content_lower, file_path_lower)

        # Generate tags
        tags = self._generate_tags(content_lower, category, platform)

        return CategoryResult(
            category=category,
            subcategory=subcategory,
            platform=platform,
            confidence=confidence,
            keywords=keywords,
            importance=importance,
            doc_type=doc_type,
            tags=tags,
        )

    def _detect_platform(self, content: str, file_path: str) -> PlatformType:
        """Detect the platform based on content and file path"""

        platform_scores = {}

        # Check file path for platform indicators
        for platform, keywords in self.platform_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in file_path:
                    score += 2  # File path matches are more reliable
                if keyword in content:
                    score += 1
            platform_scores[platform] = score

        # Return platform with highest score
        if platform_scores:
            best_platform = max(platform_scores, key=platform_scores.get)
            if platform_scores[best_platform] > 0:
                return best_platform

        return PlatformType.UNKNOWN

    def _detect_category(self, content: str, file_path: str) -> DocumentCategory:
        """Detect the category based on content"""

        category_scores = {}

        # Check against category patterns
        for category, patterns in self.category_patterns.items():
            score = 0
            for pattern in patterns:
                if pattern in content:
                    score += 1
                if pattern in file_path:
                    score += 2
            category_scores[category] = score

        # Return category with highest score
        if category_scores:
            best_category = max(category_scores, key=category_scores.get)
            if category_scores[best_category] > 0:
                return best_category

        return DocumentCategory.GENERAL

    def _detect_subcategory(
        self, content: str, category: DocumentCategory, platform: PlatformType
    ) -> Optional[str]:
        """Detect subcategory based on category and platform"""

        subcategory_patterns = {
            DocumentCategory.TRADING_API: {
                "spot_trading": ["spot", "market order", "limit order"],
                "futures_trading": ["futures", "perpetual", "derivatives"],
                "order_management": ["place order", "cancel order", "order status"],
                "market_data": ["ticker", "kline", "depth", "trades"],
            },
            DocumentCategory.SMART_CONTRACT: {
                "erc20": ["erc20", "token", "transfer", "approve"],
                "erc721": ["erc721", "nft", "mint", "tokenuri"],
                "defi": ["defi", "dex", "swap", "liquidity", "pool"],
                "governance": ["governance", "vote", "proposal", "dao"],
            },
            DocumentCategory.AUTHENTICATION: {
                "api_key": ["api key", "hmac", "signature"],
                "oauth": ["oauth", "oauth2", "authorization code"],
                "jwt": ["jwt", "json web token", "bearer token"],
                "session": ["session", "cookie", "csrf"],
            },
        }

        if category in subcategory_patterns:
            for subcategory, patterns in subcategory_patterns[category].items():
                for pattern in patterns:
                    if pattern in content:
                        return subcategory

        return None

    def _calculate_confidence(
        self, content: str, category: DocumentCategory, platform: PlatformType
    ) -> float:
        """Calculate confidence score for categorization"""

        base_score = 0.5

        # Check category patterns
        category_patterns = self.category_patterns.get(category, [])
        category_matches = sum(1 for pattern in category_patterns if pattern in content)
        category_score = min(category_matches * 0.1, 0.3)

        # Check platform keywords
        platform_keywords = self.platform_keywords.get(platform, [])
        platform_matches = sum(1 for keyword in platform_keywords if keyword in content)
        platform_score = min(platform_matches * 0.05, 0.2)

        # Calculate final confidence
        confidence = base_score + category_score + platform_score
        return min(confidence, 1.0)

    def _extract_keywords(
        self, content: str, category: DocumentCategory, platform: PlatformType
    ) -> List[str]:
        """Extract relevant keywords from content"""

        keywords = []

        # Add category-specific keywords
        if category in self.category_patterns:
            for pattern in self.category_patterns[category]:
                if pattern in content:
                    keywords.append(pattern)

        # Add platform-specific keywords
        if platform in self.platform_keywords:
            for keyword in self.platform_keywords[platform]:
                if keyword in content:
                    keywords.append(keyword)

        # Add technical keywords
        for tech_area, tech_keywords in self.technical_keywords.items():
            for keyword in tech_keywords:
                if keyword in content:
                    keywords.append(keyword)

        return list(set(keywords))  # Remove duplicates

    def _determine_importance(self, content: str, file_path: str) -> str:
        """Determine document importance"""

        for importance, indicators in self.importance_indicators.items():
            for indicator in indicators:
                if indicator in content or indicator in file_path:
                    return importance

        # Default importance based on file path
        if any(term in file_path for term in ["readme", "getting", "start", "intro"]):
            return "high"
        elif any(term in file_path for term in ["example", "tutorial", "guide"]):
            return "medium"
        else:
            return "medium"

    def _determine_doc_type(self, content: str, file_path: str) -> str:
        """Determine document type"""

        if any(term in content for term in ["curl", "endpoint", "response", "request"]):
            return "api"
        elif any(
            term in content for term in ["tutorial", "guide", "walkthrough", "step"]
        ):
            return "tutorial"
        elif any(term in content for term in ["example", "sample", "demo"]):
            return "example"
        elif any(term in content for term in ["reference", "documentation", "spec"]):
            return "reference"
        else:
            return "general"

    def _generate_tags(
        self, content: str, category: DocumentCategory, platform: PlatformType
    ) -> List[str]:
        """Generate tags for the document"""

        tags = []

        # Add category tag
        tags.append(category.value)

        # Add platform tag
        if platform != PlatformType.UNKNOWN:
            tags.append(platform.value)

        # Add technical tags
        technical_tags = {
            "rest_api": ["rest", "api", "endpoint", "http"],
            "websocket": ["websocket", "ws", "real time", "streaming"],
            "authentication": ["auth", "login", "token", "key"],
            "trading": ["order", "trade", "market", "price"],
            "blockchain": ["block", "hash", "transaction", "smart contract"],
            "mobile": ["flutter", "dart", "mobile", "app"],
            "web": ["javascript", "html", "css", "browser"],
            "python": ["python", "pip", "import", "class"],
            "security": ["security", "encryption", "signature", "hash"],
        }

        for tag, keywords in technical_tags.items():
            if any(keyword in content for keyword in keywords):
                tags.append(tag)

        return tags


# Convenience functions for backward compatibility
def categorize_document(
    content: str, file_path: str = "", metadata: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Categorize a document and return result as dictionary"""

    categorizer = DocumentCategorizer()
    result = categorizer.categorize_document(content, file_path, metadata)

    return {
        "category": result.category.value,
        "subcategory": result.subcategory,
        "platform": result.platform.value,
        "confidence": result.confidence,
        "keywords": result.keywords,
        "importance": result.importance,
        "doc_type": result.doc_type,
        "tags": result.tags,
    }


def get_all_categories() -> List[str]:
    """Get all available categories"""
    return [category.value for category in DocumentCategory]


def get_all_platforms() -> List[str]:
    """Get all available platforms"""
    return [
        platform.value for platform in PlatformType if platform != PlatformType.UNKNOWN
    ]


if __name__ == "__main__":
    # Test the categorization system
    sample_content = """
    Extended Exchange Trading API

    This document describes the REST API for trading on Extended Exchange.

    ## Authentication
    All API calls require API key authentication using HMAC-SHA256 signature.

    ## Place Order
    POST /api/v1/order

    Place a new order on the exchange.

    Parameters:
    - symbol: Trading pair (e.g., BTC/USDT)
    - side: buy or sell
    - type: market or limit
    - quantity: Order quantity
    - price: Order price (for limit orders)

    Example:
    curl -X POST "https://api.extended-exchange.com/api/v1/order" \
         -H "X-API-Key: your-api-key" \
         -H "Content-Type: application/json" \
         -d '{"symbol": "BTC/USDT", "side": "buy", "type": "limit", "quantity": 0.1, "price": 50000}'
    """

    result = categorize_document(sample_content, "extended_exchange_api.md")
    print("Categorization Result:")
    print(f"Category: {result['category']}")
    print(f"Subcategory: {result['subcategory']}")
    print(f"Platform: {result['platform']}")
    print(f"Confidence: {result['confidence']:.2f}")
    print(f"Keywords: {result['keywords']}")
    print(f"Importance: {result['importance']}")
    print(f"Doc Type: {result['doc_type']}")
    print(f"Tags: {result['tags']}")
