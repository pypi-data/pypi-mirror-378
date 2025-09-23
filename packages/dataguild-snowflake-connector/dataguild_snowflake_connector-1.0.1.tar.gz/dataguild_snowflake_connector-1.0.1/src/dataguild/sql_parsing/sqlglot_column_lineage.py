"""
DataGuild SQLGlot Column Lineage Parser

This module provides comprehensive column-level lineage extraction using SQLGlot,
based on DataHub's proven approach but adapted for DataGuild's architecture.

Key Features:
1. Schema-aware column lineage extraction
2. Support for complex SQL transformations
3. Proper handling of CTEs, subqueries, and joins
4. Column qualification and normalization
5. Transformation logic extraction
6. Confidence scoring based on parsing success

Authored by: DataGuild Engineering Team
Based on: DataHub's sqlglot_lineage.py
"""

import logging
import traceback
from collections import defaultdict
from typing import (
    AbstractSet,
    Any,
    Dict,
    Iterable,
    List,
    Optional,
    Set,
    Tuple,
    Union,
)

import sqlglot
import sqlglot.errors
import sqlglot.lineage
import sqlglot.optimizer
import sqlglot.optimizer.annotate_types
import sqlglot.optimizer.optimizer
import sqlglot.optimizer.qualify
import sqlglot.optimizer.qualify_columns
import sqlglot.optimizer.unnest_subqueries

from dataguild.sql_parsing.sqlglot_lineage import (
    ColumnRef,
    DownstreamColumnRef,
    ColumnLineageInfo,
)
from dataguild.sql_parsing.sqlglot_utils import parse_sql_query, get_query_fingerprint

logger = logging.getLogger(__name__)

# SQL parsing configuration
SQL_PARSE_RESULT_CACHE_SIZE = 1000
SQL_LINEAGE_TIMEOUT_SECONDS = 10
SQL_PARSER_TRACE = False

# Optimization rules for SQLGlot
_OPTIMIZE_RULES = (
    sqlglot.optimizer.optimizer.qualify,
    sqlglot.optimizer.optimizer.pushdown_projections,
    sqlglot.optimizer.optimizer.unnest_subqueries,
    sqlglot.optimizer.optimizer.quote_identifiers,
)

# Dialects with case-insensitive columns
DIALECTS_WITH_CASE_INSENSITIVE_COLS = {"snowflake", "bigquery", "redshift"}
DIALECTS_WITH_DEFAULT_UPPERCASE_COLS = {"snowflake"}


class _TableName:
    """Internal table name representation for SQLGlot processing."""
    
    def __init__(self, database: Optional[str] = None, db_schema: Optional[str] = None, table: str = ""):
        self.database = database
        self.db_schema = db_schema
        self.table = table
    
    @classmethod
    def from_sqlglot_table(cls, table: sqlglot.exp.Table) -> "_TableName":
        """Create TableName from SQLGlot table expression."""
        return cls(
            database=table.catalog,
            db_schema=table.db,
            table=table.name or "",
        )
    
    def as_sqlglot_table(self) -> sqlglot.exp.Table:
        """Convert to SQLGlot table expression."""
        return sqlglot.exp.Table(
            catalog=self.database,
            db=self.db_schema,
            this=self.table,
        )
    
    def qualified(self, dialect: sqlglot.Dialect, default_db: Optional[str] = None, default_schema: Optional[str] = None) -> "_TableName":
        """Qualify table name with default database/schema if needed."""
        qualified = _TableName(
            database=self.database or default_db,
            db_schema=self.db_schema or default_schema,
            table=self.table,
        )
        return qualified
    
    def __hash__(self) -> int:
        return hash((self.database, self.db_schema, self.table))
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, _TableName):
            return False
        return (self.database, self.db_schema, self.table) == (other.database, other.db_schema, other.table)
    
    def __str__(self) -> str:
        parts = []
        if self.database:
            parts.append(self.database)
        if self.db_schema:
            parts.append(self.db_schema)
        parts.append(self.table)
        return ".".join(parts)


