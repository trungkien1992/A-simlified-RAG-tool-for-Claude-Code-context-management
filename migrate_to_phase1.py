#!/usr/bin/env python3
"""
Migration script to Phase 1 - Hybrid Architecture
Migrates existing data to the new dual database system
"""

import asyncio
import logging
from pathlib import Path
from src.astra_universal_rag.hybrid.hybrid_rag import HybridRAG
from src.astra_universal_rag.config_phase1 import phase1_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def migrate_existing_data():
    """Migrate existing ChromaDB data to include graph references"""
    logger.info("Starting migration to Phase 1 hybrid architecture...")
    
    # Initialize hybrid system
    rag = HybridRAG()
    rag.initialize_graph(
        uri=phase1_settings.neo4j_uri,
        username=phase1_settings.neo4j_username,
        password=phase1_settings.neo4j_password
    )
    
    # Check existing data
    commit_cache = Path("data/.rag_commits")
    if commit_cache.exists():
        logger.info(f"Found existing commit cache at {commit_cache}")
        
        # Re-ingest with dual pipeline
        result = await rag.ingest_repository(
            repo_path=".",
            repo_url="https://github.com/astra/universal-rag"
        )
        logger.info(f"Migration complete: {result}")
    else:
        logger.warning("No existing data found to migrate")
        
    logger.info("✅ Migration to Phase 1 completed")


if __name__ == "__main__":
    asyncio.run(migrate_existing_data())
