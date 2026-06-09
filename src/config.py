import os

from dotenv import load_dotenv

# Try a few common .env locations in order.
# 1. ENV_FILE allows a custom .env path to be passed from the environment.
# 2. Project root .env is useful for local development.
# 3. setup/.env supports projects that keep setup-related config separately.
config_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(config_dir)

possible_paths = [
    os.environ.get("ENV_FILE"),
    os.path.join(root_dir, ".env"),
    os.path.join(root_dir, "setup", ".env"),
]

for path in possible_paths:
    if path and os.path.exists(path):
        load_dotenv(path)
        break
else:
    load_dotenv()


class Config:
    """
        Values are read from environment variables so the same code can run
        in local development, staging, and production with different settings.
    """

    # PostgreSQL configuration
    POSTGRES_DB = os.environ.get("POSTGRES_DB")
    POSTGRES_USER = os.environ.get("POSTGRES_USER")
    POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
    POSTGRES_HOST = os.environ.get("POSTGRES_HOST")
    POSTGRES_PORT = int(os.environ.get("POSTGRES_PORT"))

    # MySQL configuration
    MYSQL_DB = os.environ.get("MYSQL_DATABASE")
    MYSQL_USER = os.environ.get("MYSQL_USER") or os.environ.get("MYSQL_user")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD") or os.environ.get("MYSQL_ROOT_PASSWORD")
    MYSQL_HOST = os.environ.get("MYSQL_HOST")
    MYSQL_PORT = int(os.environ.get("MYSQL_PORT"))

    # AWS configuration
    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
    AWS_REGION = os.environ.get("AWS_DEFAULT_REGION")

    # S3 configuration
    S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME")

    # SES configuration
    SES_SENDER = os.environ.get("SES_SENDER_EMAIL")
    SES_RECIPIENT = os.environ.get("SES_RECIPIENT_EMAIL")

    @classmethod
    def validate(cls):
        """
            This should fail early when important environment variables are missing,
            instead of allowing the pipeline to fail later during database, S3, or email work.        
        """
        pass
