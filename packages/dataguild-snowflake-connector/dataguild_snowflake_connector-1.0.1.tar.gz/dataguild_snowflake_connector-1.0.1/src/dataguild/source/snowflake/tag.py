"""
DataGuild Enhanced Snowflake Tag Extractor

Clean and enhanced tag extraction for Snowflake objects with improved
performance, error handling, and maintainability over DataHub's implementation.

Key Improvements:
1. Better error handling and logging
2. Simple caching with cleanup
3. Enhanced filtering logic
4. Cleaner method signatures
5. Better performance tracking
6. Simplified tag processing

Author: DataGuild Engineering Team
"""

import logging
from typing import Dict, Iterable, List, Optional

from dataguild.emitter.mce_builder import get_sys_time
from dataguild.emitter.mcp import MetadataChangeProposalWrapper
from dataguild.api.workunit import MetadataWorkUnit
from dataguild.source.snowflake.constants import SnowflakeObjectDomain
from dataguild.source.snowflake.config import (
    SnowflakeV2Config,
    TagOption,
)
from dataguild.source.snowflake.report import SnowflakeV2Report
from dataguild.source.snowflake.schema import (
    SnowflakeDataDictionary,
    SnowflakeTag,
    _SnowflakeTagCache,
)
from dataguild.source.snowflake.utils import (
    SnowflakeCommonMixin,
    SnowflakeIdentifierBuilder,
)
from dataguild.track.p2a import AuditStamp
from dataguild.track.p2a import (
    StructuredPropertyDefinition,
)
from dataguild.source.snowflake.schema import ChangeTypeClass
from dataguild.metadata.urns import (
    ContainerUrn,
    DatasetUrn,
    DataTypeUrn,
    EntityTypeUrn,
    SchemaFieldUrn,
    StructuredPropertyUrn,
)

logger = logging.getLogger(__name__)


