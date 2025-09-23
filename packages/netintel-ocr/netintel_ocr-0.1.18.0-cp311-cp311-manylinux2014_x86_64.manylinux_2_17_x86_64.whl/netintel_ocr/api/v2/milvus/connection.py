"""
Milvus Connection Management
"""

from typing import Optional, Dict, Any, List
from pymilvus import (
    connections,
    utility,
    Collection,
    DataType,
    MilvusClient,
    MilvusException,
)
import logging
from contextlib import contextmanager
import time
from ..config import settings
from ..exceptions import MilvusConnectionError


logger = logging.getLogger(__name__)


class MilvusConnectionManager:
    """Manages Milvus database connections"""

    def __init__(
        self,
        alias: str = "default",
        host: Optional[str] = None,
        port: Optional[int] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        database: Optional[str] = None,
        secure: bool = False,
        **kwargs,
    ):
        self.alias = alias
        self.host = host or settings.milvus_host
        self.port = port or settings.milvus_port
        self.user = user or settings.milvus_user
        self.password = password or settings.milvus_password
        self.database = database or settings.milvus_database
        self.secure = secure or settings.milvus_secure
        self.kwargs = kwargs

        self._connected = False
        self._client: Optional[MilvusClient] = None
        self._connection_params = self._build_connection_params()

    def _build_connection_params(self) -> Dict[str, Any]:
        """Build connection parameters"""

        params = {
            "alias": self.alias,
            "host": self.host,
            "port": self.port,
            "db_name": self.database,
            "secure": self.secure,
        }

        if self.user and self.password:
            params["user"] = self.user
            params["password"] = self.password

        # Add any additional parameters
        params.update(self.kwargs)

        return params

    def connect(self, retry: int = 3, retry_delay: int = 2) -> bool:
        """Establish connection to Milvus"""

        for attempt in range(retry):
            try:
                # Close existing connection if any
                if self._connected:
                    self.disconnect()

                # Create connection
                connections.connect(**self._connection_params)

                # Create client for high-level operations
                uri = f"{'https' if self.secure else 'http'}://{self.host}:{self.port}"
                self._client = MilvusClient(
                    uri=uri,
                    user=self.user,
                    password=self.password,
                    db_name=self.database,
                )

                self._connected = True
                logger.info(f"Connected to Milvus at {self.host}:{self.port}/{self.database}")
                return True

            except Exception as e:
                logger.warning(f"Connection attempt {attempt + 1} failed: {str(e)}")
                if attempt < retry - 1:
                    time.sleep(retry_delay)
                else:
                    raise MilvusConnectionError(
                        message=f"Failed to connect to Milvus after {retry} attempts",
                        host=self.host,
                        port=self.port,
                    )

        return False

    def disconnect(self):
        """Disconnect from Milvus"""

        try:
            if self._connected:
                connections.disconnect(self.alias)
                self._connected = False
                self._client = None
                logger.info("Disconnected from Milvus")
        except Exception as e:
            logger.error(f"Error disconnecting from Milvus: {str(e)}")

    def is_connected(self) -> bool:
        """Check if connected to Milvus"""

        try:
            if not self._connected:
                return False

            # Ping the server
            connections.get_connection_addr(self.alias)
            return True
        except:
            self._connected = False
            return False

    @contextmanager
    def get_connection(self):
        """Context manager for Milvus connection"""

        if not self._connected:
            self.connect()

        try:
            yield self
        finally:
            pass  # Keep connection alive for reuse

    def list_collections(self) -> List[str]:
        """List all collections in the database"""

        if not self.is_connected():
            self.connect()

        try:
            return utility.list_collections()
        except Exception as e:
            logger.error(f"Failed to list collections: {str(e)}")
            raise MilvusConnectionError(
                message=f"Failed to list collections: {str(e)}",
                host=self.host,
                port=self.port,
            )

    def has_collection(self, collection_name: str) -> bool:
        """Check if a collection exists"""

        if not self.is_connected():
            self.connect()

        try:
            return utility.has_collection(collection_name)
        except Exception as e:
            logger.error(f"Failed to check collection existence: {str(e)}")
            return False

    def get_collection(self, collection_name: str) -> Optional[Collection]:
        """Get a collection object"""

        if not self.is_connected():
            self.connect()

        try:
            if self.has_collection(collection_name):
                return Collection(collection_name)
            return None
        except Exception as e:
            logger.error(f"Failed to get collection {collection_name}: {str(e)}")
            return None

    def get_server_info(self) -> Dict[str, Any]:
        """Get Milvus server information"""

        if not self.is_connected():
            self.connect()

        try:
            version = utility.get_server_version()
            return {
                "connected": True,
                "host": self.host,
                "port": self.port,
                "database": self.database,
                "version": version,
                "collections": self.list_collections(),
            }
        except Exception as e:
            logger.error(f"Failed to get server info: {str(e)}")
            return {
                "connected": False,
                "error": str(e),
            }

    def health_check(self) -> Dict[str, Any]:
        """Perform health check"""

        health = {
            "status": "unknown",
            "connection": False,
            "server_available": False,
            "database": self.database,
            "collections_accessible": False,
        }

        try:
            # Check connection
            if self.is_connected():
                health["connection"] = True

                # Check server availability
                version = utility.get_server_version()
                if version:
                    health["server_available"] = True
                    health["server_version"] = version

                # Check collections access
                collections = self.list_collections()
                health["collections_accessible"] = True
                health["collections_count"] = len(collections)

                health["status"] = "healthy"
            else:
                health["status"] = "disconnected"

        except Exception as e:
            health["status"] = "error"
            health["error"] = str(e)

        return health

    @property
    def client(self) -> Optional[MilvusClient]:
        """Get the Milvus client instance"""

        if not self._connected:
            self.connect()
        return self._client

    def execute_with_retry(
        self,
        func,
        *args,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        **kwargs,
    ):
        """Execute a function with retry logic"""

        last_error = None

        for attempt in range(max_retries):
            try:
                # Ensure connection
                if not self.is_connected():
                    self.connect()

                # Execute function
                return func(*args, **kwargs)

            except MilvusException as e:
                last_error = e
                logger.warning(f"Milvus operation failed (attempt {attempt + 1}): {str(e)}")

                # Check if error is recoverable
                if "connection" in str(e).lower():
                    # Try to reconnect
                    self.disconnect()
                    time.sleep(retry_delay)
                else:
                    # Non-recoverable error
                    raise

            except Exception as e:
                last_error = e
                logger.error(f"Unexpected error in Milvus operation: {str(e)}")
                raise

        # All retries exhausted
        raise MilvusConnectionError(
            message=f"Operation failed after {max_retries} attempts: {str(last_error)}",
            host=self.host,
            port=self.port,
        )


# Global connection manager instance
milvus_conn = MilvusConnectionManager()


def get_milvus_connection() -> MilvusConnectionManager:
    """Get the global Milvus connection manager"""

    if not milvus_conn.is_connected():
        milvus_conn.connect()
    return milvus_conn


def ensure_connection(func):
    """Decorator to ensure Milvus connection before executing function"""

    def wrapper(*args, **kwargs):
        conn = get_milvus_connection()
        if not conn.is_connected():
            conn.connect()
        return func(*args, **kwargs)

    return wrapper