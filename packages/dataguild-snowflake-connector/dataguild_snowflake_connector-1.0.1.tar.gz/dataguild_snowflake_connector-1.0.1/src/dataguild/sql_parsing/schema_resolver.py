"""
DataGuild SQL Schema Resolver.

This module provides comprehensive SQL parsing and schema resolution capabilities
for extracting table references, column usage, and data lineage information from SQL queries.
"""

import re
import logging
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import sqlparse
from sqlparse import sql
from sqlparse.tokens import Token

logger = logging.getLogger(__name__)


class QueryType(str, Enum):
    """Types of SQL queries."""
    SELECT = "SELECT"
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    CREATE = "CREATE"
    DROP = "DROP"
    ALTER = "ALTER"
    WITH = "WITH"
    MERGE = "MERGE"
    TRUNCATE = "TRUNCATE"
    UNKNOWN = "UNKNOWN"


class TableType(str, Enum):
    """Types of table references."""
    SOURCE = "SOURCE"  # Tables being read from
    TARGET = "TARGET"  # Tables being written to
    TEMPORARY = "TEMPORARY"  # Temporary tables or CTEs


@dataclass
class TableReference:
    """Represents a table reference in SQL."""

    name: str
    alias: Optional[str] = None
    schema: Optional[str] = None
    database: Optional[str] = None
    table_type: TableType = TableType.SOURCE
    line_number: Optional[int] = None
    column_number: Optional[int] = None

    def get_full_name(self) -> str:
        """Get fully qualified table name."""
        parts = []
        if self.database:
            parts.append(self.database)
        if self.schema:
            parts.append(self.schema)
        parts.append(self.name)
        return '.'.join(parts)

    def get_qualified_name(self) -> str:
        """Get qualified name (schema.table or just table)."""
        if self.schema:
            return f"{self.schema}.{self.name}"
        return self.name

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "alias": self.alias,
            "schema": self.schema,
            "database": self.database,
            "full_name": self.get_full_name(),
            "qualified_name": self.get_qualified_name(),
            "table_type": self.table_type.value,
            "line_number": self.line_number,
            "column_number": self.column_number,
        }


@dataclass
class ColumnReference:
    """Represents a column reference in SQL."""

    column: str
    table: Optional[str] = None
    alias: Optional[str] = None
    function: Optional[str] = None
    is_aggregate: bool = False
    is_literal: bool = False

    def get_qualified_name(self) -> str:
        """Get qualified column name."""
        if self.table:
            return f"{self.table}.{self.column}"
        return self.column

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "column": self.column,
            "table": self.table,
            "alias": self.alias,
            "qualified_name": self.get_qualified_name(),
            "function": self.function,
            "is_aggregate": self.is_aggregate,
            "is_literal": self.is_literal,
        }


@dataclass
class ParsedQuery:
    """Represents a parsed SQL query with extracted metadata."""

    query_type: QueryType
    tables: List[TableReference] = field(default_factory=list)
    columns: List[ColumnReference] = field(default_factory=list)
    cte_tables: List[TableReference] = field(default_factory=list)
    joins: List[Dict[str, Any]] = field(default_factory=list)
    where_conditions: List[str] = field(default_factory=list)
    group_by_columns: List[str] = field(default_factory=list)
    order_by_columns: List[str] = field(default_factory=list)
    having_conditions: List[str] = field(default_factory=list)
    subqueries: List["ParsedQuery"] = field(default_factory=list)
    
    # Additional attributes for column lineage extraction
    sql_query: Optional[str] = None  # Original SQL query
    table_schemas: Optional[Dict[str, Dict[str, str]]] = None  # Table schemas for column resolution
    default_db: Optional[str] = None  # Default database
    default_schema: Optional[str] = None  # Default schema

    def get_source_tables(self) -> List[TableReference]:
        """Get all source tables (tables being read from)."""
        return [t for t in self.tables if t.table_type == TableType.SOURCE]

    def get_target_tables(self) -> List[TableReference]:
        """Get all target tables (tables being written to)."""
        return [t for t in self.tables if t.table_type == TableType.TARGET]

    def get_all_tables(self) -> List[TableReference]:
        """Get all table references including CTEs."""
        return self.tables + self.cte_tables

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "query_type": self.query_type.value,
            "tables": [t.to_dict() for t in self.tables],
            "columns": [c.to_dict() for c in self.columns],
            "cte_tables": [t.to_dict() for t in self.cte_tables],
            "joins": self.joins,
            "where_conditions": self.where_conditions,
            "group_by_columns": self.group_by_columns,
            "order_by_columns": self.order_by_columns,
            "having_conditions": self.having_conditions,
            "subquery_count": len(self.subqueries),
        }


