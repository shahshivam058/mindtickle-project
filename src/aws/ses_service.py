from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import boto3
from botocore.config import Config as BotoConfig
from botocore.exceptions import ClientError

from src.config import Config
from src.exceptions import EmailDispatchError
from src.logger import get_logger

logger = get_logger(__name__)


class SESService:
    """
        Keeping email logic in one class makes the main pipeline easier to read
        and keeps AWS SES details separate from report generation.
    """

    def __init__(self, config: Config = Config):
        self.sender = config.SES_SENDER
        self.recipient = config.SES_RECIPIENT
        self.retry_config = BotoConfig(retries={"max_attempts": 5, "mode": "standard"})
        self.client = boto3.client(
            "ses",
            aws_access_key_id=config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
            region_name=config.AWS_REGION,
            config=self.retry_config,
        )

    def send_email_with_attachment(
        self, subject: str, body_text: str, attachment_content: str, attachment_name: str
    ) -> bool:
        """
            The email is built as a raw MIME message because SES requires this format
            when sending attachments.
        """
        logger.info(f"Sending email from {self.sender} to {self.recipient} via SES")

        # Create a multipart message container
        msg = MIMEMultipart()
        msg["Subject"] = subject
        msg["From"] = self.sender
        msg["To"] = self.recipient

        # Add the body to the message
        text_part = MIMEText(body_text, "plain")
        msg.attach(text_part)

        # Attach the CSV file
        attachment = MIMEApplication(attachment_content.encode("utf-8"))
        attachment.add_header("Content-Disposition", "attachment", filename=attachment_name)
        msg.attach(attachment)

        try:
            response = self.client.send_raw_email(
                Source=self.sender,
                Destinations=[self.recipient],
                RawMessage={"Data": msg.as_string()},
            )
            logger.info(f"Email sent successfully! Message ID: {response.get('MessageId')}")
            return True
        except ClientError as e:
            logger.error(f"Failed to send email via SES: {e}")
            raise EmailDispatchError(f"Failed to send email via SES: {e}") from e
