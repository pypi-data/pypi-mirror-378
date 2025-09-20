"""
database utilities for fuero
provides database connectivity and orm-like functionality
"""

import sqlite3
import json
from typing import Dict, List, Any, Optional, Union, Tuple
from contextlib import contextmanager
import os


class DatabaseConnection:
    """database connection wrapper"""
    
    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()
    
    def execute(self, query: str, params: Optional[Tuple] = None) -> 'DatabaseCursor':
        """Execute SQL query"""
        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)
        return DatabaseCursor(self.cursor)
    
    def executemany(self, query: str, params_list: List[Tuple]) -> 'DatabaseCursor':
        """Execute SQL query with multiple parameter sets"""
        self.cursor.executemany(query, params_list)
        return DatabaseCursor(self.cursor)
    
    def commit(self):
        """Commit transaction"""
        self.connection.commit()
    
    def rollback(self):
        """Rollback transaction"""
        self.connection.rollback()
    
    def close(self):
        """Close connection"""
        self.connection.close()


class DatabaseCursor:
    """database cursor wrapper"""
    
    def __init__(self, cursor):
        self.cursor = cursor
    
    def fetchone(self) -> Optional[Tuple]:
        """Fetch one row"""
        return self.cursor.fetchone()
    
    def fetchall(self) -> List[Tuple]:
        """Fetch all rows"""
        return self.cursor.fetchall()
    
    def fetchmany(self, size: int) -> List[Tuple]:
        """Fetch specified number of rows"""
        return self.cursor.fetchmany(size)
    
    @property
    def rowcount(self) -> int:
        """Number of affected rows"""
        return self.cursor.rowcount
    
    @property
    def lastrowid(self) -> Optional[int]:
        """ID of last inserted row"""
        return self.cursor.lastrowid


