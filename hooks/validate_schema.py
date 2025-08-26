#!/usr/bin/env python3

import argparse
import json
import os
import sys
from typing import List, Dict, Any, Tuple, Optional

from naming_utils import (
    validate_naming_convention,
    convert_naming_convention,
    get_supported_case_styles
)


# Dialect Configuration System
BIGQUERY_TYPES = {
    'STRING', 'BYTES', 'INTEGER', 'INT64', 'FLOAT', 'FLOAT64', 'NUMERIC', 'BIGNUMERIC',
    'BOOLEAN', 'BOOL', 'TIMESTAMP', 'DATE', 'TIME', 'DATETIME', 'GEOGRAPHY', 'RECORD', 'STRUCT'
}

BIGQUERY_MODES = {'NULLABLE', 'REQUIRED', 'REPEATED'}

BIGQUERY_REQUIRED_ATTRS = {'name', 'type', 'mode', 'description'}

BIGQUERY_OPTIONAL_ATTRS = {'fields'}

# Dialect registry for extensibility
DIALECT_CONFIG = {
    'bigquery': {
        'types': BIGQUERY_TYPES,
        'modes': BIGQUERY_MODES,
        'required_attrs': BIGQUERY_REQUIRED_ATTRS,
        'optional_attrs': BIGQUERY_OPTIONAL_ATTRS
    }
    # Future dialects can be added here:
    # 'postgresql': {...},
    # 'hive': {...},
    # 'sqlserver': {...}
}


def apply_naming_fix(name: str, case_style: str) -> str:
    """Apply the correct naming convention to a field name."""
    return convert_naming_convention(name, case_style)


def apply_field_fixes(field: Dict[str, Any], case_style: str) -> Dict[str, Any]:
    """Apply naming fixes to a field and its nested fields recursively."""
    if 'name' in field:
        fixed_name = apply_naming_fix(field['name'], case_style)
        if fixed_name != field['name']:
            field = field.copy()  # Don't modify original
            field['name'] = fixed_name
    
    # Handle nested fields for RECORD types
    if field.get('type') == 'RECORD' and 'fields' in field and isinstance(field['fields'], list):
        field = field.copy()  # Don't modify original
        field['fields'] = [apply_field_fixes(nested_field, case_style) for nested_field in field['fields']]
    
    return field


# Naming validation is now handled by naming_utils module


def validate_field(field: Dict[str, Any], dialect_config: Dict[str, Any], case_style: str, path: str = "") -> List[str]:
    errors = []
    field_path = f"{path}.{field.get('name', 'UNNAMED')}" if path else field.get('name', 'UNNAMED')
    
    # Use dialect-specific required attributes
    required_attrs = dialect_config['required_attrs']
    for attr in required_attrs:
        if attr not in field:
            errors.append(f"Field {field_path}: Missing required attribute '{attr}'")
        elif not field[attr]:
            errors.append(f"Field {field_path}: Attribute '{attr}' cannot be empty")
    
    if 'name' in field:
        naming_error = validate_naming_convention(field['name'], case_style)
        if naming_error:
            errors.append(f"Field {field_path}: {naming_error}")
    
    # Use dialect-specific type and mode validation
    if 'type' in field and field['type'] not in dialect_config['types']:
        errors.append(f"Field {field_path}: Invalid type '{field['type']}'. "
                     f"Valid types: {', '.join(sorted(dialect_config['types']))}")
    
    if 'mode' in field and field['mode'] not in dialect_config['modes']:
        errors.append(f"Field {field_path}: Invalid mode '{field['mode']}'. "
                     f"Valid modes: {', '.join(sorted(dialect_config['modes']))}")
    
    if field.get('type') == 'RECORD' and 'fields' in field:
        if not isinstance(field['fields'], list):
            errors.append(f"Field {field_path}: 'fields' must be a list for RECORD type")
        else:
            for nested_field in field['fields']:
                errors.extend(validate_field(nested_field, dialect_config, case_style, field_path))
    
    return errors


