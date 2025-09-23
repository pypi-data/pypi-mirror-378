"""
DataGuild Advanced S3 Utilities

Comprehensive S3 integration for lineage extraction, data discovery,
and cloud storage metadata processing.
"""

import boto3
import re
import json
from urllib.parse import urlparse
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

import logging
logger = logging.getLogger(__name__)


class S3ObjectType(Enum):
    """Types of S3 objects."""
    PARQUET = "parquet"
    CSV = "csv"
    JSON = "json"
    AVRO = "avro"
    ORC = "orc"
    DELTA = "delta"
    ICEBERG = "iceberg"
    DIRECTORY = "directory"
    UNKNOWN = "unknown"


@dataclass
class S3ObjectInfo:
    """Information about an S3 object."""
    bucket: str
    key: str
    size: int
    last_modified: datetime
    etag: str
    storage_class: str
    object_type: S3ObjectType
    metadata: Dict[str, str]

    @property
    def full_path(self) -> str:
        """Get full S3 path."""
        return f"s3://{self.bucket}/{self.key}"

    @property
    def file_extension(self) -> Optional[str]:
        """Get file extension."""
        if '.' in self.key:
            return self.key.split('.')[-1].lower()
        return None


class AdvancedS3Util:
    """
    Advanced S3 utilities for DataGuild with comprehensive
    metadata extraction and lineage capabilities.
    """

    def __init__(self, aws_access_key: Optional[str] = None, aws_secret_key: Optional[str] = None, region: str = 'us-east-1'):
        self.region = region
        self.session = boto3.Session(
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=region
        )
        self.s3_client = self.session.client('s3')

        # File type detection
        self.file_type_mappings = {
            'parquet': S3ObjectType.PARQUET,
            'csv': S3ObjectType.CSV,
            'json': S3ObjectType.JSON,
            'jsonl': S3ObjectType.JSON,
            'avro': S3ObjectType.AVRO,
            'orc': S3ObjectType.ORC,
        }

        # Performance metrics
        self.objects_scanned = 0
        self.objects_classified = 0

    def make_s3_urn_for_lineage(self, s3_path: str, env: str = "PROD") -> str:
        """
        Create standardized S3 URN for lineage tracking.

        Args:
            s3_path: Full S3 path (s3://bucket/key)
            env: Environment (PROD, DEV, STAGING)

        Returns:
            Standardized DataGuild S3 URN
        """
        if not s3_path.startswith('s3://'):
            raise ValueError(f"Invalid S3 path format: {s3_path}")

        parsed = urlparse(s3_path)
        bucket = parsed.netloc
        key = parsed.path.lstrip('/')

        # Normalize the path for consistent URNs
        normalized_key = self._normalize_s3_key(key)

        return f"urn:li:dataset:(urn:li:dataPlatform:s3,{bucket}/{normalized_key},{env})"

    def _normalize_s3_key(self, key: str) -> str:
        """Normalize S3 key for consistent URN generation."""
        # Remove trailing slashes
        normalized = key.rstrip('/')

        # Handle partitioned paths (Hive-style)
        if '=' in normalized:
            # Extract partition information for special handling
            parts = normalized.split('/')
            non_partition_parts = []
            partition_parts = []

            for part in parts:
                if '=' in part:
                    partition_parts.append(part)
                else:
                    non_partition_parts.append(part)

            # Reconstruct with partitions at the end
            if non_partition_parts and partition_parts:
                normalized = '/'.join(non_partition_parts) + '/{' + ','.join(partition_parts) + '}'

        return normalized

    def discover_s3_objects(
        self,
        bucket: str,
        prefix: str = "",
        max_objects: int = 10000,
        include_metadata: bool = True
    ) -> List[S3ObjectInfo]:
        """
        Discover S3 objects with comprehensive metadata extraction.

        Args:
            bucket: S3 bucket name
            prefix: Key prefix to filter objects
            max_objects: Maximum number of objects to return
            include_metadata: Whether to include object metadata

        Returns:
            List of S3ObjectInfo objects
        """
        objects = []
        continuation_token = None

        try:
            while len(objects) < max_objects:
                # Prepare list_objects_v2 parameters
                list_params = {
                    'Bucket': bucket,
                    'MaxKeys': min(1000, max_objects - len(objects))
                }

                if prefix:
                    list_params['Prefix'] = prefix

                if continuation_token:
                    list_params['ContinuationToken'] = continuation_token

                # List objects
                response = self.s3_client.list_objects_v2(**list_params)

                if 'Contents' not in response:
                    break

                # Process each object
                for obj in response['Contents']:
                    if len(objects) >= max_objects:
                        break

                    # Determine object type
                    object_type = self._classify_s3_object(obj['Key'])

                    # Get additional metadata if requested
                    metadata = {}
                    if include_metadata:
                        try:
                            head_response = self.s3_client.head_object(
                                Bucket=bucket,
                                Key=obj['Key']
                            )
                            metadata = head_response.get('Metadata', {})
                        except Exception as e:
                            logger.debug(f"Failed to get metadata for {obj['Key']}: {e}")

                    # Create S3ObjectInfo
                    object_info = S3ObjectInfo(
                        bucket=bucket,
                        key=obj['Key'],
                        size=obj['Size'],
                        last_modified=obj['LastModified'],
                        etag=obj['ETag'].strip('"'),
                        storage_class=obj.get('StorageClass', 'STANDARD'),
                        object_type=object_type,
                        metadata=metadata
                    )

                    objects.append(object_info)
                    self.objects_scanned += 1

                    if object_type != S3ObjectType.UNKNOWN:
                        self.objects_classified += 1

                # Check if there are more objects
                if not response.get('IsTruncated', False):
                    break

                continuation_token = response.get('NextContinuationToken')

        except Exception as e:
            logger.error(f"Failed to discover S3 objects in {bucket}: {e}")
            raise

        logger.info(f"Discovered {len(objects)} S3 objects in {bucket} (prefix: {prefix})")
        return objects

    def _classify_s3_object(self, key: str) -> S3ObjectType:
        """Classify S3 object based on key patterns."""
        key_lower = key.lower()

        # Check file extension
        if '.' in key:
            extension = key.split('.')[-1].lower()
            if extension in self.file_type_mappings:
                return self.file_type_mappings[extension]

        # Check for special directory patterns
        if key.endswith('/'):
            return S3ObjectType.DIRECTORY

        # Check for Delta Lake
        if '_delta_log' in key_lower or key_lower.endswith('.delta'):
            return S3ObjectType.DELTA

        # Check for Iceberg
        if 'metadata.json' in key_lower or 'manifest-list' in key_lower:
            return S3ObjectType.ICEBERG

        return S3ObjectType.UNKNOWN

    def extract_table_schema_from_path(self, s3_path: str) -> Optional[Dict[str, str]]:
        """
        Extract database/schema/table information from S3 path.
        Handles common patterns like:
        - s3://bucket/database/schema/table/
        - s3://bucket/data/database.schema.table/
        """
        parsed = urlparse(s3_path)
        key_parts = parsed.path.strip('/').split('/')

        if len(key_parts) >= 3:
            # Pattern: bucket/database/schema/table
            return {
                'database': key_parts[0],
                'schema': key_parts[1],
                'table': key_parts[2]
            }
        elif len(key_parts) >= 2:
            # Pattern: bucket/data/database.schema.table
            table_part = key_parts[-1]
            if table_part.count('.') >= 2:
                parts = table_part.split('.')
                return {
                    'database': parts[0],
                    'schema': parts[1],
                    'table': '.'.join(parts[2:])
                }

        return None

    def generate_lineage_mappings(
        self,
        external_table_locations: List[str],
        discovered_tables: Set[str],
        env: str = "PROD"
    ) -> List[Dict[str, str]]:
        """
        Generate lineage mappings between S3 objects and external tables.

        Args:
            external_table_locations: List of S3 locations from external tables
            discovered_tables: Set of discovered table identifiers
            env: Environment for URN generation

        Returns:
            List of lineage mapping dictionaries
        """
        lineage_mappings = []

        for location in external_table_locations:
            if not location.startswith('s3://'):
                continue

            try:
                # Create S3 URN
                s3_urn = self.make_s3_urn_for_lineage(location, env)

                # Try to match with discovered tables
                schema_info = self.extract_table_schema_from_path(location)

                if schema_info:
                    # Try to find matching table
                    table_identifier = f"{schema_info['database']}.{schema_info['schema']}.{schema_info['table']}"

                    if table_identifier in discovered_tables:
                        lineage_mappings.append({
                            'upstream_urn': s3_urn,
                            'downstream_urn': f"urn:li:dataset:(urn:li:dataPlatform:snowflake,{table_identifier},{env})",
                            'lineage_type': 'COPY'
                        })
                    else:
                        # Create generic mapping
                        lineage_mappings.append({
                            'upstream_urn': s3_urn,
                            'downstream_urn': f"urn:li:dataset:(urn:li:dataPlatform:external,{table_identifier},{env})",
                            'lineage_type': 'COPY'
                        })
                else:
                    # Create generic S3 mapping
                    lineage_mappings.append({
                        'upstream_urn': s3_urn,
                        'downstream_urn': f"urn:li:dataset:(urn:li:dataPlatform:external,{location.replace('s3://', '')},{env})",
                        'lineage_type': 'COPY'
                    })

            except Exception as e:
                logger.warning(f"Failed to create lineage mapping for {location}: {e}")

        logger.info(f"Generated {len(lineage_mappings)} S3 lineage mappings")
        return lineage_mappings

    def analyze_s3_dataset(self, bucket: str, prefix: str) -> Dict[str, Any]:
        """
        Analyze S3 dataset for metadata extraction.

        Returns comprehensive analysis including:
        - Object counts by type
        - Size distribution
        - Partitioning patterns
        - Schema inference hints
        """
        objects = self.discover_s3_objects(bucket, prefix, max_objects=5000)

        # Basic statistics
        total_objects = len(objects)
        total_size = sum(obj.size for obj in objects)

        # Type distribution
        type_distribution = {}
        for obj_type in S3ObjectType:
            count = sum(1 for obj in objects if obj.object_type == obj_type)
            if count > 0:
                type_distribution[obj_type.value] = count

        # Size analysis
        size_stats = {
            'total_bytes': total_size,
            'avg_size_bytes': total_size / total_objects if total_objects > 0 else 0,
            'min_size_bytes': min(obj.size for obj in objects) if objects else 0,
            'max_size_bytes': max(obj.size for obj in objects) if objects else 0
        }

        # Partitioning analysis
        partition_patterns = self._analyze_partitioning_patterns(objects)

        # Temporal analysis
        temporal_stats = self._analyze_temporal_patterns(objects)

        analysis = {
            'bucket': bucket,
            'prefix': prefix,
            'total_objects': total_objects,
            'total_size_bytes': total_size,
            'type_distribution': type_distribution,
            'size_statistics': size_stats,
            'partition_patterns': partition_patterns,
            'temporal_statistics': temporal_stats,
            'analysis_timestamp': datetime.now().isoformat()
        }

        return analysis

    def _analyze_partitioning_patterns(self, objects: List[S3ObjectInfo]) -> Dict[str, Any]:
        """Analyze partitioning patterns in S3 objects."""
        partition_columns = set()
        partition_values = defaultdict(set)

        for obj in objects:
            # Look for Hive-style partitioning
            key_parts = obj.key.split('/')
            for part in key_parts:
                if '=' in part:
                    column, value = part.split('=', 1)
                    partition_columns.add(column)
                    partition_values[column].add(value)

        return {
            'has_partitioning': len(partition_columns) > 0,
            'partition_columns': list(partition_columns),
            'partition_cardinality': {
                col: len(values) for col, values in partition_values.items()
            }
        }

    def _analyze_temporal_patterns(self, objects: List[S3ObjectInfo]) -> Dict[str, Any]:
        """Analyze temporal patterns in S3 objects."""
        if not objects:
            return {}

        timestamps = [obj.last_modified for obj in objects]

        return {
            'earliest_object': min(timestamps).isoformat(),
            'latest_object': max(timestamps).isoformat(),
            'objects_by_year': self._group_by_time_period(timestamps, 'year'),
            'objects_by_month': self._group_by_time_period(timestamps, 'month')
        }

    def _group_by_time_period(self, timestamps: List[datetime], period: str) -> Dict[str, int]:
        """Group timestamps by time period."""
        groups = defaultdict(int)

        for ts in timestamps:
            if period == 'year':
                key = str(ts.year)
            elif period == 'month':
                key = f"{ts.year}-{ts.month:02d}"
            elif period == 'day':
                key = f"{ts.year}-{ts.month:02d}-{ts.day:02d}"
            else:
                key = str(ts.year)

            groups[key] += 1

        return dict(groups)

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get S3 utility performance statistics."""
        return {
            'objects_scanned': self.objects_scanned,
            'objects_classified': self.objects_classified,
            'classification_rate': (
                self.objects_classified / self.objects_scanned
                if self.objects_scanned > 0 else 0
            )
        }


# Convenience functions for backward compatibility
def make_s3_urn_for_lineage(s3_path: str, env: str = "PROD") -> str:
    """Create S3 URN for lineage (convenience function)."""
    util = AdvancedS3Util()
    return util.make_s3_urn_for_lineage(s3_path, env)

def make_s3_urn(s3_path: str, env: str = "PROD") -> str:
    """Alternative name for S3 URN creation."""
    return make_s3_urn_for_lineage(s3_path, env)