class SnowflakeTagExtractor(SnowflakeCommonMixin):
    """Enhanced Snowflake tag extractor with improved performance and error handling."""

    def __init__(
        self,
        config: SnowflakeV2Config,
        data_dictionary: SnowflakeDataDictionary,
        report: SnowflakeV2Report,
        snowflake_identifiers: SnowflakeIdentifierBuilder,
    ) -> None:
        self.config = config
        self.data_dictionary = data_dictionary
        self.report = report
        self.snowflake_identifiers = snowflake_identifiers

        # Enhanced caching with cleanup tracking
        self.tag_cache: Dict[str, _SnowflakeTagCache] = {}
        self.cache_stats = {"hits": 0, "misses": 0, "size": 0}

        logger.info("Enhanced Snowflake tag extractor initialized")

    def get_tags_for_object(
        self,
        domain: str,
        db_name: str,
        schema_name: Optional[str] = None,
        table_name: Optional[str] = None,
    ) -> List[SnowflakeTag]:
        """Get tags for a Snowflake object with enhanced error handling."""
        try:
            if self.config.extract_tags == TagOption.without_lineage:
                tags = self._get_tags_without_propagation(
                    domain, db_name, schema_name, table_name
                )
            elif self.config.extract_tags == TagOption.with_lineage:
                tags = self._get_tags_with_propagation(
                    domain, db_name, schema_name, table_name
                )
            else:
                return []

            # Filter and return allowed tags
            filtered_tags = self._filter_tags(tags)
            return filtered_tags if filtered_tags else []

        except Exception as e:
            logger.error(f"Failed to get tags for {domain} {db_name}: {e}")
            return []

    def get_column_tags_for_table(
        self,
        table_name: str,
        schema_name: str,
        db_name: str,
    ) -> Dict[str, List[SnowflakeTag]]:
        """Get column-level tags with enhanced processing."""
        try:
            temp_column_tags: Dict[str, List[SnowflakeTag]] = {}

            if self.config.extract_tags == TagOption.without_lineage:
                # Use cached approach for better performance
                if db_name not in self.tag_cache:
                    self._load_database_tags_to_cache(db_name)

                temp_column_tags = self.tag_cache[db_name].get_column_tags_for_table(
                    table_name, schema_name, db_name
                )

            elif self.config.extract_tags == TagOption.with_lineage:
                self.report.num_get_tags_on_columns_for_table_queries += 1

                quoted_table = self.snowflake_identifiers.get_quoted_identifier_for_table(
                    db_name, schema_name, table_name
                )

                temp_column_tags = self.data_dictionary.get_tags_on_columns_for_table(
                    quoted_table_name=quoted_table,
                    db_name=db_name,
                )

            # Filter column tags
            column_tags: Dict[str, List[SnowflakeTag]] = {}
            for column_name, tags in temp_column_tags.items():
                filtered_tags = self._filter_tags(tags)
                if filtered_tags:
                    column_tags[column_name] = filtered_tags

            return column_tags

        except Exception as e:
            logger.error(f"Failed to get column tags for {table_name}: {e}")
            return {}

    def get_tags_on_object(
        self,
        domain: str,
        db_name: str,
        schema_name: Optional[str] = None,
        table_name: Optional[str] = None,
    ) -> List[SnowflakeTag]:
        """Get tags for a Snowflake object - alias for get_tags_for_object method."""
        return self.get_tags_for_object(domain, db_name, schema_name, table_name)

    def create_structured_property_templates(self) -> Iterable[MetadataWorkUnit]:
        """Create structured property templates with enhanced validation."""
        try:
            # Get all tags from all databases instead of calling non-existent get_all_tags()
            all_tags = []
            databases = self.data_dictionary.get_databases()
            for database in databases:
                try:
                    tag_cache = self.data_dictionary.get_tags_for_database_without_propagation(database.name)
                    all_tags.extend(tag_cache.get_all_tags())
                except Exception as e:
                    logger.warning(f"Failed to get tags for database {database.name}: {e}")
                    continue
            
            for tag in all_tags:
                if not self._is_tag_allowed_for_structured_properties(tag):
                    continue

                if self.config.extract_tags_as_structured_properties:
                    self.report.num_structured_property_templates_created += 1
                    yield from self._generate_structured_property_workunits(tag)

        except Exception as e:
            logger.error(f"Failed to create structured property templates: {e}")

    def _get_tags_without_propagation(
        self,
        domain: str,
        db_name: str,
        schema_name: Optional[str],
        table_name: Optional[str],
    ) -> List[SnowflakeTag]:
        """Get tags without propagation using enhanced caching."""
        # Load to cache if not present
        if db_name not in self.tag_cache:
            self._load_database_tags_to_cache(db_name)

        try:
            if domain == SnowflakeObjectDomain.DATABASE:
                return self.tag_cache[db_name].get_database_tags(db_name)

            elif domain == SnowflakeObjectDomain.SCHEMA:
                if schema_name is None:
                    raise ValueError("Schema name required for schema domain")
                return self.tag_cache[db_name].get_schema_tags(schema_name, db_name)

            elif domain == SnowflakeObjectDomain.TABLE:
                if schema_name is None or table_name is None:
                    raise ValueError("Schema and table names required for table domain")
                return self.tag_cache[db_name].get_table_tags(
                    table_name, schema_name, db_name
                )

            else:
                raise ValueError(f"Unsupported domain: {domain}")

        except Exception as e:
            logger.error(f"Failed to get tags without propagation: {e}")
            return []

    def _get_tags_with_propagation(
        self,
        domain: str,
        db_name: str,
        schema_name: Optional[str],
        table_name: Optional[str],
    ) -> List[SnowflakeTag]:
        """Get tags with propagation using direct queries."""
        try:
            identifier = self._build_object_identifier(domain, db_name, schema_name, table_name)

            self.report.num_get_tags_for_object_queries += 1

            return self.data_dictionary.get_tags_for_object_with_propagation(
                domain=domain,
                quoted_identifier=identifier,
                db_name=db_name
            )

        except Exception as e:
            logger.error(f"Failed to get tags with propagation: {e}")
            return []

    def _build_object_identifier(
        self,
        domain: str,
        db_name: str,
        schema_name: Optional[str],
        table_name: Optional[str]
    ) -> str:
        """Build quoted identifier for object."""
        if domain == SnowflakeObjectDomain.DATABASE:
            return self.snowflake_identifiers.get_quoted_identifier_for_database(db_name)

        elif domain == SnowflakeObjectDomain.SCHEMA:
            if schema_name is None:
                raise ValueError("Schema name required")
            return self.snowflake_identifiers.get_quoted_identifier_for_schema(
                db_name, schema_name
            )

        elif domain == SnowflakeObjectDomain.TABLE:
            if schema_name is None or table_name is None:
                raise ValueError("Schema and table names required")
            return self.snowflake_identifiers.get_quoted_identifier_for_table(
                db_name, schema_name, table_name
            )

        else:
            raise ValueError(f"Unsupported domain: {domain}")

    def _load_database_tags_to_cache(self, db_name: str) -> None:
        """Load database tags to cache with error handling."""
        try:
            self.tag_cache[db_name] = (
                self.data_dictionary.get_tags_for_database_without_propagation(db_name)
            )
            self.cache_stats["misses"] += 1
            self.cache_stats["size"] = len(self.tag_cache)

        except Exception as e:
            logger.error(f"Failed to load tags for database {db_name}: {e}")
            # Create empty cache entry to avoid repeated failures
            self.tag_cache[db_name] = _SnowflakeTagCache()

    def _is_tag_allowed_for_structured_properties(self, tag: SnowflakeTag) -> bool:
        """Check if tag is allowed for structured properties."""
        try:
            identifier = tag._id_prefix_as_str()
            return self.config.structured_property_pattern.allowed(identifier)
        except Exception as e:
            logger.error(f"Failed to check tag allowance: {e}")
            return False

    def _generate_structured_property_workunits(
        self, tag: SnowflakeTag
    ) -> Iterable[MetadataWorkUnit]:
        """Generate structured property workunits with enhanced validation."""
        try:
            identifier = self.snowflake_identifiers.snowflake_identifier(
                tag.structured_property_identifier()
            )

            urn = StructuredPropertyUrn(identifier).urn()

            aspect = StructuredPropertyDefinition(
                qualifiedName=identifier,
                displayName=tag.name,
                valueType=DataTypeUrn("datahub.string").urn(),
                entityTypes=[
                    EntityTypeUrn(f"datahub.{ContainerUrn.ENTITY_TYPE}").urn(),
                    EntityTypeUrn(f"datahub.{DatasetUrn.ENTITY_TYPE}").urn(),
                    EntityTypeUrn(f"datahub.{SchemaFieldUrn.ENTITY_TYPE}").urn(),
                ],
                lastModified=AuditStamp(
                    time=get_sys_time(),
                    actor="urn:li:corpuser:datahub"
                ),
            )

            yield MetadataChangeProposalWrapper(
                entityUrn=urn,
                aspect=aspect,
                changeType=ChangeTypeClass.ADDITION,
                headers={"If-None-Match": "*"},
            ).as_workunit()

        except Exception as e:
            logger.error(f"Failed to generate structured property workunit for {tag.name}: {e}")

    def _filter_tags(self, tags: Optional[List[SnowflakeTag]]) -> Optional[List[SnowflakeTag]]:
        """Filter tags with enhanced validation and reporting."""
        if not tags:
            return tags

        logger.info(f"🔍 DEBUG: Filtering {len(tags)} tags")
        allowed_tags = []

        for i, tag in enumerate(tags):
            logger.info(f"🔍 DEBUG: Processing tag {i+1}: {type(tag)} - {tag}")
            try:
                # Determine identifier based on config
                identifier = (
                    tag._id_prefix_as_str()
                    if self.config.extract_tags_as_structured_properties
                    else tag.tag_identifier()
                )

                # Report entity scanned
                self.report.report_entity_scanned(identifier, "tag")

                # Get appropriate pattern
                pattern = (
                    self.config.structured_property_pattern
                    if self.config.extract_tags_as_structured_properties
                    else self.config.tag_pattern
                )

                # Check if allowed
                if pattern.allowed(identifier):
                    allowed_tags.append(tag)
                else:
                    self.report.report_dropped(identifier)

            except Exception as e:
                logger.error(f"Failed to filter tag {tag.name}: {e}")
                continue

        return allowed_tags

    def get_cache_stats(self) -> Dict:
        """Get caching statistics for monitoring."""
        return {
            "cache_size": len(self.tag_cache),
            "cache_hits": self.cache_stats["hits"],
            "cache_misses": self.cache_stats["misses"],
            "databases_cached": list(self.tag_cache.keys())
        }

    def clear_cache(self) -> None:
        """Clear tag cache for memory management."""
        self.tag_cache.clear()
        self.cache_stats = {"hits": 0, "misses": 0, "size": 0}
        logger.info("Tag cache cleared")


