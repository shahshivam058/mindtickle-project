import csv
import io
from collections import Counter
from datetime import date
from typing import List, Dict, Any, Union
from src.logger import get_logger

logger = get_logger(__name__)

def generate_report(
    active_users: List[Dict[str, Any]], 
    completions: List[Dict[str, Any]]
) -> str:

    logger.info("Starting report generation/aggregation")
    
    # 1. Map user_id to user_name for active users
    active_user_map = {user["user_id"]: user["user_name"] for user in active_users}
    
    # 2. Aggregate completions for active users by (user_name, date)
    aggregation = Counter()
    for completion in completions:
        uid = completion["user_id"]
        
        # Skip if user is not active
        if uid not in active_user_map:
            continue
            
        u_name = active_user_map[uid]
        c_date = completion["completion_date"]
        
        # Normalize date to string (YYYY-MM-DD)
        if isinstance(c_date, date):
            date_str = c_date.strftime("%Y-%m-%d")
        else:
            date_str = str(c_date)
            
        aggregation[(u_name, date_str)] += 1
        
    # 3. Compile aggregated records
    report_records = []
    for (name, date_str), count in aggregation.items():
        report_records.append({
            "Name": name,
            "Number of lessons completed": count,
            "Date": date_str
        })
        
    # Sort by Date descending, then Name ascending for readable, consistent report ordering
    report_records.sort(key=lambda x: (x["Date"], x["Name"]))
    
    # 4. Generate CSV
    output = io.StringIO()
    # Write CSV with CRLF line endings (default for Excel and standard CSV)
    writer = csv.DictWriter(
        output, 
        fieldnames=["Name", "Number of lessons completed", "Date"],
        lineterminator="\n"
    )
    writer.writeheader()
    writer.writerows(report_records)
    
    csv_content = output.getvalue()
    output.close()
    
    logger.info(f"Report compiled successfully with {len(report_records)} rows")
    return csv_content
