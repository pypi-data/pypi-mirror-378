"""Utility functions for ArgLog."""

from typing import Any, Dict, Union, Optional


def infer_column_type(value: Any) -> str:
    """Infer SQL column type from a Python value.
    
    Args:
        value: Python value to infer type from
        
    Returns:
        SQL column type string
    """
    if value is None:
        return 'TEXT'
    elif isinstance(value, bool):
        return 'BOOLEAN'
    elif isinstance(value, int):
        return 'INTEGER'
    elif isinstance(value, float):
        return 'REAL'
    elif isinstance(value, (list, tuple)):
        # For lists/tuples, store as TEXT (could be JSON serialized)
        return 'TEXT'
    elif isinstance(value, dict):
        # For dicts, store as TEXT (could be JSON serialized)
        return 'TEXT'
    else:
        return 'TEXT'


def validate_data(data: Dict[str, Any], schema: Dict[str, str], partial: bool = False) -> Dict[str, Any]:
    """Validate and convert data according to schema.
    
    Args:
        data: Data dictionary to validate
        schema: Schema dictionary mapping column names to types
        partial: Whether to allow partial data (for updates)
        
    Returns:
        Validated and converted data dictionary
        
    Raises:
        ValueError: If data validation fails
    """
    validated = {}
    
    for column, value in data.items():
        if column not in schema:
            if not partial:
                # For new columns, infer the type and include them
                inferred_type = infer_column_type(value)
                expected_type = inferred_type
            else:
                # For partial updates, skip unknown columns
                continue
        else:
            # Get expected type from schema
            expected_type = schema[column]
        
        # Convert and validate
        try:
            converted_value = convert_value(value, expected_type)
            validated[column] = converted_value
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid value for column '{column}': {e}")
    
    return validated


def convert_value(value: Any, target_type: str) -> Any:
    """Convert a value to the target SQL type.
    
    Args:
        value: Value to convert
        target_type: Target SQL type
        
    Returns:
        Converted value
        
    Raises:
        ValueError: If conversion fails
    """
    if value is None:
        return None
    
    target_type = target_type.upper()
    
    if target_type == 'INTEGER':
        if isinstance(value, bool):
            return int(value)
        return int(value)
    elif target_type == 'REAL':
        return float(value)
    elif target_type == 'BOOLEAN':
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on')
        return bool(value)
    elif target_type == 'TEXT':
        if isinstance(value, (list, tuple, dict)):
            import json
            return json.dumps(value)
        return str(value)
    else:
        return str(value)  # Default to string


def format_schema_for_display(schema: Dict[str, str]) -> str:
    """Format schema dictionary for display.
    
    Args:
        schema: Schema dictionary
        
    Returns:
        Formatted string representation
    """
    if not schema:
        return "No schema defined"
    
    lines = ["Schema:"]
    for column, col_type in schema.items():
        lines.append(f"  {column}: {col_type}")
    
    return "\n".join(lines)


def sanitize_table_name(name: str) -> str:
    """Sanitize a string to be used as a table name.
    
    Args:
        name: Original name
        
    Returns:
        Sanitized name safe for use as table name
    """
    import re
    
    # Replace non-alphanumeric characters with underscores
    sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', name)
    
    # Ensure it starts with a letter or underscore
    if sanitized and not sanitized[0].isalpha() and sanitized[0] != '_':
        sanitized = '_' + sanitized
    
    # Ensure it's not empty
    if not sanitized:
        sanitized = 'experiment'
    
    return sanitized


def merge_configs(base_config: Dict[str, Any], user_config: Dict[str, Any]) -> Dict[str, Any]:
    """Merge user configuration with base configuration.
    
    Args:
        base_config: Base configuration dictionary
        user_config: User configuration dictionary
        
    Returns:
        Merged configuration dictionary
    """
    merged = base_config.copy()
    merged.update(user_config)
    return merged