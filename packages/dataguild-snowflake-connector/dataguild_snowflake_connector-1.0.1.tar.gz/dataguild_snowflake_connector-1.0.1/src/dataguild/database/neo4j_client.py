"""
DataGuild Neo4j Client

Comprehensive Neo4j client for storing and querying lineage relationships,
graph traversals, and complex metadata dependencies with full graph support.
"""

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union, Tuple
from dataclasses import dataclass
from neo4j import GraphDatabase, Driver, Session
from neo4j.exceptions import ServiceUnavailable, AuthError, TransientError
import threading

logger = logging.getLogger(__name__)


@dataclass
class Neo4jConfig:
    """Configuration for Neo4j connection."""
    uri: str = "bolt://localhost:7687"
    username: str = "neo4j"
    password: str = "neo4j"
    database: str = "neo4j"
    max_connection_lifetime: int = 3600
    max_connection_pool_size: int = 100
    connection_acquisition_timeout: int = 60
    encrypted: bool = False
    trust: str = "TRUST_SYSTEM_CA_SIGNED_CERTIFICATES"


class Neo4jClient:
    """
    Comprehensive Neo4j client for DataGuild lineage and graph operations.
    
    Provides connection management, transaction handling, and specialized
    methods for storing and querying lineage relationships, graph traversals,
    and complex metadata dependencies.
    """
    
    def __init__(self, config: Union[Neo4jConfig, Dict[str, Any]]):
        """
        Initialize Neo4j client.
        
        Args:
            config: Neo4j configuration object or dictionary
        """
        if isinstance(config, dict):
            config = Neo4jConfig(**config)
        
        self.config = config
        self._driver: Optional[Driver] = None
        self._lock = threading.Lock()
        
        # Initialize driver
        self._init_driver()
        
        # Create constraints and indexes
        self._create_constraints()
    
    def _init_driver(self) -> None:
        """Initialize Neo4j driver."""
        try:
            self._driver = GraphDatabase.driver(
                self.config.uri,
                auth=(self.config.username, self.config.password),
                max_connection_lifetime=self.config.max_connection_lifetime,
                max_connection_pool_size=self.config.max_connection_pool_size,
                connection_acquisition_timeout=self.config.connection_acquisition_timeout,
                encrypted=self.config.encrypted,
                trust=self.config.trust
            )
            
            # Test connection
            with self._driver.session(database=self.config.database) as session:
                session.run("RETURN 1")
            
            logger.info(f"Neo4j driver initialized: {self.config.uri}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Neo4j driver: {e}")
            raise
    
    def _create_constraints(self) -> None:
        """Create constraints and indexes for optimal performance."""
        constraints_and_indexes = [
            # Entity constraints
            "CREATE CONSTRAINT entity_urn_unique IF NOT EXISTS FOR (e:Entity) REQUIRE e.urn IS UNIQUE",
            "CREATE INDEX entity_type_index IF NOT EXISTS FOR (e:Entity) ON (e.type)",
            "CREATE INDEX entity_platform_index IF NOT EXISTS FOR (e:Entity) ON (e.platform)",
            "CREATE INDEX entity_name_index IF NOT EXISTS FOR (e:Entity) ON (e.name)",
            
            # Dataset constraints
            "CREATE INDEX dataset_full_name_index IF NOT EXISTS FOR (d:Dataset) ON (d.full_name)",
            "CREATE INDEX dataset_type_index IF NOT EXISTS FOR (d:Dataset) ON (d.dataset_type)",
            
            # Column constraints
            "CREATE INDEX column_name_index IF NOT EXISTS FOR (c:Column) ON (c.name)",
            "CREATE INDEX column_data_type_index IF NOT EXISTS FOR (c:Column) ON (c.data_type)",
            
            # Relationship constraints
            "CREATE INDEX relationship_type_index IF NOT EXISTS FOR ()-[r:RELATES_TO]-() ON (r.type)",
            "CREATE INDEX relationship_direction_index IF NOT EXISTS FOR ()-[r:RELATES_TO]-() ON (r.direction)",
            
            # Lineage constraints
            "CREATE INDEX lineage_confidence_index IF NOT EXISTS FOR ()-[r:LINEAGE]-() ON (r.confidence)",
            "CREATE INDEX lineage_created_index IF NOT EXISTS FOR ()-[r:LINEAGE]-() ON (r.created_at)",
        ]
        
        with self._driver.session(database=self.config.database) as session:
            for constraint in constraints_and_indexes:
                try:
                    session.run(constraint)
                except Exception as e:
                    logger.warning(f"Failed to create constraint/index: {constraint} - {e}")
    
    def _get_session(self) -> Session:
        """Get Neo4j session."""
        if not self._driver:
            raise RuntimeError("Neo4j driver not initialized")
        return self._driver.session(database=self.config.database)
    
    def create_entity_node(self, entity_data: Dict[str, Any]) -> str:
        """
        Create an entity node in the graph.
        
        Args:
            entity_data: Entity data dictionary
            
        Returns:
            Node ID
        """
        with self._get_session() as session:
            result = session.run("""
                MERGE (e:Entity {urn: $urn})
                SET e.type = $type,
                    e.name = $name,
                    e.platform = $platform,
                    e.description = $description,
                    e.metadata = $metadata,
                    e.created_at = datetime($created_at),
                    e.updated_at = datetime($updated_at)
                RETURN id(e) as node_id
            """, {
                'urn': entity_data.get('urn'),
                'type': entity_data.get('entity_type', 'DATASET'),
                'name': entity_data.get('name'),
                'platform': entity_data.get('platform'),
                'description': entity_data.get('description'),
                'metadata': json.dumps(entity_data.get('metadata', {})),
                'created_at': entity_data.get('created_at', datetime.now(timezone.utc).isoformat()),
                'updated_at': entity_data.get('updated_at', datetime.now(timezone.utc).isoformat())
            })
            
            return str(result.single()['node_id'])
    
    def create_dataset_node(self, dataset_data: Dict[str, Any], entity_urn: str) -> str:
        """
        Create a dataset node and link it to entity.
        
        Args:
            dataset_data: Dataset data dictionary
            entity_urn: Parent entity URN
            
        Returns:
            Node ID
        """
        with self._get_session() as session:
            result = session.run("""
                MATCH (e:Entity {urn: $entity_urn})
                MERGE (d:Dataset {urn: $dataset_urn})
                SET d.name = $name,
                    d.full_name = $full_name,
                    d.dataset_type = $dataset_type,
                    d.description = $description,
                    d.database = $database,
                    d.schema = $schema,
                    d.properties = $properties,
                    d.created_at = datetime($created_at),
                    d.updated_at = datetime($updated_at)
                MERGE (e)-[:HAS_DATASET]->(d)
                RETURN id(d) as node_id
            """, {
                'entity_urn': entity_urn,
                'dataset_urn': dataset_data.get('urn', f"{entity_urn}:dataset"),
                'name': dataset_data.get('name'),
                'full_name': dataset_data.get('full_name', dataset_data.get('name')),
                'dataset_type': dataset_data.get('type', 'TABLE'),
                'description': dataset_data.get('description'),
                'database': dataset_data.get('database'),
                'schema': dataset_data.get('schema'),
                'properties': json.dumps(dataset_data.get('properties', {})),
                'created_at': dataset_data.get('created_at', datetime.now(timezone.utc).isoformat()),
                'updated_at': dataset_data.get('updated_at', datetime.now(timezone.utc).isoformat())
            })
            
            return str(result.single()['node_id'])
    
    def create_column_nodes(self, columns_data: List[Dict[str, Any]], dataset_urn: str) -> List[str]:
        """
        Create column nodes and link them to dataset.
        
        Args:
            columns_data: List of column data dictionaries
            dataset_urn: Parent dataset URN
            
        Returns:
            List of node IDs
        """
        if not columns_data:
            return []
        
        node_ids = []
        with self._get_session() as session:
            for i, column_data in enumerate(columns_data):
                result = session.run("""
                    MATCH (d:Dataset {urn: $dataset_urn})
                    MERGE (c:Column {urn: $column_urn})
                    SET c.name = $name,
                        c.position = $position,
                        c.data_type = $data_type,
                        c.native_data_type = $native_data_type,
                        c.description = $description,
                        c.nullable = $nullable,
                        c.is_primary_key = $is_primary_key,
                        c.is_foreign_key = $is_foreign_key,
                        c.properties = $properties,
                        c.created_at = datetime($created_at)
                    MERGE (d)-[:HAS_COLUMN]->(c)
                    RETURN id(c) as node_id
                """, {
                    'dataset_urn': dataset_urn,
                    'column_urn': f"{dataset_urn}:{column_data.get('name')}",
                    'name': column_data.get('name'),
                    'position': i + 1,
                    'data_type': column_data.get('type', {}).get('type_name') if isinstance(column_data.get('type'), dict) else column_data.get('type'),
                    'native_data_type': column_data.get('nativeDataType'),
                    'description': column_data.get('description'),
                    'nullable': column_data.get('nullable', True),
                    'is_primary_key': column_data.get('is_primary_key', False),
                    'is_foreign_key': column_data.get('is_foreign_key', False),
                    'properties': json.dumps(column_data.get('properties', {})),
                    'created_at': datetime.now(timezone.utc).isoformat()
                })
                
                node_ids.append(str(result.single()['node_id']))
        
        return node_ids
    
    def create_lineage_relationship(self, source_urn: str, target_urn: str, 
                                  relationship_type: str = "DOWNSTREAM_OF",
                                  confidence: float = 1.0, 
                                  metadata: Dict[str, Any] = None) -> str:
        """
        Create a lineage relationship between entities.
        
        Args:
            source_urn: Source entity URN
            target_urn: Target entity URN
            relationship_type: Type of relationship
            confidence: Confidence score
            metadata: Additional metadata
            
        Returns:
            Relationship ID
        """
        with self._get_session() as session:
            result = session.run("""
                MATCH (source:Entity {urn: $source_urn})
                MATCH (target:Entity {urn: $target_urn})
                MERGE (source)-[r:LINEAGE {
                    type: $relationship_type,
                    direction: 'DOWNSTREAM'
                }]->(target)
                SET r.confidence = $confidence,
                    r.metadata = $metadata,
                    r.created_at = datetime($created_at),
                    r.updated_at = datetime($updated_at)
                RETURN id(r) as rel_id
            """, {
                'source_urn': source_urn,
                'target_urn': target_urn,
                'relationship_type': relationship_type,
                'confidence': confidence,
                'metadata': json.dumps(metadata or {}),
                'created_at': datetime.now(timezone.utc).isoformat(),
                'updated_at': datetime.now(timezone.utc).isoformat()
            })
            
            return str(result.single()['rel_id'])
    
    def create_column_lineage_relationship(self, source_column_urn: str, target_column_urn: str,
                                         transformation: str = "DIRECT_COPY",
                                         confidence: float = 1.0,
                                         metadata: Dict[str, Any] = None) -> str:
        """
        Create a column-level lineage relationship.
        
        Args:
            source_column_urn: Source column URN
            target_column_urn: Target column URN
            transformation: Type of transformation
            confidence: Confidence score
            metadata: Additional metadata
            
        Returns:
            Relationship ID
        """
        with self._get_session() as session:
            result = session.run("""
                MATCH (source:Column {urn: $source_column_urn})
                MATCH (target:Column {urn: $target_column_urn})
                MERGE (source)-[r:COLUMN_LINEAGE {
                    transformation: $transformation
                }]->(target)
                SET r.confidence = $confidence,
                    r.metadata = $metadata,
                    r.created_at = datetime($created_at),
                    r.updated_at = datetime($updated_at)
                RETURN id(r) as rel_id
            """, {
                'source_column_urn': source_column_urn,
                'target_column_urn': target_column_urn,
                'transformation': transformation,
                'confidence': confidence,
                'metadata': json.dumps(metadata or {}),
                'created_at': datetime.now(timezone.utc).isoformat(),
                'updated_at': datetime.now(timezone.utc).isoformat()
            })
            
            return str(result.single()['rel_id'])
    
    def get_entity_by_urn(self, urn: str) -> Optional[Dict[str, Any]]:
        """Get entity by URN."""
        with self._get_session() as session:
            result = session.run("""
                MATCH (e:Entity {urn: $urn})
                RETURN e
            """, {'urn': urn})
            
            record = result.single()
            if record:
                entity = dict(record['e'])
                # Parse JSON fields
                if 'metadata' in entity and isinstance(entity['metadata'], str):
                    entity['metadata'] = json.loads(entity['metadata'])
                return entity
            return None
    
    def get_lineage_graph(self, entity_urn: str, max_depth: int = 3, 
                         direction: str = "BOTH") -> Dict[str, Any]:
        """
        Get lineage graph for an entity.
        
        Args:
            entity_urn: Entity URN
            max_depth: Maximum depth to traverse
            direction: Direction to traverse ("UPSTREAM", "DOWNSTREAM", "BOTH")
            
        Returns:
            Graph data with nodes and relationships
        """
        with self._get_session() as session:
            if direction == "BOTH":
                query = """
                    MATCH path = (center:Entity {urn: $urn})-[:LINEAGE*1..$max_depth]-(connected:Entity)
                    RETURN path, length(path) as depth
                    ORDER BY depth
                """
            elif direction == "UPSTREAM":
                query = """
                    MATCH path = (center:Entity {urn: $urn})<-[:LINEAGE*1..$max_depth]-(connected:Entity)
                    RETURN path, length(path) as depth
                    ORDER BY depth
                """
            else:  # DOWNSTREAM
                query = """
                    MATCH path = (center:Entity {urn: $urn})-[:LINEAGE*1..$max_depth]->(connected:Entity)
                    RETURN path, length(path) as depth
                    ORDER BY depth
                """
            
            result = session.run(query, {'urn': entity_urn, 'max_depth': max_depth})
            
            nodes = set()
            relationships = []
            
            for record in result:
                path = record['path']
                depth = record['depth']
                
                # Extract nodes and relationships from path
                for i, node in enumerate(path.nodes):
                    node_data = dict(node)
                    if 'metadata' in node_data and isinstance(node_data['metadata'], str):
                        node_data['metadata'] = json.loads(node_data['metadata'])
                    nodes.add((node_data['urn'], node_data))
                
                for i, rel in enumerate(path.relationships):
                    rel_data = dict(rel)
                    if 'metadata' in rel_data and isinstance(rel_data['metadata'], str):
                        rel_data['metadata'] = json.loads(rel_data['metadata'])
                    relationships.append({
                        'source': path.nodes[i]['urn'],
                        'target': path.nodes[i + 1]['urn'],
                        'relationship': rel_data,
                        'depth': depth
                    })
            
            return {
                'nodes': [node_data for _, node_data in nodes],
                'relationships': relationships,
                'center_urn': entity_urn,
                'max_depth': max_depth,
                'direction': direction
            }
    
    def get_column_lineage(self, column_urn: str, max_depth: int = 2) -> Dict[str, Any]:
        """
        Get column-level lineage.
        
        Args:
            column_urn: Column URN
            max_depth: Maximum depth to traverse
            
        Returns:
            Column lineage data
        """
        with self._get_session() as session:
            result = session.run("""
                MATCH path = (center:Column {urn: $column_urn})-[:COLUMN_LINEAGE*1..$max_depth]-(connected:Column)
                RETURN path, length(path) as depth
                ORDER BY depth
            """, {'column_urn': column_urn, 'max_depth': max_depth})
            
            nodes = set()
            relationships = []
            
            for record in result:
                path = record['path']
                depth = record['depth']
                
                for node in path.nodes:
                    node_data = dict(node)
                    if 'metadata' in node_data and isinstance(node_data['metadata'], str):
                        node_data['metadata'] = json.loads(node_data['metadata'])
                    nodes.add((node_data['urn'], node_data))
                
                for i, rel in enumerate(path.relationships):
                    rel_data = dict(rel)
                    if 'metadata' in rel_data and isinstance(rel_data['metadata'], str):
                        rel_data['metadata'] = json.loads(rel_data['metadata'])
                    relationships.append({
                        'source': path.nodes[i]['urn'],
                        'target': path.nodes[i + 1]['urn'],
                        'relationship': rel_data,
                        'depth': depth
                    })
            
            return {
                'nodes': [node_data for _, node_data in nodes],
                'relationships': relationships,
                'center_urn': column_urn,
                'max_depth': max_depth
            }
    
    def find_impact_analysis(self, entity_urn: str, max_depth: int = 5) -> Dict[str, Any]:
        """
        Find all entities that would be impacted by changes to the given entity.
        
        Args:
            entity_urn: Entity URN
            max_depth: Maximum depth to traverse
            
        Returns:
            Impact analysis data
        """
        with self._get_session() as session:
            # Find downstream dependencies
            downstream_result = session.run("""
                MATCH path = (center:Entity {urn: $urn})-[:LINEAGE*1..$max_depth]->(impacted:Entity)
                RETURN impacted, length(path) as depth
                ORDER BY depth
            """, {'urn': entity_urn, 'max_depth': max_depth})
            
            downstream_entities = []
            for record in downstream_result:
                entity = dict(record['impacted'])
                if 'metadata' in entity and isinstance(entity['metadata'], str):
                    entity['metadata'] = json.loads(entity['metadata'])
                downstream_entities.append({
                    'entity': entity,
                    'impact_depth': record['depth']
                })
            
            # Find upstream dependencies
            upstream_result = session.run("""
                MATCH path = (center:Entity {urn: $urn})<-[:LINEAGE*1..$max_depth]-(dependency:Entity)
                RETURN dependency, length(path) as depth
                ORDER BY depth
            """, {'urn': entity_urn, 'max_depth': max_depth})
            
            upstream_entities = []
            for record in upstream_result:
                entity = dict(record['dependency'])
                if 'metadata' in entity and isinstance(entity['metadata'], str):
                    entity['metadata'] = json.loads(entity['metadata'])
                upstream_entities.append({
                    'entity': entity,
                    'dependency_depth': record['depth']
                })
            
            return {
                'center_urn': entity_urn,
                'downstream_impact': downstream_entities,
                'upstream_dependencies': upstream_entities,
                'max_depth': max_depth,
                'total_downstream': len(downstream_entities),
                'total_upstream': len(upstream_entities)
            }
    
    def search_entities_by_pattern(self, pattern: str, entity_type: Optional[str] = None,
                                 platform: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Search entities by pattern matching.
        
        Args:
            pattern: Search pattern
            entity_type: Filter by entity type
            platform: Filter by platform
            limit: Maximum results
            
        Returns:
            List of matching entities
        """
        with self._get_session() as session:
            where_conditions = ["(e.name =~ $pattern OR e.description =~ $pattern)"]
            params = {'pattern': f".*{pattern}.*", 'limit': limit}
            
            if entity_type:
                where_conditions.append("e.type = $entity_type")
                params['entity_type'] = entity_type
            
            if platform:
                where_conditions.append("e.platform = $platform")
                params['platform'] = platform
            
            query = f"""
                MATCH (e:Entity)
                WHERE {' AND '.join(where_conditions)}
                RETURN e
                ORDER BY e.updated_at DESC
                LIMIT $limit
            """
            
            result = session.run(query, params)
            
            entities = []
            for record in result:
                entity = dict(record['e'])
                if 'metadata' in entity and isinstance(entity['metadata'], str):
                    entity['metadata'] = json.loads(entity['metadata'])
                entities.append(entity)
            
            return entities
    
    def get_entity_statistics(self) -> Dict[str, Any]:
        """Get overall entity statistics."""
        with self._get_session() as session:
            # Entity counts by type
            entity_counts = session.run("""
                MATCH (e:Entity)
                RETURN e.type as entity_type, count(e) as count
                ORDER BY count DESC
            """)
            
            # Platform distribution
            platform_counts = session.run("""
                MATCH (e:Entity)
                WHERE e.platform IS NOT NULL
                RETURN e.platform as platform, count(e) as count
                ORDER BY count DESC
            """)
            
            # Relationship counts
            relationship_counts = session.run("""
                MATCH ()-[r:LINEAGE]->()
                RETURN r.type as relationship_type, count(r) as count
                ORDER BY count DESC
            """)
            
            # Column counts
            column_counts = session.run("""
                MATCH (c:Column)
                RETURN count(c) as total_columns
            """)
            
            return {
                'entity_counts': [dict(record) for record in entity_counts],
                'platform_counts': [dict(record) for record in platform_counts],
                'relationship_counts': [dict(record) for record in relationship_counts],
                'total_columns': column_counts.single()['total_columns'] if column_counts.single() else 0
            }
    
    def clear_database(self) -> None:
        """Clear all data from the database."""
        with self._get_session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            logger.info("Neo4j database cleared")
    
    def close(self) -> None:
        """Close Neo4j driver."""
        if self._driver:
            self._driver.close()
            logger.info("Neo4j driver closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def __repr__(self) -> str:
        """String representation."""
        return f"Neo4jClient(uri='{self.config.uri}', database='{self.config.database}')"


# Convenience factory functions
def create_neo4j_client(
    uri: str = "bolt://localhost:7687",
    username: str = "neo4j",
    password: str = "neo4j",
    database: str = "neo4j",
    **kwargs
) -> Neo4jClient:
    """Create Neo4j client with connection parameters."""
    config = Neo4jConfig(
        uri=uri, username=username, password=password, database=database, **kwargs
    )
    return Neo4jClient(config)


def create_neo4j_client_from_env() -> Neo4jClient:
    """Create Neo4j client from environment variables."""
    import os
    
    config = Neo4jConfig(
        uri=os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
        username=os.getenv('NEO4J_USERNAME', 'neo4j'),
        password=os.getenv('NEO4J_PASSWORD', 'neo4j'),
        database=os.getenv('NEO4J_DATABASE', 'neo4j')
    )
    return Neo4jClient(config)


