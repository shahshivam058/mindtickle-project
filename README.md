# Objective : 

At Mindtickle, we strive to meet our clients' unique needs. Currently, a client company has requested a report detailing the number of lesson completed on daily basis by each of its active user. Your goal is to create a Python script to compile this report, store it in an AWS S3 Bucket, and dispatch it via email (AWS SES) as attachment. The file should be of CSV format with the following columns - Name, Number of lessons completed, Date

The challenge lies in aggregating data from difference database sources: PostgreSQL and MySQL. While you won't need to create the databases from scratch, you'll utilize our provided docker-compose file to spin up sample databases. The initial data and relations can be checked in `setup/init.mysql.sql` and `setup/init.pg.sql` files. You can use this data for reference and can add your own data as well to these files for testing purposes.



# Daily Lesson Completion Reporting System - Reviewer Guide

This guide provides supplementary setup and execution instructions for the daily lesson completion reporting system assignment.

## 🏗 Architecture Design

The code is structured as a modular Python package located in the `src/` directory. By splitting the concerns, the components are fully reusable across different environments (e.g. standalone scripts, Cron jobs, AWS Lambda, or orchestration tools like Airflow/Prefect):


### Module Breakdown

* **`src/config.py`**: Holds system configuration and dynamically loads `.env` variables from the root or `setup/` directories.
* **`src/db/`**: Reusable context-managed database adapters (`postgres_client.py` and `mysql_client.py`) equipped with server-side chunk generators.
* **`src/report_generator.py`**: A pure functional utility `generate_report` that acts as the ETL processor.
* **`src/aws/`**: Clean wrappers for AWS integrations (`s3_service.py` and `ses_service.py`).
* **`src/exceptions.py`**: Centralized custom exceptions (`DatabaseError`, `EmailDispatchError`) for structured error management.
* **`src/logger.py`**: Centralized logger that outputs structured logs in JSON format for easy ingestion.
* **`src/main.py`**: Central orchestrator controlling execution flow and dry-runs.

---

## 🔧 Installation & Setup

### 1. Database Setup

```bash
cd setup
copy .env.example .env  # Create environment config
docker-compose up --build
```
This initializes:
- PostgreSQL with a `mindtickle_users` table.
- MySQL with a `lesson_completion` table.

### 2. Python Environment Setup

```bash
python -m venv venv
source venv/Scripts/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## 🚀 Execution

### Mode A: Dry Run (No AWS credentials needed)

Runs the pipeline using streamed database extraction and pandas aggregation, saving the final CSV report locally to the current directory:
```bash
python -m src.main --dry-run
```

### Mode B: Production Run (Requires AWS credentials)

1. Ensure the following environment variables are set (in your `.env` or system environment):
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
