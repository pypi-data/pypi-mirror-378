"""
DataGuild SQL Stored Procedures Base Module

Comprehensive stored procedure metadata extraction and work unit generation
for SQL databases including lineage extraction, schema parsing, and
container relationship management.
"""

import logging
from typing import Any, Dict, Iterable, List, Optional, Set, Union
from dataclasses import dataclass
from datetime import datetime

from dataguild.api.workunit import MetadataWorkUnit
from dataguild.metadata.schemas import (
    SchemaMetadata, SchemaField, SchemaFieldDataType, StringType,
    Status, DatasetProperties, SubTypes
)
from dataguild.sql_parsing.schema_resolver import SchemaResolver
from dataguild.sql_parsing.sql_parsing_aggregator import SqlParsingAggregator

logger = logging.getLogger(__name__)


@dataclass
class ProcedureParameter:
    """Represents a stored procedure parameter."""
    name: str
    data_type: str
    mode: str  # IN, OUT, INOUT
    default_value: Optional[str] = None
    description: Optional[str] = None


@dataclass
class StoredProcedure:
    """Base class for stored procedure metadata."""
    name: str
    database: str
    schema: str
    language: str
    definition: Optional[str] = None
    parameters: List[ProcedureParameter] = None
    return_type: Optional[str] = None
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None
    owner: Optional[str] = None
    security_type: Optional[str] = None  # DEFINER, INVOKER

    def __post_init__(self):
        if self.parameters is None:
            self.parameters = []

    @property
    def qualified_name(self) -> str:
        """Get fully qualified procedure name."""
        return f"{self.database}.{self.schema}.{self.name}"

    @property
    def signature(self) -> str:
        """Get procedure signature with parameters."""
        param_strs = []
        for param in self.parameters:
            param_str = f"{param.mode} {param.name} {param.data_type}"
            if param.default_value:
                param_str += f" DEFAULT {param.default_value}"
            param_strs.append(param_str)

        return f"{self.name}({', '.join(param_strs)})"


def generate_procedure_container_workunits(
        database_key: str,
        schema_key: str,
        platform: str = "sql",
        platform_instance: Optional[str] = None,
) -> Iterable[MetadataWorkUnit]:
    """
    Generate container work units for stored procedure organization.

    Creates the hierarchical container structure for organizing stored procedures
    within database schemas, enabling proper navigation and organization in
    the DataGuild metadata catalog.

    Args:
        database_key: Database container key
        schema_key: Schema container key
        platform: Data platform name (e.g., 'snowflake', 'postgres')
        platform_instance: Optional platform instance identifier

    Yields:
        MetadataWorkUnit instances for procedure containers
    """
    # Generate procedure collection container
    procedure_container_urn = f"urn:li:container:({database_key},{schema_key},procedures)"

    # Container properties for procedure collection
    container_properties = {
        "name": "Stored Procedures",
        "description": f"Collection of stored procedures in schema {schema_key}",
        "platform": platform,
        "container_type": "PROCEDURE_COLLECTION",
        "parent_container": f"urn:li:container:{schema_key}",
        "created": int(datetime.now().timestamp() * 1000),
    }

    if platform_instance:
        container_properties["platform_instance"] = platform_instance

    # Status aspect for container
    status_aspect = Status(removed=False)

    # Generate container work unit
    yield MetadataWorkUnit(
        id=f"procedure-container-{database_key}-{schema_key}",
        mcp_raw={
            "entityUrn": procedure_container_urn,
            "aspect": container_properties,
            "aspectName": "containerProperties"
        }
    )

    # Generate status work unit
    yield MetadataWorkUnit(
        id=f"procedure-container-status-{database_key}-{schema_key}",
        mcp_raw={
            "entityUrn": procedure_container_urn,
            "aspect": status_aspect.to_dict(),
            "aspectName": "status"
        }
    )

    logger.debug(f"Generated procedure container work units for {schema_key}")


