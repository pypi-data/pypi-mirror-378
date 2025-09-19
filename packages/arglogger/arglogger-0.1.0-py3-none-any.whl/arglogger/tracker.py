"""Main ArgLogger class for logging experiment results."""

import argparse
import datetime
from typing import Dict, Any, Optional, Union
from .backends import BackendInterface, SQLiteBackend, CSVBackend
from .utils import infer_column_type, validate_data


class ArgLogger:
    """Main class for logging experiment results.
    
    This class automatically creates database tables or CSV files based on
    argparse configurations and provides methods to save experiment results.
    """
    
    def __init__(
        self,
        experiment_name: str,
        backend: str = 'sqlite',
        storage_path: Optional[str] = None,
        parser: Optional[argparse.ArgumentParser] = None,
        args: Optional[argparse.Namespace] = None,
        auto_timestamp: bool = True
    ):
        """Initialize the ArgLogger.
        
        Args:
            experiment_name: Name of the experiment (used as table/file name)
            backend: Storage backend ('sqlite' or 'csv')
            storage_path: Path to store the data (defaults to experiment_name)
            parser: ArgumentParser instance to extract schema from
            args: Parsed arguments to extract schema from
            auto_timestamp: Whether to automatically add timestamp columns
        """
        self.experiment_name = experiment_name
        self.auto_timestamp = auto_timestamp
        self.base_args = args  # 保存原始args用于自动填充
        
        # Initialize storage backend
        if backend.lower() == 'sqlite':
            db_path = storage_path or f"{experiment_name}.db"
            self.backend = SQLiteBackend(db_path)
        elif backend.lower() == 'csv':
            csv_path = storage_path or f"{experiment_name}.csv"
            self.backend = CSVBackend(csv_path)
        else:
            raise ValueError(f"Unsupported backend: {backend}")
        
        # Initialize schema from argparse
        self.schema = {}
        if parser is not None:
            self._extract_schema_from_parser(parser)
        elif args is not None:
            self._extract_schema_from_args(args)
        
        # Add timestamp columns if enabled
        if self.auto_timestamp:
            self.schema['created_at'] = 'TEXT'
            self.schema['updated_at'] = 'TEXT'
        
        # Initialize the table/file
        if self.schema:
            self.backend.create_table(experiment_name, self.schema)
    
    def _extract_schema_from_parser(self, parser: argparse.ArgumentParser):
        """Extract schema from ArgumentParser instance."""
        for action in parser._actions:
            if action.dest == 'help':
                continue
            
            # Get the argument name
            arg_name = action.dest
            
            # Infer the column type based on action type and default value
            column_type = self._infer_type_from_action(action)
            self.schema[arg_name] = column_type
    
    def _extract_schema_from_args(self, args: argparse.Namespace):
        """Extract schema from parsed arguments."""
        for key, value in vars(args).items():
            column_type = infer_column_type(value)
            self.schema[key] = column_type
    
    def _infer_type_from_action(self, action: argparse.Action) -> str:
        """Infer SQL column type from argparse action."""
        # Handle different action types
        if action.type == int:
            return 'INTEGER'
        elif action.type == float:
            return 'REAL'
        elif action.type == bool or isinstance(action, argparse.BooleanOptionalAction):
            return 'BOOLEAN'
        elif hasattr(action, 'choices') and action.choices:
            # For choices, infer from the first choice
            return infer_column_type(list(action.choices)[0])
        elif action.default is not None:
            return infer_column_type(action.default)
        else:
            return 'TEXT'  # Default to TEXT
    
    def add_column(self, column_name: str, column_type: str = 'TEXT'):
        """Add a new column to the schema and storage.
        
        Args:
            column_name: Name of the column to add
            column_type: SQL type of the column (TEXT, INTEGER, REAL, BOOLEAN)
        """
        if column_name not in self.schema:
            self.schema[column_name] = column_type
            self.backend.add_column(self.experiment_name, column_name, column_type)
    
    def log_result(self, results: Dict[str, Any], **kwargs):
        """Log experiment results.
        
        Args:
            results: Dictionary of results to log
            **kwargs: Additional results as keyword arguments
        """
        # Start with base args if available
        data = {}
        if self.base_args is not None:
            data.update(vars(self.base_args))
        
        # Combine with results and kwargs (these override base args)
        data.update(results)
        data.update(kwargs)
        
        # Add timestamps if enabled
        if self.auto_timestamp:
            current_time = datetime.datetime.now().isoformat()
            data['created_at'] = current_time
            data['updated_at'] = current_time
        
        # Check for new columns and add them to schema
        for column, value in data.items():
            if column not in self.schema:
                column_type = infer_column_type(value)
                self.add_column(column, column_type)
        
        # Validate data against schema
        validated_data = validate_data(data, self.schema)
        
        # Insert data
        self.backend.insert_data(self.experiment_name, validated_data)
    
    def get_results(self, limit: Optional[int] = None) -> list:
        """Get experiment results.
        
        Args:
            limit: Maximum number of results to return
            
        Returns:
            List of result dictionaries
        """
        return self.backend.get_data(self.experiment_name, limit=limit)
    
    def update_result(self, condition: Dict[str, Any], updates: Dict[str, Any]):
        """Update existing results.
        
        Args:
            condition: Condition to match results (e.g., {'id': 1})
            updates: Updates to apply
        """
        if self.auto_timestamp:
            updates['updated_at'] = datetime.datetime.now().isoformat()
        
        validated_updates = validate_data(updates, self.schema, partial=True)
        self.backend.update_data(self.experiment_name, condition, validated_updates)
    
    def delete_results(self, condition: Dict[str, Any]):
        """Delete results matching condition.
        
        Args:
            condition: Condition to match results for deletion
        """
        self.backend.delete_data(self.experiment_name, condition)
    
    def get_schema(self) -> Dict[str, str]:
        """Get the current schema.
        
        Returns:
            Dictionary mapping column names to types
        """
        return self.schema.copy()
    
    def close(self):
        """Close the backend connection."""
        if hasattr(self.backend, 'close'):
            self.backend.close()