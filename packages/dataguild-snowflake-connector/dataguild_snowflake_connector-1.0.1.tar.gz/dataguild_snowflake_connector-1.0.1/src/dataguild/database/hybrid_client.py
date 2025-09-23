"""
DataGuild Hybrid Database Client

Unified client for querying both PostgreSQL (metadata) and Neo4j (lineage)
databases with intelligent query routing and combined result aggregation.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union, Tuple
from dataclasses import dataclass

from dataguild.database.postgresql_client import PostgreSQLClient, PostgreSQLConfig
from dataguild.database.neo4j_client import Neo4jClient, Neo4jConfig

logger = logging.getLogger(__name__)


@dataclass
class HybridQueryResult:
    """Result from hybrid database query."""
    data: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    query_type: str
    execution_time_ms: float
    sources: List[str]  # Which databases were queried


class DataGuildHybridClient:
    """
    Unified client for DataGuild metadata and lineage operations.
    
    Provides intelligent query routing between PostgreSQL (structured data)
    and Neo4j (graph relationships) with combined result aggregation.
    """
    
    def __init__(self, postgres_config: Optional[Union[PostgreSQLConfig, Dict[str, Any]]] = None,
                 neo4j_config: Optional[Union[Neo4jConfig, Dict[str, Any]]] = None):
        """
        Initialize hybrid client.
        
        Args:
            postgres_config: PostgreSQL configuration
            neo4j_config: Neo4j configuration
        """
        self.postgres_client = None
        self.neo4j_client = None
        
        # Initialize clients
        self._init_postgres_client(postgres_config)
        self._init_neo4j_client(neo4j_config)
    
    def _init_postgres_client(self, config: Optional[Union[PostgreSQLConfig, Dict[str, Any]]]) -> None:
        """Initialize PostgreSQL client."""
        try:
            if config:
                if isinstance(config, dict):
                    self.postgres_client = PostgreSQLClient(PostgreSQLConfig(**config))
                else:
                    self.postgres_client = PostgreSQLClient(config)
            else:
                from dataguild.database.postgresql_client import create_postgresql_client_from_env
                self.postgres_client = create_postgresql_client_from_env()
            logger.info("PostgreSQL client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL client: {e}")
            raise
    
    def _init_neo4j_client(self, config: Optional[Union[Neo4jConfig, Dict[str, Any]]]) -> None:
        """Initialize Neo4j client."""
        try:
            if config:
                if isinstance(config, dict):
                    self.neo4j_client = Neo4jClient(Neo4jConfig(**config))
                else:
                    self.neo4j_client = Neo4jClient(config)
            else:
                from dataguild.database.neo4j_client import create_neo4j_client_from_env
                self.neo4j_client = create_neo4j_client_from_env()
            logger.info("Neo4j client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Neo4j client: {e}")
            raise
    
    def get_entity_complete(self, urn: str) -> Optional[Dict[str, Any]]:
        """
        Get complete entity information from both databases.
        
        Args:
            urn: Entity URN
            
        Returns:
            Complete entity data with metadata and lineage
        """
        start_time = datetime.now()
        
        try:
            # Get basic entity info from PostgreSQL
            entity = self.postgres_client.get_entity_by_urn(urn)
            if not entity:
                return None
            
            # Get lineage from Neo4j
            lineage_graph = self.neo4j_client.get_lineage_graph(urn, max_depth=3)
            
            # Get usage stats from PostgreSQL
            usage_stats = self._get_usage_stats_for_entity(urn)
            
            # Get operational events from PostgreSQL
            operational_events = self._get_operational_events_for_entity(urn)
            
            # Combine results
            complete_entity = {
                **entity,
                'lineage': lineage_graph,
                'usage_stats': usage_stats,
                'operational_events': operational_events,
                'last_updated': datetime.now(timezone.utc).isoformat()
            }
            
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return HybridQueryResult(
                data=[complete_entity],
                metadata={
                    'query_type': 'entity_complete',
                    'urn': urn,
                    'sources_queried': ['postgresql', 'neo4j']
                },
                query_type='entity_complete',
                execution_time_ms=execution_time,
                sources=['postgresql', 'neo4j']
            )
            
        except Exception as e:
            logger.error(f"Failed to get complete entity {urn}: {e}")
            return None
    
    def search_entities_advanced(self, query: str, entity_type: Optional[str] = None,
                                platform: Optional[str] = None, include_lineage: bool = False,
                                limit: int = 100) -> HybridQueryResult:
        """
        Advanced entity search with optional lineage information.
        
        Args:
            query: Search query
            entity_type: Filter by entity type
            platform: Filter by platform
            include_lineage: Whether to include lineage information
            limit: Maximum results
            
        Returns:
            Search results with optional lineage
        """
        start_time = datetime.now()
        
        try:
            # Search entities in PostgreSQL
            entities = self.postgres_client.search_entities(
                query, entity_type, platform, limit
            )
            
            # Add lineage information if requested
            if include_lineage:
                for entity in entities:
                    urn = entity.get('urn')
                    if urn:
                        lineage = self.neo4j_client.get_lineage_graph(urn, max_depth=2)
                        entity['lineage_summary'] = {
                            'upstream_count': len([r for r in lineage.get('relationships', []) 
                                                 if r.get('source') == urn]),
                            'downstream_count': len([r for r in lineage.get('relationships', []) 
                                                   if r.get('target') == urn])
                        }
            
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return HybridQueryResult(
                data=entities,
                metadata={
                    'query_type': 'entity_search',
                    'query': query,
                    'entity_type': entity_type,
                    'platform': platform,
                    'include_lineage': include_lineage,
                    'total_results': len(entities)
                },
                query_type='entity_search',
                execution_time_ms=execution_time,
                sources=['postgresql'] + (['neo4j'] if include_lineage else [])
            )
            
        except Exception as e:
            logger.error(f"Failed to search entities: {e}")
            return HybridQueryResult(
                data=[], metadata={'error': str(e)}, query_type='entity_search',
                execution_time_ms=0, sources=[]
            )
    
    def get_lineage_impact_analysis(self, entity_urn: str, max_depth: int = 5) -> HybridQueryResult:
        """
        Get comprehensive impact analysis for an entity.
        
        Args:
            entity_urn: Entity URN
            max_depth: Maximum depth to analyze
            
        Returns:
            Impact analysis with both upstream and downstream effects
        """
        start_time = datetime.now()
        
        try:
            # Get impact analysis from Neo4j
            impact_analysis = self.neo4j_client.find_impact_analysis(entity_urn, max_depth)
            
            # Get detailed entity information from PostgreSQL
            center_entity = self.postgres_client.get_entity_by_urn(entity_urn)
            
            # Enrich downstream entities with metadata
            enriched_downstream = []
            for item in impact_analysis.get('downstream_impact', []):
                entity = item['entity']
                entity_urn = entity.get('urn')
                if entity_urn:
                    detailed_entity = self.postgres_client.get_entity_by_urn(entity_urn)
                    if detailed_entity:
                        enriched_downstream.append({
                            **item,
                            'entity': {**entity, **detailed_entity}
                        })
                    else:
                        enriched_downstream.append(item)
            
            # Enrich upstream entities with metadata
            enriched_upstream = []
            for item in impact_analysis.get('upstream_dependencies', []):
                entity = item['entity']
                entity_urn = entity.get('urn')
                if entity_urn:
                    detailed_entity = self.postgres_client.get_entity_by_urn(entity_urn)
                    if detailed_entity:
                        enriched_upstream.append({
                            **item,
                            'entity': {**entity, **detailed_entity}
                        })
                    else:
                        enriched_upstream.append(item)
            
            # Combine results
            result_data = {
                'center_entity': center_entity,
                'downstream_impact': enriched_downstream,
                'upstream_dependencies': enriched_upstream,
                'summary': {
                    'total_downstream': len(enriched_downstream),
                    'total_upstream': len(enriched_upstream),
                    'max_depth_analyzed': max_depth
                }
            }
            
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return HybridQueryResult(
                data=[result_data],
                metadata={
                    'query_type': 'impact_analysis',
                    'entity_urn': entity_urn,
                    'max_depth': max_depth
                },
                query_type='impact_analysis',
                execution_time_ms=execution_time,
                sources=['postgresql', 'neo4j']
            )
            
        except Exception as e:
            logger.error(f"Failed to get impact analysis for {entity_urn}: {e}")
            return HybridQueryResult(
                data=[], metadata={'error': str(e)}, query_type='impact_analysis',
                execution_time_ms=0, sources=[]
            )
    
    def get_column_lineage_detailed(self, column_urn: str, max_depth: int = 3) -> HybridQueryResult:
        """
        Get detailed column-level lineage information.
        
        Args:
            column_urn: Column URN
            max_depth: Maximum depth to traverse
            
        Returns:
            Detailed column lineage with metadata
        """
        start_time = datetime.now()
        
        try:
            # Get column lineage from Neo4j
            column_lineage = self.neo4j_client.get_column_lineage(column_urn, max_depth)
            
            # Enrich column nodes with detailed metadata from PostgreSQL
            enriched_nodes = []
            for node in column_lineage.get('nodes', []):
                node_urn = node.get('urn')
                if node_urn:
                    # Extract dataset URN from column URN
                    dataset_urn = ':'.join(node_urn.split(':')[:-1])
                    dataset_info = self.postgres_client.get_dataset_with_columns(dataset_urn)
                    if dataset_info:
                        # Find the specific column
                        for col in dataset_info.get('columns', []):
                            if col.get('name') == node.get('name'):
                                enriched_nodes.append({**node, **col})
                                break
                        else:
                            enriched_nodes.append(node)
                    else:
                        enriched_nodes.append(node)
                else:
                    enriched_nodes.append(node)
            
            # Combine results
            result_data = {
                'column_lineage': {
                    **column_lineage,
                    'nodes': enriched_nodes
                },
                'summary': {
                    'total_columns': len(enriched_nodes),
                    'total_relationships': len(column_lineage.get('relationships', [])),
                    'max_depth': max_depth
                }
            }
            
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return HybridQueryResult(
                data=[result_data],
                metadata={
                    'query_type': 'column_lineage',
                    'column_urn': column_urn,
                    'max_depth': max_depth
                },
                query_type='column_lineage',
                execution_time_ms=execution_time,
                sources=['postgresql', 'neo4j']
            )
            
        except Exception as e:
            logger.error(f"Failed to get column lineage for {column_urn}: {e}")
            return HybridQueryResult(
                data=[], metadata={'error': str(e)}, query_type='column_lineage',
                execution_time_ms=0, sources=[]
            )
    
    def get_usage_analytics(self, entity_urn: Optional[str] = None, 
                           time_range: str = "WEEK") -> HybridQueryResult:
        """
        Get usage analytics for entities.
        
        Args:
            entity_urn: Optional specific entity URN
            time_range: Time range for analytics
            
        Returns:
            Usage analytics data
        """
        start_time = datetime.now()
        
        try:
            if entity_urn:
                # Get usage for specific entity
                usage_stats = self._get_usage_stats_for_entity(entity_urn)
                result_data = {
                    'entity_urn': entity_urn,
                    'usage_stats': usage_stats
                }
            else:
                # Get aggregate usage statistics
                result_data = self._get_aggregate_usage_stats()
            
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return HybridQueryResult(
                data=[result_data],
                metadata={
                    'query_type': 'usage_analytics',
                    'entity_urn': entity_urn,
                    'time_range': time_range
                },
                query_type='usage_analytics',
                execution_time_ms=execution_time,
                sources=['postgresql']
            )
            
        except Exception as e:
            logger.error(f"Failed to get usage analytics: {e}")
            return HybridQueryResult(
                data=[], metadata={'error': str(e)}, query_type='usage_analytics',
                execution_time_ms=0, sources=[]
            )
    
    def get_database_statistics(self) -> HybridQueryResult:
        """
        Get comprehensive database statistics.
        
        Returns:
            Statistics from both databases
        """
        start_time = datetime.now()
        
        try:
            # Get PostgreSQL statistics
            postgres_stats = self._get_postgres_statistics()
            
            # Get Neo4j statistics
            neo4j_stats = self.neo4j_client.get_entity_statistics()
            
            # Combine statistics
            result_data = {
                'postgresql': postgres_stats,
                'neo4j': neo4j_stats,
                'summary': {
                    'total_entities': postgres_stats.get('total_entities', 0),
                    'total_datasets': postgres_stats.get('total_datasets', 0),
                    'total_columns': postgres_stats.get('total_columns', 0),
                    'total_lineage_relationships': neo4j_stats.get('total_relationships', 0)
                }
            }
            
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return HybridQueryResult(
                data=[result_data],
                metadata={
                    'query_type': 'database_statistics',
                    'sources_queried': ['postgresql', 'neo4j']
                },
                query_type='database_statistics',
                execution_time_ms=execution_time,
                sources=['postgresql', 'neo4j']
            )
            
        except Exception as e:
            logger.error(f"Failed to get database statistics: {e}")
            return HybridQueryResult(
                data=[], metadata={'error': str(e)}, query_type='database_statistics',
                execution_time_ms=0, sources=[]
            )
    
    def _get_usage_stats_for_entity(self, entity_urn: str) -> List[Dict[str, Any]]:
        """Get usage statistics for a specific entity."""
        conn = self.postgres_client._get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT us.*, e.urn, e.name as entity_name
                    FROM usage_stats us
                    JOIN entities e ON us.entity_id = e.id
                    WHERE e.urn = %s
                    ORDER BY us.timestamp DESC
                    LIMIT 100
                """, (entity_urn,))
                
                results = cursor.fetchall()
                return [dict(row) for row in results]
        finally:
            self.postgres_client._return_connection(conn)
    
    def _get_operational_events_for_entity(self, entity_urn: str) -> List[Dict[str, Any]]:
        """Get operational events for a specific entity."""
        conn = self.postgres_client._get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT oe.*, e.urn, e.name as entity_name
                    FROM operational_events oe
                    JOIN entities e ON oe.entity_id = e.id
                    WHERE e.urn = %s
                    ORDER BY oe.timestamp DESC
                    LIMIT 100
                """, (entity_urn,))
                
                results = cursor.fetchall()
                return [dict(row) for row in results]
        finally:
            self.postgres_client._return_connection(conn)
    
    def _get_aggregate_usage_stats(self) -> Dict[str, Any]:
        """Get aggregate usage statistics."""
        conn = self.postgres_client._get_connection()
        try:
            with conn.cursor() as cursor:
                # Get usage summary
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_usage_records,
                        COUNT(DISTINCT entity_id) as unique_entities,
                        SUM(query_count) as total_queries,
                        SUM(unique_user_count) as total_unique_users,
                        AVG(query_count) as avg_queries_per_entity
                    FROM usage_stats
                """)
                
                usage_summary = dict(cursor.fetchone())
                
                # Get top entities by usage
                cursor.execute("""
                    SELECT e.urn, e.name, SUM(us.query_count) as total_queries
                    FROM usage_stats us
                    JOIN entities e ON us.entity_id = e.id
                    GROUP BY e.id, e.urn, e.name
                    ORDER BY total_queries DESC
                    LIMIT 10
                """)
                
                top_entities = [dict(row) for row in cursor.fetchall()]
                
                return {
                    'usage_summary': usage_summary,
                    'top_entities_by_usage': top_entities
                }
        finally:
            self.postgres_client._return_connection(conn)
    
    def _get_postgres_statistics(self) -> Dict[str, Any]:
        """Get PostgreSQL database statistics."""
        conn = self.postgres_client._get_connection()
        try:
            with conn.cursor() as cursor:
                # Get entity counts
                cursor.execute("SELECT COUNT(*) FROM entities")
                total_entities = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM datasets")
                total_datasets = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM columns")
                total_columns = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM lineage_relationships")
                total_lineage = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM usage_stats")
                total_usage = cursor.fetchone()[0]
                
                # Get entity type distribution
                cursor.execute("""
                    SELECT entity_type, COUNT(*) as count
                    FROM entities
                    GROUP BY entity_type
                    ORDER BY count DESC
                """)
                entity_types = [dict(row) for row in cursor.fetchall()]
                
                return {
                    'total_entities': total_entities,
                    'total_datasets': total_datasets,
                    'total_columns': total_columns,
                    'total_lineage_relationships': total_lineage,
                    'total_usage_records': total_usage,
                    'entity_type_distribution': entity_types
                }
        finally:
            self.postgres_client._return_connection(conn)
    
    def close(self) -> None:
        """Close database connections."""
        if self.postgres_client:
            self.postgres_client.close()
        if self.neo4j_client:
            self.neo4j_client.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def __repr__(self) -> str:
        """String representation."""
        return f"DataGuildHybridClient(postgres={self.postgres_client is not None}, neo4j={self.neo4j_client is not None})"


# Convenience factory functions
def create_hybrid_client(
    postgres_config: Optional[Dict[str, Any]] = None,
    neo4j_config: Optional[Dict[str, Any]] = None
) -> DataGuildHybridClient:
    """Create hybrid client with optional configurations."""
    return DataGuildHybridClient(postgres_config, neo4j_config)


def create_hybrid_client_from_env() -> DataGuildHybridClient:
    """Create hybrid client from environment variables."""
    return DataGuildHybridClient()


