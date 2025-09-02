#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

from hooks.dialect_config import DIALECT_CONFIG
from hooks.naming_utils import convert_naming_convention
from hooks.naming_utils import get_supported_case_styles
from hooks.naming_utils import validate_naming_convention


# Dialect configurations are now imported from dialect_config.py


def apply_naming_fix(name: str, case_style: str) -> str:
    """Apply the correct naming convention to a field name."""
    return convert_naming_convention(name, case_style)


def apply_field_fixes(
        field: dict[str, Any], case_style: str,
) -> dict[str, Any]:
    """Apply naming fixes to a field and its nested fields recursively."""
    if 'name' in field:
        fixed_name = apply_naming_fix(field['name'], case_style)
        if fixed_name != field['name']:
            field = field.copy()  # Don't modify original
            field['name'] = fixed_name

    # Handle nested fields for RECORD types
    if (
        field.get('type') == 'RECORD' and 'fields' in field and
        isinstance(field['fields'], list)
    ):
        field = field.copy()  # Don't modify original
        field['fields'] = [
            apply_field_fixes(nested_field, case_style)
            for nested_field in field['fields']
        ]

    return field


# Naming validation is now handled by naming_utils module


def validate_field(
        field: dict[str, Any],
        dialect_config: dict[str, Any],
        case_style: str,
        path: str = '',
        mode: str = 'lint',
) -> tuple[list[str], list[str]]:
    errors = []
    fixable_errors = []  # Errors that can be auto-fixed (naming only)
    field_path = (
        f"{path}.{field.get('name', 'UNNAMED')}"
        if path else field.get('name', 'UNNAMED')
    )

    # Use dialect-specific required attributes
    required_attrs = dialect_config['required_attrs']
    for attr in required_attrs:
        if attr not in field:
            errors.append(
                f"Field {field_path}: Missing required attribute '{attr}'",
            )
        elif not field[attr]:
            errors.append(
                f"Field {field_path}: Attribute '{attr}' cannot be empty",
            )

    if 'name' in field:
        naming_error = validate_naming_convention(field['name'], case_style)
        if naming_error:
            if mode == 'fix':
                fixable_errors.append(f"Field {field_path}: {naming_error}")
            else:
                errors.append(f"Field {field_path}: {naming_error}")

    # Use dialect-specific type and mode validation
    if 'type' in field and field['type'] not in dialect_config['types']:
        errors.append(
            f"Field {field_path}: Invalid type '{field['type']}'. "
            f"Valid types: {', '.join(sorted(dialect_config['types']))}",
        )

    if 'mode' in field and field['mode'] not in dialect_config['modes']:
        errors.append(
            f"Field {field_path}: Invalid mode '{field['mode']}'. "
            f"Valid modes: {', '.join(sorted(dialect_config['modes']))}",
        )

    if field.get('type') == 'RECORD' and 'fields' in field:
        if not isinstance(field['fields'], list):
            errors.append(
                f"Field {field_path}: 'fields' must be a list for RECORD type",
            )
        else:
            for nested_field in field['fields']:
                nested_errors, nested_fixable = validate_field(
                    nested_field, dialect_config, case_style, field_path, mode,
                )
                errors.extend(nested_errors)
                fixable_errors.extend(nested_fixable)

    return (errors, fixable_errors)


def validate_schema(
        file_path: str,
        dialect: str,
        case_style: str,
        mode: str = 'lint',
) -> tuple[list[str], list[str], dict[str, Any] | None]:
    if dialect not in DIALECT_CONFIG:
        return (
            [
                f"Unsupported dialect '{dialect}'. "
                f"Available dialects: {', '.join(DIALECT_CONFIG.keys())}",
            ],
            [],
            None,
        )

    dialect_config = DIALECT_CONFIG[dialect]
    errors = []
    fixable_errors = []
    fixed_data = None

    try:
        with open(file_path, encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return ([f"Invalid JSON in {file_path}: {e}"], [], None)
    except Exception as e:
        return ([f"Error reading {file_path}: {e}"], [], None)

    if not isinstance(data, list):
        return ([f"{file_path}: Schema must be a list of field objects"], [], None)

    if not data:
        return ([f"{file_path}: Schema cannot be empty"], [], None)

    # For fix mode, create a copy of data to modify
    if mode == 'fix':
        fixed_data = json.loads(json.dumps(data))  # Deep copy

    for i, field in enumerate(data):
        if not isinstance(field, dict):
            errors.append(f"{file_path}: Field {i} must be an object")
            continue

        field_errors, field_fixable = validate_field(field, dialect_config, case_style, '', mode)
        errors.extend(
            [f"{file_path}: {error}" for error in field_errors],
        )
        fixable_errors.extend(
            [f"{file_path}: {error}" for error in field_fixable],
        )

        # Apply fixes if in fix mode
        if mode == 'fix' and fixed_data and 'name' in field:
            fixed_data[i] = apply_field_fixes(
                fixed_data[i], case_style,
            )

    return (errors, fixable_errors, fixed_data)


def discover_files(file_type: str, path_regex: str | None) -> list[str]:
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
        description=(
            'Validate schema files for compliance with specified dialect '
            'and conventions.'
        ),
    )
    parser.add_argument(
        '--file-type',
        default='json',
        help='File extension to validate (default: json)',
    )
    parser.add_argument(
        '--path-regex',
        help='Regex pattern to filter file paths',
    )
    parser.add_argument(
        '--dialect',
        default='bigquery',
        choices=['bigquery'],
        help='Schema dialect to validate against (default: bigquery)',
    )
    parser.add_argument(
        '--case',
        default='snake',
        choices=get_supported_case_styles(),
        help=(
            'Naming convention for field names. Supported: snake, camel, '
            'pascal, upper, kebab, train, flat, cobol, title (default: snake)'
        ),
    )
    parser.add_argument(
        '--mode',
        default='lint',
        choices=['lint', 'fix'],
        help=(
            'Operation mode: lint (check only) or fix (apply corrections) '
            '(default: lint)'
        ),
    )
    parser.add_argument(
        'files',
        nargs='*',
        help=(
            'Specific files to validate (if not provided, discovers files '
            'automatically)'
        ),
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

        validation_errors, fixable_errors, fixed_data = validate_schema(
            file_path, args.dialect, args.case, args.mode,
        )
        if args.mode == 'fix':
            # In fix mode, only show non-fixable errors
            all_errors.extend(validation_errors)
            # Show what was fixed
            if fixable_errors and fixed_data is not None:
                print(f"✓ Fixed {len(fixable_errors)} naming issue(s) in {file_path}")
                for error in fixable_errors:
                    print(f"  - {error.replace(file_path + ': ', '')}")
        else:
            # In lint mode, show all errors
            all_errors.extend(validation_errors)
            all_errors.extend(fixable_errors)

        # Apply fixes if in fix mode and fixes are available
        if args.mode == 'fix' and fixed_data is not None:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(
                        fixed_data, f, indent=2, ensure_ascii=False,
                    )
                print(f"✓ Applied fixes to {file_path}")
            except Exception as e:
                all_errors.append(f"Error writing fixes to {file_path}: {e}")

    if all_errors:
        print('\n'.join(all_errors))
        return 1

    if args.mode == 'fix':
        print(
            f"✓ All {len(candidate_files)} schema file(s) processed "
            f"successfully.",
        )
    else:
        print(
            f"✓ All {len(candidate_files)} schema file(s) passed validation.",
        )
    return 0


if __name__ == '__main__':
    sys.exit(main())