class _ColumnRef:
    """Internal column reference for SQLGlot processing."""
    
    def __init__(self, table: _TableName, column: str):
        self.table = table
        self.column = column
    
    def __hash__(self) -> int:
        return hash((self.table, self.column))
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, _ColumnRef):
            return False
        return self.table == other.table and self.column == other.column
    
    def __lt__(self, other) -> bool:
        if not isinstance(other, _ColumnRef):
            return NotImplemented
        return (str(self.table), self.column) < (str(other.table), other.column)
    
    def __le__(self, other) -> bool:
        return self < other or self == other
    
    def __gt__(self, other) -> bool:
        return not self <= other
    
    def __ge__(self, other) -> bool:
        return not self < other


class _DownstreamColumnRef:
    """Internal downstream column reference for SQLGlot processing."""
    
    def __init__(self, table: Optional[_TableName] = None, column: str = "", column_type: Optional[sqlglot.exp.DataType] = None):
        self.table = table
        self.column = column
        self.column_type = column_type


class _ColumnLineageInfo:
    """Internal column lineage info for SQLGlot processing."""
    
    def __init__(self, downstream: _DownstreamColumnRef, upstreams: List[_ColumnRef], logic: Optional[str] = None):
        self.downstream = downstream
        self.upstreams = upstreams
        self.logic = logic


class _ColumnResolver:
    """Column resolver for schema-aware column mapping."""
    
    def __init__(self, sqlglot_db_schema: sqlglot.MappingSchema, table_schema_normalized_mapping: Dict[_TableName, Dict[str, str]], use_case_insensitive_cols: bool):
        self.sqlglot_db_schema = sqlglot_db_schema
        self.table_schema_normalized_mapping = table_schema_normalized_mapping
        self.use_case_insensitive_cols = use_case_insensitive_cols
    
    def schema_aware_fuzzy_column_resolve(self, table: Optional[_TableName], sqlglot_column: str) -> str:
        """Resolve column name using schema information."""
        default_col_name = (
            sqlglot_column.lower() if self.use_case_insensitive_cols else sqlglot_column
        )
        if table and table in self.table_schema_normalized_mapping:
            return self.table_schema_normalized_mapping[table].get(
                sqlglot_column, default_col_name
            )
        else:
            return default_col_name


class SqlParsingResult:
    """Result of SQL parsing with column lineage information."""
    
    def __init__(self, 
                 query_type: str = "UNKNOWN",
                 in_tables: List[str] = None,
                 out_tables: List[str] = None,
                 column_lineage: List[ColumnLineageInfo] = None,
                 joins: List[Dict[str, Any]] = None,
                 confidence: float = 0.0,
                 error: Optional[Exception] = None):
        self.query_type = query_type
        self.in_tables = in_tables or []
        self.out_tables = out_tables or []
        self.column_lineage = column_lineage or []
        self.joins = joins or []
        self.confidence = confidence
        self.error = error
    
    @classmethod
    def make_from_error(cls, error: Exception) -> "SqlParsingResult":
        """Create result from parsing error."""
        return cls(error=error, confidence=0.0)


def _extract_table_names(iterable: Iterable[sqlglot.exp.Table]) -> Set[_TableName]:
    """Extract table names from SQLGlot table expressions."""
    return {_TableName.from_sqlglot_table(table) for table in iterable}


