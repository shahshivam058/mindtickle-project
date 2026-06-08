# Objective : 

At Mindtickle, we strive to meet our clients' unique needs. Currently, a client company has requested a report detailing the number of lesson completed on daily basis by each of its active user. Your goal is to create a Python script to compile this report, store it in an AWS S3 Bucket, and dispatch it via email (AWS SES) as attachment. The file should be of CSV format with the following columns - Name, Number of lessons completed, Date

The challenge lies in aggregating data from difference database sources: PostgreSQL and MySQL. While you won't need to create the databases from scratch, you'll utilize our provided docker-compose file to spin up sample databases. The initial data and relations can be checked in `setup/init.mysql.sql` and `setup/init.pg.sql` files. You can use this data for reference and can add your own data as well to these files for testing purposes.



# Daily Lesson Completion Reporting System - Reviewer Guide

This guide provides supplementary setup and execution instructions for the daily lesson completion reporting system assignment.

## 🏗 Architecture Design

The code is structured as a modular Python package located in the `src/` directory. By splitting the concerns, the components are fully reusable across different environments (e.g. standalone scripts, Cron jobs, AWS Lambda, or orchestration tools like Airflow/Prefect):

- **`src/config.py`**: Reads configuration variables from environment variables (with `.env` file loading fallback).
- **`src/db/`**: Reusable database clients:
  - `postgres_client.py`: Class `PostgresClient` context manager for Postgres queries.
  - `mysql_client.py`: Class `MySQLClient` context manager for MySQL queries.
- **`src/report_generator.py`**: A pure functional utility `generate_report` that transforms raw DB records into the required CSV format (`Name, Number of lessons completed, Date`). Contains no side-effects.
- **`src/aws/`**: Reusable AWS service clients:
  - `s3_service.py`: Class `S3Service` utility for S3 uploads with standard 5-attempt retry.
  - `ses_service.py`: Class `SESService` utility for sending raw MIME emails with attachments with standard 5-attempt retry.
- **`src/logger.py`**: Custom centralized logger helper to output all system logs in JSON format.
- **`src/main.py`**: The central orchestrator that glues the modules together. Supports a `--dry-run` execution flag.

---

## 🔧 Installation & Setup

### 1. Database Setup


```bash
cd setup


# Start the containers
docker-compose up --build

```
This initializes:
- PostgreSQL with a `mindtickle_users` table and sample active/inactive users.
- MySQL with a `lesson_completion` table containing sample completion data.

### 2. Python Environment Setup

```bash
python -m venv venv
source venv/Scripts/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 🚀 Execution

### Mode A: Dry Run (No AWS credentials needed)

```bash
python -m src.main --dry-run
```

### Mode B: Production Run (Requires AWS credentials)

1. Ensure the following environment variables are set:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_DEFAULT_REGION`
   - `S3_BUCKET_NAME`
   - `SES_SENDER_EMAIL`
   - `SES_RECIPIENT_EMAIL`

2. Run:
   ```bash
   python -m src.main
   ```