def validate_schema(file_path: str, dialect: str, case_style: str, mode: str = 'lint') -> Tuple[List[str], Optional[Dict[str, Any]]]:
    if dialect not in DIALECT_CONFIG:
        return ([f"Unsupported dialect '{dialect}'. Available dialects: {', '.join(DIALECT_CONFIG.keys())}"], None)
    
    dialect_config = DIALECT_CONFIG[dialect]
    errors = []
    fixed_data = None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return ([f"Invalid JSON in {file_path}: {e}"], None)
    except Exception as e:
        return ([f"Error reading {file_path}: {e}"], None)
    
    if not isinstance(data, list):
        return ([f"{file_path}: Schema must be a list of field objects"], None)
    
    if not data:
        return ([f"{file_path}: Schema cannot be empty"], None)
    
    # For fix mode, create a copy of data to modify
    if mode == 'fix':
        fixed_data = json.loads(json.dumps(data))  # Deep copy
    
    for i, field in enumerate(data):
        if not isinstance(field, dict):
            errors.append(f"{file_path}: Field {i} must be an object")
            continue
        
        field_errors = validate_field(field, dialect_config, case_style)
        errors.extend([f"{file_path}: {error}" for error in field_errors])
        
        # Apply fixes if in fix mode
        if mode == 'fix' and fixed_data and 'name' in field:
            fixed_data[i] = apply_field_fixes(fixed_data[i], case_style)
    
    return (errors, fixed_data)


def discover_files(file_type: str, path_regex: Optional[str]) -> List[str]:
    import re
    files = []
    
    for root, _, filenames in os.walk('.'):
        for filename in filenames:
            if filename.endswith(f'.{file_type}'):
                file_path = os.path.join(root, filename)
                
                if path_regex:
                    if re.search(path_regex, file_path):
                        files.append(file_path)
                else:
                    files.append(file_path)
    
    return files


def main():
    parser = argparse.ArgumentParser(
        description='Validate schema files for compliance with specified dialect and conventions.'
    )
    parser.add_argument(
        '--file-type', 
        default='json',
        help='File extension to validate (default: json)'
    )
    parser.add_argument(
        '--path-regex',
        help='Regex pattern to filter file paths'
    )
    parser.add_argument(
        '--dialect',
        default='bigquery',
        choices=['bigquery'],
        help='Schema dialect to validate against (default: bigquery)'
    )
    parser.add_argument(
        '--case',
        default='snake',
        choices=get_supported_case_styles(),
        help='Naming convention for field names. Supported: snake, camel, pascal, upper, kebab, train, flat, cobol, title (default: snake)'
    )
    parser.add_argument(
        '--mode',
        default='lint',
        choices=['lint', 'fix'],
        help='Operation mode: lint (check only) or fix (apply corrections) (default: lint)'
    )
    parser.add_argument(
        'files',
        nargs='*',
        help='Specific files to validate (if not provided, discovers files automatically)'
    )
    
    args = parser.parse_args()
    
    if args.files:
        candidate_files = args.files
    else:
        candidate_files = discover_files(args.file_type, args.path_regex)
    
    if not candidate_files:
        print(f"No {args.file_type} files found matching the criteria.")
        return 0
    
    all_errors = []
    
    for file_path in candidate_files:
        if not os.path.exists(file_path):
            all_errors.append(f"File not found: {file_path}")
            continue
            
        validation_errors, fixed_data = validate_schema(file_path, args.dialect, args.case, args.mode)
        all_errors.extend(validation_errors)
        
        # Apply fixes if in fix mode and fixes are available
        if args.mode == 'fix' and fixed_data is not None and not validation_errors:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(fixed_data, f, indent=2, ensure_ascii=False)
                print(f"✓ Applied fixes to {file_path}")
            except Exception as e:
                all_errors.append(f"Error writing fixes to {file_path}: {e}")
    
    if all_errors:
        print("\n".join(all_errors))
        return 1
    
    if args.mode == 'fix':
        print(f"✓ All {len(candidate_files)} schema file(s) processed successfully.")
    else:
        print(f"✓ All {len(candidate_files)} schema file(s) passed validation.")
    return 0


if __name__ == '__main__':
    sys.exit(main())