def _table_level_lineage(statement: sqlglot.Expression, dialect: sqlglot.Dialect) -> Tuple[AbstractSet[_TableName], AbstractSet[_TableName]]:
    """Extract table-level lineage from SQL statement."""
    # Generate table-level lineage
    modified = (
        _extract_table_names(
            expr.this
            for expr in statement.find_all(
                sqlglot.exp.Create,
                sqlglot.exp.Insert,
                sqlglot.exp.Update,
                sqlglot.exp.Delete,
                sqlglot.exp.Merge,
                sqlglot.exp.Alter,
            )
            if isinstance(expr.this, sqlglot.exp.Table)
        )
        | _extract_table_names(
            expr.this.this
            for expr in statement.find_all(
                sqlglot.exp.Create,
                sqlglot.exp.Insert,
            )
            if isinstance(expr.this, sqlglot.exp.Schema)
            and isinstance(expr.this.this, sqlglot.exp.Table)
        )
        | _extract_table_names(
            expr.this
            for expr in ([statement] if isinstance(statement, sqlglot.exp.Drop) else [])
            if isinstance(expr.this, sqlglot.exp.Table)
            and expr.this.this
            and expr.this.name
        )
    )

    tables = (
        _extract_table_names(
            table
            for table in statement.find_all(sqlglot.exp.Table)
            if not isinstance(table.parent, sqlglot.exp.Drop)
        )
        - modified
        - {
            _TableName(database=None, db_schema=None, table=cte.alias_or_name)
            for cte in statement.find_all(sqlglot.exp.CTE)
        }
    )
    
    # Update statements implicitly read from the table being updated
    if isinstance(statement, sqlglot.exp.Update):
        tables = tables | modified

    return tables, modified


def _prepare_query_columns(
    statement: sqlglot.exp.Expression,
    dialect: sqlglot.Dialect,
    table_schemas: Dict[_TableName, Dict[str, str]],
    default_db: Optional[str],
    default_schema: Optional[str],
) -> Tuple[sqlglot.exp.Expression, _ColumnResolver]:
    """Prepare query for column-level lineage extraction."""
    
    # Check if this is a supported statement type
    if not isinstance(statement, (sqlglot.exp.Query, sqlglot.exp.DerivedTable)):
        raise ValueError(f"Unsupported statement type: {type(statement)}")

    use_case_insensitive_cols = str(dialect).lower() in DIALECTS_WITH_CASE_INSENSITIVE_COLS

    # Create SQLGlot schema mapping
    sqlglot_db_schema = sqlglot.MappingSchema(
        dialect=dialect,
        normalize=False,
    )
    
    table_schema_normalized_mapping: Dict[_TableName, Dict[str, str]] = defaultdict(dict)
    
    for table, table_schema in table_schemas.items():
        normalized_table_schema: Dict[str, str] = {}
        for col, col_type in table_schema.items():
            if use_case_insensitive_cols:
                col_normalized = (
                    col.upper()
                    if str(dialect).lower() in DIALECTS_WITH_DEFAULT_UPPERCASE_COLS
                    else col.lower()
                )
            else:
                col_normalized = col

            table_schema_normalized_mapping[table][col_normalized] = col
            normalized_table_schema[col_normalized] = col_type or "UNKNOWN"

        sqlglot_db_schema.add_table(
            table.as_sqlglot_table(),
            column_mapping=normalized_table_schema,
        )

    # Normalize column casing if needed
    if use_case_insensitive_cols:
        def _sqlglot_force_column_normalizer(node: sqlglot.exp.Expression) -> sqlglot.exp.Expression:
            if isinstance(node, sqlglot.exp.Column):
                node.this.set("quoted", False)
            return node

        statement = statement.transform(_sqlglot_force_column_normalizer, copy=False)

    # Optimize the statement and qualify column references
    try:
        statement = sqlglot.optimizer.optimizer.optimize(
            statement,
            dialect=dialect,
            schema=sqlglot_db_schema,
            qualify_columns=True,
            validate_qualify_columns=False,
            allow_partial_qualification=True,
            identify=True,
            catalog=default_db,
            db=default_schema,
            rules=_OPTIMIZE_RULES,
        )
    except (sqlglot.errors.OptimizeError, ValueError) as e:
        raise ValueError(f"SQLGlot failed to map columns to source tables: {e}") from e

    # Try to annotate types
    try:
        statement = sqlglot.optimizer.annotate_types.annotate_types(
            statement, schema=sqlglot_db_schema
        )
    except (sqlglot.errors.OptimizeError, sqlglot.errors.ParseError) as e:
        logger.debug(f"SQLGlot failed to annotate types: {e}")

    return statement, _ColumnResolver(
        sqlglot_db_schema=sqlglot_db_schema,
        table_schema_normalized_mapping=table_schema_normalized_mapping,
        use_case_insensitive_cols=use_case_insensitive_cols,
    )


