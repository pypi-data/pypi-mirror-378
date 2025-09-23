"""
Database handlers for PostgreSQL and SQLite with unified interface.

This module provides handlers for both PostgreSQL and SQLite databases
with a common base class for consistent usage patterns.

Required dependencies:
    - For PostgreSQL: pip install qufe[database]
    - For SQLite: No additional dependencies (uses standard library)
"""

import os
import sqlite3
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Optional, Any, Union
from contextlib import contextmanager


def help():
    """
    Display help information for database handler functionality.

    Shows usage examples and available handlers.
    """
    print("qufe.dbhandler - Database Handlers")
    print("=" * 40)
    print()
    print("AVAILABLE HANDLERS:")
    print("  • PostgreSQLHandler - For PostgreSQL databases")
    print("  • SQLiteHandler - For SQLite3 databases")
    print()

    # Check PostgreSQL dependencies
    try:
        _import_sqlalchemy()
        print("PostgreSQL: ✓ Dependencies installed")
    except ImportError:
        print("PostgreSQL: ✗ Missing dependencies")
        print("  Install with: pip install qufe[database]")

    print("SQLite3: ✓ Ready (standard library)")
    print()

    print("QUICK EXAMPLES:")
    print()
    print("# SQLite - Quick data peek")
    print("from qufe.dbhandler import SQLiteHandler")
    print("SQLiteHandler.quick_peek('data.db')")
    print("df = SQLiteHandler.to_dataframe('data.db', 'table_name')")
    print()
    print("# PostgreSQL - Environment-based connection")
    print("from qufe.dbhandler import PostgreSQLHandler")
    print("db = PostgreSQLHandler()  # Uses .env or environment vars")
    print("results = db.execute_query('SELECT * FROM users LIMIT 5')")


# =====================================================================
# Lazy imports for optional dependencies
# =====================================================================

def _import_sqlalchemy():
    """Lazy import SQLAlchemy with helpful error message."""
    try:
        from sqlalchemy import create_engine, text
        from sqlalchemy.engine import Engine
        return create_engine, text, Engine
    except ImportError as e:
        raise ImportError(
            "PostgreSQL functionality requires SQLAlchemy. "
            "Install with: pip install qufe[database]"
        ) from e


def _import_dotenv():
    """Lazy import python-dotenv with graceful fallback."""
    try:
        from dotenv import load_dotenv
        return load_dotenv
    except ImportError:
        return None


def _import_pandas():
    """Lazy import pandas with graceful fallback."""
    try:
        import pandas as pd
        return pd
    except ImportError:
        return None


# =====================================================================
# Base Handler Class
# =====================================================================

