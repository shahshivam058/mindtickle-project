import pymysql
import pymysql.cursors

from src.config import Config
from src.exceptions import DatabaseError
from src.logger import get_logger

logger = get_logger(__name__)


class MySQLClient:
    """
        This class is used as a context manager so the database connection
        is opened before the query runs and closed automatically afterward.
    """

    def __init__(self, config: Config = Config):
        self.db = config.MYSQL_DB
        self.user = config.MYSQL_USER
        self.password = config.MYSQL_PASSWORD
        self.host = config.MYSQL_HOST
        self.port = config.MYSQL_PORT
        self.conn = None

    def __enter__(self):
        logger.info(f"Connecting to MySQL database at {self.host}:{self.port}")
        try:
            self.conn = pymysql.connect(
                database=self.db,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
            )
            return self
        except Exception as e:
            raise DatabaseError(f"MySQL connection failed: {e}") from e

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()
            logger.info("Closed MySQL connection")

    def fetch_lesson_completions_generator(self, chunk_size: int = 100000):
        """
            Streaming keeps memory usage low when the users table is large,
            because the full result set is not loaded into Python at once.
        """
        query = "SELECT user_id, lesson_id, completion_date FROM lesson_completion"

        try:
            with self.conn.cursor(pymysql.cursors.SSCursor) as cursor:
                cursor.execute(query)
                while True:
                    rows = cursor.fetchmany(chunk_size)
                    if not rows:
                        break
                    yield [
                        {"user_id": row[0], "lesson_id": row[1], "completion_date": row[2]}
                        for row in rows
                    ]
        except Exception as e:
            raise DatabaseError(f"MySQL fetch lesson completions generator failed: {e}") from e
