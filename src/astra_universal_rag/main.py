#!/usr/bin/env python3
"""
Universal RAG Backend
High-performance Python-based RAG service for multi-platform knowledge bases
Integrates Extended Exchange API, X10 Python SDK, Starknet.dart SDK, and Cairo documentation

RAGFlow-inspired features:
- Deep document understanding
- Template-based chunking
- Grounded citations with reduced hallucinations
- Multi-modal content support
- Advanced search capabilities
"""

import time
import logging
import uuid
from typing import Dict, Any
from datetime import datetime
from chromadb.utils import embedding_functions
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pydantic import BaseModel

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Local imports
from .config import RAG_CONFIG, settings
from .models import QueryRequest, QueryResponse, IndexRequest, StatsResponse
from .rag_system import AstraRAG
from .security import get_api_key
from .optimization_manager import RAGOptimizationManager

# Phase 3: Proactive Context System
try:
    from .proactive_context_engine import ProactiveContextEngine, ContextRequest
    from .predictive_analysis import PredictiveAnalyzer

    PROACTIVE_AVAILABLE = True
except ImportError:
    PROACTIVE_AVAILABLE = False
    print(
        "Warning: Proactive context modules not found. Phase 3 functionality disabled."
    )

# Enhanced categorization and indexing
try:
    from .categorization_system import (
        categorize_document,
        get_all_categories,
        get_all_platforms,
    )

    from .optimization_manager import (
        RAGOptimizationManager,
        optimize_rag_system,
        get_rag_health,
    )
except ImportError:
    print("Warning: Some advanced modules not found. Using basic functionality.")

    def categorize_document(x):
        return {"category": "general", "subcategory": "document"}

    def get_all_categories():
        return ["general", "api", "trading", "blockchain"]

    def get_all_platforms():
        return [
            "extended_exchange",
            "x10_python",
            "starknet_dart",
            "cairo",
        ]