# =============================================
# Utility Functions (Fixed)
# =============================================

def validate_tag_domain(domain: str) -> bool:
    """Validate that domain is supported for tag extraction."""
    supported_domains = {
        SnowflakeObjectDomain.DATABASE,
        SnowflakeObjectDomain.SCHEMA,
        SnowflakeObjectDomain.TABLE,
    }
    return domain in supported_domains


def get_tag_extraction_summary(extractor: SnowflakeTagExtractor) -> Dict:
    """
    Get summary of tag extraction operations.

    Args:
        extractor: SnowflakeTagExtractor instance

    Returns:
        Dictionary with extraction summary statistics
    """
    try:
        cache_stats = extractor.get_cache_stats()
    except Exception as e:
        logger.error(f"Failed to get cache stats: {e}")
        cache_stats = {"cache_hits": 0, "cache_misses": 0, "cache_size": 0}

    try:
        extraction_mode = extractor.config.extract_tags.value if hasattr(extractor.config.extract_tags, 'value') else str(extractor.config.extract_tags)
        structured_properties_enabled = getattr(extractor.config, 'extract_tags_as_structured_properties', False)
    except Exception as e:
        logger.error(f"Failed to get config info: {e}")
        extraction_mode = "unknown"
        structured_properties_enabled = False

    try:
        templates_created = getattr(extractor.report, 'num_structured_property_templates_created', 0)
        tag_queries_made = getattr(extractor.report, 'num_get_tags_for_object_queries', 0)
    except Exception as e:
        logger.error(f"Failed to get report info: {e}")
        templates_created = 0
        tag_queries_made = 0

    # Calculate cache efficiency
    total_requests = cache_stats.get("cache_hits", 0) + cache_stats.get("cache_misses", 0)
    cache_efficiency = (
        (cache_stats.get("cache_hits", 0) / max(total_requests, 1)) * 100
        if total_requests > 0 else 0
    )

    return {
        "extraction_mode": extraction_mode,
        "structured_properties_enabled": structured_properties_enabled,
        "cache_performance": {
            "databases_cached": cache_stats.get("cache_size", 0),
            "cache_efficiency": round(cache_efficiency, 2),
            "cache_hits": cache_stats.get("cache_hits", 0),
            "cache_misses": cache_stats.get("cache_misses", 0),
        },
        "templates_created": templates_created,
        "tag_queries_made": tag_queries_made,
        "databases_in_cache": cache_stats.get("databases_cached", [])
    }


