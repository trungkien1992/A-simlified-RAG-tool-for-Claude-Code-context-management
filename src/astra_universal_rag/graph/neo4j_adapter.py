#!/usr/bin/env python3
"""
Neo4j Adapter - Phase 1
Handles all interactions with the Neo4j graph database
"""

import os
import logging
from typing import Dict, List, Any, Optional, Tuple
from neo4j import GraphDatabase, Driver, Transaction
from ..schemas.universal_schema import GraphNode, GraphEdge, EntityType, RelationType

logger = logging.getLogger(__name__)


class Neo4jAdapter:
    """Adapter for Neo4j graph database operations"""
    
    def __init__(self, uri: str, username: str, password: str):
        self.uri = uri
        self.username = username
        self.password = password
        self._driver: Optional[Driver] = None
        
    @property
    def driver(self) -> Driver:
        """Lazy initialization of Neo4j driver"""
        if self._driver is None:
            self._driver = GraphDatabase.driver(
                self.uri, 
                auth=(self.username, self.password)
            )
            logger.info(f"Connected to Neo4j at {self.uri}")
        return self._driver
        
    def close(self):
        """Close the Neo4j connection"""
        if self._driver:
            self._driver.close()
            self._driver = None
            
    def create_node(self, node: GraphNode) -> str:
        """Create a node in the graph"""
        with self.driver.session() as session:
            result = session.write_transaction(
                self._create_node_tx, node
            )
            return result
            
    @staticmethod
    def _create_node_tx(tx: Transaction, node: GraphNode) -> str:
        query = f"""
        CREATE (n:{node.type.value} {{
            id: $id,
            vector_id: $vector_id
        }})
        SET n += $properties
        RETURN n.id as id
        """
        result = tx.run(
            query,
            id=node.id,
            vector_id=node.vector_id,
            properties=node.properties
        )
        return result.single()["id"]
        
    def create_edge(self, edge: GraphEdge) -> bool:
        """Create an edge between two nodes"""
        with self.driver.session() as session:
            return session.write_transaction(
                self._create_edge_tx, edge
            )
            
    @staticmethod
    def _create_edge_tx(tx: Transaction, edge: GraphEdge) -> bool:
        query = f"""
        MATCH (a {{id: $source_id}})
        MATCH (b {{id: $target_id}})
        CREATE (a)-[r:{edge.type.value} {{weight: $weight}}]->(b)
        SET r += $properties
        RETURN r
        """
        result = tx.run(
            query,
            source_id=edge.source_id,
            target_id=edge.target_id,
            weight=edge.weight,
            properties=edge.properties
        )
        return result.single() is not None
        
    def find_related_nodes(
        self, 
        node_id: str, 
        relationship_types: List[RelationType],
        max_depth: int = 2
    ) -> List[Dict[str, Any]]:
        """Find all nodes related to a given node"""
        with self.driver.session() as session:
            return session.read_transaction(
                self._find_related_nodes_tx,
                node_id,
                relationship_types,
                max_depth
            )
            
    @staticmethod
    def _find_related_nodes_tx(
        tx: Transaction,
        node_id: str,
        relationship_types: List[RelationType],
        max_depth: int
    ) -> List[Dict[str, Any]]:
        rel_types = "|".join([r.value for r in relationship_types])
        query = f"""
        MATCH path = (start {{id: $node_id}})-[:{rel_types}*1..{max_depth}]-(end)
        RETURN DISTINCT end, length(path) as distance
        ORDER BY distance
        """
        result = tx.run(query, node_id=node_id)
        return [
            {
                "node": dict(record["end"]),
                "distance": record["distance"]
            }
            for record in result
        ]
        
    def execute_cypher(self, query: str, parameters: Dict[str, Any] = None) -> List[Dict]:
        """Execute arbitrary Cypher query"""
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return [dict(record) for record in result]
