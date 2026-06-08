import os
from dotenv import load_dotenv


load_dotenv()


class Config:

    # PostgreSQL configuration
    POSTGRES_DB = os.environ.get("POSTGRES_DB", "mt-pg")
    POSTGRES_USER = os.environ.get("POSTGRES_USER", "user")
    POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "password")
    POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = int(os.environ.get("POSTGRES_PORT", 5432))

    # MySQL configuration
    MYSQL_DB = os.environ.get("MYSQL_DATABASE", "mt-mysql")
    MYSQL_USER = os.environ.get("MYSQL_USER", os.environ.get("MYSQL_user", "root"))
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", os.environ.get("MYSQL_ROOT_PASSWORD", "password"))
    MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.environ.get("MYSQL_PORT", 3306))

    # AWS configuration
    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
    AWS_REGION = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
    
    # S3 configuration
    S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME", "mindtickle-reports-bucket")
    
    # SES configuration
    SES_SENDER = os.environ.get("SES_SENDER_EMAIL", "sender@example.com")
    SES_RECIPIENT = os.environ.get("SES_RECIPIENT_EMAIL", "recipient@example.com")

    @classmethod
    def validate(cls):
        pass
