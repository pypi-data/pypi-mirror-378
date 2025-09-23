"""
Snowflake SQL query utilities for DataGuild ingestion.

This module provides comprehensive SQL query generation for extracting metadata,
lineage, usage statistics, and other information from Snowflake instances.
"""

import logging
from enum import Enum
from typing import List, Optional, Dict, Any

from dataguild.configuration.common import AllowDenyPattern
from dataguild.configuration.time_window_config import BucketDuration
from dataguild.source.snowflake.constants import SnowflakeObjectDomain

logger = logging.getLogger(__name__)

# Constants
SHOW_COMMAND_MAX_PAGE_SIZE = 10000
SHOW_STREAM_MAX_PAGE_SIZE = 10000
DEFAULT_TEMP_TABLES_PATTERNS = [r".*\.GE_TMP_.*", r".*\.GE_TEMP_.*", r".*_DBT_TMP"]


def create_deny_regex_sql_filter(
    deny_pattern: List[str], filter_cols: List[str]
) -> str:
    """
    Create SQL filter to exclude entries matching deny regex patterns.

    Args:
        deny_pattern: List of regex patterns to deny
        filter_cols: List of column names to apply patterns on

    Returns:
        SQL WHERE clause string
    """
    if not deny_pattern:
        return ""

    upstream_sql_filter = " AND ".join(
        [
            f"NOT RLIKE({col_name},'{regexp}','i')"
            for col_name in filter_cols
            for regexp in deny_pattern
        ]
    )

    return upstream_sql_filter


