#!/usr/bin/env python3

"""
Comprehensive naming convention utilities for schema field validation.
Supports 9 different naming conventions using case-converter library.
"""

import re
from typing import Optional

try:
    from caseconverter import (
        snakecase, camelcase, pascalcase, macrocase, kebabcase,
        flatcase, cobolcase, titlecase
    )
    HAS_CASE_CONVERTER = True
except ImportError:
    HAS_CASE_CONVERTER = False


# Fallback regex patterns if case-converter is not available
NAMING_PATTERNS = {
    'snake': re.compile(r'^[a-z]+(_[a-z0-9]+)*$'),
    'camel': re.compile(r'^[a-z][a-zA-Z0-9]*$'),
    'pascal': re.compile(r'^[A-Z][a-zA-Z0-9]*$'),
    'upper': re.compile(r'^[A-Z]+(_[A-Z0-9]+)*$'),
    'kebab': re.compile(r'^[a-z]+(-[a-z0-9]+)*$'),
    'train': re.compile(r'^[A-Z][a-z]*(-[A-Z][a-z0-9]*)*$'),
    'flat': re.compile(r'^[a-z0-9]+$'),
    'cobol': re.compile(r'^[A-Z]+(-[A-Z0-9]+)*$'),
    'title': re.compile(r'^[A-Z][a-z]*( [A-Z][a-z0-9]*)*$')
}

# Case style mappings
CASE_STYLES = {
    'snake': 'snake_case',
    'camel': 'camelCase', 
    'pascal': 'PascalCase',
    'upper': 'UPPER_CASE',
    'kebab': 'kebab-case',
    'train': 'Train-Case',
    'flat': 'flatcase',
    'cobol': 'COBOL-CASE',
    'title': 'Title Case'
}


def train_case(text: str) -> str:
    """Convert text to Train-Case (custom implementation)."""
    # Convert to kebab first, then capitalize each segment
    kebab_text = to_kebab_case(text)
    return '-'.join(word.capitalize() for word in kebab_text.split('-'))


def to_snake_case(text: str) -> str:
    """Convert text to snake_case."""
    if HAS_CASE_CONVERTER:
        return snakecase(text)
    # Fallback implementation
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
    return s2.lower().replace('-', '_').replace(' ', '_').replace('.', '_')


def to_camel_case(text: str) -> str:
    """Convert text to camelCase."""
    if HAS_CASE_CONVERTER:
        return camelcase(text)
    # Fallback implementation
    snake_text = to_snake_case(text)
    components = snake_text.split('_')
    return components[0].lower() + ''.join(word.capitalize() for word in components[1:])


def to_pascal_case(text: str) -> str:
    """Convert text to PascalCase."""
    if HAS_CASE_CONVERTER:
        return pascalcase(text)
    # Fallback implementation
    snake_text = to_snake_case(text)
    return ''.join(word.capitalize() for word in snake_text.split('_'))


def to_upper_case(text: str) -> str:
    """Convert text to UPPER_CASE."""
    if HAS_CASE_CONVERTER:
        return macrocase(text)
    return to_snake_case(text).upper()


def to_kebab_case(text: str) -> str:
    """Convert text to kebab-case."""
    if HAS_CASE_CONVERTER:
        return kebabcase(text)
    return to_snake_case(text).replace('_', '-')


def to_train_case(text: str) -> str:
    """Convert text to Train-Case."""
    return train_case(text)


def to_flat_case(text: str) -> str:
    """Convert text to flatcase."""
    if HAS_CASE_CONVERTER:
        return flatcase(text)
    return to_snake_case(text).replace('_', '')


def to_cobol_case(text: str) -> str:
    """Convert text to COBOL-CASE."""
    if HAS_CASE_CONVERTER:
        return cobolcase(text)
    return to_upper_case(text).replace('_', '-')


