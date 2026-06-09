import psycopg2

from src.config import Config
from src.exceptions import DatabaseError
from src.logger import get_logger

logger = get_logger(__name__)


class PostgresClient:
    """
        This class is used as a context manager so the database connection
        is opened before the query runs and closed automatically afterward.
    """

    def __init__(self, config: Config = Config):
        self.db = config.POSTGRES_DB
        self.user = config.POSTGRES_USER
        self.password = config.POSTGRES_PASSWORD
        self.host = config.POSTGRES_HOST
        self.port = config.POSTGRES_PORT
        self.conn = None

    def __enter__(self):
        logger.info(f"Connecting to PostgreSQL database at {self.host}:{self.port}")
        try:
            self.conn = psycopg2.connect(
                dbname=self.db,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
            )
            return self
        except Exception as e:
            raise DatabaseError(f"PostgreSQL connection failed: {e}") from e

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()
            logger.info("Closed PostgreSQL connection")

    def fetch_active_users_generator(self, chunk_size: int = 50000):
        """
            Streaming keeps memory usage low when the users table is large,
            because the full result set is not loaded into Python at once.
        """
        query = "SELECT user_id, user_name FROM mindtickle_users WHERE active_status = 'active'"

        try:
            # psycopg2 uses named cursors for server-side streaming
            with self.conn.cursor(name="pg_active_users_stream") as cursor:
                cursor.itersize = chunk_size
                cursor.execute(query)
                while True:
                    rows = cursor.fetchmany(chunk_size)
                    if not rows:
                        break
                    yield [{"user_id": row[0], "user_name": row[1]} for row in rows]
        except Exception as e:
            raise DatabaseError(f"PostgreSQL fetch active users generator failed: {e}") from e
