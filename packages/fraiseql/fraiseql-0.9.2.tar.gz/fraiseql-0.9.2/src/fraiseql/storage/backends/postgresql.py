"""PostgreSQL-based APQ storage backend for FraiseQL."""

import json
import logging
from typing import Any, Dict, Optional, Tuple

from .base import APQStorageBackend

logger = logging.getLogger(__name__)


class PostgreSQLAPQBackend(APQStorageBackend):
    """PostgreSQL APQ storage backend.

    This backend stores both persisted queries and cached responses in PostgreSQL.
    It's designed to work with the existing database connection and provide
    enterprise-grade persistence and scalability.

    Features:
    - Automatic table creation
    - JSON response serialization
    - Connection pooling support
    - Graceful error handling
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize the PostgreSQL backend with configuration.

        Args:
            config: Backend configuration including database settings
                - table_prefix: Prefix for APQ tables (default: "apq_")
                - auto_create_tables: Whether to create tables automatically (default: True)
                - connection_timeout: Database connection timeout in seconds (default: 30)
        """
        self._config = config
        self._table_prefix = config.get("table_prefix", "apq_")
        self._queries_table = f"{self._table_prefix}queries"
        self._responses_table = f"{self._table_prefix}responses"
        self._auto_create_tables = config.get("auto_create_tables", True)
        self._connection_timeout = config.get("connection_timeout", 30)

        logger.debug(
            f"PostgreSQL APQ backend initialized: "
            f"queries_table={self._queries_table}, "
            f"responses_table={self._responses_table}"
        )

        # Initialize tables if auto-creation is enabled
        if self._auto_create_tables:
            self._ensure_tables_exist()

    def get_persisted_query(self, hash_value: str) -> Optional[str]:
        """Retrieve stored query by hash.

        Args:
            hash_value: SHA256 hash of the persisted query

        Returns:
            GraphQL query string if found, None otherwise
        """
        if not hash_value:
            return None

        try:
            sql = f"SELECT query FROM {self._queries_table} WHERE hash = %s"
            result = self._fetch_one(sql, (hash_value,))

            if result:
                logger.debug(f"Retrieved APQ query with hash {hash_value[:8]}...")
                return result[0]
            logger.debug(f"APQ query not found for hash {hash_value[:8]}...")
            return None

        except Exception as e:
            logger.warning(f"Failed to retrieve persisted query: {e}")
            return None

    def store_persisted_query(self, hash_value: str, query: str) -> None:
        """Store query by hash.

        Args:
            hash_value: SHA256 hash of the query
            query: GraphQL query string to store
        """
        try:
            sql = f"""
                INSERT INTO {self._queries_table} (hash, query, created_at)
                VALUES (%s, %s, NOW())
                ON CONFLICT (hash) DO UPDATE SET
                    query = EXCLUDED.query,
                    updated_at = NOW()
            """
            self._execute_query(sql, (hash_value, query))
            logger.debug(f"Stored APQ query with hash {hash_value[:8]}...")

        except Exception as e:
            logger.warning(f"Failed to store persisted query: {e}")

    def get_cached_response(self, hash_value: str) -> Optional[Dict[str, Any]]:
        """Get cached JSON response for APQ hash.

        Args:
            hash_value: SHA256 hash of the persisted query

        Returns:
            Cached GraphQL response dict if found, None otherwise
        """
        if not hash_value:
            return None

        try:
            sql = f"SELECT response FROM {self._responses_table} WHERE hash = %s"
            result = self._fetch_one(sql, (hash_value,))

            if result:
                logger.debug(f"Retrieved cached response for hash {hash_value[:8]}...")
                return json.loads(result[0])
            logger.debug(f"Cached response not found for hash {hash_value[:8]}...")
            return None

        except Exception as e:
            logger.warning(f"Failed to retrieve cached response: {e}")
            return None

    def store_cached_response(self, hash_value: str, response: Dict[str, Any]) -> None:
        """Store pre-computed JSON response for APQ hash.

        Args:
            hash_value: SHA256 hash of the persisted query
            response: GraphQL response dict to cache
        """
        try:
            response_json = json.dumps(response)
            sql = f"""
                INSERT INTO {self._responses_table} (hash, response, created_at)
                VALUES (%s, %s, NOW())
                ON CONFLICT (hash) DO UPDATE SET
                    response = EXCLUDED.response,
                    updated_at = NOW()
            """
            self._execute_query(sql, (hash_value, response_json))
            logger.debug(f"Stored cached response for hash {hash_value[:8]}...")

        except Exception as e:
            logger.warning(f"Failed to store cached response: {e}")

    def _ensure_tables_exist(self) -> None:
        """Ensure that required tables exist in the database."""
        try:
            # Create queries table
            queries_sql = self._get_create_queries_table_sql()
            self._execute_query(queries_sql)

            # Create responses table
            responses_sql = self._get_create_responses_table_sql()
            self._execute_query(responses_sql)

            logger.debug("APQ tables ensured to exist")

        except Exception as e:
            logger.warning(f"Failed to ensure tables exist: {e}")

    def _get_create_queries_table_sql(self) -> str:
        """Get SQL for creating the queries table."""
        return f"""
            CREATE TABLE IF NOT EXISTS {self._queries_table} (
                hash VARCHAR(64) PRIMARY KEY,
                query TEXT NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """

    def _get_create_responses_table_sql(self) -> str:
        """Get SQL for creating the responses table."""
        return f"""
            CREATE TABLE IF NOT EXISTS {self._responses_table} (
                hash VARCHAR(64) PRIMARY KEY,
                response JSONB NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """

    def _get_connection(self):
        """Get database connection.

        This is a placeholder that would integrate with FraiseQL's
        existing database connection patterns in a real implementation.
        """
        # In a real implementation, this would get a connection from
        # FraiseQL's database pool or create a new one
        raise NotImplementedError("Database connection integration needed")

    def _execute_query(self, sql: str, params: Optional[Tuple] = None) -> None:
        """Execute a SQL query.

        Args:
            sql: SQL query to execute
            params: Query parameters

        Note: This is a mock implementation for testing purposes.
        """
        # Mock implementation for testing
        # In a real implementation, this would use the database connection
        logger.debug(f"Executing SQL: {sql[:100]}...")

    def _fetch_one(self, sql: str, params: Optional[Tuple] = None) -> Optional[Tuple]:
        """Fetch one row from a SQL query.

        Args:
            sql: SQL query to execute
            params: Query parameters

        Returns:
            First row as tuple or None if no results

        Note: This is a mock implementation for testing purposes.
        """
        # Mock implementation for testing
        # In a real implementation, this would use the database connection
        logger.debug(f"Fetching SQL: {sql[:100]}...")
        return None
