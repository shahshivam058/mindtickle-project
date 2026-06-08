import boto3
from botocore.exceptions import ClientError
from botocore.config import Config as BotoConfig
from src.logger import get_logger
from src.config import Config

logger = get_logger(__name__)

class S3Service:
    
    def __init__(self, config: Config = Config):
        self.bucket_name = config.S3_BUCKET_NAME
        self.retry_config = BotoConfig(
            retries={
                "max_attempts": 5,
                "mode": "standard"
            }
        )
        self.client = boto3.client(
            "s3",
            aws_access_key_id=config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
            region_name=config.AWS_REGION,
            config=self.retry_config
        )

    def upload_csv(self, csv_content: str, destination_key: str) -> bool:
        logger.info(f"Uploading report to s3://{self.bucket_name}/{destination_key}")
        try:
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=destination_key,
                Body=csv_content.encode("utf-8"),
                ContentType="text/csv"
            )
            logger.info("Successfully uploaded report to S3")
            return True
        except ClientError as e:
            logger.error(f"Failed to upload report to S3: {e}")
            raise