def to_title_case(text: str) -> str:
    """Convert text to Title Case."""
    if HAS_CASE_CONVERTER:
        return titlecase(text)
    # Fallback implementation
    snake_text = to_snake_case(text)
    return ' '.join(word.capitalize() for word in snake_text.split('_'))


# Validation functions
def is_snake_case(text: str) -> bool:
    """Check if text follows snake_case convention."""
    return bool(NAMING_PATTERNS['snake'].match(text))


def is_camel_case(text: str) -> bool:
    """Check if text follows camelCase convention."""
    return bool(NAMING_PATTERNS['camel'].match(text))


def is_pascal_case(text: str) -> bool:
    """Check if text follows PascalCase convention."""
    return bool(NAMING_PATTERNS['pascal'].match(text))


def is_upper_case(text: str) -> bool:
    """Check if text follows UPPER_CASE convention."""
    return bool(NAMING_PATTERNS['upper'].match(text))


def is_kebab_case(text: str) -> bool:
    """Check if text follows kebab-case convention."""
    return bool(NAMING_PATTERNS['kebab'].match(text))


def is_train_case(text: str) -> bool:
    """Check if text follows Train-Case convention."""
    return bool(NAMING_PATTERNS['train'].match(text))


def is_flat_case(text: str) -> bool:
    """Check if text follows flatcase convention."""
    return bool(NAMING_PATTERNS['flat'].match(text))


def is_cobol_case(text: str) -> bool:
    """Check if text follows COBOL-CASE convention."""
    return bool(NAMING_PATTERNS['cobol'].match(text))


def is_title_case(text: str) -> bool:
    """Check if text follows Title Case convention."""
    return bool(NAMING_PATTERNS['title'].match(text))


# Main validation and conversion functions
VALIDATION_FUNCTIONS = {
    'snake': is_snake_case,
    'camel': is_camel_case,
    'pascal': is_pascal_case,
    'upper': is_upper_case,
    'kebab': is_kebab_case,
    'train': is_train_case,
    'flat': is_flat_case,
    'cobol': is_cobol_case,
    'title': is_title_case
}

CONVERSION_FUNCTIONS = {
    'snake': to_snake_case,
    'camel': to_camel_case,
    'pascal': to_pascal_case,
    'upper': to_upper_case,
    'kebab': to_kebab_case,
    'train': to_train_case,
    'flat': to_flat_case,
    'cobol': to_cobol_case,
    'title': to_title_case
}


def validate_naming_convention(name: str, case_style: str) -> Optional[str]:
    """
    Validate if a field name follows the specified naming convention.
    
    Args:
        name: The field name to validate
        case_style: The naming convention to check against
        
    Returns:
        Error message if validation fails, None if validation passes
    """
    if case_style not in VALIDATION_FUNCTIONS:
        return f"Unsupported case style '{case_style}'. Supported: {', '.join(VALIDATION_FUNCTIONS.keys())}"
    
    validation_func = VALIDATION_FUNCTIONS[case_style]
    if not validation_func(name):
        expected = convert_naming_convention(name, case_style)
        case_name = CASE_STYLES[case_style]
        return f"Field name '{name}' does not follow {case_name}. Expected: {expected}"
    
    return None


def convert_naming_convention(name: str, case_style: str) -> str:
    """
    Convert a field name to the specified naming convention.
    
    Args:
        name: The field name to convert
        case_style: The target naming convention
        
    Returns:
        The converted field name
    """
    if case_style not in CONVERSION_FUNCTIONS:
        return name
    
    conversion_func = CONVERSION_FUNCTIONS[case_style]
    return conversion_func(name)


def get_supported_case_styles() -> list:
    """Get list of all supported case styles."""
    return list(CASE_STYLES.keys())


def get_case_style_examples() -> dict:
    """Get examples for each supported case style."""
    examples = {}
    sample_text = "customer_id"
    
    for style in CASE_STYLES.keys():
        converted = convert_naming_convention(sample_text, style)
        examples[style] = f"{CASE_STYLES[style]}: {converted}"
    
    return examples