def optimize_tag_extraction_performance(extractor: SnowflakeTagExtractor) -> Dict[str, str]:
    """
    Provide performance optimization recommendations for tag extraction.

    Args:
        extractor: SnowflakeTagExtractor instance

    Returns:
        Dictionary with optimization recommendations
    """
    try:
        cache_stats = extractor.get_cache_stats()
        total_requests = cache_stats["cache_hits"] + cache_stats["cache_misses"]

        recommendations = {}

        # Cache efficiency recommendations
        if total_requests > 0:
            efficiency = (cache_stats["cache_hits"] / total_requests) * 100
            if efficiency < 50:
                recommendations["cache_efficiency"] = (
                    "Low cache efficiency detected. Consider using 'without_lineage' mode "
                    "for better caching when lineage propagation is not required."
                )
            elif efficiency > 90:
                recommendations["cache_efficiency"] = (
                    "Excellent cache efficiency! Current configuration is optimal."
                )

        # Memory usage recommendations
        if cache_stats["cache_size"] > 10:
            recommendations["memory_usage"] = (
                "Large number of databases cached. Consider periodic cache clearing "
                "for memory optimization using clear_cache() method."
            )

        # Configuration recommendations
        if hasattr(extractor.config, 'extract_tags'):
            if extractor.config.extract_tags == TagOption.with_lineage:
                recommendations["configuration"] = (
                    "Using 'with_lineage' mode. Switch to 'without_lineage' if tag "
                    "propagation is not needed for better performance."
                )

        return recommendations

    except Exception as e:
        logger.error(f"Failed to generate performance recommendations: {e}")
        return {"error": "Could not generate recommendations due to an error"}