class SchemaResolver:
    """
    Comprehensive SQL schema resolver for extracting table and column references.

    Parses SQL queries to identify data lineage, table dependencies, and column usage
    patterns for metadata extraction and governance.
    """

    def __init__(
            self,
            default_schema: Optional[str] = None,
            default_database: Optional[str] = None,
            case_sensitive: bool = False
    ):
        """
        Initialize SchemaResolver.

        Args:
            default_schema: Default schema name for unqualified tables
            default_database: Default database name for unqualified tables
            case_sensitive: Whether to treat identifiers as case sensitive
        """
        self.default_schema = default_schema
        self.default_database = default_database
        self.case_sensitive = case_sensitive

        # Regex patterns for various SQL constructs
        self.patterns = self._compile_patterns()

        # Keywords that indicate table operations
        self.dml_keywords = {
            'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'MERGE', 'TRUNCATE',
            'CREATE', 'DROP', 'ALTER', 'WITH'
        }

        # Aggregate functions
        self.aggregate_functions = {
            'COUNT', 'SUM', 'AVG', 'MIN', 'MAX', 'STDDEV', 'VARIANCE',
            'FIRST', 'LAST', 'ARRAY_AGG', 'STRING_AGG', 'LISTAGG'
        }

    def _compile_patterns(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns for SQL parsing."""
        patterns = {}

        # Table name pattern (handles schema.table and database.schema.table)
        patterns['table_name'] = re.compile(
            r'(?:(\w+)\.)?(?:(\w+)\.)?(\w+)(?:\s+(?:AS\s+)?(\w+))?',
            re.IGNORECASE
        )

        # Column name pattern
        patterns['column_name'] = re.compile(
            r'(?:(\w+)\.)?(\w+)(?:\s+(?:AS\s+)?(\w+))?',
            re.IGNORECASE
        )

        # Function pattern
        patterns['function'] = re.compile(
            r'(\w+)\s*\(',
            re.IGNORECASE
        )

        # CTE pattern
        patterns['cte'] = re.compile(
            r'WITH\s+(\w+)(?:\s*\([^)]+\))?\s+AS\s*\(',
            re.IGNORECASE
        )

        return patterns

    def parse_query(self, sql_query: str) -> ParsedQuery:
        """
        Parse a SQL query and extract schema information.

        Args:
            sql_query: SQL query string to parse

        Returns:
            ParsedQuery object with extracted metadata
        """
        try:
            # Clean and normalize the query
            normalized_query = self._normalize_query(sql_query)

            # Parse the query using sqlparse
            parsed_statements = sqlparse.parse(normalized_query)

            if not parsed_statements:
                logger.warning("No SQL statements found in query")
                return ParsedQuery(query_type=QueryType.UNKNOWN)

            # Process the first statement (most common case)
            statement = parsed_statements[0]

            # Determine query type
            query_type = self._determine_query_type(statement)

            # Create parsed query object
            parsed_query = ParsedQuery(
                query_type=query_type,
                sql_query=sql_query  # Store the original SQL query
            )

            # Extract different components based on query type
            if query_type == QueryType.SELECT:
                self._parse_select_statement(statement, parsed_query)
            elif query_type == QueryType.INSERT:
                self._parse_insert_statement(statement, parsed_query)
            elif query_type == QueryType.UPDATE:
                self._parse_update_statement(statement, parsed_query)
            elif query_type == QueryType.DELETE:
                self._parse_delete_statement(statement, parsed_query)
            elif query_type == QueryType.WITH:
                self._parse_with_statement(statement, parsed_query)
            else:
                # Generic parsing for other statement types
                self._parse_generic_statement(statement, parsed_query)

            return parsed_query

        except Exception as e:
            logger.error(f"Error parsing SQL query: {e}")
            logger.debug(f"Query: {sql_query}")
            return ParsedQuery(query_type=QueryType.UNKNOWN)

    def _normalize_query(self, sql_query: str) -> str:
        """Normalize SQL query for parsing."""
        # Remove comments
        sql_query = re.sub(r'--.*$', '', sql_query, flags=re.MULTILINE)
        sql_query = re.sub(r'/\*.*?\*/', '', sql_query, flags=re.DOTALL)

        # Normalize whitespace
        sql_query = re.sub(r'\s+', ' ', sql_query)

        return sql_query.strip()

    def _determine_query_type(self, statement: sql.Statement) -> QueryType:
        """Determine the type of SQL query."""
        first_token = statement.token_first(skip_whitespace=True)
        if first_token and first_token.ttype is Token.Keyword.DML:
            keyword = first_token.value.upper()
            try:
                return QueryType(keyword)
            except ValueError:
                return QueryType.UNKNOWN
        return QueryType.UNKNOWN

    def _parse_select_statement(self, statement: sql.Statement, parsed_query: ParsedQuery) -> None:
        """Parse SELECT statement."""
        # Extract FROM clause tables
        from_clause = self._find_clause(statement, 'FROM')
        if from_clause:
            tables = self._extract_tables_from_clause(from_clause, TableType.SOURCE)
            parsed_query.tables.extend(tables)

        # Extract JOIN tables
        join_info = self._extract_joins(statement)
        parsed_query.joins.extend(join_info)

        # Add joined tables to tables list
        for join in join_info:
            if 'table' in join:
                parsed_query.tables.append(join['table'])

        # Extract SELECT columns
        select_clause = self._find_clause(statement, 'SELECT')
        if select_clause:
            columns = self._extract_columns_from_select(select_clause)
            parsed_query.columns.extend(columns)

        # Extract WHERE conditions
        where_clause = self._find_clause(statement, 'WHERE')
        if where_clause:
            parsed_query.where_conditions = self._extract_conditions(where_clause)

        # Extract GROUP BY columns
        group_by_clause = self._find_clause(statement, 'GROUP BY')
        if group_by_clause:
            parsed_query.group_by_columns = self._extract_column_names(group_by_clause)

        # Extract ORDER BY columns
        order_by_clause = self._find_clause(statement, 'ORDER BY')
        if order_by_clause:
            parsed_query.order_by_columns = self._extract_column_names(order_by_clause)

        # Extract HAVING conditions
        having_clause = self._find_clause(statement, 'HAVING')
        if having_clause:
            parsed_query.having_conditions = self._extract_conditions(having_clause)

    def _parse_insert_statement(self, statement: sql.Statement, parsed_query: ParsedQuery) -> None:
        """Parse INSERT statement."""
        # Extract target table
        target_tables = self._extract_insert_target(statement)
        parsed_query.tables.extend(target_tables)

        # Look for SELECT in INSERT ... SELECT
        select_part = self._find_select_in_insert(statement)
        if select_part:
            select_query = ParsedQuery(query_type=QueryType.SELECT)
            self._parse_select_statement(select_part, select_query)
            parsed_query.tables.extend(select_query.tables)
            parsed_query.subqueries.append(select_query)

    def _parse_update_statement(self, statement: sql.Statement, parsed_query: ParsedQuery) -> None:
        """Parse UPDATE statement."""
        # Extract target table
        target_tables = self._extract_update_target(statement)
        parsed_query.tables.extend(target_tables)

        # Extract WHERE conditions
        where_clause = self._find_clause(statement, 'WHERE')
        if where_clause:
            parsed_query.where_conditions = self._extract_conditions(where_clause)

    def _parse_delete_statement(self, statement: sql.Statement, parsed_query: ParsedQuery) -> None:
        """Parse DELETE statement."""
        # Extract target table
        target_tables = self._extract_delete_target(statement)
        parsed_query.tables.extend(target_tables)

        # Extract WHERE conditions
        where_clause = self._find_clause(statement, 'WHERE')
        if where_clause:
            parsed_query.where_conditions = self._extract_conditions(where_clause)

    def _parse_with_statement(self, statement: sql.Statement, parsed_query: ParsedQuery) -> None:
        """Parse WITH (CTE) statement."""
        # Extract CTE tables
        cte_tables = self._extract_cte_tables(statement)
        parsed_query.cte_tables.extend(cte_tables)

        # Find the main query after CTEs
        main_query = self._find_main_query_after_cte(statement)
        if main_query:
            # Recursively parse the main query
            main_parsed = self.parse_query(str(main_query))
            parsed_query.tables.extend(main_parsed.tables)
            parsed_query.columns.extend(main_parsed.columns)
            parsed_query.joins.extend(main_parsed.joins)

    def _parse_generic_statement(self, statement: sql.Statement, parsed_query: ParsedQuery) -> None:
        """Generic parsing for unsupported statement types."""
        # Extract any table-like identifiers
        identifiers = self._extract_identifiers(statement)
        for identifier in identifiers:
            table_ref = self._create_table_reference(identifier, TableType.SOURCE)
            if table_ref:
                parsed_query.tables.append(table_ref)

    def _find_clause(self, statement: sql.Statement, clause_name: str) -> Optional[sql.Token]:
        """Find a specific clause in the SQL statement."""
        for token in statement.tokens:
            if token.ttype is Token.Keyword and token.value.upper() == clause_name:
                return token
            elif hasattr(token, 'tokens'):
                result = self._find_clause(token, clause_name)
                if result:
                    return result
        return None

    def _extract_tables_from_clause(self, clause: sql.Token, table_type: TableType) -> List[TableReference]:
        """Extract table references from a clause."""
        tables = []

        # Simple implementation - this would be more complex in a full parser
        clause_str = str(clause).strip()

        # Remove the clause keyword (FROM, JOIN, etc.)
        parts = clause_str.split()[1:]  # Skip first word (FROM/JOIN)

        for part in parts:
            if ',' in part:
                # Multiple tables separated by commas
                for table_name in part.split(','):
                    table_ref = self._parse_table_identifier(table_name.strip(), table_type)
                    if table_ref:
                        tables.append(table_ref)
            else:
                table_ref = self._parse_table_identifier(part, table_type)
                if table_ref:
                    tables.append(table_ref)

        return tables

    def _parse_table_identifier(self, identifier: str, table_type: TableType) -> Optional[TableReference]:
        """Parse a table identifier into a TableReference."""
        if not identifier or identifier.upper() in self.dml_keywords:
            return None

        # Handle aliases (table AS alias or table alias)
        parts = identifier.split()
        table_name = parts[0]
        alias = None

        if len(parts) >= 2:
            if parts[1].upper() == 'AS' and len(parts) >= 3:
                alias = parts[2]
            else:
                alias = parts[1]

        return self._create_table_reference(table_name, table_type, alias)

    def _create_table_reference(
            self,
            full_name: str,
            table_type: TableType,
            alias: Optional[str] = None
    ) -> Optional[TableReference]:
        """Create a TableReference from a full table name."""
        # Split the full name into parts
        parts = full_name.split('.')

        if len(parts) == 1:
            # Just table name
            return TableReference(
                name=parts[0],
                schema=self.default_schema,
                database=self.default_database,
                alias=alias,
                table_type=table_type
            )
        elif len(parts) == 2:
            # schema.table
            return TableReference(
                name=parts[1],
                schema=parts[0],
                database=self.default_database,
                alias=alias,
                table_type=table_type
            )
        elif len(parts) == 3:
            # database.schema.table
            return TableReference(
                name=parts[2],
                schema=parts[1],
                database=parts[0],
                alias=alias,
                table_type=table_type
            )
        else:
            logger.warning(f"Invalid table name format: {full_name}")
            return None

    def _extract_joins(self, statement: sql.Statement) -> List[Dict[str, Any]]:
        """Extract JOIN information from statement."""
        joins = []
        # Simplified JOIN extraction - would be more sophisticated in practice
        statement_str = str(statement).upper()

        join_types = ['INNER JOIN', 'LEFT JOIN', 'RIGHT JOIN', 'FULL JOIN', 'CROSS JOIN', 'JOIN']

        for join_type in join_types:
            if join_type in statement_str:
                # This is a simplified extraction
                # In practice, you'd need more sophisticated parsing
                joins.append({
                    'join_type': join_type,
                    'table': None,  # Would extract actual table here
                    'condition': None  # Would extract ON condition here
                })

        return joins

    def _extract_columns_from_select(self, select_clause: sql.Token) -> List[ColumnReference]:
        """Extract column references from SELECT clause."""
        columns = []

        # Simplified column extraction
        select_str = str(select_clause)

        # Handle SELECT *
        if '*' in select_str:
            columns.append(ColumnReference(column='*'))

        # This would be much more sophisticated in practice
        # to handle functions, expressions, etc.

        return columns

    def _extract_conditions(self, clause: sql.Token) -> List[str]:
        """Extract conditions from WHERE/HAVING clause."""
        conditions = []
        clause_str = str(clause)

        # Very simplified condition extraction
        # Split by AND/OR (this is overly simplistic)
        parts = re.split(r'\s+(?:AND|OR)\s+', clause_str, flags=re.IGNORECASE)

        for part in parts:
            part = part.strip()
            if part and part.upper() not in ['WHERE', 'HAVING']:
                conditions.append(part)

        return conditions

    def _extract_column_names(self, clause: sql.Token) -> List[str]:
        """Extract column names from GROUP BY/ORDER BY clause."""
        column_names = []
        clause_str = str(clause)

        # Remove clause keyword
        parts = clause_str.split()[2:]  # Skip "GROUP BY" or "ORDER BY"

        for part in parts:
            # Remove commas and extra whitespace
            part = part.replace(',', '').strip()
            if part:
                column_names.append(part)

        return column_names

    def _extract_insert_target(self, statement: sql.Statement) -> List[TableReference]:
        """Extract target table from INSERT statement."""
        # Simplified extraction
        return []

    def _extract_update_target(self, statement: sql.Statement) -> List[TableReference]:
        """Extract target table from UPDATE statement."""
        # Simplified extraction
        return []

    def _extract_delete_target(self, statement: sql.Statement) -> List[TableReference]:
        """Extract target table from DELETE statement."""
        # Simplified extraction
        return []

    def _extract_cte_tables(self, statement: sql.Statement) -> List[TableReference]:
        """Extract CTE (Common Table Expression) tables."""
        cte_tables = []
        # Simplified CTE extraction
        return cte_tables

    def _find_main_query_after_cte(self, statement: sql.Statement) -> Optional[sql.Statement]:
        """Find the main query after CTE definitions."""
        # Simplified - would need proper parsing
        return None

    def _find_select_in_insert(self, statement: sql.Statement) -> Optional[sql.Statement]:
        """Find SELECT statement within INSERT ... SELECT."""
        # Simplified - would need proper parsing
        return None

    def _extract_identifiers(self, statement: sql.Statement) -> List[str]:
        """Extract identifier tokens from statement."""
        identifiers = []

        for token in statement.flatten():
            if token.ttype is Token.Name:
                identifiers.append(token.value)

        return identifiers

    def get_lineage_info(self, sql_query: str) -> Dict[str, Any]:
        """
        Extract data lineage information from SQL query.

        Args:
            sql_query: SQL query to analyze

        Returns:
            Dictionary containing lineage information
        """
        parsed_query = self.parse_query(sql_query)

        lineage_info = {
            "query_type": parsed_query.query_type.value,
            "source_tables": [t.to_dict() for t in parsed_query.get_source_tables()],
            "target_tables": [t.to_dict() for t in parsed_query.get_target_tables()],
            "column_lineage": self._analyze_column_lineage(parsed_query),
            "table_dependencies": self._analyze_table_dependencies(parsed_query),
        }

        return lineage_info

    def _analyze_column_lineage(self, parsed_query: ParsedQuery) -> List[Dict[str, Any]]:
        """Analyze column-level lineage from parsed query using SQLGlot."""
        try:
            # Import the new column lineage parser
            from dataguild.sql_parsing.sqlglot_column_lineage import extract_column_lineage_from_sql
            
            # Get the SQL query from the parsed query
            sql_query = getattr(parsed_query, 'sql_query', None)
            if not sql_query:
                logger.debug("No SQL query available for column lineage analysis")
                return []
            
            # Extract column lineage using SQLGlot
            column_lineage_infos = extract_column_lineage_from_sql(
                sql=sql_query,
                dialect="snowflake",  # Default to Snowflake for now
                table_schemas=getattr(parsed_query, 'table_schemas', None),
                default_db=getattr(parsed_query, 'default_db', None),
                default_schema=getattr(parsed_query, 'default_schema', None),
            )
            
            # Convert to the expected format
            column_lineage = []
            for lineage_info in column_lineage_infos:
                lineage_entry = {
                    "target_column": {
                        "dataset": lineage_info.downstream.dataset,
                        "column": lineage_info.downstream.column,
                        "qualified_name": lineage_info.downstream.qualified_name,
                    },
                    "source_columns": [
                        {
                            "table": upstream.table,
                            "column": upstream.column,
                            "qualified_name": upstream.qualified_name,
                        }
                        for upstream in lineage_info.upstreams
                    ],
                    "transformations": [lineage_info.sql_expression] if lineage_info.sql_expression else [],
                    "confidence_score": lineage_info.confidence_score,
                    "transformation_type": lineage_info.transformation_type,
                }
                column_lineage.append(lineage_entry)
            
            logger.debug(f"Extracted {len(column_lineage)} column lineage entries")
            return column_lineage
            
        except Exception as e:
            logger.debug(f"Failed to analyze column lineage: {e}")
            # Fallback to simple analysis
            column_lineage = []
            for column in parsed_query.columns:
                lineage_entry = {
                    "target_column": column.to_dict(),
                    "source_columns": [],  # Would trace back to source columns
                    "transformations": []  # Would identify functions/operations
                }
                column_lineage.append(lineage_entry)
            return column_lineage

    def _analyze_table_dependencies(self, parsed_query: ParsedQuery) -> List[Dict[str, Any]]:
        """Analyze table-level dependencies from parsed query."""
        dependencies = []

        source_tables = parsed_query.get_source_tables()
        target_tables = parsed_query.get_target_tables()

        for target in target_tables:
            for source in source_tables:
                dependencies.append({
                    "source_table": source.to_dict(),
                    "target_table": target.to_dict(),
                    "dependency_type": "DIRECT",
                    "query_type": parsed_query.query_type.value
                })

        return dependencies


# Convenience functions
def parse_sql(sql_query: str, default_schema: Optional[str] = None) -> ParsedQuery:
    """
    Parse SQL query and extract schema information.

    Args:
        sql_query: SQL query to parse
        default_schema: Default schema for unqualified tables

    Returns:
        ParsedQuery object with extracted metadata
    """
    resolver = SchemaResolver(default_schema=default_schema)
    return resolver.parse_query(sql_query)


def extract_table_names(sql_query: str) -> List[str]:
    """
    Extract table names from SQL query.

    Args:
        sql_query: SQL query to analyze

    Returns:
        List of table names
    """
    parsed_query = parse_sql(sql_query)
    return [table.get_full_name() for table in parsed_query.get_all_tables()]


def get_query_lineage(sql_query: str) -> Dict[str, Any]:
    """
    Get data lineage information from SQL query.

    Args:
        sql_query: SQL query to analyze

    Returns:
        Dictionary containing lineage information
    """
    resolver = SchemaResolver()
    return resolver.get_lineage_info(sql_query)


# Export all classes and functions
__all__ = [
    'SchemaResolver',
    'ParsedQuery',
    'TableReference',
    'ColumnReference',
    'QueryType',
    'TableType',
    'parse_sql',
    'extract_table_names',
    'get_query_lineage',
]