# Claude Code enhancements
from .code_aware_chunker import CodeAwareChunker, CodeChunk
from .claude_search import ClaudeOptimizedSearch, ClaudeSearchAnalytics

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI application
app = FastAPI(
    title="Universal RAG API",
    description="High-performance RAG service for multi-platform knowledge bases",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag_system = AstraRAG()

# Initialize Claude Code enhancements
code_chunker = None
claude_search = None
search_analytics = ClaudeSearchAnalytics()

# Initialize Phase 3: Proactive Context System
proactive_engine = None
predictive_analyzer = None

optimization_manager = RAGOptimizationManager()

# Task management system for asynchronous operations
tasks = {}


@app.on_event("startup")
async def startup_event():
    """Initialize RAG system on startup"""
    await rag_system.initialize()

    # Initialize Claude Code enhancements
    global code_chunker, claude_search, proactive_engine, predictive_analyzer
    code_chunker = CodeAwareChunker(RAG_CONFIG)
    claude_search = ClaudeOptimizedSearch(
        rag_system, rag_system.collection, code_chunker
    )

    # Initialize Phase 3: Proactive Context System
    if PROACTIVE_AVAILABLE:
        proactive_engine = ProactiveContextEngine(rag_system)
        predictive_analyzer = PredictiveAnalyzer(rag_system)
        await proactive_engine.initialize()
        print("✅ Phase 3: Proactive Context System initialized")

    print("✅ Claude Code enhancements initialized")


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {"service": "Universal RAG API", "version": "1.0.0", "status": "running"}


@app.post("/index", response_model=Dict[str, Any], dependencies=[Depends(get_api_key)])
async def index_documentation(request: IndexRequest, background_tasks: BackgroundTasks):
    """Index SDK documentation - Requires API key"""
    task_id = str(uuid.uuid4())
    tasks[task_id] = {
        "status": "in_progress",
        "start_time": time.time(),
        "operation": "index_documentation",
        "force_reindex": request.force_reindex,
    }

    background_tasks.add_task(run_index_task, task_id, request.force_reindex)
    return {
        "task_id": task_id,
        "status": "started",
        "message": "Indexing task started. Use /status/{task_id} to check progress.",
    }


@app.post("/search", response_model=QueryResponse)
async def search_knowledge_base(request: QueryRequest):
    """Search the knowledge base"""
    result = await rag_system.search(
        query=request.query,
        max_results=request.max_results,
        category=request.category,
        min_similarity=request.min_similarity,
    )

    return QueryResponse(
        results=result["results"],
        query_time=result["query_time"],
        total_results=result["total_results"],
    )


@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Get knowledge base statistics"""
    stats = rag_system.get_stats()
    return StatsResponse(
        total_documents=stats["total_documents"],
        categories=stats["categories"],
        last_updated=stats["last_updated"],
        embedding_model=stats["embedding_model"],
    )


@app.get("/categories")
async def get_categories():
    """Get all available categories from the enhanced categorization system"""
    return {
        "categories": get_all_categories(),
        "platforms": get_all_platforms(),
        "current_stats": rag_system.get_stats()["categories"],
    }


@app.get("/platforms")
async def get_platforms():
    """Get all available platforms"""
    return {"platforms": get_all_platforms()}


@app.post("/search/advanced")
async def advanced_search(request: QueryRequest):
    """Advanced search with enhanced filtering"""
    result = await rag_system.search(
        query=request.query,
        max_results=request.max_results,
        category=request.category,
        min_similarity=request.min_similarity,
    )

    # Add enhanced metadata to results
    enhanced_results = []
    for doc in result["results"]:
        enhanced_doc = doc.copy()
        enhanced_doc["enhanced_metadata"] = {
            "platform": enhanced_doc.get("metadata", {}).get("platform", "unknown"),
            "doc_type": enhanced_doc.get("metadata", {}).get("doc_type", "unknown"),
            "importance": enhanced_doc.get("metadata", {}).get("importance", "medium"),
            "complexity": enhanced_doc.get("metadata", {}).get(
                "complexity", "intermediate"
            ),
            "tags": enhanced_doc.get("metadata", {}).get("tags", []),
        }
        enhanced_results.append(enhanced_doc)

    return QueryResponse(
        results=enhanced_results,
        query_time=result["query_time"],
        total_results=result["total_results"],
    )


@app.get("/search/suggestions")
async def get_search_suggestions(query: str = ""):
    """Get intelligent search suggestions"""
    if not query:
        return {
            "suggestions": [
                "How to create account",
                "Trading API authentication",
                "Place order with X10 SDK",
                "Cairo smart contract deployment",
                "WebSocket market data",
                "NFT marketplace example",
                "Error handling best practices",
                "Starknet.dart mobile integration",
            ]
        }

    # Generate contextual suggestions based on query
    suggestions = []
    query_lower = query.lower()

    if "account" in query_lower:
        suggestions.extend(
            [
                "Create account with X10 SDK",
                "Account management Starknet.dart",
                "Deploy account Cairo contract",
                "Account authentication Extended Exchange",
            ]
        )
    elif "order" in query_lower:
        suggestions.extend(
            [
                "Place limit order",
                "Cancel order API",
                "Order types Extended Exchange",
                "Order management best practices",
            ]
        )
    elif "contract" in query_lower:
        suggestions.extend(
            [
                "Deploy Cairo smart contract",
                "ERC20 token contract",
                "Contract testing with Forge",
                "OpenZeppelin contracts",
            ]
        )
    else:
        suggestions.extend(
            [
                f"{query} tutorial",
                f"{query} example",
                f"{query} API reference",
                f"How to {query}",
            ]
        )

    return {"suggestions": suggestions[:8]}


@app.post("/optimize", dependencies=[Depends(get_api_key)])
async def optimize_system(background_tasks: BackgroundTasks):
    """Trigger system optimization - Requires API key"""
    task_id = str(uuid.uuid4())
    tasks[task_id] = {
        "status": "in_progress",
        "start_time": time.time(),
        "operation": "optimize_system",
    }

    background_tasks.add_task(run_optimize_task, task_id)
    return {
        "task_id": task_id,
        "status": "started",
        "message": "Optimization task started. Use /status/{task_id} to check progress.",
    }


@app.get("/health/detailed")
async def get_detailed_health():
    """Get detailed system health report"""
    try:
        health_report = await get_rag_health(
            rag_system.chroma_client, RAG_CONFIG["collection_name"]
        )
        return health_report
    except Exception as e:
        return {"status": "error", "message": f"Health check failed: {str(e)}"}


@app.get("/metrics")
async def get_system_metrics():
    """Get comprehensive system metrics"""
    stats = rag_system.get_stats()

    # Get platform breakdown
    platform_stats = {}
    if rag_system.collection:
        results = rag_system.collection.get(include=["metadatas"])
        metadatas = results["metadatas"] if results["metadatas"] else []

        for metadata in metadatas:
            platform = metadata.get("platform", "unknown")
            platform_stats[platform] = platform_stats.get(platform, 0) + 1

    return {
        "total_documents": stats["total_documents"],
        "categories": stats["categories"],
        "platform_breakdown": platform_stats,
        "embedding_model": stats["embedding_model"],
        "last_updated": stats["last_updated"],
        "available_platforms": get_all_platforms(),
        "available_categories": get_all_categories(),
    }


# Claude Code Enhancement Endpoints


@app.post("/search/claude")
async def search_for_claude_code(request: QueryRequest):
    """Claude-optimized search endpoint with larger context and intelligent chunking"""
    if not claude_search:
        raise HTTPException(status_code=503, detail="Claude search not initialized")

    _ = time.time()  # Fixed F841

    try:
        result = await claude_search.search_for_claude(
            query=request.query,
            context_type=request.category or "development",
            max_context_size=RAG_CONFIG["claude_context_size"],
        )

        # Log search for analytics
        search_analytics.log_search(
            query=request.query,
            intent=result.query_type,
            results_count=len(result.results),
            search_time=result.search_time,
        )

        return {
            "results": result.results,
            "total_context_size": result.total_context_size,
            "query_type": result.query_type,
            "related_files": result.related_files,
            "cross_references": result.cross_references,
            "development_context": result.development_context,
            "search_time": result.search_time,
            "optimized_for": "claude_code_sonnet_4",
            "enhancement_status": "active",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Claude search failed: {str(e)}")


@app.post("/index/code_aware")
async def index_with_code_awareness(background_tasks: BackgroundTasks):
    """Re-index with code-aware chunking for better Claude context"""
    if not code_chunker:
        raise HTTPException(status_code=503, detail="Code chunker not initialized")

    task_id = str(uuid.uuid4())
    tasks[task_id] = {
        "status": "in_progress",
        "start_time": time.time(),
        "operation": "code_aware_indexing",
    }

    background_tasks.add_task(run_code_aware_indexing_task, task_id)
    return {
        "task_id": task_id,
        "status": "started",
        "message": "Code-aware indexing initiated. Use /status/{task_id} to check progress.",
        "enhancement": "claude_code_chunking",
        "expected_improvements": [
            "4x larger chunk sizes",
            "Language-specific parsing",
            "Preserved code structure",
            "Better function/class grouping",
        ],
    }


@app.get("/claude/status")
async def get_claude_optimization_status():
    """Get status of Claude Code optimizations"""
    return {
        "claude_enhancements": {
            "chunk_size": RAG_CONFIG["chunk_size"],
            "claude_context_size": RAG_CONFIG["claude_context_size"],
            "code_aware_chunking": RAG_CONFIG["code_aware_chunking"],
            "max_results": RAG_CONFIG["max_results"],
        },
        "components_initialized": {
            "code_chunker": code_chunker is not None,
            "claude_search": claude_search is not None,
            "search_analytics": True,
        },
        "usage_analytics": search_analytics.get_insights(),
        "optimization_level": "high_performance",
        "target_model": "claude_sonnet_4",
    }


@app.get("/claude/analytics")
async def get_claude_analytics():
    """Get Claude Code usage analytics and insights"""
    return {
        "analytics": search_analytics.get_insights(),
        "system_performance": {
            "average_context_size": RAG_CONFIG["claude_context_size"],
            "chunk_overlap": RAG_CONFIG["chunk_overlap"],
            "supported_languages": [
                "python",
                "dart",
                "cairo",
                "markdown",
                "json",
                "yaml",
            ],
        },
        "optimization_suggestions": [
            "Use specific file paths in queries for better context",
            "Include intent keywords (debug, feature, refactor, test)",
            "Combine related concepts in single queries",
            "Use technical terminology for better matching",
        ],
    }


@app.post("/claude/suggest_files")
async def suggest_files_for_query(request: QueryRequest):
    """Get file suggestions based on query and development intent"""
    if not claude_search:
        raise HTTPException(status_code=503, detail="Claude search not initialized")

    intent = claude_search._analyze_query_intent(request.query)
    keywords = claude_search._extract_technical_keywords(request.query)

    suggestions = await claude_search.get_file_suggestions(request.query, intent)

    return {
        "query": request.query,
        "detected_intent": intent,
        "keywords": keywords,
        "suggested_files": suggestions,
        "search_strategy": f"Optimized for {intent} workflow",
        "next_steps": [
            f"Search for specific files: {', '.join(suggestions[:3])}",
            f"Use intent-specific keywords: {intent}",
            "Include file extensions for precise matching",
        ],
    }


@app.get("/status/{task_id}")
async def get_task_status(task_id: str):
    """Get the status of a background task"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    task = tasks[task_id]
    response = {
        "task_id": task_id,
        "status": task["status"],
        "operation": task["operation"],
        "start_time": task["start_time"],
    }

    if task["status"] == "completed":
        response.update(
            {
                "end_time": task["end_time"],
                "time_taken": task["time_taken"],
                "result": task.get("result", {}),
            }
        )
        if "documents_indexed" in task:
            response["documents_indexed"] = task["documents_indexed"]

    elif task["status"] == "failed":
        response.update({"end_time": task["end_time"], "error": task["error"]})

    return response


# Phase 3: Proactive Context Endpoints


@app.post("/context/proactive")
async def proactive_context_injection(request: Dict[str, Any]):
    """
    Phase 3: Real-time proactive context injection endpoint
    Receives editor events and provides intelligent context before the developer asks
    """
    if not PROACTIVE_AVAILABLE or not proactive_engine:
        raise HTTPException(
            status_code=503,
            detail="Proactive context system not available. Please ensure Phase 3 modules are installed.",
        )

    try:
        # Extract event information from request
        event_type = request.get("event_type", "unknown")
        filepath = request.get("filepath", "")
        developer_id = request.get("developer_id", "anonymous")
        cursor_position = request.get("cursor_position", {})
        function_name = request.get("function_name", "")
        class_name = request.get("class_name", "")

        # Validate required fields
        if not filepath:
            raise HTTPException(status_code=400, detail="filepath is required")

        # Create context request
        context_request = ContextRequest(
            event_type=event_type,
            filepath=filepath,
            developer_id=developer_id,
            cursor_position=cursor_position,
            function_name=function_name,
            class_name=class_name,
        )

        # Get proactive context using Dynamic Context Assembly Engine
        context_package = await proactive_engine.get_proactive_context(context_request)

        # Enhance with predictive analysis
        predictive_insights = await predictive_analyzer.analyze_developer_intent(
            context_request
        )

        # Combine everything into a comprehensive response
        response = {
            "timestamp": datetime.now().isoformat(),
            "event_processed": {
                "type": event_type,
                "file": filepath,
                "developer": developer_id,
                "function": function_name,
                "class": class_name,
            },
            "context_package": context_package,
            "predictive_insights": predictive_insights,
            "proactive_level": "god_mode_phase3",
            "assembly_time": context_package.get("assembly_time", 0),
            "prediction_time": predictive_insights.get("analysis_time", 0),
        }

        # Log the proactive context event for analytics
        await proactive_engine.log_context_event(context_request, response)

        return response

    except Exception as e:
        logger.error(f"Proactive context injection failed: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to generate proactive context: {str(e)}"
        )


@app.get("/context/proactive/stats")
async def get_proactive_context_stats():
    """Get statistics about proactive context system usage"""
    if not PROACTIVE_AVAILABLE or not proactive_engine:
        raise HTTPException(
            status_code=503, detail="Proactive context system not available"
        )

    stats = await proactive_engine.get_usage_stats()
    prediction_stats = await predictive_analyzer.get_prediction_accuracy()

    return {
        "proactive_context_stats": stats,
        "prediction_accuracy": prediction_stats,
        "system_status": "operational",
        "phase": "god_mode_phase3",
        "features": [
            "Real-time context injection",
            "Graph-aware context assembly",
            "Predictive developer intent analysis",
            "Impact analysis and blast radius",
            "Cross-file relationship tracking",
            "Ambient awareness system",
        ],
    }


class ContextFeedback(BaseModel):
    session_id: str
    developer_id: str
    task_id: str
    rating: float  # e.g., a score from 0.0 to 1.0
    feedback_notes: str = ""


@app.post("/context/feedback")
async def receive_context_feedback(feedback: ContextFeedback):
    optimization_manager.log_feedback(feedback)
    return {"status": "feedback received"}


# Background task functions


async def run_index_task(task_id: str, force_reindex: bool):
    """Background task for indexing with task status tracking"""
    try:
        start_time = time.time()
        result = await rag_system.index_astratrade_documentation(force_reindex)
        end_time = time.time()

        tasks[task_id].update(
            {
                "status": "completed",
                "end_time": end_time,
                "time_taken": end_time - start_time,
                "documents_indexed": result.get("documents_indexed", 0),
                "result": result,
            }
        )

    except Exception as e:
        tasks[task_id].update(
            {"status": "failed", "end_time": time.time(), "error": str(e)}
        )


async def run_optimize_task(task_id: str):
    """Background task for optimization with task status tracking"""
    try:
        start_time = time.time()
        result = await optimize_rag_system(
            rag_system.chroma_client, settings.collection_name
        )
        end_time = time.time()

        tasks[task_id].update(
            {
                "status": "completed",
                "end_time": end_time,
                "time_taken": end_time - start_time,
                "result": result,
            }
        )

    except Exception as e:
        tasks[task_id].update(
            {"status": "failed", "end_time": time.time(), "error": str(e)}
        )


async def run_code_aware_indexing_task(task_id: str):
    """Background task for code-aware indexing with task status tracking"""
    try:
        start_time = time.time()
        result = await reindex_with_code_aware_chunking()
        end_time = time.time()

        tasks[task_id].update(
            {
                "status": "completed",
                "end_time": end_time,
                "time_taken": end_time - start_time,
                "result": result,
            }
        )

    except Exception as e:
        tasks[task_id].update(
            {"status": "failed", "end_time": time.time(), "error": str(e)}
        )


async def reindex_with_code_aware_chunking():
    """Background task to re-index the collection with code-aware chunking"""
    try:
        print("🔄 Starting code-aware re-indexing...")

        # Get all existing documents
        existing_docs = rag_system.collection.get(include=["documents", "metadatas"])

        if not existing_docs["documents"]:
            print("⚠️ No documents found to re-index")
            return

        # Clear collection for fresh indexing
        rag_system.collection.delete()

        # Re-create collection
        embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=RAG_CONFIG["embedding_model"]
        )
        rag_system.collection = rag_system.chroma_client.create_collection(
            name=RAG_CONFIG["collection_name"],
            embedding_function=embedding_function,
            metadata={
                "description": "Code-aware chunked knowledge base for Claude Code"
            },
        )

        total_docs = 0

        # Process each document with code-aware chunking
        for i, (doc_content, metadata) in enumerate(
            zip(existing_docs["documents"], existing_docs["metadatas"])
        ):
            file_path = metadata.get("file_path", f"document_{i}")

            # Use code-aware chunking
            if code_chunker:
                chunks = code_chunker.chunk_for_claude_context(file_path, doc_content)
            else:
                # Fallback to larger standard chunks
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=RAG_CONFIG["chunk_size"],
                    chunk_overlap=RAG_CONFIG["chunk_overlap"],
                )
                chunk_texts = text_splitter.split_text(doc_content)
                chunks = [
                    CodeChunk(
                        content=chunk_text,
                        metadata=metadata,
                        start_line=1,
                        end_line=len(chunk_text.split("\n")),
                        chunk_type="generic",
                        language="unknown",
                    )
                    for chunk_text in chunk_texts
                ]

            # Add chunks to collection
            for j, chunk in enumerate(chunks):
                chunk_id = f"code_aware_{i}_{j}"

                # Enhance metadata with code-aware information
                enhanced_metadata = {
                    **metadata,
                    "chunk_id": chunk_id,
                    "chunk_type": chunk.chunk_type,
                    "language": chunk.language,
                    "importance": chunk.importance,
                    "start_line": chunk.start_line,
                    "end_line": chunk.end_line,
                    "claude_optimized": True,
                    "chunk_size": len(chunk.content),
                }

                rag_system.collection.add(
                    ids=[chunk_id],
                    documents=[chunk.content],
                    metadatas=[enhanced_metadata],
                )

                total_docs += 1

        print(f"✅ Code-aware re-indexing completed: {total_docs} chunks indexed")
        return {"status": "completed", "total_chunks": total_docs}

    except Exception as e:
        print(f"❌ Code-aware re-indexing failed: {e}")
        return {"status": "failed", "error": str(e)}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
