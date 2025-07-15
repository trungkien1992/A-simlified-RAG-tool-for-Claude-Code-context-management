#!/usr/bin/env python3
"""
Pydantic models and data structures for Astra RAG system
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from pydantic import BaseModel


# Request models
class QueryRequest(BaseModel):
    query: str
    max_results: Optional[int] = 5
    category: Optional[str] = None
    min_similarity: Optional[float] = 0.6


class IndexRequest(BaseModel):
    force_reindex: bool = False


# Response models
class QueryResponse(BaseModel):
    results: List[Dict[str, Any]]
    query_time: float
    total_results: int


class IndexResponse(BaseModel):
    status: str
    documents_indexed: int
    time_taken: float


class StatsResponse(BaseModel):
    total_documents: int
    categories: Dict[str, int]
    last_updated: str
    embedding_model: str


# Data classes
@dataclass
class ProcessedDocument:
    content: str
    title: str
    category: str
    subcategory: Optional[str]
    metadata: Dict[str, Any]
    source_url: Optional[str] = None
    file_path: Optional[str] = None