class QueryBuilder:
    """sql query builder"""
    
    def __init__(self, table: str):
        self.table = table
        self.query_type = None
        self.select_fields = []
        self.where_conditions = []
        self.join_clauses = []
        self.order_by_fields = []
        self.group_by_fields = []
        self.having_conditions = []
        self.limit_value = None
        self.offset_value = None
        self.insert_data = {}
        self.update_data = {}
    
    def select(self, *fields) -> 'QueryBuilder':
        """Add SELECT fields"""
        self.query_type = 'SELECT'
        self.select_fields.extend(fields if fields else ['*'])
        return self
    
    def where(self, condition: str, *params) -> 'QueryBuilder':
        """Add WHERE condition"""
        self.where_conditions.append((condition, params))
        return self
    
    def join(self, table: str, condition: str, join_type: str = 'INNER') -> 'QueryBuilder':
        """Add JOIN clause"""
        self.join_clauses.append(f"{join_type} JOIN {table} ON {condition}")
        return self
    
    def order_by(self, field: str, direction: str = 'ASC') -> 'QueryBuilder':
        """Add ORDER BY clause"""
        self.order_by_fields.append(f"{field} {direction}")
        return self
    
    def group_by(self, *fields) -> 'QueryBuilder':
        """Add GROUP BY clause"""
        self.group_by_fields.extend(fields)
        return self
    
    def having(self, condition: str) -> 'QueryBuilder':
        """Add HAVING clause"""
        self.having_conditions.append(condition)
        return self
    
    def limit(self, count: int) -> 'QueryBuilder':
        """Add LIMIT clause"""
        self.limit_value = count
        return self
    
    def offset(self, count: int) -> 'QueryBuilder':
        """Add OFFSET clause"""
        self.offset_value = count
        return self
    
    def insert(self, data: Dict[str, Any]) -> 'QueryBuilder':
        """Set INSERT data"""
        self.query_type = 'INSERT'
        self.insert_data = data
        return self
    
    def update(self, data: Dict[str, Any]) -> 'QueryBuilder':
        """Set UPDATE data"""
        self.query_type = 'UPDATE'
        self.update_data = data
        return self
    
    def delete(self) -> 'QueryBuilder':
        """Set DELETE query"""
        self.query_type = 'DELETE'
        return self
    
    def build(self) -> Tuple[str, Tuple]:
        """Build SQL query and parameters"""
        if self.query_type == 'SELECT':
            return self._build_select()
        elif self.query_type == 'INSERT':
            return self._build_insert()
        elif self.query_type == 'UPDATE':
            return self._build_update()
        elif self.query_type == 'DELETE':
            return self._build_delete()
        else:
            raise ValueError("No query type specified")
    
    def _build_select(self) -> Tuple[str, Tuple]:
        """Build SELECT query"""
        fields = ', '.join(self.select_fields)
        query = f"SELECT {fields} FROM {self.table}"
        params = []
        
        # Add JOINs
        for join_clause in self.join_clauses:
            query += f" {join_clause}"
        
        # Add WHERE
        if self.where_conditions:
            where_parts = []
            for condition, condition_params in self.where_conditions:
                where_parts.append(condition)
                params.extend(condition_params)
            query += f" WHERE {' AND '.join(where_parts)}"
        
        # Add GROUP BY
        if self.group_by_fields:
            query += f" GROUP BY {', '.join(self.group_by_fields)}"
        
        # Add HAVING
        if self.having_conditions:
            query += f" HAVING {' AND '.join(self.having_conditions)}"
        
        # Add ORDER BY
        if self.order_by_fields:
            query += f" ORDER BY {', '.join(self.order_by_fields)}"
        
        # Add LIMIT and OFFSET
        if self.limit_value:
            query += f" LIMIT {self.limit_value}"
        if self.offset_value:
            query += f" OFFSET {self.offset_value}"
        
        return query, tuple(params)
    
    def _build_insert(self) -> Tuple[str, Tuple]:
        """Build INSERT query"""
        fields = ', '.join(self.insert_data.keys())
        placeholders = ', '.join(['?' for _ in self.insert_data])
        query = f"INSERT INTO {self.table} ({fields}) VALUES ({placeholders})"
        params = tuple(self.insert_data.values())
        return query, params
    
    def _build_update(self) -> Tuple[str, Tuple]:
        """Build UPDATE query"""
        set_parts = [f"{field} = ?" for field in self.update_data.keys()]
        query = f"UPDATE {self.table} SET {', '.join(set_parts)}"
        params = list(self.update_data.values())
        
        # Add WHERE
        if self.where_conditions:
            where_parts = []
            for condition, condition_params in self.where_conditions:
                where_parts.append(condition)
                params.extend(condition_params)
            query += f" WHERE {' AND '.join(where_parts)}"
        
        return query, tuple(params)
    
    def _build_delete(self) -> Tuple[str, Tuple]:
        """Build DELETE query"""
        query = f"DELETE FROM {self.table}"
        params = []
        
        # Add WHERE
        if self.where_conditions:
            where_parts = []
            for condition, condition_params in self.where_conditions:
                where_parts.append(condition)
                params.extend(condition_params)
            query += f" WHERE {' AND '.join(where_parts)}"
        
        return query, tuple(params)