def _get_direct_raw_col_upstreams(
    lineage_node: sqlglot.lineage.Node,
    dialect: Optional[sqlglot.Dialect] = None,
    default_db: Optional[str] = None,
    default_schema: Optional[str] = None,
) -> Set[_ColumnRef]:
    """Extract direct column upstreams from lineage node."""
    direct_raw_col_upstreams: Set[_ColumnRef] = set()

    for node in lineage_node.walk():
        if node.downstream:
            continue

        elif isinstance(node.expression, sqlglot.exp.Table):
            table_ref = _TableName.from_sqlglot_table(node.expression)

            if node.name == "*":
                continue

            # Parse the column name
            normalized_col = sqlglot.parse_one(node.name).this.name
            if hasattr(node, "subfield") and node.subfield:
                normalized_col = f"{normalized_col}.{node.subfield}"

            direct_raw_col_upstreams.add(
                _ColumnRef(table=table_ref, column=normalized_col)
            )
        elif isinstance(node.expression, sqlglot.exp.Placeholder) and node.name != "*":
            # Handle placeholder expressions from lateral joins
            try:
                parsed = sqlglot.parse_one(node.name, dialect=dialect)
                if isinstance(parsed, sqlglot.exp.Column) and parsed.table:
                    table_ref = _TableName.from_sqlglot_table(
                        sqlglot.parse_one(
                            parsed.table, into=sqlglot.exp.Table, dialect=dialect
                        )
                    )

                    # Qualify if needed
                    if (
                        not (table_ref.database or table_ref.db_schema)
                        and dialect is not None
                    ):
                        table_ref = table_ref.qualified(
                            dialect=dialect,
                            default_db=default_db,
                            default_schema=default_schema,
                        )

                    # Extract column name
                    if isinstance(parsed.this, sqlglot.exp.Identifier):
                        column_name = parsed.this.name
                    else:
                        column_name = str(parsed.this)
                    direct_raw_col_upstreams.add(
                        _ColumnRef(table=table_ref, column=column_name)
                    )
            except Exception as e:
                logger.debug(f"Failed to parse placeholder column expression: {node.name}: {e}")

    return direct_raw_col_upstreams


def _is_single_column_expression(expression: sqlglot.exp.Expression) -> bool:
    """Check if expression is a single column reference."""
    if isinstance(expression, sqlglot.exp.Alias):
        expression = expression.this
    return isinstance(expression, sqlglot.exp.Column)


def _get_column_transformation(
    lineage_node: sqlglot.lineage.Node,
    dialect: sqlglot.Dialect,
    parent: Optional[sqlglot.lineage.Node] = None,
) -> str:
    """Extract column transformation logic."""
    if not lineage_node.downstream:
        if parent:
            expression = parent.expression
            is_copy = _is_single_column_expression(expression)
        else:
            is_copy = True
            expression = lineage_node.expression
        return expression.sql(dialect=dialect)
    elif len(lineage_node.downstream) > 1 or not _is_single_column_expression(lineage_node.expression):
        return lineage_node.expression.sql(dialect=dialect)
    else:
        return _get_column_transformation(
            lineage_node=lineage_node.downstream[0],
            dialect=dialect,
            parent=lineage_node,
        )


