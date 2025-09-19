"""Schema transformation utilities for ClickHouse migration."""

import logging
import re
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class ClickHouseEngineTransformer:
    """Transforms ClickHouse table engines for compatibility between different deployments."""

    # Mapping from ClickHouse Cloud engines to self-hosted equivalents
    CLOUD_TO_SELFHOSTED_ENGINES = {
        'SharedMergeTree': 'MergeTree',
        'SharedReplacingMergeTree': 'ReplacingMergeTree',
        'SharedSummingMergeTree': 'SummingMergeTree',
        'SharedAggregatingMergeTree': 'AggregatingMergeTree',
        'SharedCollapsingMergeTree': 'CollapsingMergeTree',
        'SharedVersionedCollapsingMergeTree': 'VersionedCollapsingMergeTree',
        'SharedGraphiteMergeTree': 'GraphiteMergeTree',
    }

    # Mapping from self-hosted to cloud engines (reverse)
    SELFHOSTED_TO_CLOUD_ENGINES = {v: k for k, v in CLOUD_TO_SELFHOSTED_ENGINES.items()}

    def __init__(self, transformation_mode: str = 'cloud_to_selfhosted'):
        """
        Initialize the transformer.

        Args:
            transformation_mode: Either 'cloud_to_selfhosted' or 'selfhosted_to_cloud'
        """
        self.transformation_mode = transformation_mode

        if transformation_mode == 'cloud_to_selfhosted':
            self.engine_mapping = self.CLOUD_TO_SELFHOSTED_ENGINES
        elif transformation_mode == 'selfhosted_to_cloud':
            self.engine_mapping = self.SELFHOSTED_TO_CLOUD_ENGINES
        else:
            raise ValueError(f"Invalid transformation_mode: {transformation_mode}")

    def transform_create_statement(self, create_statement: str) -> str:
        """
        Transform a CREATE TABLE statement to use compatible engines.

        Args:
            create_statement: Original CREATE TABLE statement

        Returns:
            Transformed CREATE TABLE statement
        """
        original_statement = create_statement

        for source_engine, target_engine in self.engine_mapping.items():
            # Pattern to match ENGINE = SourceEngine with optional parameters
            pattern = rf'\bENGINE\s*=\s*{re.escape(source_engine)}\b'
            replacement = f'ENGINE = {target_engine}'

            create_statement = re.sub(pattern, replacement, create_statement, flags=re.IGNORECASE)

            if create_statement != original_statement:
                logger.info(f"Transformed engine {source_engine} -> {target_engine}")
                break

        # Handle specific SharedMergeTree cases that need ORDER BY
        if 'ENGINE = MergeTree' in create_statement and 'ORDER BY' not in create_statement.upper():
            # Try to extract a reasonable ORDER BY from the original schema
            order_by_clause = self._extract_or_generate_order_by(create_statement)
            if order_by_clause:
                # Insert ORDER BY after the ENGINE clause
                pattern = r'(ENGINE\s*=\s*MergeTree[^,\n]*)'
                replacement = f'\\1\n{order_by_clause}'
                create_statement = re.sub(pattern, replacement, create_statement, flags=re.IGNORECASE)
                logger.info(f"Added {order_by_clause} to MergeTree engine")

        return create_statement

    def _extract_or_generate_order_by(self, create_statement: str) -> Optional[str]:
        """
        Extract or generate an appropriate ORDER BY clause.

        Args:
            create_statement: CREATE TABLE statement

        Returns:
            ORDER BY clause or None
        """
        # Try to find primary key or unique columns
        lines = create_statement.split('\n')
        columns = []

        for line in lines:
            line = line.strip()
            if line and not line.startswith('--') and '(' in line:
                # Extract column name from column definition
                # Pattern: column_name DataType [modifiers]
                match = re.match(r'`?([a-zA-Z_][a-zA-Z0-9_]*)`?\s+\w+', line.strip('(),'))
                if match:
                    column_name = match.group(1)
                    # Prefer id-like columns for ordering
                    if any(key_word in column_name.lower() for key_word in ['id', 'key', 'uuid']):
                        return f"ORDER BY {column_name}"
                    columns.append(column_name)

        # If no id-like column found, use the first column
        if columns:
            return f"ORDER BY {columns[0]}"

        return None

    def get_supported_engines(self, connection) -> set:
        """
        Get list of supported engines from a ClickHouse connection.

        Args:
            connection: ClickHouseConnection instance

        Returns:
            Set of supported engine names
        """
        try:
            result = connection.execute_query("SELECT name FROM system.table_engines")
            return {row[0] for row in result.result_rows}
        except Exception as e:
            logger.warning(f"Could not retrieve supported engines: {e}")
            return set()

    def is_transformation_needed(self, create_statement: str, target_connection) -> bool:
        """
        Check if transformation is needed for the given statement.

        Args:
            create_statement: CREATE TABLE statement
            target_connection: Target ClickHouseConnection

        Returns:
            True if transformation is needed
        """
        supported_engines = self.get_supported_engines(target_connection)

        for source_engine in self.engine_mapping.keys():
            if f'ENGINE = {source_engine}' in create_statement and source_engine not in supported_engines:
                return True

        return False

    def analyze_compatibility(self, source_connection, target_connection) -> Dict[str, any]:
        """
        Analyze compatibility between source and target connections.

        Args:
            source_connection: Source ClickHouseConnection
            target_connection: Target ClickHouseConnection

        Returns:
            Compatibility analysis results
        """
        source_engines = self.get_supported_engines(source_connection)
        target_engines = self.get_supported_engines(target_connection)

        cloud_engines_in_source = source_engines.intersection(self.CLOUD_TO_SELFHOSTED_ENGINES.keys())
        missing_in_target = cloud_engines_in_source - target_engines

        return {
            'source_engines': source_engines,
            'target_engines': target_engines,
            'cloud_engines_found': list(cloud_engines_in_source),
            'transformation_needed': len(missing_in_target) > 0,
            'engines_to_transform': list(missing_in_target),
            'recommended_mode': 'cloud_to_selfhosted' if missing_in_target else None
        }