class Database:
    """database utilities and orm-like functionality"""
    
    def __init__(self):
        self.connections = {}
    
    # Connection management
    def connect_sqlite(self, database_path: str, connection_name: str = 'default') -> DatabaseConnection:
        """Connect to SQLite database"""
        try:
            conn = sqlite3.connect(database_path)
            conn.row_factory = sqlite3.Row  # Enable dict-like access
            db_conn = DatabaseConnection(conn)
            self.connections[connection_name] = db_conn
            return db_conn
        except sqlite3.Error as e:
            raise ConnectionError(f"Failed to connect to SQLite database: {e}")
    
    def get_connection(self, connection_name: str = 'default') -> DatabaseConnection:
        """Get existing connection"""
        if connection_name not in self.connections:
            raise ValueError(f"Connection '{connection_name}' not found")
        return self.connections[connection_name]
    
    def close_connection(self, connection_name: str = 'default'):
        """Close database connection"""
        if connection_name in self.connections:
            self.connections[connection_name].close()
            del self.connections[connection_name]
    
    def close_all_connections(self):
        """Close all database connections"""
        for conn in self.connections.values():
            conn.close()
        self.connections.clear()
    
    @contextmanager
    def transaction(self, connection_name: str = 'default'):
        """Context manager for database transactions"""
        conn = self.get_connection(connection_name)
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
    
    # Query execution
    def execute(self, query: str, params: Optional[Tuple] = None, 
                connection_name: str = 'default') -> DatabaseCursor:
        """Execute SQL query"""
        conn = self.get_connection(connection_name)
        return conn.execute(query, params)
    
    def execute_many(self, query: str, params_list: List[Tuple], 
                     connection_name: str = 'default') -> DatabaseCursor:
        """Execute SQL query with multiple parameter sets"""
        conn = self.get_connection(connection_name)
        return conn.executemany(query, params_list)
    
    def fetch_one(self, query: str, params: Optional[Tuple] = None, 
                  connection_name: str = 'default') -> Optional[Dict]:
        """Execute query and fetch one row as dictionary"""
        cursor = self.execute(query, params, connection_name)
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def fetch_all(self, query: str, params: Optional[Tuple] = None, 
                  connection_name: str = 'default') -> List[Dict]:
        """Execute query and fetch all rows as list of dictionaries"""
        cursor = self.execute(query, params, connection_name)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def fetch_many(self, query: str, size: int, params: Optional[Tuple] = None, 
                   connection_name: str = 'default') -> List[Dict]:
        """Execute query and fetch specified number of rows"""
        cursor = self.execute(query, params, connection_name)
        rows = cursor.fetchmany(size)
        return [dict(row) for row in rows]
    
    # Query builder
    def query(self, table: str) -> QueryBuilder:
        """Create query builder for table"""
        return QueryBuilder(table)
    
    def execute_builder(self, builder: QueryBuilder, connection_name: str = 'default') -> DatabaseCursor:
        """Execute query builder"""
        query, params = builder.build()
        return self.execute(query, params, connection_name)
    
    # Table operations
    def create_table(self, table_name: str, columns: Dict[str, str], 
                     connection_name: str = 'default') -> bool:
        """Create table with specified columns"""
        column_defs = []
        for col_name, col_type in columns.items():
            column_defs.append(f"{col_name} {col_type}")
        
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(column_defs)})"
        
        try:
            self.execute(query, connection_name=connection_name)
            self.get_connection(connection_name).commit()
            return True
        except Exception:
            return False
    
    def drop_table(self, table_name: str, connection_name: str = 'default') -> bool:
        """Drop table"""
        try:
            self.execute(f"DROP TABLE IF EXISTS {table_name}", connection_name=connection_name)
            self.get_connection(connection_name).commit()
            return True
        except Exception:
            return False
    
    def table_exists(self, table_name: str, connection_name: str = 'default') -> bool:
        """Check if table exists"""
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
        result = self.fetch_one(query, (table_name,), connection_name)
        return result is not None
    
    def get_table_info(self, table_name: str, connection_name: str = 'default') -> List[Dict]:
        """Get table column information"""
        query = f"PRAGMA table_info({table_name})"
        return self.fetch_all(query, connection_name=connection_name)
    
    def get_table_names(self, connection_name: str = 'default') -> List[str]:
        """Get list of all table names"""
        query = "SELECT name FROM sqlite_master WHERE type='table'"
        results = self.fetch_all(query, connection_name=connection_name)
        return [row['name'] for row in results]
    
    # CRUD operations
    def insert(self, table: str, data: Dict[str, Any], 
               connection_name: str = 'default') -> Optional[int]:
        """Insert record and return last row ID"""
        builder = self.query(table).insert(data)
        cursor = self.execute_builder(builder, connection_name)
        self.get_connection(connection_name).commit()
        return cursor.lastrowid
    
    def insert_many(self, table: str, data_list: List[Dict[str, Any]], 
                    connection_name: str = 'default') -> int:
        """Insert multiple records"""
        if not data_list:
            return 0
        
        # All records should have the same keys
        fields = list(data_list[0].keys())
        placeholders = ', '.join(['?' for _ in fields])
        query = f"INSERT INTO {table} ({', '.join(fields)}) VALUES ({placeholders})"
        
        params_list = [tuple(record[field] for field in fields) for record in data_list]
        cursor = self.execute_many(query, params_list, connection_name)
        self.get_connection(connection_name).commit()
        return cursor.rowcount
    
    def update(self, table: str, data: Dict[str, Any], where: str, 
               where_params: Tuple = (), connection_name: str = 'default') -> int:
        """Update records"""
        builder = self.query(table).update(data).where(where, *where_params)
        cursor = self.execute_builder(builder, connection_name)
        self.get_connection(connection_name).commit()
        return cursor.rowcount
    
    def delete(self, table: str, where: str, where_params: Tuple = (), 
               connection_name: str = 'default') -> int:
        """Delete records"""
        builder = self.query(table).delete().where(where, *where_params)
        cursor = self.execute_builder(builder, connection_name)
        self.get_connection(connection_name).commit()
        return cursor.rowcount
    
    def select(self, table: str, fields: List[str] = None, where: str = None, 
               where_params: Tuple = (), order_by: str = None, limit: int = None,
               connection_name: str = 'default') -> List[Dict]:
        """Select records"""
        builder = self.query(table).select(*(fields or ['*']))
        
        if where:
            builder.where(where, *where_params)
        if order_by:
            builder.order_by(order_by)
        if limit:
            builder.limit(limit)
        
        cursor = self.execute_builder(builder, connection_name)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    # Utility functions
    def count(self, table: str, where: str = None, where_params: Tuple = (), 
              connection_name: str = 'default') -> int:
        """Count records in table"""
        builder = self.query(table).select('COUNT(*)')
        if where:
            builder.where(where, *where_params)
        
        cursor = self.execute_builder(builder, connection_name)
        result = cursor.fetchone()
        return result[0] if result else 0
    
    def exists(self, table: str, where: str, where_params: Tuple = (), 
               connection_name: str = 'default') -> bool:
        """Check if record exists"""
        return self.count(table, where, where_params, connection_name) > 0
    
    def get_last_insert_id(self, connection_name: str = 'default') -> Optional[int]:
        """Get last insert row ID"""
        result = self.fetch_one("SELECT last_insert_rowid()", connection_name=connection_name)
        return result['last_insert_rowid()'] if result else None
    
    # Backup and restore
    def backup_database(self, backup_path: str, connection_name: str = 'default') -> bool:
        """Backup database to file"""
        try:
            conn = self.get_connection(connection_name).connection
            with open(backup_path, 'w') as f:
                for line in conn.iterdump():
                    f.write('%s\n' % line)
            return True
        except Exception:
            return False
    
    def restore_database(self, backup_path: str, connection_name: str = 'default') -> bool:
        """Restore database from backup file"""
        try:
            if not os.path.exists(backup_path):
                return False
            
            conn = self.get_connection(connection_name).connection
            with open(backup_path, 'r') as f:
                sql_script = f.read()
            
            conn.executescript(sql_script)
            conn.commit()
            return True
        except Exception:
            return False
    
    # JSON support
    def insert_json(self, table: str, json_data: str, connection_name: str = 'default') -> Optional[int]:
        """Insert JSON data"""
        try:
            data = json.loads(json_data)
            return self.insert(table, data, connection_name)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON data")
    
    def select_as_json(self, table: str, where: str = None, where_params: Tuple = (), 
                       connection_name: str = 'default') -> str:
        """Select records and return as JSON"""
        records = self.select(table, where=where, where_params=where_params, 
                            connection_name=connection_name)
        return json.dumps(records, default=str)