def _select_statement_cll(
    statement: sqlglot.exp.Expression,
    dialect: sqlglot.Dialect,
    root_scope: sqlglot.optimizer.Scope,
    column_resolver: _ColumnResolver,
    output_table: Optional[_TableName],
    table_name_schema_mapping: Dict[_TableName, Dict[str, str]],
    default_db: Optional[str] = None,
    default_schema: Optional[str] = None,
) -> List[_ColumnLineageInfo]:
    """Extract column-level lineage from SELECT statement."""
    column_lineage: List[_ColumnLineageInfo] = []

    try:
        output_columns = [
            (select_col.alias_or_name, select_col) for select_col in statement.selects
        ]
        logger.debug("output columns: %s", [col[0] for col in output_columns])

        for output_col, _original_col_expression in output_columns:
            if not output_col or output_col == "*":
                continue

            # Skip special BigQuery columns
            if str(dialect).lower() == "bigquery" and output_col.lower() in {
                "_partitiontime",
                "_partitiondate",
            }:
                continue

            lineage_node = sqlglot.lineage.lineage(
                output_col,
                statement,
                dialect=dialect,
                scope=root_scope,
                trim_selects=False,
            )

            # Generate SELECT lineage
            direct_raw_col_upstreams = _get_direct_raw_col_upstreams(
                lineage_node,
                dialect,
                default_db,
                default_schema,
            )

            # Resolve the output column
            original_col_expression = lineage_node.expression
            if output_col.startswith("_col_"):
                output_col = original_col_expression.this.sql(dialect=dialect)

            output_col = column_resolver.schema_aware_fuzzy_column_resolve(
                output_table, output_col
            )

            # Resolve upstream columns
            direct_resolved_col_upstreams = {
                _ColumnRef(
                    table=edge.table,
                    column=column_resolver.schema_aware_fuzzy_column_resolve(
                        edge.table, edge.column
                    ),
                )
                for edge in direct_raw_col_upstreams
            }

            if not direct_resolved_col_upstreams:
                logger.debug(f'  "{output_col}" has no upstreams')
            
            column_lineage.append(
                _ColumnLineageInfo(
                    downstream=_DownstreamColumnRef(
                        table=output_table,
                        column=output_col,
                    ),
                    upstreams=sorted(direct_resolved_col_upstreams),
                    logic=_get_column_transformation(lineage_node, dialect),
                )
            )

    except (sqlglot.errors.OptimizeError, ValueError, IndexError) as e:
        raise ValueError(f"SQLGlot failed to compute lineage: {e}") from e

    return column_lineage


def _column_level_lineage(
    statement: sqlglot.exp.Expression,
    dialect: sqlglot.Dialect,
    downstream_table: Optional[_TableName],
    table_name_schema_mapping: Dict[_TableName, Dict[str, str]],
    default_db: Optional[str],
    default_schema: Optional[str],
) -> List[_ColumnLineageInfo]:
    """Extract column-level lineage from SQL statement."""
    
    # Prepare query for column lineage extraction
    try:
        (select_statement, column_resolver) = _prepare_query_columns(
            statement,
            dialect=dialect,
            table_schemas=table_name_schema_mapping,
            default_db=default_db,
            default_schema=default_schema,
        )
    except ValueError as e:
        logger.debug(f"Failed to prepare query columns: {e}")
        return []

    # Build scope for lineage extraction
    try:
        root_scope = sqlglot.optimizer.build_scope(select_statement)
        if root_scope is None:
            logger.debug("Failed to build scope for statement")
            return []
    except (sqlglot.errors.OptimizeError, ValueError, IndexError) as e:
        logger.debug(f"SQLGlot failed to preprocess statement: {e}")
        return []

    # Generate column-level lineage
    column_lineage = _select_statement_cll(
        select_statement,
        dialect=dialect,
        root_scope=root_scope,
        column_resolver=column_resolver,
        output_table=downstream_table,
        table_name_schema_mapping=table_name_schema_mapping,
        default_db=default_db,
        default_schema=default_schema,
    )

    return column_lineage