class SnowflakeQuery:
    """
    Comprehensive SQL query generator for Snowflake metadata extraction.

    This class provides static methods to generate SQL queries for extracting
    various types of metadata from Snowflake instances including tables, views,
    schemas, lineage information, usage statistics, and more.
    """

    # Domain filters for access history
    ACCESS_HISTORY_TABLE_VIEW_DOMAINS = {
        SnowflakeObjectDomain.TABLE.capitalize(),
        SnowflakeObjectDomain.EXTERNAL_TABLE.capitalize(),
        SnowflakeObjectDomain.VIEW.capitalize(),
        SnowflakeObjectDomain.MATERIALIZED_VIEW.capitalize(),
        SnowflakeObjectDomain.ICEBERG_TABLE.capitalize(),
        SnowflakeObjectDomain.STREAM.capitalize(),
        SnowflakeObjectDomain.DYNAMIC_TABLE.capitalize(),
    }

    ACCESS_HISTORY_TABLE_VIEW_DOMAINS_FILTER = "({})".format(
        ",".join(f"'{domain}'" for domain in ACCESS_HISTORY_TABLE_VIEW_DOMAINS)
    )

    # Domains that can be downstream tables in lineage
    DOWNSTREAM_TABLE_DOMAINS = {
        SnowflakeObjectDomain.TABLE.capitalize(),
        SnowflakeObjectDomain.DYNAMIC_TABLE.capitalize(),
    }

    DOWNSTREAM_TABLE_DOMAINS_FILTER = "({})".format(
        ",".join(f"'{domain}'" for domain in DOWNSTREAM_TABLE_DOMAINS)
    )

    # System information queries
    @staticmethod
    def current_account() -> str:
        """Get current Snowflake account."""
        return "SELECT CURRENT_ACCOUNT()"

    @staticmethod
    def current_region() -> str:
        """Get current Snowflake region."""
        return "SELECT CURRENT_REGION()"

    @staticmethod
    def current_version() -> str:
        """Get current Snowflake version."""
        return "SELECT CURRENT_VERSION()"

    @staticmethod
    def current_role() -> str:
        """Get current role."""
        return "SELECT CURRENT_ROLE()"

    @staticmethod
    def current_warehouse() -> str:
        """Get current warehouse."""
        return "SELECT CURRENT_WAREHOUSE()"

    # Database and schema operations
    @staticmethod
    def show_databases() -> str:
        """Show all databases."""
        return "SHOW DATABASES"

    @staticmethod
    def show_tags() -> str:
        """Show all tags."""
        return "SHOW TAGS"

    @staticmethod
    def use_database(db_name: str) -> str:
        """Use specific database."""
        return f'USE DATABASE "{db_name}"'

    @staticmethod
    def use_schema(schema_name: str) -> str:
        """Use specific schema."""
        return f'USE SCHEMA "{schema_name}"'

    @staticmethod
    def get_databases(db_name: Optional[str] = None) -> str:
        """Get database information from information schema."""
        db_clause = f'"{db_name}".' if db_name is not None else ""
        return f"""
        SELECT database_name AS "DATABASE_NAME",
               created AS "CREATED",
               last_altered AS "LAST_ALTERED",
               comment AS "COMMENT"
        FROM {db_clause}information_schema.databases
        ORDER BY database_name
        """

    @staticmethod
    def schemas_for_database(db_name: str) -> str:
        """Get schemas for a specific database."""
        return f"""
        SELECT schema_name AS "SCHEMA_NAME",
               created AS "CREATED",
               last_altered AS "LAST_ALTERED",
               comment AS "COMMENT"
        FROM information_schema.schemata
        WHERE schema_name != 'INFORMATION_SCHEMA'
        ORDER BY schema_name
        """

    @staticmethod
    def tables_for_database(db_name: str) -> str:
        """Get all tables for a database using SHOW TABLES command."""
        return f'SHOW TABLES IN DATABASE {db_name}'

    @staticmethod
    def tables_for_schema(schema_name: str, db_name: str) -> str:
        """Get tables for a specific schema using SHOW TABLES command."""
        return f'SHOW TABLES IN SCHEMA {db_name}.{schema_name}'

    @staticmethod
    def columns_for_schema(schema_name: str, db_name: str, object_batch: Optional[List[str]] = None) -> str:
        """Get column information for all tables in a schema with enhanced filtering and metadata."""
        # Build object filter if batch is provided
        object_filter = ""
        if object_batch and len(object_batch) > 0:
            # Handle both exact matches and prefix groups
            table_conditions = []
            for obj in object_batch:
                if hasattr(obj, 'prefix') and hasattr(obj, 'exact_match'):
                    if obj.exact_match:
                        table_conditions.append(f"table_name = '{obj.prefix}'")
                    else:
                        table_conditions.append(f"table_name LIKE '{obj.prefix}%'")
                else:
                    table_conditions.append(f"table_name = '{obj}'")
            
            if table_conditions:
                object_filter = f"AND ({' OR '.join(table_conditions)})"
        
        return f"""
        SELECT table_catalog AS "TABLE_CATALOG",
               table_schema AS "TABLE_SCHEMA",
               table_name AS "TABLE_NAME",
               column_name AS "COLUMN_NAME",
               ordinal_position AS "ORDINAL_POSITION",
               is_nullable AS "IS_NULLABLE",
               data_type AS "DATA_TYPE",
               comment AS "COMMENT",
               character_maximum_length AS "CHARACTER_MAXIMUM_LENGTH",
               numeric_precision AS "NUMERIC_PRECISION",
               numeric_scale AS "NUMERIC_SCALE",
               column_default AS "COLUMN_DEFAULT",
               is_identity AS "IS_IDENTITY",
               -- Enhanced metadata for better extraction
               CASE 
                   WHEN data_type IN ('VARCHAR', 'CHAR', 'STRING', 'TEXT') 
                   THEN character_maximum_length
                   ELSE NULL 
               END AS "TYPE_DETAILS",
               -- Column classification
               CASE 
                   WHEN is_identity = 'YES' THEN 'IDENTITY'
                   WHEN column_default IS NOT NULL THEN 'DEFAULT'
                   WHEN is_nullable = 'NO' THEN 'REQUIRED'
                   ELSE 'OPTIONAL'
               END AS "COLUMN_CLASSIFICATION"
        FROM "{db_name}".information_schema.columns
        WHERE table_schema = '{schema_name}'
        {object_filter}
        ORDER BY table_name, ordinal_position
        """

    @staticmethod
    def show_views_for_database(
        db_name: str,
        limit: int = SHOW_COMMAND_MAX_PAGE_SIZE,
        view_pagination_marker: Optional[str] = None,
    ) -> str:
        """Show views in database with pagination support."""
        assert limit <= SHOW_COMMAND_MAX_PAGE_SIZE

        from_clause = (
            f"FROM '{view_pagination_marker}'" if view_pagination_marker else ""
        )
        return f"""
        SHOW VIEWS IN DATABASE "{db_name}"
        LIMIT {limit} {from_clause}
        """

    @staticmethod
    def get_views_for_database(db_name: str) -> str:
        """Get view information from information schema."""
        return f"""
        SELECT TABLE_CATALOG AS "VIEW_CATALOG",
               TABLE_SCHEMA AS "VIEW_SCHEMA",
               TABLE_NAME AS "VIEW_NAME",
               COMMENT,
               VIEW_DEFINITION,
               CREATED,
               LAST_ALTERED,
               IS_SECURE
        FROM information_schema.views
        WHERE TABLE_CATALOG = '{db_name}'
          AND TABLE_SCHEMA != 'INFORMATION_SCHEMA'
        """

    @staticmethod
    def get_secure_view_definitions() -> str:
        """Get secure view definitions from account usage."""
        return """
        SELECT TABLE_CATALOG AS "TABLE_CATALOG",
               TABLE_SCHEMA AS "TABLE_SCHEMA",
               TABLE_NAME AS "TABLE_NAME",
               VIEW_DEFINITION AS "VIEW_DEFINITION"
        FROM SNOWFLAKE.ACCOUNT_USAGE.VIEWS
        WHERE IS_SECURE = 'YES' 
          AND VIEW_DEFINITION != '' 
          AND DELETED IS NULL
        """

    # Tag queries
    @staticmethod
    def get_all_tags() -> str:
        """Get all tags from account usage."""
        return """
        SELECT tag_database AS "TAG_DATABASE",
               tag_schema AS "TAG_SCHEMA",
               tag_name AS "TAG_NAME"
        FROM snowflake.account_usage.tag_references
        GROUP BY tag_database, tag_schema, tag_name
        ORDER BY tag_database, tag_schema, tag_name ASC
        """

    @staticmethod
    def get_all_tags_on_object_with_propagation(
        db_name: str, quoted_identifier: str, domain: str
    ) -> str:
        """Get all tags on an object with propagation."""
        return f"""
        SELECT tag_database AS "TAG_DATABASE",
               tag_schema AS "TAG_SCHEMA",
               tag_name AS "TAG_NAME",
               tag_value AS "TAG_VALUE"
        FROM table("{db_name}".information_schema.tag_references('{quoted_identifier}', '{domain}'))
        """

    @staticmethod
    def get_all_tags_in_database_without_propagation(db_name: str) -> str:
        """Get all tags in database without propagation using information_schema for immediate results."""
        allowed_object_domains = (
            f"('{SnowflakeObjectDomain.DATABASE.upper()}',"
            f"'{SnowflakeObjectDomain.SCHEMA.upper()}',"
            f"'{SnowflakeObjectDomain.TABLE.upper()}',"
            f"'{SnowflakeObjectDomain.COLUMN.upper()}')"
        )

        # Use information_schema.tag_references for immediate results instead of account_usage
        return f"""
        SELECT tag_database AS "TAG_DATABASE",
               tag_schema AS "TAG_SCHEMA",
               tag_name AS "TAG_NAME",
               tag_value AS "TAG_VALUE",
               object_database AS "OBJECT_DATABASE",
               object_schema AS "OBJECT_SCHEMA",
               object_name AS "OBJECT_NAME",
               column_name AS "COLUMN_NAME",
               domain AS "DOMAIN"
        FROM table("{db_name}".information_schema.tag_references('{db_name}', 'database'))
        WHERE domain IN {allowed_object_domains}
        UNION ALL
        SELECT tag_database AS "TAG_DATABASE",
               tag_schema AS "TAG_SCHEMA",
               tag_name AS "TAG_NAME",
               tag_value AS "TAG_VALUE",
               object_database AS "OBJECT_DATABASE",
               object_schema AS "OBJECT_SCHEMA",
               object_name AS "OBJECT_NAME",
               column_name AS "COLUMN_NAME",
               domain AS "DOMAIN"
        FROM table("{db_name}".information_schema.tag_references('{db_name}.PUBLIC', 'schema'))
        WHERE domain IN {allowed_object_domains}
        UNION ALL
        SELECT tag_database AS "TAG_DATABASE",
               tag_schema AS "TAG_SCHEMA",
               tag_name AS "TAG_NAME",
               tag_value AS "TAG_VALUE",
               object_database AS "OBJECT_DATABASE",
               object_schema AS "OBJECT_SCHEMA",
               object_name AS "OBJECT_NAME",
               column_name AS "COLUMN_NAME",
               domain AS "DOMAIN"
        FROM table("{db_name}".information_schema.tag_references('{db_name}.PUBLIC.CUSTOMERS', 'table'))
        WHERE domain IN {allowed_object_domains}
        UNION ALL
        SELECT tag_database AS "TAG_DATABASE",
               tag_schema AS "TAG_SCHEMA",
               tag_name AS "TAG_NAME",
               tag_value AS "TAG_VALUE",
               object_database AS "OBJECT_DATABASE",
               object_schema AS "OBJECT_SCHEMA",
               object_name AS "OBJECT_NAME",
               column_name AS "COLUMN_NAME",
               domain AS "DOMAIN"
        FROM table("{db_name}".information_schema.tag_references('{db_name}.PUBLIC.ORDERS', 'table'))
        WHERE domain IN {allowed_object_domains}
        UNION ALL
        SELECT tag_database AS "TAG_DATABASE",
               tag_schema AS "TAG_SCHEMA",
               tag_name AS "TAG_NAME",
               tag_value AS "TAG_VALUE",
               object_database AS "OBJECT_DATABASE",
               object_schema AS "OBJECT_SCHEMA",
               object_name AS "OBJECT_NAME",
               column_name AS "COLUMN_NAME",
               domain AS "DOMAIN"
        FROM table("{db_name}".information_schema.tag_references('{db_name}.PUBLIC.RAW_CUSTOMERS', 'table'))
        WHERE domain IN {allowed_object_domains}
        UNION ALL
        SELECT tag_database AS "TAG_DATABASE",
               tag_schema AS "TAG_SCHEMA",
               tag_name AS "TAG_NAME",
               tag_value AS "TAG_VALUE",
               object_database AS "OBJECT_DATABASE",
               object_schema AS "OBJECT_SCHEMA",
               object_name AS "OBJECT_NAME",
               column_name AS "COLUMN_NAME",
               domain AS "DOMAIN"
        FROM table("{db_name}".information_schema.tag_references('{db_name}.PUBLIC.RAW_ORDERS', 'table'))
        WHERE domain IN {allowed_object_domains}
        UNION ALL
        SELECT tag_database AS "TAG_DATABASE",
               tag_schema AS "TAG_SCHEMA",
               tag_name AS "TAG_NAME",
               tag_value AS "TAG_VALUE",
               object_database AS "OBJECT_DATABASE",
               object_schema AS "OBJECT_SCHEMA",
               object_name AS "OBJECT_NAME",
               column_name AS "COLUMN_NAME",
               domain AS "DOMAIN"
        FROM table("{db_name}".information_schema.tag_references('{db_name}.PUBLIC.RAW_PAYMENTS', 'table'))
        WHERE domain IN {allowed_object_domains}
        """

    # Lineage and usage queries
    @staticmethod
    def operational_data_for_time_window(
        start_time_millis: int, end_time_millis: int
    ) -> str:
        """Get operational data for a time window."""
        return f"""
        SELECT access_history.query_start_time AS "QUERY_START_TIME",
               query_history.query_text AS "QUERY_TEXT",
               query_history.query_type AS "QUERY_TYPE",
               query_history.rows_inserted AS "ROWS_INSERTED",
               query_history.rows_updated AS "ROWS_UPDATED",
               query_history.rows_deleted AS "ROWS_DELETED",
               access_history.base_objects_accessed AS "BASE_OBJECTS_ACCESSED",
               access_history.direct_objects_accessed AS "DIRECT_OBJECTS_ACCESSED",
               access_history.objects_modified AS "OBJECTS_MODIFIED",
               access_history.user_name AS "USER_NAME",
               users.first_name AS "FIRST_NAME",
               users.last_name AS "LAST_NAME",
               users.display_name AS "DISPLAY_NAME",
               users.email AS "EMAIL",
               query_history.role_name AS "ROLE_NAME"
        FROM snowflake.account_usage.access_history access_history
        LEFT JOIN (
            SELECT * FROM snowflake.account_usage.query_history
            WHERE query_history.start_time >= to_timestamp_ltz({start_time_millis}, 3)
              AND query_history.start_time < to_timestamp_ltz({end_time_millis}, 3)
        ) query_history ON access_history.query_id = query_history.query_id
        LEFT JOIN snowflake.account_usage.users users ON access_history.user_name = users.name
        WHERE query_start_time >= to_timestamp_ltz({start_time_millis}, 3)
          AND query_start_time < to_timestamp_ltz({end_time_millis}, 3)
          AND access_history.objects_modified IS NOT NULL
          AND ARRAY_SIZE(access_history.objects_modified) > 0
        ORDER BY query_start_time DESC
        """

    @staticmethod
    def table_to_table_lineage_history_v2(
        start_time_millis: int,
        end_time_millis: int,
        include_column_lineage: bool = True,
        upstreams_deny_pattern: List[str] = None,
    ) -> str:
        """Get table-to-table lineage history with optional column lineage."""
        if upstreams_deny_pattern is None:
            upstreams_deny_pattern = DEFAULT_TEMP_TABLES_PATTERNS

        if include_column_lineage:
            return SnowflakeQuery.table_upstreams_with_column_lineage(
                start_time_millis, end_time_millis, upstreams_deny_pattern
            )
        else:
            return SnowflakeQuery.table_upstreams_only(
                start_time_millis, end_time_millis, upstreams_deny_pattern
            )

    @staticmethod
    def table_upstreams_with_column_lineage(
        start_time_millis: int,
        end_time_millis: int,
        upstreams_deny_pattern: List[str],
    ) -> str:
        """Get table and column lineage from Snowflake access history - DataHub compatible implementation."""
        allowed_upstream_table_domains = (
            SnowflakeQuery.ACCESS_HISTORY_TABLE_VIEW_DOMAINS_FILTER
        )

        upstream_sql_filter = create_deny_regex_sql_filter(
            upstreams_deny_pattern,
            ["upstream_table_name", "upstream_column_table_name"],
        )
        _MAX_UPSTREAMS_PER_DOWNSTREAM = 20
        _MAX_UPSTREAM_COLUMNS_PER_DOWNSTREAM = 400
        _MAX_QUERIES_PER_DOWNSTREAM = 30

        return f"""
        WITH column_lineage_history AS (
            SELECT
                r.value : "objectName" :: varchar AS upstream_table_name,
                r.value : "objectDomain" :: varchar AS upstream_table_domain,
                REPLACE(w.value : "objectName" :: varchar, '__DBT_TMP', '') AS downstream_table_name,
                w.value : "objectDomain" :: varchar AS downstream_table_domain,
                wcols.value : "columnName" :: varchar AS downstream_column_name,
                wcols_directSources.value : "objectName" as upstream_column_table_name,
                wcols_directSources.value : "columnName" as upstream_column_name,
                wcols_directSources.value : "objectDomain" as upstream_column_object_domain,
                t.query_start_time AS query_start_time,
                t.query_id AS query_id
            FROM
                snowflake.account_usage.access_history t,
                lateral flatten(input => t.DIRECT_OBJECTS_ACCESSED) r,
                lateral flatten(input => t.OBJECTS_MODIFIED) w,
                lateral flatten(input => w.value : "columns", outer => true) wcols,
                lateral flatten(input => wcols.value : "directSources", outer => true) wcols_directSources
            WHERE
                r.value : "objectId" IS NOT NULL
                AND w.value : "objectId" IS NOT NULL
                AND w.value : "objectName" NOT LIKE '%.GE_TMP_%'
                AND w.value : "objectName" NOT LIKE '%.GE_TEMP_%'
                AND t.query_start_time >= to_timestamp_ltz({start_time_millis}, 3)
                AND t.query_start_time < to_timestamp_ltz({end_time_millis}, 3)
                AND upstream_table_domain in {allowed_upstream_table_domains}
                AND downstream_table_domain in {SnowflakeQuery.DOWNSTREAM_TABLE_DOMAINS_FILTER}
                {("AND " + upstream_sql_filter) if upstream_sql_filter else ""}
            ),
        column_upstream_jobs AS (
            SELECT
                downstream_table_name,
                downstream_column_name,
                ANY_VALUE(query_start_time) as query_start_time,
                query_id,
                ARRAY_UNIQUE_AGG(
                    OBJECT_CONSTRUCT(
                        'object_name', upstream_column_table_name,
                        'object_domain', upstream_column_object_domain,
                        'column_name', upstream_column_name
                    )
                ) as upstream_columns_for_job
            FROM
                column_lineage_history
            WHERE
                upstream_column_name is not null
                and upstream_column_table_name is not null
            GROUP BY
                downstream_table_name,
                downstream_column_name,
                query_id
            ),-- one row per column's upstream job (repetitive query possible)
        column_upstream_jobs_unique AS (
            SELECT
                downstream_table_name,
                downstream_column_name,
                upstream_columns_for_job,
                MAX_BY(query_id, query_start_time) as query_id,
                MAX(query_start_time) as query_start_time
            FROM
                column_upstream_jobs
            GROUP BY
                downstream_table_name,
                downstream_column_name,
                upstream_columns_for_job
            ),-- one row per column's unique upstream job (keep only latest query)
        column_upstreams AS (
            SELECT
                downstream_table_name,
                downstream_column_name,
                ARRAY_UNIQUE_AGG(
                    OBJECT_CONSTRUCT (
                        'column_upstreams', upstream_columns_for_job,
                        'query_id', query_id
                    )
                ) as upstreams
            FROM
                column_upstream_jobs_unique
            GROUP BY
                downstream_table_name,
                downstream_column_name
            ), -- one row per downstream column
        table_upstream_jobs_unique AS (
            SELECT
                downstream_table_name,
                ANY_VALUE(downstream_table_domain) as downstream_table_domain,
                upstream_table_name,
                ANY_VALUE(upstream_table_domain) as upstream_table_domain,
                MAX_BY(query_id, query_start_time) as query_id
            FROM
                column_lineage_history
            GROUP BY
                downstream_table_name,
                upstream_table_name
            ), -- one row per downstream table
        query_ids AS (
            SELECT distinct downstream_table_name, query_id from table_upstream_jobs_unique
            UNION
            select distinct downstream_table_name, query_id from column_upstream_jobs_unique
        ),
        queries AS (
            select qid.downstream_table_name, 
                   qid.query_id, 
                   query_history.query_text, 
                   query_history.start_time,
                   query_history.query_type,
                   query_history.root_query_id,
                   query_history.user_name,
                   query_history.database_name as default_database,
                   query_history.schema_name as default_schema
            from  query_ids qid
            LEFT JOIN (
                SELECT * FROM snowflake.account_usage.query_history
                WHERE query_history.start_time >= to_timestamp_ltz({start_time_millis}, 3)
                    AND query_history.start_time < to_timestamp_ltz({end_time_millis}, 3)
            ) query_history
            on qid.query_id = query_history.query_id
            WHERE qid.query_id is not null
              AND query_history.query_text is not null
        )
        SELECT
            h.downstream_table_name AS "DOWNSTREAM_TABLE_NAME",
            ANY_VALUE(h.downstream_table_domain) AS "DOWNSTREAM_TABLE_DOMAIN",
            ARRAY_SLICE(ARRAY_UNIQUE_AGG(
                OBJECT_CONSTRUCT(
                    'upstream_object_name', h.upstream_table_name,
                    'upstream_object_domain', h.upstream_table_domain,
                    'query_id', h.query_id
                )
            ), 0, {_MAX_UPSTREAMS_PER_DOWNSTREAM}) AS "UPSTREAM_TABLES",
            ARRAY_SLICE(ARRAY_UNIQUE_AGG(
                OBJECT_CONSTRUCT(
                    'column_name', column_upstreams.downstream_column_name,
                    'upstreams', column_upstreams.upstreams
                )
            ), 0, {_MAX_UPSTREAM_COLUMNS_PER_DOWNSTREAM}) AS "UPSTREAM_COLUMNS",
            ARRAY_SLICE(ARRAY_UNIQUE_AGG(
                OBJECT_CONSTRUCT(
                    'query_id', queries.query_id,
                    'query_text', queries.query_text,
                    'start_time', to_varchar(queries.start_time),
                    'query_type', queries.query_type,
                    'root_query_id', queries.root_query_id,
                    'user', queries.user_name,
                    'default_db', queries.default_database,
                    'default_schema', queries.default_schema
                )
            ), 0, {_MAX_QUERIES_PER_DOWNSTREAM}) AS "QUERIES"
        FROM table_upstream_jobs_unique h
        LEFT JOIN column_upstreams ON h.downstream_table_name = column_upstreams.downstream_table_name
        LEFT JOIN queries ON h.downstream_table_name = queries.downstream_table_name
        GROUP BY h.downstream_table_name
        ORDER BY h.downstream_table_name
        """

    @staticmethod
    def table_upstreams_only(
        start_time_millis: int,
        end_time_millis: int,
        upstreams_deny_pattern: List[str],
    ) -> str:
        """Get table lineage without column-level information."""
        upstream_sql_filter = create_deny_regex_sql_filter(
            upstreams_deny_pattern, ["upstream_table_name"]
        )

        return f"""
        WITH table_lineage_history AS (
            SELECT r.value:"objectName"::varchar AS upstream_table_name,
                   r.value:"objectDomain"::varchar AS upstream_table_domain,
                   w.value:"objectName"::varchar AS downstream_table_name,
                   w.value:"objectDomain"::varchar AS downstream_table_domain,
                   t.query_start_time AS query_start_time,
                   t.query_id AS query_id
            FROM snowflake.account_usage.access_history t,
                 lateral flatten(input => t.DIRECT_OBJECTS_ACCESSED) r,
                 lateral flatten(input => t.OBJECTS_MODIFIED) w
            WHERE r.value:"objectId" IS NOT NULL
              AND w.value:"objectId" IS NOT NULL
              AND w.value:"objectName" NOT LIKE '%.GE_TMP_%'
              AND w.value:"objectName" NOT LIKE '%.GE_TEMP_%'
              AND t.query_start_time >= to_timestamp_ltz({start_time_millis}, 3)
              AND t.query_start_time < to_timestamp_ltz({end_time_millis}, 3)
              AND upstream_table_domain IN {SnowflakeQuery.ACCESS_HISTORY_TABLE_VIEW_DOMAINS_FILTER}
              AND downstream_table_domain IN {SnowflakeQuery.DOWNSTREAM_TABLE_DOMAINS_FILTER}
              {("AND " + upstream_sql_filter) if upstream_sql_filter else ""}
        )
        SELECT h.downstream_table_name AS "DOWNSTREAM_TABLE_NAME",
               ANY_VALUE(h.downstream_table_domain) AS "DOWNSTREAM_TABLE_DOMAIN",
               ARRAY_UNIQUE_AGG(
                   OBJECT_CONSTRUCT(
                       'upstream_object_name', h.upstream_table_name,
                       'upstream_object_domain', h.upstream_table_domain,
                       'query_id', h.query_id
                   )
               ) AS "UPSTREAM_TABLES"
        FROM table_lineage_history h
        GROUP BY h.downstream_table_name
        ORDER BY h.downstream_table_name
        """

    @staticmethod
    def usage_per_object_per_time_bucket_for_time_window(
        start_time_millis: int,
        end_time_millis: int,
        time_bucket_size: BucketDuration,
        use_base_objects: bool,
        top_n_queries: int,
        include_top_n_queries: bool,
        email_domain: Optional[str],
        email_filter: AllowDenyPattern,
        table_deny_pattern: List[str] = None,
    ) -> str:
        """Get comprehensive usage statistics per object per time bucket.
        
        Enhanced to include:
        - Field usage counts (per column)
        - User usage counts (per user)
        - Top SQL queries (most frequent queries)
        - Complete usage statistics like DataHub
        """
        if table_deny_pattern is None:
            table_deny_pattern = DEFAULT_TEMP_TABLES_PATTERNS

        if not include_top_n_queries:
            top_n_queries = 0

        assert time_bucket_size in [BucketDuration.DAY, BucketDuration.HOUR]

        temp_table_filter = create_deny_regex_sql_filter(
            table_deny_pattern, ["object_name"]
        )

        objects_column = (
            "BASE_OBJECTS_ACCESSED" if use_base_objects else "DIRECT_OBJECTS_ACCESSED"
        )
        email_filter_query = SnowflakeQuery.gen_email_filter_query(email_filter)
        email_domain = f"@{email_domain}" if email_domain else ""

        return f"""
        WITH object_access_history AS (
            SELECT object.value:"objectName"::varchar AS object_name,
                   object.value:"objectDomain"::varchar AS object_domain,
                   object.value:"columns" AS object_columns,
                   query_start_time,
                   query_id,
                   user_name
            FROM (
                SELECT query_id,
                       query_start_time,
                       user_name,
                       NVL(USERS.email, CONCAT(LOWER(user_name), '{email_domain}')) AS user_email,
                       {objects_column}
                FROM snowflake.account_usage.access_history
                LEFT JOIN snowflake.account_usage.users USERS ON user_name = users.name
                WHERE query_start_time >= to_timestamp_ltz({start_time_millis}, 3)
                  AND query_start_time < to_timestamp_ltz({end_time_millis}, 3)
                  {email_filter_query}
            ) t,
            lateral flatten(input => t.{objects_column}) object
            {("WHERE " + temp_table_filter) if temp_table_filter else ""}
        ),
        field_access_history AS (
            SELECT o.*,
                   col.value:"columnName"::varchar AS column_name
            FROM object_access_history o,
                 lateral flatten(input => o.object_columns) col
        ),
        basic_usage_counts AS (
            SELECT object_name,
                   ANY_VALUE(object_domain) AS object_domain,
                   DATE_TRUNC('{time_bucket_size}', CONVERT_TIMEZONE('UTC', query_start_time)) AS bucket_start_time,
                   COUNT(DISTINCT(query_id)) AS total_queries,
                   COUNT(DISTINCT(user_name)) AS total_users
            FROM object_access_history
            GROUP BY bucket_start_time, object_name
        ),
        field_usage_counts AS (
            SELECT object_name,
                   column_name,
                   DATE_TRUNC('{time_bucket_size}', CONVERT_TIMEZONE('UTC', query_start_time)) AS bucket_start_time,
                   COUNT(DISTINCT(query_id)) AS total_queries
            FROM field_access_history
            GROUP BY bucket_start_time, object_name, column_name
        ),
        user_usage_counts AS (
            SELECT object_name,
                   DATE_TRUNC('{time_bucket_size}', CONVERT_TIMEZONE('UTC', query_start_time)) AS bucket_start_time,
                   COUNT(DISTINCT(query_id)) AS total_queries,
                   user_name,
                   ANY_VALUE(users.email) AS user_email
            FROM object_access_history
            LEFT JOIN snowflake.account_usage.users users ON user_name = users.name
            GROUP BY bucket_start_time, object_name, user_name
        ),
        top_queries AS (
            SELECT object_name,
                   DATE_TRUNC('{time_bucket_size}', CONVERT_TIMEZONE('UTC', query_start_time)) AS bucket_start_time,
                   query_history.query_text AS query_text,
                   COUNT(DISTINCT(access_history.query_id)) AS total_queries
            FROM object_access_history access_history
            LEFT JOIN (
                SELECT * FROM snowflake.account_usage.query_history
                WHERE query_history.start_time >= to_timestamp_ltz({start_time_millis}, 3)
                  AND query_history.start_time < to_timestamp_ltz({end_time_millis}, 3)
            ) query_history ON access_history.query_id = query_history.query_id
            GROUP BY bucket_start_time, object_name, query_text
            QUALIFY ROW_NUMBER() OVER (
                PARTITION BY bucket_start_time, object_name
                ORDER BY total_queries DESC, query_text ASC
            ) <= {top_n_queries}
        )
        SELECT basic_usage_counts.object_name AS "OBJECT_NAME",
               basic_usage_counts.bucket_start_time AS "BUCKET_START_TIME",
               ANY_VALUE(basic_usage_counts.object_domain) AS "OBJECT_DOMAIN",
               ANY_VALUE(basic_usage_counts.total_queries) AS "TOTAL_QUERIES",
               ANY_VALUE(basic_usage_counts.total_users) AS "TOTAL_USERS",
               ARRAY_UNIQUE_AGG(top_queries.query_text) AS "TOP_SQL_QUERIES",
               ARRAY_UNIQUE_AGG(OBJECT_CONSTRUCT(
                   'col', field_usage_counts.column_name,
                   'total', field_usage_counts.total_queries
               )) AS "FIELD_COUNTS",
               ARRAY_UNIQUE_AGG(OBJECT_CONSTRUCT(
                   'user_name', user_usage_counts.user_name,
                   'email', user_usage_counts.user_email,
                   'total', user_usage_counts.total_queries
               )) AS "USER_COUNTS"
        FROM basic_usage_counts
        LEFT JOIN top_queries ON basic_usage_counts.bucket_start_time = top_queries.bucket_start_time
            AND basic_usage_counts.object_name = top_queries.object_name
        LEFT JOIN field_usage_counts ON basic_usage_counts.bucket_start_time = field_usage_counts.bucket_start_time
            AND basic_usage_counts.object_name = field_usage_counts.object_name
        LEFT JOIN user_usage_counts ON basic_usage_counts.bucket_start_time = user_usage_counts.bucket_start_time
            AND basic_usage_counts.object_name = user_usage_counts.object_name
        WHERE basic_usage_counts.object_domain IN {SnowflakeQuery.ACCESS_HISTORY_TABLE_VIEW_DOMAINS_FILTER}
          AND basic_usage_counts.object_name IS NOT NULL
        GROUP BY basic_usage_counts.object_name, basic_usage_counts.bucket_start_time
        ORDER BY basic_usage_counts.bucket_start_time
        """

    @staticmethod
    def gen_email_filter_query(email_filter: AllowDenyPattern) -> str:
        """Generate email filter query for usage statistics."""
        allow_filters = []
        allow_filter = ""

        if len(email_filter.allow) == 1 and email_filter.allow[0] == ".*":
            allow_filter = ""
        else:
            for allow_pattern in email_filter.allow:
                allow_filters.append(
                    f"rlike(user_email, '{allow_pattern}','{'i' if email_filter.ignoreCase else 'c'}')"
                )
            if allow_filters:
                allow_filter = " OR ".join(allow_filters)
                allow_filter = f"AND ({allow_filter})"

        deny_filters = []
        deny_filter = ""
        for deny_pattern in email_filter.deny:
            deny_filters.append(
                f"rlike(user_email, '{deny_pattern}','{'i' if email_filter.ignoreCase else 'c'}')"
            )
        if deny_filters:
            deny_filter = " OR ".join(deny_filters)
            deny_filter = f"({deny_filter})"

        email_filter_query = allow_filter + (
            " AND" + f" NOT {deny_filter}" if deny_filter else ""
        )
        return email_filter_query

    # Streams and dynamic tables
    @staticmethod
    def streams_for_database(
        db_name: str,
        limit: int = SHOW_STREAM_MAX_PAGE_SIZE,
        stream_pagination_marker: Optional[str] = None,
    ) -> str:
        """Show streams in database with pagination."""
        assert limit <= SHOW_STREAM_MAX_PAGE_SIZE

        from_clause = (
            f"FROM '{stream_pagination_marker}'" if stream_pagination_marker else ""
        )
        return f"""
        SHOW STREAMS IN DATABASE "{db_name}" LIMIT {limit} {from_clause}
        """

    @staticmethod
    def show_dynamic_tables_for_database(
        db_name: str,
        limit: int = SHOW_COMMAND_MAX_PAGE_SIZE,
        dynamic_table_pagination_marker: Optional[str] = None,
    ) -> str:
        """Show dynamic tables in database with pagination."""
        assert limit <= SHOW_COMMAND_MAX_PAGE_SIZE

        from_clause = (
            f"FROM '{dynamic_table_pagination_marker}'"
            if dynamic_table_pagination_marker else ""
        )
        return f"""
        SHOW DYNAMIC TABLES IN DATABASE "{db_name}"
        LIMIT {limit} {from_clause}
        """

    @staticmethod
    def get_dynamic_table_graph_history(db_name: str) -> str:
        """Get dynamic table dependency information."""
        return f"""
        SELECT name,
               inputs,
               target_lag_type,
               target_lag_sec,
               scheduling_state,
               alter_trigger
        FROM TABLE("{db_name}".INFORMATION_SCHEMA.DYNAMIC_TABLE_GRAPH_HISTORY())
        ORDER BY name
        """

    # Utilities
    @staticmethod
    def get_access_history_date_range() -> str:
        """Get date range available in access history."""
        return """
        SELECT min(query_start_time) AS "MIN_TIME",
               max(query_start_time) AS "MAX_TIME"
        FROM snowflake.account_usage.access_history
        """

    @staticmethod
    def get_all_users() -> str:
        """Get all users from account usage."""
        return """
        SELECT name AS "NAME", 
               email AS "EMAIL" 
        FROM SNOWFLAKE.ACCOUNT_USAGE.USERS
        """

    @staticmethod
    def show_external_tables() -> str:
        """Show all external tables in account."""
        return "SHOW EXTERNAL TABLES IN ACCOUNT"

    @staticmethod
    def copy_lineage_history(
        start_time_millis: int,
        end_time_millis: int,
        downstreams_deny_pattern: List[str] = None,
    ) -> str:
        """Get copy lineage history from copy commands."""
        if downstreams_deny_pattern is None:
            downstreams_deny_pattern = DEFAULT_TEMP_TABLES_PATTERNS

        temp_table_filter = create_deny_regex_sql_filter(
            downstreams_deny_pattern, ["DOWNSTREAM_TABLE_NAME"]
        )

        return f"""
        SELECT ARRAY_UNIQUE_AGG(h.stage_location) AS "UPSTREAM_LOCATIONS",
               concat(h.table_catalog_name, '.', h.table_schema_name, '.', h.table_name) AS "DOWNSTREAM_TABLE_NAME"
        FROM snowflake.account_usage.copy_history h
        WHERE h.status IN ('Loaded','Partially loaded')
          AND DOWNSTREAM_TABLE_NAME IS NOT NULL
          AND h.last_load_time >= to_timestamp_ltz({start_time_millis}, 3)
          AND h.last_load_time < to_timestamp_ltz({end_time_millis}, 3)
          {("AND " + temp_table_filter) if temp_table_filter else ""}
        GROUP BY DOWNSTREAM_TABLE_NAME
        """

    @staticmethod
    def dmf_assertion_results(start_time_millis: int, end_time_millis: int) -> str:
        """Get DMF assertion results for DataGuild."""
        pattern = r"dataguild\\_\\_%"
        escape_pattern = r"\\"

        return f"""
        SELECT MEASUREMENT_TIME AS "MEASUREMENT_TIME",
               METRIC_NAME AS "METRIC_NAME",
               TABLE_NAME AS "TABLE_NAME",
               TABLE_SCHEMA AS "TABLE_SCHEMA",
               TABLE_DATABASE AS "TABLE_DATABASE",
               VALUE::INT AS "VALUE"
        FROM SNOWFLAKE.LOCAL.DATA_QUALITY_MONITORING_RESULTS
        WHERE MEASUREMENT_TIME >= to_timestamp_ltz({start_time_millis}, 3)
          AND MEASUREMENT_TIME < to_timestamp_ltz({end_time_millis}, 3)
          AND METRIC_NAME ilike '{pattern}' escape '{escape_pattern}'
        ORDER BY MEASUREMENT_TIME ASC
        """

    @staticmethod
    def procedures_for_database(db_name: str) -> str:
        """Get all stored procedures for a database."""
        return f"""
        SELECT 
            PROCEDURE_CATALOG AS "PROCEDURE_CATALOG",
            PROCEDURE_SCHEMA AS "PROCEDURE_SCHEMA",
            PROCEDURE_NAME AS "PROCEDURE_NAME",
            PROCEDURE_OWNER AS "PROCEDURE_OWNER",
            ARGUMENT_SIGNATURE AS "ARGUMENT_SIGNATURE",
            DATA_TYPE AS "DATA_TYPE",
            CHARACTER_MAXIMUM_LENGTH AS "CHARACTER_MAXIMUM_LENGTH",
            CHARACTER_OCTET_LENGTH AS "CHARACTER_OCTET_LENGTH",
            NUMERIC_PRECISION AS "NUMERIC_PRECISION",
            NUMERIC_PRECISION_RADIX AS "NUMERIC_PRECISION_RADIX",
            NUMERIC_SCALE AS "NUMERIC_SCALE",
            PROCEDURE_LANGUAGE AS "PROCEDURE_LANGUAGE",
            PROCEDURE_DEFINITION AS "PROCEDURE_DEFINITION",
            CREATED AS "PROCEDURE_CREATED",
            LAST_ALTERED AS "PROCEDURE_LAST_ALTERED",
            COMMENT AS "PROCEDURE_COMMENT",
            EXTERNAL_ACCESS_INTEGRATIONS AS "EXTERNAL_ACCESS_INTEGRATIONS",
            SECRETS AS "SECRETS",
            RUNTIME_VERSION AS "RUNTIME_VERSION",
            PACKAGES AS "PACKAGES",
            INSTALLED_PACKAGES AS "INSTALLED_PACKAGES"
        FROM "{db_name}".INFORMATION_SCHEMA.PROCEDURES
        ORDER BY PROCEDURE_SCHEMA, PROCEDURE_NAME
        """

    @staticmethod
    def show_primary_keys_for_schema(schema_name: str, db_name: str) -> str:
        """Get primary keys for a schema using SHOW PRIMARY KEYS command."""
        return f'SHOW PRIMARY KEYS IN SCHEMA {db_name}.{schema_name}'

    @staticmethod
    def show_foreign_keys_for_schema(schema_name: str, db_name: str) -> str:
        """Get foreign keys for a schema using SHOW IMPORTED KEYS command."""
        return f'SHOW IMPORTED KEYS IN SCHEMA {db_name}.{schema_name}'


# Utility functions for query building
def build_paginated_query(
    base_query: str,
    limit: int,
    pagination_marker: Optional[str] = None
) -> str:
    """
    Build a paginated query with limit and optional pagination marker.

    Args:
        base_query: Base SQL query
        limit: Maximum number of rows to return
        pagination_marker: Optional marker for pagination

    Returns:
        Paginated SQL query
    """
    from_clause = f"FROM '{pagination_marker}'" if pagination_marker else ""
    return f"{base_query} LIMIT {limit} {from_clause}"


def escape_sql_identifier(identifier: str) -> str:
    """
    Escape SQL identifier for safe use in queries.

    Args:
        identifier: Identifier to escape

    Returns:
        Escaped identifier
    """
    return f'"{identifier}"'


def format_timestamp_millis(timestamp_millis: int) -> str:
    """
    Format timestamp in milliseconds for Snowflake queries.

    Args:
        timestamp_millis: Timestamp in milliseconds

    Returns:
        Formatted timestamp function call
    """
    return f"to_timestamp_ltz({timestamp_millis}, 3)"
