#!/usr/bin/env python3
"""
Dialect configuration system for schema validation.

This module contains all dialect-specific configurations including types,
modes, required/optional attributes for different database systems.
"""
from __future__ import annotations

from typing import Any

# BigQuery Configuration
BIGQUERY_TYPES = {
    'STRING', 'BYTES', 'INTEGER', 'INT64', 'FLOAT', 'FLOAT64', 'NUMERIC',
    'BIGNUMERIC', 'BOOLEAN', 'BOOL', 'TIMESTAMP', 'DATE', 'TIME',
    'DATETIME', 'GEOGRAPHY', 'RECORD', 'STRUCT',
}

BIGQUERY_MODES = {'NULLABLE', 'REQUIRED', 'REPEATED'}

BIGQUERY_REQUIRED_ATTRS = {'name', 'type', 'mode', 'description'}

BIGQUERY_OPTIONAL_ATTRS = {'fields'}

# PostgreSQL Configuration (Future)
POSTGRESQL_TYPES = {
    'bigint', 'bigserial', 'bit', 'boolean', 'box', 'bytea', 'character',
    'character varying', 'cidr', 'circle', 'date', 'double precision',
    'inet', 'integer', 'interval', 'json', 'jsonb', 'line', 'lseg',
    'macaddr', 'money', 'numeric', 'path', 'pg_lsn', 'point', 'polygon',
    'real', 'smallint', 'smallserial', 'serial', 'text', 'time',
    'timestamp', 'tsquery', 'tsvector', 'txid_snapshot', 'uuid', 'xml',
}

POSTGRESQL_MODES = {'NOT NULL', 'NULL'}

POSTGRESQL_REQUIRED_ATTRS = {'name', 'type', 'description'}

POSTGRESQL_OPTIONAL_ATTRS = {'constraints', 'default'}

# Hive Configuration (Future)
HIVE_TYPES = {
    'tinyint', 'smallint', 'int', 'bigint', 'boolean', 'float', 'double',
    'string', 'timestamp', 'binary', 'decimal', 'char', 'varchar', 'date',
    'array', 'map', 'struct', 'uniontype',
}

HIVE_MODES = {'NOT NULL', 'NULL'}

HIVE_REQUIRED_ATTRS = {'name', 'type', 'description'}

HIVE_OPTIONAL_ATTRS = {'comment', 'partitioned'}

# SQL Server Configuration (Future)
SQLSERVER_TYPES = {
    'bigint', 'binary', 'bit', 'char', 'date', 'datetime', 'datetime2',
    'datetimeoffset', 'decimal', 'float', 'geography', 'geometry',
    'hierarchyid', 'image', 'int', 'money', 'nchar', 'ntext', 'numeric',
    'nvarchar', 'real', 'smalldatetime', 'smallint', 'smallmoney',
    'sql_variant', 'text', 'time', 'timestamp', 'tinyint', 'uniqueidentifier',
    'varbinary', 'varchar', 'xml',
}

SQLSERVER_MODES = {'NOT NULL', 'NULL'}

SQLSERVER_REQUIRED_ATTRS = {'name', 'type', 'description'}

SQLSERVER_OPTIONAL_ATTRS = {'constraints', 'default', 'identity'}

# Main dialect registry for extensibility
DIALECT_CONFIG = {
    'bigquery': {
        'types': BIGQUERY_TYPES,
        'modes': BIGQUERY_MODES,
        'required_attrs': BIGQUERY_REQUIRED_ATTRS,
        'optional_attrs': BIGQUERY_OPTIONAL_ATTRS,
    },
    # Future dialects (commented out until fully implemented)
    # 'postgresql': {
    #     'types': POSTGRESQL_TYPES,
    #     'modes': POSTGRESQL_MODES,
    #     'required_attrs': POSTGRESQL_REQUIRED_ATTRS,
    #     'optional_attrs': POSTGRESQL_OPTIONAL_ATTRS,
    # },
    # 'hive': {
    #     'types': HIVE_TYPES,
    #     'modes': HIVE_MODES,
    #     'required_attrs': HIVE_REQUIRED_ATTRS,
    #     'optional_attrs': HIVE_OPTIONAL_ATTRS,
    # },
    # 'sqlserver': {
    #     'types': SQLSERVER_TYPES,
    #     'modes': SQLSERVER_MODES,
    #     'required_attrs': SQLSERVER_REQUIRED_ATTRS,
    #     'optional_attrs': SQLSERVER_OPTIONAL_ATTRS,
    # },
}


def get_supported_dialects() -> list[str]:
    """Get list of all supported database dialects."""
    return list(DIALECT_CONFIG.keys())


def get_dialect_config(dialect: str) -> dict[str, Any] | None:
    """Get configuration for a specific dialect."""
    return DIALECT_CONFIG.get(dialect)


def validate_dialect(dialect: str) -> bool:
    """Check if a dialect is supported."""
    return dialect in DIALECT_CONFIG


def get_dialect_info(dialect: str) -> dict[str, Any] | None:
    """Get comprehensive information about a dialect."""
    if dialect not in DIALECT_CONFIG:
        return None

    config = DIALECT_CONFIG[dialect]
    return {
        'name': dialect,
        'types_count': len(config['types']),
        'modes_count': len(config['modes']),
        'required_attrs': sorted(config['required_attrs']),
        'optional_attrs': sorted(config['optional_attrs']),
        'supported_types': sorted(config['types']),
        'supported_modes': sorted(config['modes']),
    }