def _translate_internal_column_lineage(
    table_name_urn_mapping: Dict[_TableName, str],
    raw_column_lineage: _ColumnLineageInfo,
    dialect: sqlglot.Dialect,
) -> ColumnLineageInfo:
    """Translate internal column lineage to public format."""
    downstream_urn = None
    if raw_column_lineage.downstream.table and raw_column_lineage.downstream.table in table_name_urn_mapping:
        downstream_urn = table_name_urn_mapping[raw_column_lineage.downstream.table]
    
    return ColumnLineageInfo(
        downstream=DownstreamColumnRef(
            dataset=downstream_urn or "unknown_dataset",
            column=raw_column_lineage.downstream.column,
        ),
        upstreams=[
            ColumnRef(
                table=table_name_urn_mapping[upstream.table] if upstream.table in table_name_urn_mapping else str(upstream.table),
                column=upstream.column,
            )
            for upstream in raw_column_lineage.upstreams
        ],
        sql_expression=raw_column_lineage.logic,
    )


def parse_sql_for_column_lineage(
    sql: str,
    dialect: str = "snowflake",
    table_schemas: Optional[Dict[str, Dict[str, str]]] = None,
    default_db: Optional[str] = None,
    default_schema: Optional[str] = None,
) -> SqlParsingResult:
    """
    Parse SQL query and extract column-level lineage information.
    
    Args:
        sql: SQL query string to parse
        dialect: SQL dialect (default: snowflake)
        table_schemas: Optional table schemas for better column resolution
        default_db: Default database for unqualified table names
        default_schema: Default schema for unqualified table names
    
    Returns:
        SqlParsingResult with column lineage information
    """
    try:
        # Parse the SQL statement
        statement = parse_sql_query(sql, dialect=dialect)
        if not statement:
            return SqlParsingResult.make_from_error(ValueError("Failed to parse SQL query"))

        # Get SQLGlot dialect
        sqlglot_dialect = sqlglot.Dialect.get_or_raise(dialect)
        
        # Normalize default database/schema
        if dialect.lower() == "snowflake":
            default_db = default_db.upper() if default_db else None
            default_schema = default_schema.upper() if default_schema else None

        # Extract table-level lineage
        tables, modified = _table_level_lineage(statement, dialect=sqlglot_dialect)
        
        # Determine downstream table
        downstream_table: Optional[_TableName] = None
        if len(modified) == 1:
            downstream_table = next(iter(modified))

        # Convert table schemas to internal format
        table_name_schema_mapping: Dict[_TableName, Dict[str, str]] = {}
        table_name_urn_mapping: Dict[_TableName, str] = {}
        
        for table in tables | modified:
            qualified_table = table.qualified(
                dialect=sqlglot_dialect, 
                default_db=default_db, 
                default_schema=default_schema
            )
            
            # Create URN for table using string representation
            table_name_str = str(qualified_table)
            table_urn = f"urn:li:dataset:(urn:li:dataPlatform:{dialect},{table_name_str},PROD)"
            table_name_urn_mapping[qualified_table] = table_urn
            table_name_urn_mapping[table] = table_urn
            
            # Add schema info if available - try multiple table name formats
            if table_schemas:
                # Try different table name formats to match schema
                table_keys_to_try = [
                    str(qualified_table),  # Full qualified name
                    qualified_table.table,  # Just table name
                    f"{qualified_table.db_schema}.{qualified_table.table}" if qualified_table.db_schema else qualified_table.table,  # Schema.table
                ]
                
                for table_key in table_keys_to_try:
                    if table_key in table_schemas:
                        table_name_schema_mapping[qualified_table] = table_schemas[table_key]
                        break

        # Extract column-level lineage
        column_lineage: List[ColumnLineageInfo] = []
        try:
            logger.debug(f"Extracting column lineage for {len(tables | modified)} tables with {len(table_name_schema_mapping)} schemas")
            raw_column_lineage = _column_level_lineage(
                statement,
                dialect=sqlglot_dialect,
                downstream_table=downstream_table,
                table_name_schema_mapping=table_name_schema_mapping,
                default_db=default_db,
                default_schema=default_schema,
            )
            
            logger.debug(f"Raw column lineage extracted: {len(raw_column_lineage)} entries")
            
            # Translate to public format
            column_lineage = [
                _translate_internal_column_lineage(
                    table_name_urn_mapping, internal_col_lineage, sqlglot_dialect
                )
                for internal_col_lineage in raw_column_lineage
            ]
            
            logger.debug(f"Translated column lineage: {len(column_lineage)} entries")
        except Exception as e:
            logger.debug(f"Failed to extract column lineage: {e}", exc_info=True)

        # Calculate confidence based on success and table schema coverage
        total_tables = len(tables | modified)
        schemas_provided = len(table_name_schema_mapping)
        schema_coverage = schemas_provided / total_tables if total_tables > 0 else 0
        
        if column_lineage:
            # High confidence if we have column lineage and good schema coverage
            confidence = 0.9 if schema_coverage >= 0.5 else 0.7
        else:
            # Lower confidence if no column lineage extracted
            confidence = 0.3 if schema_coverage >= 0.5 else 0.1
        
        # Convert tables to URNs
        in_urns = sorted({table_name_urn_mapping[table] for table in tables if table in table_name_urn_mapping})
        out_urns = sorted({table_name_urn_mapping[table] for table in modified if table in table_name_urn_mapping})
        
        return SqlParsingResult(
            query_type="SELECT",  # Simplified for now
            in_tables=in_urns,
            out_tables=out_urns,
            column_lineage=column_lineage,
            confidence=confidence,
        )
        
    except Exception as e:
        logger.debug(f"Failed to parse SQL for column lineage: {e}", exc_info=True)
        return SqlParsingResult.make_from_error(e)


