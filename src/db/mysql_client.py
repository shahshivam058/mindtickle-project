import pymysql
from typing import List, Dict, Any
from src.logger import get_logger
from src.config import Config

logger = get_logger(__name__)

class MySQLClient:
    
    def __init__(self, config: Config = Config):
        self.db = config.MYSQL_DB
        self.user = config.MYSQL_USER
        self.password = config.MYSQL_PASSWORD
        self.host = config.MYSQL_HOST
        self.port = config.MYSQL_PORT
        self.conn = None

    def __enter__(self):
        logger.info(f"Connecting to MySQL database at {self.host}:{self.port}")
        self.conn = pymysql.connect(
            database=self.db,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()
            logger.info("Closed MySQL connection")

    def fetch_lesson_completions(self) -> List[Dict[str, Any]]:
        query = "SELECT user_id, lesson_id, completion_date FROM lesson_completion"
        
        with self.conn.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            return [
                {
                    "user_id": row[0],
                    "lesson_id": row[1],
                    "completion_date": row[2]
                }
                for row in rows
            ]
