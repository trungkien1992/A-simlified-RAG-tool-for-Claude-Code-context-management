#!/usr/bin/env python3
"""
Dual Pipeline Ingestion - Phase 1
Populates both ChromaDB (vectors) and Neo4j (graph) during ingestion
"""

import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from ..graph.neo4j_adapter import Neo4jAdapter
from ..schemas.universal_schema import GraphNode, GraphEdge, EntityType, RelationType
from ..code_aware_chunker import CodeAwareChunker

logger = logging.getLogger(__name__)


class DualPipelineIngestion:
    """Handles ingestion into both vector and graph databases"""
    
    def __init__(self, vector_store, graph_adapter: Neo4jAdapter):
        self.vector_store = vector_store
        self.graph_adapter = graph_adapter
        self.chunker = CodeAwareChunker()
        
    def ingest_repository(self, repo_path: str, repo_url: str) -> Dict[str, Any]:
        """Ingest a Git repository into both databases"""
        repo_path = Path(repo_path)
        
        # Create repository node in graph
        repo_node = GraphNode(
            id=f"repo:{repo_url}",
            type=EntityType.REPOSITORY,
            properties={
                "url": repo_url,
                "path": str(repo_path),
                "name": repo_path.name
            }
        )
        self.graph_adapter.create_node(repo_node)
        
        # Process commits
        commits_ingested = self._ingest_commits(repo_path, repo_node.id)
        
        # Process files
        files_ingested = self._ingest_files(repo_path, repo_node.id)
        
        return {
            "repository": repo_url,
            "commits_ingested": commits_ingested,
            "files_ingested": files_ingested
        }
        
    def _ingest_commits(self, repo_path: Path, repo_id: str) -> int:
        """Ingest commits from cache into both databases"""
        commit_cache = repo_path / "data" / ".rag_commits"
        if not commit_cache.exists():
            return 0
            
        count = 0
        for commit_file in commit_cache.glob("*.json"):
            with open(commit_file, "r") as f:
                commit_data = json.load(f)
                
            # Create commit node in graph
            commit_node = GraphNode(
                id=f"commit:{commit_data['sha']}",
                type=EntityType.COMMIT,
                properties={
                    "sha": commit_data["sha"],
                    "message": commit_data["message"],
                    "author": commit_data["author"],
                    "timestamp": commit_data["timestamp"]
                }
            )
            node_id = self.graph_adapter.create_node(commit_node)
            
            # Create developer node if not exists
            dev_node = GraphNode(
                id=f"dev:{commit_data['author']}",
                type=EntityType.DEVELOPER,
                properties={
                    "name": commit_data["author"],
                    "email": commit_data.get("author_email", "")
                }
            )
            self.graph_adapter.create_node(dev_node)
            
            # Create AUTHORED_BY relationship
            self.graph_adapter.create_edge(GraphEdge(
                source_id=commit_node.id,
                target_id=dev_node.id,
                type=RelationType.AUTHORED_BY,
                properties={}
            ))
            
            # Create PART_OF_REPOSITORY relationship
            self.graph_adapter.create_edge(GraphEdge(
                source_id=commit_node.id,
                target_id=repo_id,
                type=RelationType.PART_OF_REPOSITORY,
                properties={}
            ))
            
            # Process modified files
            for file_path in commit_data.get("files_changed", []):
                file_node = GraphNode(
                    id=f"file:{repo_id}:{file_path}",
                    type=EntityType.FILE,
                    properties={
                        "path": file_path,
                        "name": Path(file_path).name
                    }
                )
                self.graph_adapter.create_node(file_node)
                
                # Create MODIFIES relationship
                self.graph_adapter.create_edge(GraphEdge(
                    source_id=commit_node.id,
                    target_id=file_node.id,
                    type=RelationType.MODIFIES,
                    properties={}
                ))
                
            # Add to vector store with graph reference
            chunks = self.chunker.chunk_commit(commit_data)
            for chunk in chunks:
                chunk.metadata["graph_node_id"] = commit_node.id
                self.vector_store.add_chunk(chunk)
                
            count += 1
            
        return count
        
    def _ingest_files(self, repo_path: Path, repo_id: str) -> int:
        """Ingest source files into both databases"""
        count = 0
        src_path = repo_path / "src"
        
        if not src_path.exists():
            src_path = repo_path  # Fallback to repo root
            
        for file_path in src_path.rglob("*.py"):
            # Skip test files for now
            if "test" in file_path.name.lower():
                continue
                
            # Create file node
            rel_path = file_path.relative_to(repo_path)
            file_node = GraphNode(
                id=f"file:{repo_id}:{rel_path}",
                type=EntityType.FILE,
                properties={
                    "path": str(rel_path),
                    "name": file_path.name,
                    "extension": file_path.suffix
                }
            )
            self.graph_adapter.create_node(file_node)
            
            # Read and chunk file content
            try:
                content = file_path.read_text(encoding="utf-8")
                chunks = self.chunker.chunk_code(content, str(rel_path))
                
                for chunk in chunks:
                    # Add graph reference to metadata
                    chunk.metadata["graph_node_id"] = file_node.id
                    
                    # If chunk is a function or class, create separate node
                    if chunk.chunk_type in ["function", "class"]:
                        entity_type = (
                            EntityType.FUNCTION 
                            if chunk.chunk_type == "function" 
                            else EntityType.CLASS
                        )
                        entity_node = GraphNode(
                            id=f"{chunk.chunk_type}:{file_node.id}:{chunk.metadata.get('name', 'unknown')}",
                            type=entity_type,
                            properties={
                                "name": chunk.metadata.get("name", "unknown"),
                                "file_path": str(rel_path),
                                "start_line": chunk.start_line,
                                "end_line": chunk.end_line
                            }
                        )
                        self.graph_adapter.create_node(entity_node)
                        
                        # Create CONTAINS relationship
                        self.graph_adapter.create_edge(GraphEdge(
                            source_id=file_node.id,
                            target_id=entity_node.id,
                            type=RelationType.CONTAINS,
                            properties={}
                        ))
                        
                        # Update chunk metadata with entity node ID
                        chunk.metadata["graph_node_id"] = entity_node.id
                        
                    # Add to vector store
                    self.vector_store.add_chunk(chunk)
                    
                count += 1
                
            except Exception as e:
                logger.error(f"Error processing file {file_path}: {e}")
                
        return count