def extract_column_lineage_from_sql(
    sql: str,
    dialect: str = "snowflake",
    table_schemas: Optional[Dict[str, Dict[str, str]]] = None,
    default_db: Optional[str] = None,
    default_schema: Optional[str] = None,
) -> List[ColumnLineageInfo]:
    """
    Extract column lineage from SQL query.
    
    This is a convenience function that returns just the column lineage information.
    
    Args:
        sql: SQL query string
        dialect: SQL dialect
        table_schemas: Optional table schemas
        default_db: Default database
        default_schema: Default schema
    
    Returns:
        List of ColumnLineageInfo objects
    """
    result = parse_sql_for_column_lineage(
        sql=sql,
        dialect=dialect,
        table_schemas=table_schemas,
        default_db=default_db,
        default_schema=default_schema,
    )
    
    return result.column_lineage


# Example usage and testing
if __name__ == "__main__":
    # Test with a simple SQL query
    test_sql = """
    SELECT 
        c.customer_id,
        UPPER(c.first_name) as first_name_upper,
        CONCAT(c.first_name, ' ', c.last_name) as full_name,
        o.order_date,
        o.amount
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    WHERE o.order_date >= '2023-01-01'
    """
    
    print("=== DataGuild SQLGlot Column Lineage Parser Test ===\n")
    
    # Test column lineage extraction
    result = parse_sql_for_column_lineage(test_sql, dialect="snowflake")
    
    print(f"Query Type: {result.query_type}")
    print(f"Input Tables: {result.in_tables}")
    print(f"Output Tables: {result.out_tables}")
    print(f"Confidence: {result.confidence}")
    print(f"Column Lineage Count: {len(result.column_lineage)}")
    
    for i, lineage in enumerate(result.column_lineage):
        print(f"\nColumn Lineage {i+1}:")
        print(f"  Downstream: {lineage.downstream}")
        print(f"  Upstreams: {[str(up) for up in lineage.upstreams]}")
        print(f"  SQL Expression: {lineage.sql_expression}")
        print(f"  Confidence: {lineage.confidence_score}")
