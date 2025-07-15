#!/usr/bin/env python3
"""
Graph database models and connections for Astra Knowledge Graph
Uses Neo4j for relationship tracking and entity management
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

# Try to import Neo4j, but make it optional for now
try:
    from neo4j import GraphDatabase, Driver

    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    GraphDatabase = None
    Driver = None

try:
    pass
except ImportError:
    # Handle case where config might not be available
    pass

logger = logging.getLogger(__name__)


@dataclass
class Developer:
    """Developer entity in the knowledge graph"""

    name: str
    email: Optional[str] = None
    node_id: Optional[str] = None


@dataclass
class Commit:
    """Commit entity in the knowledge graph"""

    hash: str
    message: str
    author: str
    timestamp: datetime
    node_id: Optional[str] = None


@dataclass
class File:
    """File entity in the knowledge graph"""

    path: str
    language: Optional[str] = None
    node_id: Optional[str] = None


@dataclass
class Feature:
    """Feature entity in the knowledge graph"""

    name: str
    ticket_id: Optional[str] = None
    description: Optional[str] = None
    node_id: Optional[str] = None


@dataclass
class PullRequest:
    """Pull request entity in the knowledge graph"""

    number: int
    title: str
    author: str
    state: str
    created_at: datetime
    node_id: Optional[str] = None


class KnowledgeGraph:
    """Knowledge graph for tracking relationships in a project"""

    def __init__(
        self,
        uri: str = "bolt://localhost:7687",
        user: str = "neo4j",
        password: str = "astratrade123",
    ):
        """Initialize connection to Neo4j database"""
        self.driver = None
        self.uri = uri
        self.user = user
        self.password = password

    async def connect(self) -> bool:
        """Connect to knowledge graph database"""
        try:
            if NEO4J_AVAILABLE:
                logger.info("📊 Neo4j available, but using in-memory graph for now...")
            else:
                logger.info(
                    "📊 Neo4j not available, using in-memory knowledge graph..."
                )

            # Initialize in-memory storage
            self.nodes = {
                "developers": {},
                "commits": {},
                "files": {},
                "features": {},
                "pull_requests": {},
            }
            self.relationships = []

            logger.info("✅ Knowledge graph initialized successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to connect to knowledge graph: {e}")
            return False

    async def close(self):
        """Close database connection"""
        if self.driver:
            self.driver.close()

    # --- Entity Creation Methods ---

    async def create_developer(self, developer: Developer) -> str:
        """Create or update a developer node"""
        node_id = f"dev_{developer.name.lower().replace(' ', '_')}"
        self.nodes["developers"][node_id] = {
            "name": developer.name,
            "email": developer.email,
            "created_at": datetime.now().isoformat(),
        }
        logger.debug(f"Created developer node: {developer.name}")
        return node_id

    async def create_commit(self, commit: Commit) -> str:
        """Create or update a commit node"""
        node_id = f"commit_{commit.hash}"
        self.nodes["commits"][node_id] = {
            "hash": commit.hash,
            "message": commit.message,
            "author": commit.author,
            "timestamp": commit.timestamp.isoformat(),
            "created_at": datetime.now().isoformat(),
        }
        logger.debug(f"Created commit node: {commit.hash[:8]}")
        return node_id

    async def create_file(self, file: File) -> str:
        """Create or update a file node"""
        node_id = f"file_{file.path.replace('/', '_').replace('.', '_')}"
        self.nodes["files"][node_id] = {
            "path": file.path,
            "language": file.language,
            "created_at": datetime.now().isoformat(),
        }
        logger.debug(f"Created file node: {file.path}")
        return node_id

    async def create_feature(self, feature: Feature) -> str:
        """Create or update a feature node"""
        node_id = f"feature_{feature.name.lower().replace(' ', '_')}"
        self.nodes["features"][node_id] = {
            "name": feature.name,
            "ticket_id": feature.ticket_id,
            "description": feature.description,
            "created_at": datetime.now().isoformat(),
        }
        logger.debug(f"Created feature node: {feature.name}")
        return node_id

    async def create_pull_request(self, pr: PullRequest) -> str:
        """Create or update a pull request node"""
        node_id = f"pr_{pr.number}"
        self.nodes["pull_requests"][node_id] = {
            "number": pr.number,
            "title": pr.title,
            "author": pr.author,
            "state": pr.state,
            "created_at": pr.created_at.isoformat(),
        }
        logger.debug(f"Created PR node: #{pr.number}")
        return node_id

    # --- Relationship Creation Methods ---

    async def create_relationship(
        self,
        from_node: str,
        relationship_type: str,
        to_node: str,
        properties: Dict[str, Any] = None,
    ):
        """Create a relationship between two nodes"""
        relationship = {
            "from": from_node,
            "type": relationship_type,
            "to": to_node,
            "properties": properties or {},
            "created_at": datetime.now().isoformat(),
        }
        self.relationships.append(relationship)
        logger.debug(
            f"Created relationship: {from_node} -{relationship_type}-> {to_node}"
        )

    async def author_commit(self, developer_id: str, commit_id: str):
        """Create AUTHORED relationship between developer and commit"""
        await self.create_relationship(developer_id, "AUTHORED", commit_id)

    async def commit_modifies_file(self, commit_id: str, file_id: str):
        """Create MODIFIED relationship between commit and file"""
        await self.create_relationship(commit_id, "MODIFIED", file_id)

    async def commit_implements_feature(self, commit_id: str, feature_id: str):
        """Create IMPLEMENTS relationship between commit and feature"""
        await self.create_relationship(commit_id, "IMPLEMENTS", feature_id)

    async def pr_includes_commit(self, pr_id: str, commit_id: str):
        """Create INCLUDES relationship between pull request and commit"""
        await self.create_relationship(pr_id, "INCLUDES", commit_id)

    async def developer_creates_pr(self, developer_id: str, pr_id: str):
        """Create CREATED relationship between developer and pull request"""
        await self.create_relationship(developer_id, "CREATED", pr_id)

    # --- Query Methods ---

    async def find_developer_work(
        self, developer_name: str, feature_keyword: str = None
    ) -> List[Dict[str, Any]]:
        """Find work done by a specific developer, optionally filtered by feature"""
        results = []

        # Find developer node
        dev_node = None
        for node_id, node_data in self.nodes["developers"].items():
            if node_data["name"].lower() == developer_name.lower():
                dev_node = node_id
                break

        if not dev_node:
            return results

        # Find commits authored by this developer
        authored_commits = []
        for rel in self.relationships:
            if (
                rel["from"] == dev_node
                and rel["type"] == "AUTHORED"
                and rel["to"] in self.nodes["commits"]
            ):
                authored_commits.append(rel["to"])

        # Find files modified by these commits
        for commit_id in authored_commits:
            commit_data = self.nodes["commits"][commit_id]

            # Filter by feature keyword if provided
            if (
                feature_keyword
                and feature_keyword.lower() not in commit_data["message"].lower()
            ):
                continue

            # Find files modified by this commit
            modified_files = []
            for rel in self.relationships:
                if (
                    rel["from"] == commit_id
                    and rel["type"] == "MODIFIED"
                    and rel["to"] in self.nodes["files"]
                ):
                    file_data = self.nodes["files"][rel["to"]]

                    # Additional filter by feature keyword in file path
                    if (
                        feature_keyword
                        and feature_keyword.lower() not in file_data["path"].lower()
                    ):
                        continue

                    modified_files.append(file_data)

            if modified_files or not feature_keyword:
                results.append({"commit": commit_data, "files": modified_files})

        return results

    async def find_feature_contributors(
        self, feature_name: str
    ) -> List[Dict[str, Any]]:
        """Find all developers who worked on a specific feature"""
        results = []

        # Find commits that implement this feature
        feature_commits = []
        for commit_id, commit_data in self.nodes["commits"].items():
            if feature_name.lower() in commit_data["message"].lower():
                feature_commits.append(commit_id)

        # Find developers who authored these commits
        contributors = set()
        for commit_id in feature_commits:
            for rel in self.relationships:
                if (
                    rel["to"] == commit_id
                    and rel["type"] == "AUTHORED"
                    and rel["from"] in self.nodes["developers"]
                ):
                    contributors.add(rel["from"])

        for dev_id in contributors:
            dev_data = self.nodes["developers"][dev_id]
            # Find their commits for this feature
            dev_commits = []
            for commit_id in feature_commits:
                for rel in self.relationships:
                    if (
                        rel["from"] == dev_id
                        and rel["type"] == "AUTHORED"
                        and rel["to"] == commit_id
                    ):
                        dev_commits.append(self.nodes["commits"][commit_id])

            results.append({"developer": dev_data, "commits": dev_commits})

        return results

    async def find_file_history(self, file_path: str) -> List[Dict[str, Any]]:
        """Find the complete change history for a specific file"""
        results = []

        # Find the file node
        file_node = None
        for node_id, node_data in self.nodes["files"].items():
            if node_data["path"] == file_path:
                file_node = node_id
                break

        if not file_node:
            return results

        # Find commits that modified this file
        modifying_commits = []
        for rel in self.relationships:
            if (
                rel["to"] == file_node
                and rel["type"] == "MODIFIED"
                and rel["from"] in self.nodes["commits"]
            ):
                modifying_commits.append(rel["from"])

        # Get commit details and their authors
        for commit_id in modifying_commits:
            commit_data = self.nodes["commits"][commit_id]

            # Find the author
            author_data = None
            for rel in self.relationships:
                if (
                    rel["to"] == commit_id
                    and rel["type"] == "AUTHORED"
                    and rel["from"] in self.nodes["developers"]
                ):
                    author_data = self.nodes["developers"][rel["from"]]
                    break

            results.append({"commit": commit_data, "author": author_data})

        # Sort by timestamp
        results.sort(key=lambda x: x["commit"]["timestamp"], reverse=True)
        return results

    # --- Statistics and Health Methods ---

    async def get_graph_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge graph"""
        return {
            "nodes": {
                "developers": len(self.nodes["developers"]),
                "commits": len(self.nodes["commits"]),
                "files": len(self.nodes["files"]),
                "features": len(self.nodes["features"]),
                "pull_requests": len(self.nodes["pull_requests"]),
                "total": sum(len(nodes) for nodes in self.nodes.values()),
            },
            "relationships": {"total": len(self.relationships), "by_type": {}},
        }

    async def get_sample_queries(self) -> List[str]:
        """Get sample queries that can be run on this graph"""
        return [
            "What has [developer] worked on related to [feature]?",
            "Who was the last person to change [file_path] and when?",
            "Show me all contributors to the [feature] feature",
            "What files has [developer] modified recently?",
            "Find the complete change history for [file_path]",
        ]


# Global instance
knowledge_graph = KnowledgeGraph()
