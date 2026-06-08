import sys
from datetime import datetime
from src.config import Config
from src.db import PostgresClient, MySQLClient
from src.report_generator import generate_report
from src.aws import S3Service, SESService
from src.logger import get_logger

logger = get_logger("main")


def run_pipeline(dry_run: bool = False) -> str:

    logger.info("Initializing Daily Lesson Completion Reporting Pipeline")
    
    Config.validate()
    
    # 1. Extraction phase
    try:
        with PostgresClient() as pg_client:
            active_users = pg_client.fetch_active_users()
            logger.info(f"Retrieved {len(active_users)} active users from PostgreSQL")
    except Exception as e:
        logger.error(f"Error fetching active users from PostgreSQL: {e}")
        raise

    try:
        with MySQLClient() as mysql_client:
            completions = mysql_client.fetch_lesson_completions()
            logger.info(f"Retrieved {len(completions)} completion records from MySQL")
    except Exception as e:
        logger.error(f"Error fetching completions from MySQL: {e}")
        raise

    # 2. Transformation phase
    csv_report = generate_report(active_users, completions)
    
    today_str = datetime.today().strftime("%Y-%m-%d")
    report_filename = f"daily_lesson_completion_report_{today_str}.csv"
    
    # 3. Loading phase (AWS S3 & SES)
    if dry_run:
        logger.info("--- DRY RUN ENABLED ---")
        logger.info(f"Report filename to generate: {report_filename}")
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

    # Email via SES
    try:
        ses = SESService()
        subject = f"Daily Lesson Completion Report - {today_str}"
        body_text = f"Hello,\n\nPlease find attached the daily lesson completion report for active users generated on {today_str}.\n\nBest regards,\nAutomated Reporting System"
        ses.send_email_with_attachment(
            subject=subject,
            body_text=body_text,
            attachment_content=csv_report,
            attachment_name=report_filename
        )
    except Exception as e:
        logger.error(f"Failed to send report email via SES: {e}")
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