class BaseDBHandler(ABC):
    """
    Abstract base class for database handlers.

    Provides common interface and shared functionality for different
    database implementations.
    """

    def __init__(self):
        """Initialize base handler."""
        self.connection = None

    @abstractmethod
    def connect(self) -> None:
        """Establish database connection."""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Close database connection."""
        pass

    @abstractmethod
    def execute_query(self, query: str, params: Optional[tuple] = None) -> List:
        """
        Execute a query and return results.

        Args:
            query: SQL query string
            params: Query parameters for safe execution

        Returns:
            List of query results
        """
        pass

    def execute_many(self, query: str, params_list: List[tuple]) -> None:
        """
        Execute same query multiple times with different parameters.

        Args:
            query: SQL query string with placeholders
            params_list: List of parameter tuples
        """
        # Default implementation - subclasses can override for optimization
        for params in params_list:
            self.execute_query(query, params)

    def table_exists(self, table_name: str) -> bool:
        """
        Check if a table exists in the database.

        Args:
            table_name: Name of the table to check

        Returns:
            True if table exists, False otherwise
        """
        # Default implementation using ANSI SQL
        query = """
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_name = ? \
                """
        result = self.execute_query(query, (table_name,))
        return bool(result and result[0][0] > 0)

    @contextmanager
    def transaction(self):
        """
        Context manager for database transactions.

        Automatically commits on success, rolls back on error.
        """
        try:
            yield self
            if hasattr(self.connection, 'commit'):
                self.connection.commit()
        except Exception as e:
            if hasattr(self.connection, 'rollback'):
                self.connection.rollback()
            raise e

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()


# =====================================================================
# PostgreSQL Handler
# =====================================================================

class PostgreSQLHandler(BaseDBHandler):
    """
    PostgreSQL connection handler with automatic environment variable support.

    Extends BaseDBHandler for PostgreSQL-specific functionality.
    """

    def __init__(
            self,
            db_name: Optional[str] = None,
            user: Optional[str] = None,
            password: Optional[str] = None,
            host: Optional[str] = None,
            port: Optional[int] = None):
        """
        Initialize PostgreSQL connection handler.

        Args:
            db_name: Database name (defaults to POSTGRES_DB env var)
            user: Username (defaults to POSTGRES_USER env var)
            password: Password (defaults to POSTGRES_PASSWORD env var)
            host: Host address (defaults to POSTGRES_HOST or 'localhost')
            port: Port number (defaults to POSTGRES_PORT or 5432)
        """
        super().__init__()

        # Import required dependencies
        self._create_engine, self._text, self._Engine = _import_sqlalchemy()

        # Try to load .env file if available
        load_dotenv = _import_dotenv()
        if load_dotenv:
            load_dotenv()

        # Set connection parameters
        self.user = user or os.getenv('POSTGRES_USER')
        self.password = password or os.getenv('POSTGRES_PASSWORD')
        self.host = host or os.getenv('POSTGRES_HOST', 'localhost')
        self.port = port or int(os.getenv('POSTGRES_PORT', '5432'))
        self.database = db_name or os.getenv('POSTGRES_DB', 'postgres')

        if not self.user or not self.password:
            raise ValueError(
                "Database credentials required. Set POSTGRES_USER and "
                "POSTGRES_PASSWORD in .env file or as parameters."
            )

        self.engine = None
        self.connect()

    def connect(self) -> None:
        """Establish PostgreSQL connection."""
        url = f"postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
        self.engine = self._create_engine(url, echo=False, future=True)
        self.connection = self.engine

    def disconnect(self) -> None:
        """Close PostgreSQL connection."""
        if self.engine:
            self.engine.dispose()
            self.engine = None
            self.connection = None

    def execute_query(self, query: str, params: Optional[tuple] = None) -> List:
        """
        Execute a SQL query and return results.

        Args:
            query: SQL query string
            params: Query parameters (not used in current implementation)

        Returns:
            List of query results
        """
        with self.engine.connect() as conn:
            return conn.execute(self._text(query)).fetchall()

    def get_database_list(self, print_result: bool = False) -> List[str]:
        """
        Get list of all databases in the PostgreSQL server.

        Args:
            print_result: Whether to print the database list

        Returns:
            List of database names
        """
        query = """
                SELECT datname
                FROM pg_database
                WHERE datistemplate = false; \
                """
        result = self.execute_query(query)
        database_names = [row.datname for row in result]

        if print_result:
            print("Available databases:")
            for db_name in database_names:
                print(f"  - {db_name}")

        return database_names

    def get_table_list(self, print_result: bool = True) -> List[Dict[str, str]]:
        """
        Get list of all tables and views in the current database.

        Args:
            print_result: Whether to print the table list

        Returns:
            List of dictionaries containing table information
        """
        query = """
                SELECT table_catalog, table_schema, table_name, table_type
                FROM information_schema.tables
                ORDER BY table_schema, table_name; \
                """
        result = self.execute_query(query)

        tables = [
            {
                'catalog': row.table_catalog,
                'schema': row.table_schema,
                'name': row.table_name,
                'type': row.table_type
            } for row in result
        ]

        if print_result:
            public_tables = [
                t['name'] for t in tables
                if t.get('schema') == 'public'
            ]
            if public_tables:
                print(f"\nDatabase: {self.database}")
                print(f"Public tables: {public_tables}")

        return tables


# =====================================================================
# SQLite Handler
# =====================================================================

class SQLiteHandler(BaseDBHandler):
    """
    SQLite database handler for local file-based databases.

    Provides convenient methods for common SQLite operations in
    Jupyter notebook environments.
    """

    def __init__(self, db_path: Union[str, Path], create_dir: bool = False):
        """
        Initialize SQLite handler.

        Args:
            db_path: Path to SQLite database file
            create_dir: Whether to create parent directory if missing
        """
        super().__init__()
        self.db_path = Path(db_path)

        if create_dir and not self.db_path.parent.exists():
            self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.connect()

    def connect(self) -> None:
        """Establish SQLite connection."""
        self.connection = sqlite3.connect(str(self.db_path))
        self.connection.row_factory = sqlite3.Row  # Enable column access by name

    def disconnect(self) -> None:
        """Close SQLite connection."""
        if self.connection:
            self.connection.close()
            self.connection = None

    def execute_query(self, query: str, params: Optional[tuple] = None) -> List:
        """
        Execute a SQL query and return results.

        Args:
            query: SQL query string
            params: Query parameters for safe execution

        Returns:
            List of query results
        """
        cursor = self.connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        # For SELECT queries, fetch results
        if query.strip().upper().startswith('SELECT'):
            return cursor.fetchall()
        else:
            # For INSERT/UPDATE/DELETE, commit and return empty list
            self.connection.commit()
            return []

    def get_tables(self) -> List[str]:
        """
        Get list of all tables in the database.

        Returns:
            List of table names
        """
        query = "SELECT name FROM sqlite_master WHERE type='table'"
        results = self.execute_query(query)
        return [row['name'] for row in results]

    def get_table_info(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Get column information for a table with multiple fallback methods.

        Tries multiple approaches in order:
        1. PRAGMA table_info (standard SQLite metadata)
        2. Parse CREATE TABLE statement from sqlite_master
        3. Infer from sample data using cursor.description

        Args:
            table_name: Name of the table

        Returns:
            List of column information dictionaries with keys:
            - cid: Column ID (position)
            - name: Column name
            - type: Data type (may be 'UNKNOWN' if inferred)
            - notnull: Whether NOT NULL constraint exists (0 or 1)
            - dflt_value: Default value
            - pk: Whether primary key (0 or 1)
        """
        # Method 1: Try PRAGMA table_info (standard approach)
        try:
            query = f"PRAGMA table_info({table_name})"
            results = self.execute_query(query)
            if results:
                return [dict(row) for row in results]
        except Exception:
            # PRAGMA might not be available in some environments
            pass

        # Method 2: Parse CREATE TABLE statement
        try:
            schema_info = self._get_schema_from_master(table_name)
            if schema_info:
                return schema_info
        except Exception:
            pass

        # Method 3: Infer from sample data
        try:
            sample_info = self._infer_from_sample(table_name)
            if sample_info:
                return sample_info
        except Exception:
            pass

        # If all methods fail, return minimal info if table exists
        if self.table_exists(table_name):
            return [{
                'cid': 0,
                'name': 'unknown',
                'type': 'UNKNOWN',
                'notnull': 0,
                'dflt_value': None,
                'pk': 0
            }]

        return []

    def _get_schema_from_master(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Extract column information from sqlite_master CREATE TABLE statement.

        Args:
            table_name: Name of the table

        Returns:
            List of column information or empty list
        """
        query = """
                SELECT sql \
                FROM sqlite_master
                WHERE type ='table' AND name =? \
                """
        results = self.execute_query(query, (table_name,))

        if not results or not results[0]['sql']:
            return []

        create_sql = results[0]['sql']

        # Basic parsing of CREATE TABLE statement
        # This is a simplified parser - production code might need more robust parsing
        columns = []

        # Extract content between parentheses
        import re
        match = re.search(r'\((.*)\)', create_sql, re.DOTALL)
        if not match:
            return []

        column_defs = match.group(1)
        # Split by comma but not within parentheses (for complex constraints)
        parts = re.split(r',(?![^()]*\))', column_defs)

        for idx, part in enumerate(parts):
            part = part.strip()
            if not part:
                continue

            # Skip constraint definitions (PRIMARY KEY, FOREIGN KEY, etc.)
            if part.upper().startswith(('PRIMARY KEY', 'FOREIGN KEY', 'UNIQUE', 'CHECK', 'CONSTRAINT')):
                continue

            # Extract column name and type
            tokens = part.split()
            if len(tokens) >= 2:
                col_name = tokens[0].strip('`"[]')
                col_type = tokens[1].upper() if len(tokens) > 1 else 'TEXT'

                # Check for constraints
                part_upper = part.upper()
                is_pk = 'PRIMARY KEY' in part_upper
                is_notnull = 'NOT NULL' in part_upper

                # Extract default value if present
                default_match = re.search(r'DEFAULT\s+([^\s,]+)', part, re.IGNORECASE)
                default_val = default_match.group(1) if default_match else None

                columns.append({
                    'cid': idx,
                    'name': col_name,
                    'type': col_type,
                    'notnull': 1 if is_notnull else 0,
                    'dflt_value': default_val,
                    'pk': 1 if is_pk else 0
                })

        return columns

    def _infer_from_sample(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Infer column information from sample data.

        Uses cursor.description after executing a SELECT query.
        Note: Data types and constraints cannot be accurately determined this way.

        Args:
            table_name: Name of the table

        Returns:
            List of column information with limited accuracy
        """
        # Use LIMIT 0 to get column info without fetching data
        query = f"SELECT * FROM {table_name} LIMIT 0"
        cursor = self.connection.cursor()
        cursor.execute(query)

        if not cursor.description:
            return []

        columns = []
        for idx, col_desc in enumerate(cursor.description):
            # cursor.description is a tuple: (name, type_code, display_size, internal_size, precision, scale, null_ok)
            # For SQLite, most of these are None except name
            columns.append({
                'cid': idx,
                'name': col_desc[0],
                'type': 'UNKNOWN',  # Cannot reliably determine from cursor
                'notnull': 0,  # Cannot determine from cursor
                'dflt_value': None,  # Cannot determine from cursor
                'pk': 0  # Cannot determine from cursor
            })

        # Try to enhance with actual data type inference if table has data
        try:
            sample_query = f"SELECT * FROM {table_name} LIMIT 1"
            sample_results = self.execute_query(sample_query)

            if sample_results and len(sample_results) > 0:
                sample_row = dict(sample_results[0])

                for col in columns:
                    col_name = col['name']
                    if col_name in sample_row:
                        value = sample_row[col_name]
                        # Basic type inference from sample value
                        if value is None:
                            pass  # Keep UNKNOWN
                        elif isinstance(value, int):
                            col['type'] = 'INTEGER'
                        elif isinstance(value, float):
                            col['type'] = 'REAL'
                        elif isinstance(value, bytes):
                            col['type'] = 'BLOB'
                        elif isinstance(value, str):
                            col['type'] = 'TEXT'
        except Exception:
            # If sampling fails, return basic column info
            pass

        return columns

    def get_table_schema(self, table_name: str, verbose: bool = False) -> Dict[str, Any]:
        """
        Get comprehensive table schema information.

        Provides detailed information about table structure including
        the method used to obtain the information.

        Args:
            table_name: Name of the table
            verbose: Whether to include additional diagnostic info

        Returns:
            Dictionary containing:
            - columns: List of column information
            - method: Method used to obtain info ('pragma', 'schema', 'inferred')
            - accuracy: Confidence level ('high', 'medium', 'low')
            - warnings: List of any warnings
        """
        result = {
            'columns': [],
            'method': None,
            'accuracy': None,
            'warnings': []
        }

        # Try PRAGMA first (most accurate)
        try:
            query = f"PRAGMA table_info({table_name})"
            pragma_results = self.execute_query(query)
            if pragma_results:
                result['columns'] = [dict(row) for row in pragma_results]
                result['method'] = 'pragma'
                result['accuracy'] = 'high'
                if verbose:
                    print(f"✓ Retrieved schema via PRAGMA for table '{table_name}'")
                return result
        except Exception as e:
            if verbose:
                print(f"✗ PRAGMA failed: {e}")
            result['warnings'].append("PRAGMA table_info not available")

        # Try parsing CREATE TABLE
        try:
            schema_info = self._get_schema_from_master(table_name)
            if schema_info:
                result['columns'] = schema_info
                result['method'] = 'schema'
                result['accuracy'] = 'medium'
                result['warnings'].append("Schema parsed from CREATE TABLE statement")
                if verbose:
                    print(f"✓ Retrieved schema via sqlite_master for table '{table_name}'")
                return result
        except Exception as e:
            if verbose:
                print(f"✗ Schema parsing failed: {e}")

        # Fall back to inference
        try:
            sample_info = self._infer_from_sample(table_name)
            if sample_info:
                result['columns'] = sample_info
                result['method'] = 'inferred'
                result['accuracy'] = 'low'
                result['warnings'].append("Column types inferred from data - constraints unknown")
                if verbose:
                    print(f"⚠ Schema inferred from sample data for table '{table_name}'")
                return result
        except Exception as e:
            if verbose:
                print(f"✗ Sample inference failed: {e}")

        # Table might not exist or is inaccessible
        if not self.table_exists(table_name):
            result['warnings'].append(f"Table '{table_name}' does not exist")
        else:
            result['warnings'].append("Unable to retrieve schema information")

        return result

    def table_exists(self, table_name: str) -> bool:
        """
        Check if a table exists.

        Args:
            table_name: Name of the table

        Returns:
            True if table exists
        """
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
        result = self.execute_query(query, (table_name,))
        return len(result) > 0

    def create_table(self, table_name: str, columns: Dict[str, str]) -> None:
        """
        Create a table with specified columns.

        Args:
            table_name: Name of the table to create
            columns: Dictionary of column_name: data_type
        """
        column_defs = ', '.join(f"{name} {dtype}" for name, dtype in columns.items())
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({column_defs})"
        self.execute_query(query)

    def insert_data(self, table_name: str, data: Dict[str, Any]) -> None:
        """
        Insert a single row of data into a table.

        Args:
            table_name: Name of the table
            data: Dictionary of column_name: value
        """
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        self.execute_query(query, tuple(data.values()))

    def read_table(self, table_name: str, columns: str = '*',
                   where: Optional[str] = None, limit: Optional[int] = None) -> List:
        """
        Read data from a table with optional filtering.

        Args:
            table_name: Name of the table
            columns: Columns to select (default: '*')
            where: WHERE clause (without 'WHERE' keyword)
            limit: Maximum number of rows to return

        Returns:
            List of query results
        """
        query = f"SELECT {columns} FROM {table_name}"
        if where:
            query += f" WHERE {where}"
        if limit:
            query += f" LIMIT {limit}"
        return self.execute_query(query)

    # =========================================================
    # Class methods for quick operations without instance
    # =========================================================

    @classmethod
    def quick_peek(cls, db_path: str, max_rows: int = 5) -> None:
        """
        Quick preview of database contents without creating instance.

        Args:
            db_path: Path to SQLite database
            max_rows: Maximum rows to show per table
        """
        with cls(db_path) as db:
            tables = db.get_tables()
            print(f"Database: {db_path}")
            print(f"Tables: {tables}\n")

            for table in tables:
                print(f"Table: {table}")
                print("-" * 40)

                # Get column info
                columns = db.get_table_info(table)
                col_names = [col['name'] for col in columns]
                print(f"Columns: {col_names}")

                # Show sample data
                rows = db.read_table(table, limit=max_rows)
                if rows:
                    print(f"Sample data ({len(rows)} rows):")
                    for row in rows:
                        print(f"  {dict(row)}")
                else:
                    print("  (empty table)")
                print()

    @classmethod
    def to_dataframe(cls, db_path: str, table_name: str,
                     where: Optional[str] = None) -> Optional[Any]:
        """
        Read table directly into pandas DataFrame.

        Args:
            db_path: Path to SQLite database
            table_name: Name of the table
            where: Optional WHERE clause

        Returns:
            pandas DataFrame or None if pandas not available
        """
        pd = _import_pandas()
        if not pd:
            print("pandas not installed. Install with: pip install pandas")
            return None

        with cls(db_path) as db:
            query = f"SELECT * FROM {table_name}"
            if where:
                query += f" WHERE {where}"

            # Use pandas read_sql for better performance
            return pd.read_sql(query, db.connection)

    @classmethod
    def read_all_dbs(cls, folder_path: str, table_name: str,
                     pattern: str = "*.db") -> Dict[str, List]:
        """
        Read same table from multiple database files in a folder.

        Args:
            folder_path: Path to folder containing .db files
            table_name: Name of table to read from each database
            pattern: File pattern to match (default: "*.db")

        Returns:
            Dictionary mapping database filename to data
        """
        folder = Path(folder_path)
        results = {}

        for db_file in folder.glob(pattern):
            try:
                with cls(db_file) as db:
                    if db.table_exists(table_name):
                        data = db.read_table(table_name)
                        results[db_file.name] = data
                    else:
                        print(f"Table '{table_name}' not found in {db_file.name}")
            except Exception as e:
                print(f"Error reading {db_file.name}: {e}")

        return results

    @classmethod
    def describe(cls, db_path: str) -> None:
        """
        Show complete database structure.

        Args:
            db_path: Path to SQLite database
        """
        with cls(db_path) as db:
            print(f"Database: {db_path}")
            print(f"Size: {os.path.getsize(db_path):,} bytes")
            print("=" * 50)

            tables = db.get_tables()
            print(f"Tables ({len(tables)}):")

            for table in tables:
                # Get row count
                count_result = db.execute_query(f"SELECT COUNT(*) as cnt FROM {table}")
                row_count = count_result[0]['cnt'] if count_result else 0

                print(f"\n  {table} ({row_count} rows)")
                print("  " + "-" * 40)

                # Show column details
                columns = db.get_table_info(table)
                for col in columns:
                    pk_marker = " [PK]" if col['pk'] else ""
                    null_marker = "" if col['notnull'] else " (nullable)"
                    default_val = f" DEFAULT {col['dflt_value']}" if col['dflt_value'] else ""
                    print(f"    {col['name']}: {col['type']}{pk_marker}{null_marker}{default_val}")

    @classmethod
    def read_by_date(cls, db_path: str, table_name: str,
                     date_column: str = 'timestamp',
                     start: Optional[str] = None,
                     end: Optional[str] = None) -> List:
        """
        Read data filtered by date range.

        Args:
            db_path: Path to SQLite database
            table_name: Name of the table
            date_column: Name of the date column
            start: Start date (inclusive)
            end: End date (inclusive)

        Returns:
            List of query results
        """
        where_clauses = []
        if start:
            where_clauses.append(f"{date_column} >= '{start}'")
        if end:
            where_clauses.append(f"{date_column} <= '{end}'")

        where = " AND ".join(where_clauses) if where_clauses else None

        with cls(db_path) as db:
            return db.read_table(table_name, where=where)
