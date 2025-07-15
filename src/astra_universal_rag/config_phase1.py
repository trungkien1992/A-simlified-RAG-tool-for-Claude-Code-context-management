#!/usr/bin/env python3
"""
Configuration updates for Phase 1 - Hybrid Architecture
"""

from pydantic import Field
from pydantic_settings import BaseSettings
from pathlib import Path
from .config import RAGSettings


class Phase1Settings(RAGSettings):
    """Extended settings for Phase 1 hybrid architecture"""
    
    # Neo4j Configuration
    neo4j_uri: str = Field(
        default="bolt://localhost:7687",
        description="Neo4j connection URI"
    )
    neo4j_username: str = Field(
        default="neo4j",
        description="Neo4j username"
    )
    neo4j_password: str = Field(
        description="Neo4j password",
        default=""
    )
    
    # Hybrid Search Configuration
    hybrid_search_enabled: bool = Field(
        default=True,
        description="Enable hybrid graph-vector search"
    )
    max_graph_traversal_depth: int = Field(
        default=3,
        description="Maximum depth for graph traversal"
    )
    graph_weight: float = Field(
        default=0.3,
        description="Weight for graph results in hybrid search (0-1)"
    )
    vector_weight: float = Field(
        default=0.7,
        description="Weight for vector results in hybrid search (0-1)"
    )
    
    # Phase 1 Feature Flags
    dual_pipeline_ingestion: bool = Field(default=True)
    graph_relationship_extraction: bool = Field(default=True)
    hybrid_retrieval: bool = Field(default=True)


# Create phase 1 settings instance
phase1_settings = Phase1Settings()
