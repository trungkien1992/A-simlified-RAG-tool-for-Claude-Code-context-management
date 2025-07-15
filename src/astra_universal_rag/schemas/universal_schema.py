#!/usr/bin/env python3
"""
Universal Knowledge Graph Schema - Phase 1
Defines the core entities and relationships for the hybrid graph-vector architecture
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime


class EntityType(Enum):
    """Core entity types in the knowledge graph"""
    REPOSITORY = "Repository"
    BRANCH = "Branch"
    COMMIT = "Commit"
    FILE = "File"
    FUNCTION = "Function"
    CLASS = "Class"
    DEVELOPER = "Developer"
    PULL_REQUEST = "PullRequest"
    ISSUE = "Issue"
    TEST = "Test"
    DOCUMENTATION = "Documentation"
    # Phase 2 entities
    JIRA_TICKET = "JiraTicket"
    CONFLUENCE_PAGE = "ConfluencePage"
    SLACK_MESSAGE = "SlackMessage"
    SLACK_THREAD = "SlackThread"
    SLACK_CHANNEL = "SlackChannel"


class RelationType(Enum):
    """Core relationship types in the knowledge graph"""
    # Code relationships
    MODIFIES = "MODIFIES"
    CALLS = "CALLS"
    IMPORTS = "IMPORTS"
    DEPENDS_ON = "DEPENDS_ON"
    TESTS = "TESTS"
    INHERITS_FROM = "INHERITS_FROM"
    IMPLEMENTS = "IMPLEMENTS"
    
    # Developer relationships
    AUTHORED_BY = "AUTHORED_BY"
    REVIEWED_BY = "REVIEWED_BY"
    ASSIGNED_TO = "ASSIGNED_TO"
    
    # Version control relationships
    BELONGS_TO_BRANCH = "BELONGS_TO_BRANCH"
    PART_OF_REPOSITORY = "PART_OF_REPOSITORY"
    CONTAINS = "CONTAINS"
    PRECEDED_BY = "PRECEDED_BY"
    
    # Cross-tool relationships (Phase 2)
    FIXES = "FIXES"
    DOCUMENTS = "DOCUMENTS"
    DISCUSSED_IN = "DISCUSSED_IN"
    MENTIONED_IN = "MENTIONED_IN"
    RELATES_TO = "RELATES_TO"


@dataclass
class GraphNode:
    """Base class for all nodes in the knowledge graph"""
    id: str
    type: EntityType
    properties: Dict[str, Any]
    vector_id: Optional[str] = None  # Link to ChromaDB vector


@dataclass
class GraphEdge:
    """Base class for all edges in the knowledge graph"""
    source_id: str
    target_id: str
    type: RelationType
    properties: Dict[str, Any]
    weight: float = 1.0