def generate_procedure_workunits(
        procedure: StoredProcedure,
        database_key: str,
        schema_key: str,
        platform: str = "sql",
        platform_instance: Optional[str] = None,
        schema_resolver: Optional[SchemaResolver] = None,
        aggregator: Optional[SqlParsingAggregator] = None,
        extract_lineage: bool = True,
        include_definition: bool = True,
) -> Iterable[MetadataWorkUnit]:
    """
    Generate comprehensive metadata work units for a stored procedure.

    Creates complete metadata representation including procedure properties,
    parameter schema, lineage information, and container relationships.

    Args:
        procedure: StoredProcedure object with metadata
        database_key: Database container key
        schema_key: Schema container key
        platform: Data platform name
        platform_instance: Optional platform instance
        schema_resolver: Optional schema resolver for lineage
        aggregator: Optional SQL parsing aggregator
        extract_lineage: Whether to extract lineage information
        include_definition: Whether to include procedure definition

    Yields:
        MetadataWorkUnit instances for the stored procedure
    """
    # Generate procedure URN
    procedure_urn = f"urn:li:dataset:(urn:li:dataPlatform:{platform},{procedure.qualified_name},{platform_instance or 'PROD'})"

    # Generate status aspect
    status_aspect = Status(removed=False)
    yield MetadataWorkUnit(
        id=f"procedure-status-{procedure.qualified_name}",
        mcp_raw={
            "entityUrn": procedure_urn,
            "aspect": status_aspect.to_dict(),
            "aspectName": "status"
        }
    )

    # Generate dataset properties
    custom_properties = {
        "procedure_language": procedure.language,
        "procedure_type": "STORED_PROCEDURE",
        "parameter_count": str(len(procedure.parameters)),
    }

    if procedure.return_type:
        custom_properties["return_type"] = procedure.return_type
    if procedure.owner:
        custom_properties["owner"] = procedure.owner
    if procedure.security_type:
        custom_properties["security_type"] = procedure.security_type

    dataset_properties = DatasetProperties(
        name=procedure.name,
        description=procedure.description or f"Stored procedure {procedure.signature}",
        custom_properties=custom_properties,
        created=int(procedure.created_at.timestamp() * 1000) if procedure.created_at else None,
        last_modified=int(procedure.modified_at.timestamp() * 1000) if procedure.modified_at else None,
    )

    yield MetadataWorkUnit(
        id=f"procedure-properties-{procedure.qualified_name}",
        mcp_raw={
            "entityUrn": procedure_urn,
            "aspect": dataset_properties.to_dict(),
            "aspectName": "datasetProperties"
        }
    )

    # Generate schema metadata for parameters
    schema_fields = []
    for i, param in enumerate(procedure.parameters):
        field = SchemaField(
            name=param.name,
            type=SchemaFieldDataType(
                type_name=param.data_type,
                nullable=param.default_value is not None,
            ),
            description=param.description or f"{param.mode} parameter of type {param.data_type}",
            nullable=param.default_value is not None,
            custom_properties={
                "parameter_mode": param.mode,
                "parameter_position": str(i + 1),
                "default_value": param.default_value or "",
            }
        )
        schema_fields.append(field)

    # Add return type as a field if present
    if procedure.return_type:
        return_field = SchemaField(
            name="__return__",
            type=SchemaFieldDataType(
                type_name=procedure.return_type,
                nullable=True,
            ),
            description=f"Return value of type {procedure.return_type}",
            nullable=True,
            custom_properties={
                "parameter_mode": "RETURN",
                "parameter_position": "0",
            }
        )
        schema_fields.insert(0, return_field)

    schema_metadata = SchemaMetadata(
        name=procedure.qualified_name,
        platform=f"urn:li:dataPlatform:{platform}",
        version=0,
        hash="",
        fields=schema_fields,
    )

    yield MetadataWorkUnit(
        id=f"procedure-schema-{procedure.qualified_name}",
        mcp_raw={
            "entityUrn": procedure_urn,
            "aspect": schema_metadata.to_dict(),
            "aspectName": "schemaMetadata"
        }
    )

    # Generate subtypes aspect
    subtypes = SubTypes(typeNames=["Stored Procedure"])
    yield MetadataWorkUnit(
        id=f"procedure-subtypes-{procedure.qualified_name}",
        mcp_raw={
            "entityUrn": procedure_urn,
            "aspect": subtypes.to_dict(),
            "aspectName": "subTypes"
        }
    )

    # Generate procedure definition aspect if available and requested
    if include_definition and procedure.definition:
        procedure_definition = {
            "definition": procedure.definition,
            "language": procedure.language,
            "signature": procedure.signature,
        }

        yield MetadataWorkUnit(
            id=f"procedure-definition-{procedure.qualified_name}",
            mcp_raw={
                "entityUrn": procedure_urn,
                "aspect": procedure_definition,
                "aspectName": "procedureDefinition"
            }
        )

    # Generate container membership
    procedure_container_urn = f"urn:li:container:({database_key},{schema_key},procedures)"
    container_membership = {
        "containers": [procedure_container_urn]
    }

    yield MetadataWorkUnit(
        id=f"procedure-container-{procedure.qualified_name}",
        mcp_raw={
            "entityUrn": procedure_urn,
            "aspect": container_membership,
            "aspectName": "container"
        }
    )

    # Generate lineage information if requested and available
    if extract_lineage and procedure.definition and schema_resolver and aggregator:
        try:
            # Parse procedure definition for lineage
            aggregator.add_procedure_definition(
                procedure_urn=procedure_urn,
                procedure_definition=procedure.definition,
                default_db=procedure.database,
                default_schema=procedure.schema,
            )

            logger.debug(f"Added procedure {procedure.qualified_name} to lineage aggregator")
        except Exception as e:
            logger.warning(f"Failed to extract lineage for procedure {procedure.qualified_name}: {e}")

    logger.debug(f"Generated work units for procedure {procedure.qualified_name}")


