"""
DataGuild PostgreSQL Client

Comprehensive PostgreSQL client for storing and querying metadata entities,
schemas, usage statistics, and operational data with full JSON support.
"""

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union, Tuple
from dataclasses import dataclass, asdict
import psycopg2
from psycopg2.extras import RealDictCursor, Json
from psycopg2.pool import SimpleConnectionPool
import threading

logger = logging.getLogger(__name__)


@dataclass
class PostgreSQLConfig:
    """Configuration for PostgreSQL connection."""
    host: str = "localhost"
    port: int = 5432
    database: str = "dataguild"
    username: str = "dataguild"
    password: str = "dataguild"
    min_connections: int = 1
    max_connections: int = 10
    ssl_mode: str = "prefer"


class PostgreSQLClient:
    """
    Comprehensive PostgreSQL client for DataGuild metadata storage.
    
    Provides connection pooling, transaction management, and specialized
    methods for storing and querying metadata entities, lineage, and usage data.
    """
    
    def __init__(self, config: Union[PostgreSQLConfig, Dict[str, Any]]):
        """
        Initialize PostgreSQL client.
        
        Args:
            config: PostgreSQL configuration object or dictionary
        """
        if isinstance(config, dict):
            config = PostgreSQLConfig(**config)
        
        self.config = config
        self._pool: Optional[SimpleConnectionPool] = None
        self._lock = threading.Lock()
        
        # Initialize connection pool
        self._init_connection_pool()
        
        # Create database schema
        self._create_schema()
    
    def _init_connection_pool(self) -> None:
        """Initialize connection pool."""
        try:
            self._pool = SimpleConnectionPool(
                minconn=self.config.min_connections,
                maxconn=self.config.max_connections,
                host=self.config.host,
                port=self.config.port,
                database=self.config.database,
                user=self.config.username,
                password=self.config.password,
                sslmode=self.config.ssl_mode
            )
            logger.info(f"PostgreSQL connection pool initialized: {self.config.host}:{self.config.port}/{self.config.database}")
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL connection pool: {e}")
            raise
    
    def _get_connection(self):
        """Get connection from pool."""
        if not self._pool:
            raise RuntimeError("Connection pool not initialized")
        return self._pool.getconn()
    
    def _return_connection(self, conn):
        """Return connection to pool."""
        if self._pool:
            self._pool.putconn(conn)
    
    def _create_schema(self) -> None:
        """Create database schema if it doesn't exist."""
        schema_sql = """
        -- Enable UUID extension
        CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
        
        -- Create custom types
        DO $$ BEGIN
            CREATE TYPE entity_type AS ENUM (
                'DATASET', 'CONTAINER', 'TAG', 'DATAJOB', 'DATAFLOW', 
                'USER', 'GROUP', 'GLOSSARY_TERM', 'DOMAIN'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
        
        DO $$ BEGIN
            CREATE TYPE dataset_type AS ENUM (
                'TABLE', 'VIEW', 'MATERIALIZED_VIEW', 'EXTERNAL_TABLE', 
                'TRANSIENT', 'BASE_TABLE'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
        
        DO $$ BEGIN
            CREATE TYPE lineage_direction AS ENUM (
                'UPSTREAM', 'DOWNSTREAM', 'BOTH'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
        
        -- Core entities table
        CREATE TABLE IF NOT EXISTS entities (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            urn VARCHAR(500) UNIQUE NOT NULL,
            entity_type entity_type NOT NULL,
            name VARCHAR(255) NOT NULL,
            platform VARCHAR(100),
            description TEXT,
            metadata JSONB DEFAULT '{}',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            created_by VARCHAR(255),
            updated_by VARCHAR(255)
        );
        
        -- Create indexes for entities
        CREATE INDEX IF NOT EXISTS idx_entities_urn ON entities(urn);
        CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(entity_type);
        CREATE INDEX IF NOT EXISTS idx_entities_platform ON entities(platform);
        CREATE INDEX IF NOT EXISTS idx_entities_metadata ON entities USING GIN(metadata);
        
        -- Databases table
        CREATE TABLE IF NOT EXISTS databases (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            entity_id UUID REFERENCES entities(id) ON DELETE CASCADE,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            platform VARCHAR(100),
            properties JSONB DEFAULT '{}',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        -- Schemas table
        CREATE TABLE IF NOT EXISTS schemas (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            entity_id UUID REFERENCES entities(id) ON DELETE CASCADE,
            database_id UUID REFERENCES databases(id) ON DELETE CASCADE,
            name VARCHAR(255) NOT NULL,
            full_name VARCHAR(500) NOT NULL,
            description TEXT,
            properties JSONB DEFAULT '{}',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        -- Datasets table (tables, views, etc.)
        CREATE TABLE IF NOT EXISTS datasets (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            entity_id UUID REFERENCES entities(id) ON DELETE CASCADE,
            database_id UUID REFERENCES databases(id) ON DELETE CASCADE,
            schema_id UUID REFERENCES schemas(id) ON DELETE CASCADE,
            name VARCHAR(255) NOT NULL,
            full_name VARCHAR(500) NOT NULL,
            dataset_type dataset_type NOT NULL,
            description TEXT,
            properties JSONB DEFAULT '{}',
            custom_properties JSONB DEFAULT '{}',
            tags JSONB DEFAULT '[]',
            created_at TIMESTAMP WITH TIME ZONE,
            updated_at TIMESTAMP WITH TIME ZONE,
            last_modified TIMESTAMP WITH TIME ZONE,
            row_count BIGINT,
            size_bytes BIGINT,
            is_partitioned BOOLEAN DEFAULT FALSE,
            partition_keys JSONB DEFAULT '[]',
            storage_format VARCHAR(100),
            location VARCHAR(1000),
            owner VARCHAR(255)
        );
        
        -- Create indexes for datasets
        CREATE INDEX IF NOT EXISTS idx_datasets_entity_id ON datasets(entity_id);
        CREATE INDEX IF NOT EXISTS idx_datasets_full_name ON datasets(full_name);
        CREATE INDEX IF NOT EXISTS idx_datasets_type ON datasets(dataset_type);
        CREATE INDEX IF NOT EXISTS idx_datasets_properties ON datasets USING GIN(properties);
        CREATE INDEX IF NOT EXISTS idx_datasets_tags ON datasets USING GIN(tags);
        
        -- Columns table
        CREATE TABLE IF NOT EXISTS columns (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            dataset_id UUID REFERENCES datasets(id) ON DELETE CASCADE,
            name VARCHAR(255) NOT NULL,
            position INTEGER,
            data_type VARCHAR(100),
            native_data_type VARCHAR(100),
            description TEXT,
            nullable BOOLEAN DEFAULT TRUE,
            is_primary_key BOOLEAN DEFAULT FALSE,
            is_foreign_key BOOLEAN DEFAULT FALSE,
            default_value TEXT,
            properties JSONB DEFAULT '{}',
            tags JSONB DEFAULT '[]',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        -- Create indexes for columns
        CREATE INDEX IF NOT EXISTS idx_columns_dataset_id ON columns(dataset_id);
        CREATE INDEX IF NOT EXISTS idx_columns_name ON columns(name);
        CREATE INDEX IF NOT EXISTS idx_columns_data_type ON columns(data_type);
        CREATE INDEX IF NOT EXISTS idx_columns_properties ON columns USING GIN(properties);
        
        -- Lineage relationships table (for PostgreSQL-based lineage queries)
        CREATE TABLE IF NOT EXISTS lineage_relationships (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            source_entity_id UUID REFERENCES entities(id) ON DELETE CASCADE,
            target_entity_id UUID REFERENCES entities(id) ON DELETE CASCADE,
            relationship_type VARCHAR(100) NOT NULL,
            direction lineage_direction NOT NULL,
            confidence_score FLOAT DEFAULT 1.0,
            is_manual BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            created_by VARCHAR(255),
            metadata JSONB DEFAULT '{}',
            UNIQUE(source_entity_id, target_entity_id, relationship_type)
        );
        
        -- Create indexes for lineage
        CREATE INDEX IF NOT EXISTS idx_lineage_source ON lineage_relationships(source_entity_id);
        CREATE INDEX IF NOT EXISTS idx_lineage_target ON lineage_relationships(target_entity_id);
        CREATE INDEX IF NOT EXISTS idx_lineage_type ON lineage_relationships(relationship_type);
        CREATE INDEX IF NOT EXISTS idx_lineage_direction ON lineage_relationships(direction);
        
        -- Usage statistics table
        CREATE TABLE IF NOT EXISTS usage_stats (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            entity_id UUID REFERENCES entities(id) ON DELETE CASCADE,
            timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
            query_count INTEGER DEFAULT 0,
            unique_user_count INTEGER DEFAULT 0,
            total_sql_queries INTEGER DEFAULT 0,
            bytes_read BIGINT DEFAULT 0,
            bytes_written BIGINT DEFAULT 0,
            top_sql_queries JSONB DEFAULT '[]',
            user_counts JSONB DEFAULT '[]',
            field_counts JSONB DEFAULT '[]',
            metrics JSONB DEFAULT '{}',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        -- Create indexes for usage stats
        CREATE INDEX IF NOT EXISTS idx_usage_entity_id ON usage_stats(entity_id);
        CREATE INDEX IF NOT EXISTS idx_usage_timestamp ON usage_stats(timestamp);
        CREATE INDEX IF NOT EXISTS idx_usage_metrics ON usage_stats USING GIN(metrics);
        
        -- Operational events table
        CREATE TABLE IF NOT EXISTS operational_events (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            entity_id UUID REFERENCES entities(id) ON DELETE CASCADE,
            event_type VARCHAR(100) NOT NULL,
            operation_type VARCHAR(100),
            actor VARCHAR(255),
            timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
            duration_ms INTEGER,
            status VARCHAR(50),
            error_message TEXT,
            metadata JSONB DEFAULT '{}',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        -- Create indexes for operational events
        CREATE INDEX IF NOT EXISTS idx_ops_entity_id ON operational_events(entity_id);
        CREATE INDEX IF NOT EXISTS idx_ops_event_type ON operational_events(event_type);
        CREATE INDEX IF NOT EXISTS idx_ops_timestamp ON operational_events(timestamp);
        CREATE INDEX IF NOT EXISTS idx_ops_metadata ON operational_events USING GIN(metadata);
        
        -- Tags table
        CREATE TABLE IF NOT EXISTS tags (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            entity_id UUID REFERENCES entities(id) ON DELETE CASCADE,
            tag_name VARCHAR(255) NOT NULL,
            tag_urn VARCHAR(500),
            description TEXT,
            properties JSONB DEFAULT '{}',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            created_by VARCHAR(255)
        );
        
        -- Create indexes for tags
        CREATE INDEX IF NOT EXISTS idx_tags_entity_id ON tags(entity_id);
        CREATE INDEX IF NOT EXISTS idx_tags_name ON tags(tag_name);
        CREATE INDEX IF NOT EXISTS idx_tags_urn ON tags(tag_urn);
        
        -- Create update triggers
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
        
        -- Apply update triggers
        DROP TRIGGER IF EXISTS update_entities_updated_at ON entities;
        CREATE TRIGGER update_entities_updated_at
            BEFORE UPDATE ON entities
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
            
        DROP TRIGGER IF EXISTS update_datasets_updated_at ON datasets;
        CREATE TRIGGER update_datasets_updated_at
            BEFORE UPDATE ON datasets
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
            
        DROP TRIGGER IF EXISTS update_columns_updated_at ON columns;
        CREATE TRIGGER update_columns_updated_at
            BEFORE UPDATE ON columns
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        """
        
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(schema_sql)
                conn.commit()
                logger.info("PostgreSQL schema created successfully")
        except Exception as e:
            logger.error(f"Failed to create PostgreSQL schema: {e}")
            conn.rollback()
            raise
        finally:
            self._return_connection(conn)
    
    def store_entity(self, entity_data: Dict[str, Any]) -> str:
        """
        Store an entity in the database.
        
        Args:
            entity_data: Entity data dictionary
            
        Returns:
            Entity ID
        """
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                # Insert entity
                cursor.execute("""
                    INSERT INTO entities (urn, entity_type, name, platform, description, metadata, created_by)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (urn) DO UPDATE SET
                        entity_type = EXCLUDED.entity_type,
                        name = EXCLUDED.name,
                        platform = EXCLUDED.platform,
                        description = EXCLUDED.description,
                        metadata = EXCLUDED.metadata,
                        updated_at = NOW()
                    RETURNING id
                """, (
                    entity_data.get('urn'),
                    entity_data.get('entity_type', 'DATASET'),
                    entity_data.get('name'),
                    entity_data.get('platform'),
                    entity_data.get('description'),
                    Json(entity_data.get('metadata', {})),
                    entity_data.get('created_by')
                ))
                
                entity_id = cursor.fetchone()[0]
                conn.commit()
                return str(entity_id)
                
        except Exception as e:
            logger.error(f"Failed to store entity: {e}")
            conn.rollback()
            raise
        finally:
            self._return_connection(conn)
    
    def store_dataset(self, dataset_data: Dict[str, Any], entity_id: str) -> str:
        """
        Store a dataset (table/view) in the database.
        
        Args:
            dataset_data: Dataset data dictionary
            entity_id: Parent entity ID
            
        Returns:
            Dataset ID
        """
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                # Get or create database
                database_id = self._get_or_create_database(cursor, dataset_data)
                
                # Get or create schema
                schema_id = self._get_or_create_schema(cursor, dataset_data, database_id)
                
                # Insert dataset
                cursor.execute("""
                    INSERT INTO datasets (
                        entity_id, database_id, schema_id, name, full_name, dataset_type,
                        description, properties, custom_properties, tags, created_at,
                        updated_at, last_modified, row_count, size_bytes, is_partitioned,
                        partition_keys, storage_format, location, owner
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    ON CONFLICT (entity_id) DO UPDATE SET
                        name = EXCLUDED.name,
                        full_name = EXCLUDED.full_name,
                        dataset_type = EXCLUDED.dataset_type,
                        description = EXCLUDED.description,
                        properties = EXCLUDED.properties,
                        custom_properties = EXCLUDED.custom_properties,
                        tags = EXCLUDED.tags,
                        updated_at = NOW(),
                        last_modified = EXCLUDED.last_modified,
                        row_count = EXCLUDED.row_count,
                        size_bytes = EXCLUDED.size_bytes
                    RETURNING id
                """, (
                    entity_id,
                    database_id,
                    schema_id,
                    dataset_data.get('name'),
                    dataset_data.get('full_name', dataset_data.get('name')),
                    dataset_data.get('type', 'TABLE'),
                    dataset_data.get('description'),
                    Json(dataset_data.get('properties', {})),
                    Json(dataset_data.get('custom_properties', {})),
                    Json(dataset_data.get('tags', [])),
                    dataset_data.get('created'),
                    dataset_data.get('last_modified'),
                    dataset_data.get('last_modified'),
                    dataset_data.get('row_count'),
                    dataset_data.get('size_bytes'),
                    dataset_data.get('is_partitioned', False),
                    Json(dataset_data.get('partition_keys', [])),
                    dataset_data.get('storage_format'),
                    dataset_data.get('location'),
                    dataset_data.get('owner')
                ))
                
                dataset_id = cursor.fetchone()[0]
                conn.commit()
                return str(dataset_id)
                
        except Exception as e:
            logger.error(f"Failed to store dataset: {e}")
            conn.rollback()
            raise
        finally:
            self._return_connection(conn)
    
    def store_columns(self, columns_data: List[Dict[str, Any]], dataset_id: str) -> None:
        """
        Store columns for a dataset.
        
        Args:
            columns_data: List of column data dictionaries
            dataset_id: Parent dataset ID
        """
        if not columns_data:
            return
            
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                # Clear existing columns
                cursor.execute("DELETE FROM columns WHERE dataset_id = %s", (dataset_id,))
                
                # Insert new columns
                for i, column_data in enumerate(columns_data):
                    cursor.execute("""
                        INSERT INTO columns (
                            dataset_id, name, position, data_type, native_data_type,
                            description, nullable, is_primary_key, is_foreign_key,
                            default_value, properties, tags
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                    """, (
                        dataset_id,
                        column_data.get('name'),
                        i + 1,
                        column_data.get('type', {}).get('type_name') if isinstance(column_data.get('type'), dict) else column_data.get('type'),
                        column_data.get('nativeDataType'),
                        column_data.get('description'),
                        column_data.get('nullable', True),
                        column_data.get('is_primary_key', False),
                        column_data.get('is_foreign_key', False),
                        column_data.get('default_value'),
                        Json(column_data.get('properties', {})),
                        Json(column_data.get('tags', []))
                    ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to store columns: {e}")
            conn.rollback()
            raise
        finally:
            self._return_connection(conn)
    
    def store_usage_stats(self, usage_data: Dict[str, Any], entity_id: str) -> str:
        """
        Store usage statistics for an entity.
        
        Args:
            usage_data: Usage statistics data
            entity_id: Entity ID
            
        Returns:
            Usage stats ID
        """
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO usage_stats (
                        entity_id, timestamp, query_count, unique_user_count,
                        total_sql_queries, bytes_read, bytes_written,
                        top_sql_queries, user_counts, field_counts, metrics
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    RETURNING id
                """, (
                    entity_id,
                    usage_data.get('timestamp'),
                    usage_data.get('query_count', 0),
                    usage_data.get('unique_user_count', 0),
                    usage_data.get('total_sql_queries', 0),
                    usage_data.get('bytes_read', 0),
                    usage_data.get('bytes_written', 0),
                    Json(usage_data.get('top_sql_queries', [])),
                    Json(usage_data.get('user_counts', [])),
                    Json(usage_data.get('field_counts', [])),
                    Json(usage_data.get('metrics', {}))
                ))
                
                usage_id = cursor.fetchone()[0]
                conn.commit()
                return str(usage_id)
                
        except Exception as e:
            logger.error(f"Failed to store usage stats: {e}")
            conn.rollback()
            raise
        finally:
            self._return_connection(conn)
    
    def store_lineage_relationship(self, source_urn: str, target_urn: str, 
                                 relationship_type: str, direction: str = "DOWNSTREAM",
                                 confidence: float = 1.0, metadata: Dict[str, Any] = None) -> str:
        """
        Store a lineage relationship between entities.
        
        Args:
            source_urn: Source entity URN
            target_urn: Target entity URN
            relationship_type: Type of relationship
            direction: Direction of relationship
            confidence: Confidence score
            metadata: Additional metadata
            
        Returns:
            Relationship ID
        """
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                # Get entity IDs
                source_id = self._get_entity_id_by_urn(cursor, source_urn)
                target_id = self._get_entity_id_by_urn(cursor, target_urn)
                
                if not source_id or not target_id:
                    raise ValueError(f"Entity not found: {source_urn} or {target_urn}")
                
                cursor.execute("""
                    INSERT INTO lineage_relationships (
                        source_entity_id, target_entity_id, relationship_type,
                        direction, confidence_score, metadata
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (source_entity_id, target_entity_id, relationship_type)
                    DO UPDATE SET
                        direction = EXCLUDED.direction,
                        confidence_score = EXCLUDED.confidence_score,
                        metadata = EXCLUDED.metadata,
                        updated_at = NOW()
                    RETURNING id
                """, (
                    source_id, target_id, relationship_type, direction,
                    confidence, Json(metadata or {})
                ))
                
                relationship_id = cursor.fetchone()[0]
                conn.commit()
                return str(relationship_id)
                
        except Exception as e:
            logger.error(f"Failed to store lineage relationship: {e}")
            conn.rollback()
            raise
        finally:
            self._return_connection(conn)
    
    def get_entity_by_urn(self, urn: str) -> Optional[Dict[str, Any]]:
        """Get entity by URN."""
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM entities WHERE urn = %s
                """, (urn,))
                result = cursor.fetchone()
                return dict(result) if result else None
        except Exception as e:
            logger.error(f"Failed to get entity by URN: {e}")
            return None
        finally:
            self._return_connection(conn)
    
    def get_dataset_with_columns(self, dataset_urn: str) -> Optional[Dict[str, Any]]:
        """Get dataset with its columns."""
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # Get dataset
                cursor.execute("""
                    SELECT d.*, e.urn, e.entity_type, e.name as entity_name
                    FROM datasets d
                    JOIN entities e ON d.entity_id = e.id
                    WHERE e.urn = %s
                """, (dataset_urn,))
                dataset = cursor.fetchone()
                
                if not dataset:
                    return None
                
                # Get columns
                cursor.execute("""
                    SELECT * FROM columns 
                    WHERE dataset_id = %s 
                    ORDER BY position
                """, (dataset['id'],))
                columns = cursor.fetchall()
                
                dataset_dict = dict(dataset)
                dataset_dict['columns'] = [dict(col) for col in columns]
                return dataset_dict
                
        except Exception as e:
            logger.error(f"Failed to get dataset with columns: {e}")
            return None
        finally:
            self._return_connection(conn)
    
    def search_entities(self, query: str, entity_type: Optional[str] = None, 
                       platform: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Search entities with filters."""
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                where_conditions = ["(e.name ILIKE %s OR e.description ILIKE %s)"]
                params = [f"%{query}%", f"%{query}%"]
                
                if entity_type:
                    where_conditions.append("e.entity_type = %s")
                    params.append(entity_type)
                
                if platform:
                    where_conditions.append("e.platform = %s")
                    params.append(platform)
                
                sql = f"""
                    SELECT e.*, d.name as dataset_name, d.dataset_type
                    FROM entities e
                    LEFT JOIN datasets d ON e.id = d.entity_id
                    WHERE {' AND '.join(where_conditions)}
                    ORDER BY e.updated_at DESC
                    LIMIT %s
                """
                params.append(limit)
                
                cursor.execute(sql, params)
                results = cursor.fetchall()
                return [dict(row) for row in results]
                
        except Exception as e:
            logger.error(f"Failed to search entities: {e}")
            return []
        finally:
            self._return_connection(conn)
    
    def get_lineage_relationships(self, entity_urn: str, direction: str = "BOTH") -> List[Dict[str, Any]]:
        """Get lineage relationships for an entity."""
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                entity_id = self._get_entity_id_by_urn(cursor, entity_urn)
                if not entity_id:
                    return []
                
                if direction == "BOTH":
                    where_clause = "(source_entity_id = %s OR target_entity_id = %s)"
                    params = [entity_id, entity_id]
                elif direction == "UPSTREAM":
                    where_clause = "target_entity_id = %s"
                    params = [entity_id]
                else:  # DOWNSTREAM
                    where_clause = "source_entity_id = %s"
                    params = [entity_id]
                
                cursor.execute(f"""
                    SELECT lr.*, 
                           se.urn as source_urn, se.name as source_name,
                           te.urn as target_urn, te.name as target_name
                    FROM lineage_relationships lr
                    JOIN entities se ON lr.source_entity_id = se.id
                    JOIN entities te ON lr.target_entity_id = te.id
                    WHERE {where_clause}
                    ORDER BY lr.created_at DESC
                """, params)
                
                results = cursor.fetchall()
                return [dict(row) for row in results]
                
        except Exception as e:
            logger.error(f"Failed to get lineage relationships: {e}")
            return []
        finally:
            self._return_connection(conn)
    
    def _get_or_create_database(self, cursor, dataset_data: Dict[str, Any]) -> str:
        """Get or create database record."""
        database_name = dataset_data.get('database', 'default')
        
        cursor.execute("""
            SELECT id FROM databases WHERE name = %s
        """, (database_name,))
        result = cursor.fetchone()
        
        if result:
            return result[0]
        
        # Create new database
        cursor.execute("""
            INSERT INTO databases (name, description, platform)
            VALUES (%s, %s, %s)
            RETURNING id
        """, (database_name, f"Database: {database_name}", dataset_data.get('platform')))
        
        return cursor.fetchone()[0]
    
    def _get_or_create_schema(self, cursor, dataset_data: Dict[str, Any], database_id: str) -> str:
        """Get or create schema record."""
        schema_name = dataset_data.get('schema', 'public')
        full_name = f"{dataset_data.get('database', 'default')}.{schema_name}"
        
        cursor.execute("""
            SELECT id FROM schemas WHERE full_name = %s
        """, (full_name,))
        result = cursor.fetchone()
        
        if result:
            return result[0]
        
        # Create new schema
        cursor.execute("""
            INSERT INTO schemas (database_id, name, full_name, description)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (database_id, schema_name, full_name, f"Schema: {full_name}"))
        
        return cursor.fetchone()[0]
    
    def _get_entity_id_by_urn(self, cursor, urn: str) -> Optional[str]:
        """Get entity ID by URN."""
        cursor.execute("SELECT id FROM entities WHERE urn = %s", (urn,))
        result = cursor.fetchone()
        return result[0] if result else None
    
    def close(self) -> None:
        """Close connection pool."""
        if self._pool:
            self._pool.closeall()
            logger.info("PostgreSQL connection pool closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def __repr__(self) -> str:
        """String representation."""
        return f"PostgreSQLClient(host='{self.config.host}', database='{self.config.database}')"


# Convenience factory functions
def create_postgresql_client(
    host: str = "localhost",
    port: int = 5432,
    database: str = "dataguild",
    username: str = "dataguild",
    password: str = "dataguild",
    **kwargs
) -> PostgreSQLClient:
    """Create PostgreSQL client with connection parameters."""
    config = PostgreSQLConfig(
        host=host, port=port, database=database,
        username=username, password=password, **kwargs
    )
    return PostgreSQLClient(config)


def create_postgresql_client_from_env() -> PostgreSQLClient:
    """Create PostgreSQL client from environment variables."""
    import os
    
    config = PostgreSQLConfig(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        port=int(os.getenv('POSTGRES_PORT', '5432')),
        database=os.getenv('POSTGRES_DB', 'dataguild'),
        username=os.getenv('POSTGRES_USER', 'dataguild'),
        password=os.getenv('POSTGRES_PASSWORD', 'dataguild')
    )
    return PostgreSQLClient(config)


