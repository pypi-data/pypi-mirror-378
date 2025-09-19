"""Backend interfaces and implementations for different storage types."""

import sqlite3
import csv
import os
import pandas as pd
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class BackendInterface(ABC):
    """Abstract base class for storage backends."""
    
    @abstractmethod
    def create_table(self, table_name: str, schema: Dict[str, str]):
        """Create a table with the given schema."""
        pass
    
    @abstractmethod
    def insert_data(self, table_name: str, data: Dict[str, Any]):
        """Insert data into the table."""
        pass
    
    @abstractmethod
    def get_data(self, table_name: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get data from the table."""
        pass
    
    @abstractmethod
    def update_data(self, table_name: str, condition: Dict[str, Any], updates: Dict[str, Any]):
        """Update data in the table."""
        pass
    
    @abstractmethod
    def delete_data(self, table_name: str, condition: Dict[str, Any]):
        """Delete data from the table."""
        pass
    
    @abstractmethod
    def add_column(self, table_name: str, column_name: str, column_type: str):
        """Add a new column to the table."""
        pass


class SQLiteBackend(BackendInterface):
    """SQLite backend implementation."""
    
    def __init__(self, db_path: str):
        """Initialize SQLite backend.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.connection = sqlite3.connect(db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row  # Enable dict-like access
    
    def create_table(self, table_name: str, schema: Dict[str, str]):
        """Create a table with the given schema."""
        # Add an auto-incrementing ID column
        columns = ["id INTEGER PRIMARY KEY AUTOINCREMENT"]
        
        for column_name, column_type in schema.items():
            columns.append(f"{column_name} {column_type}")
        
        create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})"
        
        cursor = self.connection.cursor()
        cursor.execute(create_sql)
        self.connection.commit()
    
    def insert_data(self, table_name: str, data: Dict[str, Any]):
        """Insert data into the table."""
        columns = list(data.keys())
        placeholders = ', '.join(['?' for _ in columns])
        values = list(data.values())
        
        insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
        
        cursor = self.connection.cursor()
        cursor.execute(insert_sql, values)
        self.connection.commit()
    
    def get_data(self, table_name: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get data from the table."""
        select_sql = f"SELECT * FROM {table_name}"
        if limit:
            select_sql += f" LIMIT {limit}"
        
        cursor = self.connection.cursor()
        cursor.execute(select_sql)
        rows = cursor.fetchall()
        
        return [dict(row) for row in rows]
    
    def update_data(self, table_name: str, condition: Dict[str, Any], updates: Dict[str, Any]):
        """Update data in the table."""
        set_clause = ', '.join([f"{key} = ?" for key in updates.keys()])
        where_clause = ' AND '.join([f"{key} = ?" for key in condition.keys()])
        
        update_sql = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"
        values = list(updates.values()) + list(condition.values())
        
        cursor = self.connection.cursor()
        cursor.execute(update_sql, values)
        self.connection.commit()
    
    def delete_data(self, table_name: str, condition: Dict[str, Any]):
        """Delete data from the table."""
        where_clause = ' AND '.join([f"{key} = ?" for key in condition.keys()])
        delete_sql = f"DELETE FROM {table_name} WHERE {where_clause}"
        values = list(condition.values())
        
        cursor = self.connection.cursor()
        cursor.execute(delete_sql, values)
        self.connection.commit()
    
    def add_column(self, table_name: str, column_name: str, column_type: str):
        """Add a new column to the table."""
        alter_sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
        
        cursor = self.connection.cursor()
        try:
            cursor.execute(alter_sql)
            self.connection.commit()
        except sqlite3.OperationalError as e:
            if "duplicate column name" not in str(e).lower():
                raise
    
    def close(self):
        """Close the database connection."""
        self.connection.close()


class CSVBackend(BackendInterface):
    """CSV backend implementation."""
    
    def __init__(self, csv_path: str):
        """Initialize CSV backend.
        
        Args:
            csv_path: Path to the CSV file
        """
        self.csv_path = csv_path
        self.schema = {}
        self._ensure_directory()
    
    def _ensure_directory(self):
        """Ensure the directory for the CSV file exists."""
        os.makedirs(os.path.dirname(self.csv_path) if os.path.dirname(self.csv_path) else '.', exist_ok=True)
    
    def create_table(self, table_name: str, schema: Dict[str, str]):
        """Create a CSV file with the given schema."""
        self.schema = schema.copy()
        
        # Add ID column to schema
        self.schema = {'id': 'INTEGER', **self.schema}
        
        # Create CSV file with headers if it doesn't exist
        if not os.path.exists(self.csv_path):
            with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(list(self.schema.keys()))
    
    def insert_data(self, table_name: str, data: Dict[str, Any]):
        """Insert data into the CSV file."""
        # Get next ID
        next_id = self._get_next_id()
        data_with_id = {'id': next_id, **data}
        
        # Ensure all schema columns are present
        row_data = []
        for column in self.schema.keys():
            row_data.append(data_with_id.get(column, ''))
        
        # Append to CSV
        with open(self.csv_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(row_data)
    
    def get_data(self, table_name: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get data from the CSV file."""
        if not os.path.exists(self.csv_path):
            return []
        
        try:
            df = pd.read_csv(self.csv_path)
            if limit:
                df = df.head(limit)
            return df.to_dict('records')
        except (pd.errors.EmptyDataError, FileNotFoundError):
            return []
    
    def update_data(self, table_name: str, condition: Dict[str, Any], updates: Dict[str, Any]):
        """Update data in the CSV file."""
        if not os.path.exists(self.csv_path):
            return
        
        try:
            df = pd.read_csv(self.csv_path)
            
            # Create condition mask
            mask = pd.Series([True] * len(df))
            for key, value in condition.items():
                if key in df.columns:
                    mask &= (df[key] == value)
            
            # Apply updates
            for key, value in updates.items():
                if key in df.columns:
                    df.loc[mask, key] = value
            
            # Save back to CSV
            df.to_csv(self.csv_path, index=False)
            
        except (pd.errors.EmptyDataError, FileNotFoundError):
            pass
    
    def delete_data(self, table_name: str, condition: Dict[str, Any]):
        """Delete data from the CSV file."""
        if not os.path.exists(self.csv_path):
            return
        
        try:
            df = pd.read_csv(self.csv_path)
            
            # Create condition mask
            mask = pd.Series([True] * len(df))
            for key, value in condition.items():
                if key in df.columns:
                    mask &= (df[key] == value)
            
            # Remove rows matching condition
            df = df[~mask]
            
            # Save back to CSV
            df.to_csv(self.csv_path, index=False)
            
        except (pd.errors.EmptyDataError, FileNotFoundError):
            pass
    
    def add_column(self, table_name: str, column_name: str, column_type: str):
        """Add a new column to the CSV file."""
        if column_name not in self.schema:
            self.schema[column_name] = column_type
            
            if os.path.exists(self.csv_path):
                try:
                    df = pd.read_csv(self.csv_path)
                    if column_name not in df.columns:
                        df[column_name] = ''
                        df.to_csv(self.csv_path, index=False)
                except (pd.errors.EmptyDataError, FileNotFoundError):
                    pass
    
    def _get_next_id(self) -> int:
        """Get the next available ID."""
        if not os.path.exists(self.csv_path):
            return 1
        
        try:
            df = pd.read_csv(self.csv_path)
            if len(df) == 0 or 'id' not in df.columns:
                return 1
            return df['id'].max() + 1
        except (pd.errors.EmptyDataError, FileNotFoundError):
            return 1