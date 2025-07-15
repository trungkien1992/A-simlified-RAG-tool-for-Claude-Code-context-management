#!/usr/bin/env python3
"""
Configuration module for Astra RAG system
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

# Define the project root directory, which is two levels up from this file's directory.
PROJECT_ROOT = Path(__file__).parent.parent.parent


class RAGSettings(BaseSettings):
    """
    Astra RAG system settings.
    This model loads settings from a .env file and environment variables.
    """

    # --- Paths and Models ---
    # Note: All paths are now defined relative to the project root for portability.
    project_root: Path = Field(
        default=PROJECT_ROOT, description="Root directory of the project"
    )
    data_dir: Path = Field(
        default=PROJECT_ROOT / "data", description="Directory for all persistent data"
    )
    chroma_db_path: Path = Field(
        default=PROJECT_ROOT / "data" / "chroma_db",
        description="Path to ChromaDB storage",
    )
    commit_cache_dir: Path = Field(
        default=PROJECT_ROOT / "data" / ".rag_commits",
        description="Path to cached commit files",
    )

    collection_name: str = Field(
        default="astratrade_knowledge_base", description="ChromaDB collection name"
    )
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="Embedding model name",
    )

    # --- Security ---
    # This field is required and must be set in the .env file.
    api_key: str = Field(description="API key for securing endpoints")

    # --- RAG Features ---
    template_chunking: bool = Field(default=True)
    grounded_citations: bool = Field(default=True)
    deep_doc_understanding: bool = Field(default=True)

    # --- Chunking Configuration ---
    chunk_size: int = Field(
        default=1000, description="Default chunk size for text splitting"
    )
    chunk_overlap: int = Field(default=200, description="Overlap between chunks")

    # --- Quality Assessment ---
    quality_threshold: float = Field(
        default=0.7, description="Minimum quality threshold for content"
    )

    # --- Platform Configuration ---
    platforms: list = Field(
        default_factory=lambda: [
            "flutter",
            "starknet",
            "cairo",
            "commits",
            "pull_requests",
        ],
        description="Supported platforms for indexing",
    )

    # --- Pydantic Model Configuration ---
    # This tells Pydantic to look for a .env file in the project root and ignore extra fields.
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env", env_file_encoding="utf-8", extra="ignore"
    )


# --- Singleton Settings Instance ---
# This creates a single, globally accessible instance of the settings.
# Any module that imports 'settings' will get this same object.
settings = RAGSettings()

# --- Legacy RAG_CONFIG (for compatibility during refactor) ---
# This dictionary is created from the single settings instance.
# All paths are converted to strings to ensure compatibility with older components.
RAG_CONFIG = {
    "chroma_db_path": str(settings.chroma_db_path),
    "commit_cache_dir": str(settings.commit_cache_dir),
    "collection_name": settings.collection_name,
    "embedding_model": settings.embedding_model,
    "template_chunking": settings.template_chunking,
    "grounded_citations": settings.grounded_citations,
    "deep_doc_understanding": settings.deep_doc_understanding,
    "chunk_size": settings.chunk_size,
    "chunk_overlap": settings.chunk_overlap,
    "quality_threshold": settings.quality_threshold,
    "platforms": settings.platforms,
}