def create_procedure_from_dict(data: Dict[str, Any]) -> StoredProcedure:
    """
    Create StoredProcedure object from dictionary data.

    Args:
        data: Dictionary containing procedure metadata

    Returns:
        StoredProcedure object
    """
    parameters = []
    if "parameters" in data:
        for param_data in data["parameters"]:
            parameter = ProcedureParameter(
                name=param_data["name"],
                data_type=param_data["data_type"],
                mode=param_data.get("mode", "IN"),
                default_value=param_data.get("default_value"),
                description=param_data.get("description"),
            )
            parameters.append(parameter)

    return StoredProcedure(
        name=data["name"],
        database=data["database"],
        schema=data["schema"],
        language=data.get("language", "SQL"),
        definition=data.get("definition"),
        parameters=parameters,
        return_type=data.get("return_type"),
        description=data.get("description"),
        created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
        modified_at=datetime.fromisoformat(data["modified_at"]) if data.get("modified_at") else None,
        owner=data.get("owner"),
        security_type=data.get("security_type"),
    )


def get_procedure_dependencies(
        procedure_definition: str,
        schema_resolver: Optional[SchemaResolver] = None,
) -> Set[str]:
    """
    Extract table and view dependencies from procedure definition.

    Args:
        procedure_definition: SQL definition of the procedure
        schema_resolver: Optional schema resolver for parsing

    Returns:
        Set of table/view URNs that the procedure depends on
    """
    dependencies = set()

    try:
        if schema_resolver:
            # Use schema resolver to parse SQL and extract dependencies
            parsed_result = schema_resolver.parse_sql(procedure_definition)
            if parsed_result and hasattr(parsed_result, 'table_references'):
                dependencies.update(parsed_result.table_references)
        else:
            # Simple regex-based extraction as fallback
            import re

            # Extract FROM clauses
            from_pattern = r'\bFROM\s+([^\s,;()]+)'
            from_matches = re.findall(from_pattern, procedure_definition, re.IGNORECASE)
            dependencies.update(from_matches)

            # Extract JOIN clauses
            join_pattern = r'\bJOIN\s+([^\s,;()]+)'
            join_matches = re.findall(join_pattern, procedure_definition, re.IGNORECASE)
            dependencies.update(join_matches)

            # Extract INSERT INTO clauses
            insert_pattern = r'\bINSERT\s+INTO\s+([^\s,;()]+)'
            insert_matches = re.findall(insert_pattern, procedure_definition, re.IGNORECASE)
            dependencies.update(insert_matches)

            # Extract UPDATE clauses
            update_pattern = r'\bUPDATE\s+([^\s,;()]+)'
            update_matches = re.findall(update_pattern, procedure_definition, re.IGNORECASE)
            dependencies.update(update_matches)

    except Exception as e:
        logger.warning(f"Failed to extract procedure dependencies: {e}")

    return dependencies


# Export all classes and functions
__all__ = [
    'ProcedureParameter',
    'StoredProcedure',
    'generate_procedure_container_workunits',
    'generate_procedure_workunits',
    'create_procedure_from_dict',
    'get_procedure_dependencies',
]
