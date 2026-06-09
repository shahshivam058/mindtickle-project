import sys
from datetime import datetime

from src.aws import S3Service, SESService
from src.config import Config
from src.db import MySQLClient, PostgresClient
from src.exceptions import DatabaseError, EmailDispatchError
from src.logger import get_logger
from src.report_generator import generate_report

logger = get_logger("main")


def run_pipeline(dry_run: bool = False) -> str:
    """
        This pipeline collects active user data and lesson completion data,
        generates a CSV report, optionally saves it locally for testing,
        uploads it to S3, and sends it by email.
    """


    logger.info("Initializing Daily Lesson Completion Reporting Pipeline")

    Config.validate()

    # Fetches data from PostgreSQL and MySQL and generates report using streaming
    try:
        with PostgresClient() as pg_client, MySQLClient() as mysql_client:
            active_users_gen = pg_client.fetch_active_users_generator()
            completions_gen = mysql_client.fetch_lesson_completions_generator()
            logger.info("Streaming and aggregating data from PostgreSQL and MySQL...")
            csv_report = generate_report(active_users_gen, completions_gen)
    except DatabaseError as e:
        logger.error(f"Database error during extraction or report generation: {e}")
        raise

    today_str = datetime.today().strftime("%Y-%m-%d")
    report_filename = f"daily_lesson_completion_report_{today_str}.csv"

    # Dry Run Phase creates a csv in local machine and return
    if dry_run:
        logger.info("--- DRY RUN ENABLED ---")
        logger.info(f"Report filename to generate in Current Directory : {report_filename}")
        try:
            with open(report_filename, "w", encoding="utf-8") as f:
                f.write(csv_report)
            logger.info(f"Successfully saved CSV report locally to: {report_filename}")
        except Exception as e:
            logger.error(f"Failed to save CSV locally during dry run: {e}")
        logger.info("--- DRY RUN COMPLETE ---")
        return csv_report

    # Upload to S3
    try:
        s3 = S3Service()
        s3.upload_csv(csv_report, report_filename)
    except Exception as e:
        logger.error(f"Failed to upload report to S3: {e}. Proceeding to attempt email dispatch.")

    # Send an Email via SES
    try:
        ses = SESService()
        subject = f"Daily Lesson Completion Report - {today_str}"
        body_text = f"""Hello,

Please find attached the daily lesson completion report for active users generated on {today_str}.

Best regards,
Automated Reporting System"""
        ses.send_email_with_attachment(
            subject=subject,
            body_text=body_text,
            attachment_content=csv_report,
            attachment_name=report_filename,
        )
    except EmailDispatchError as e:
        logger.error(f"Email dispatch error via SES: {e}")
        raise

    logger.info("Pipeline executed successfully!")
    return csv_report


if __name__ == "__main__":
    is_dry = "--dry-run" in sys.argv
    try:
        run_pipeline(dry_run=is_dry)
    except Exception as e:
        logger.critical(f"Pipeline failed: {e}")
        sys.exit(1)
