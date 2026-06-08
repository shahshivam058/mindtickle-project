import psycopg2
from typing import List, Dict, Any
from src.logger import get_logger
from src.config import Config

logger = get_logger(__name__)

class PostgresClient:
    
    def __init__(self, config: Config = Config):
        self.db = config.POSTGRES_DB
        self.user = config.POSTGRES_USER
        self.password = config.POSTGRES_PASSWORD
        self.host = config.POSTGRES_HOST
        self.port = config.POSTGRES_PORT
        self.conn = None

    def __enter__(self):
        logger.info(f"Connecting to PostgreSQL database at {self.host}:{self.port}")
        self.conn = psycopg2.connect(
            dbname=self.db,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()
            logger.info("Closed PostgreSQL connection")

    def fetch_active_users(self) -> List[Dict[str, Any]]:
        query = "SELECT user_id, user_name FROM mindtickle_users WHERE active_status = 'active'"
        
        with self.conn.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            return [{"user_id": row[0], "user_name": row[1]} for row in rows]