def get_tags_on_object(
        self,
        domain: str,
        db_name: str,
        schema_name: Optional[str] = None,
        table_name: Optional[str] = None,
) -> List[SnowflakeTag]:
    """
    Get tags on a Snowflake object - compatibility method for DataGuild extraction.

    This method provides compatibility with the extraction pipeline that expects
    'get_tags_on_object' method name. It delegates to get_tags_for_object.

    Args:
        domain: Object domain (DATABASE, SCHEMA, TABLE)
        db_name: Database name
        schema_name: Schema name (optional, required for SCHEMA and TABLE domains)
        table_name: Table name (optional, required for TABLE domain)

    Returns:
        List of SnowflakeTag objects
    """
    try:
        logger.debug(f"Getting tags on object: domain={domain}, db={db_name}, schema={schema_name}, table={table_name}")

        # Delegate to existing get_tags_for_object method
        tags = self.get_tags_for_object(
            domain=domain,
            db_name=db_name,
            schema_name=schema_name,
            table_name=table_name
        )

        logger.debug(f"Retrieved {len(tags) if tags else 0} tags for {domain} object")
        return tags if tags else []

    except Exception as e:
        logger.error(f"Failed to get tags on object {domain} {db_name}: {e}")
        self.report.report_warning(
            f"tag-extraction-{domain.lower()}",
            f"Failed to extract tags for {domain} {db_name}: {str(e)}"
        )
        return []


def create_tag_extraction_report(extractor: SnowflakeTagExtractor) -> str:
    """
    Create a formatted report of tag extraction operations.

    Args:
        extractor: SnowflakeTagExtractor instance

    Returns:
        Formatted string report
    """
    try:
        summary = get_tag_extraction_summary(extractor)
        recommendations = optimize_tag_extraction_performance(extractor)

        report = [
            "=== DataGuild Snowflake Tag Extraction Report ===",
            "",
            f"Extraction Mode: {summary['extraction_mode']}",
            f"Structured Properties: {'Enabled' if summary['structured_properties_enabled'] else 'Disabled'}",
            "",
            "=== Cache Performance ===",
            f"Databases Cached: {summary['cache_performance']['databases_cached']}",
            f"Cache Efficiency: {summary['cache_performance']['cache_efficiency']}%",
            f"Cache Hits: {summary['cache_performance']['cache_hits']}",
            f"Cache Misses: {summary['cache_performance']['cache_misses']}",
            "",
            "=== Operation Statistics ===",
            f"Templates Created: {summary['templates_created']}",
            f"Tag Queries Made: {summary['tag_queries_made']}",
            "",
        ]

        if recommendations:
            report.extend([
                "=== Performance Recommendations ===",
                ""
            ])
            for category, recommendation in recommendations.items():
                report.append(f"{category.replace('_', ' ').title()}: {recommendation}")
                report.append("")

        report.append("=== End Report ===")

        return "\n".join(report)

    except Exception as e:
        logger.error(f"Failed to create tag extraction report: {e}")
        return f"Error creating report: {str(e)}"


# =============================================
# Enhanced Error Handling and Monitoring
# =============================================

class TagExtractionMetrics:
    """Metrics collection for tag extraction operations."""

    def __init__(self):
        self.metrics = {
            "total_tags_extracted": 0,
            "total_objects_processed": 0,
            "cache_operations": 0,
            "errors_encountered": 0,
            "performance_warnings": 0
        }

    def increment_metric(self, metric_name: str, value: int = 1):
        """Increment a metric counter."""
        if metric_name in self.metrics:
            self.metrics[metric_name] += value

    def get_metrics(self) -> Dict[str, int]:
        """Get current metrics snapshot."""
        return self.metrics.copy()

    def reset_metrics(self):
        """Reset all metrics to zero."""
        for key in self.metrics:
            self.metrics[key] = 0


# Export all classes and functions
__all__ = [
    'SnowflakeTagExtractor',
    'validate_tag_domain',
    'get_tag_extraction_summary',
    'optimize_tag_extraction_performance',
    'create_tag_extraction_report',
    'TagExtractionMetrics',
]
