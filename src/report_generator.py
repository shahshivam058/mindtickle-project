import pandas as pd

from src.logger import get_logger

logger = get_logger(__name__)


def generate_report(active_users, completions) -> str:
    """
        This function takes active users and lesson completion records,
        removes invalid or duplicate data, keeps only active users,
        aggregates lesson completions per user per day, and returns the final CSV content.
    """
    
    logger.info("Starting robust report generation/aggregation using Pandas")

    if not active_users:
        logger.warning("No active users provided. Returning empty report.")
        return "Name,Number of lessons completed,Date\n"

    # Convert active users to DataFrame, supporting lists or generators of chunks
    if isinstance(active_users, list):
        if active_users and isinstance(active_users[0], dict):
            active_users_df = pd.DataFrame(active_users)
        else:
            # It's a list of chunks
            active_users_chunks = [pd.DataFrame(chunk) for chunk in active_users if chunk]
            if active_users_chunks:
                active_users_df = pd.concat(active_users_chunks, ignore_index=True)
            else:
                active_users_df = pd.DataFrame(columns=["user_id", "user_name"])
    else:
        # It's a generator of chunks
        active_users_chunks = [pd.DataFrame(chunk) for chunk in active_users if chunk]
        if active_users_chunks:
            active_users_df = pd.concat(active_users_chunks, ignore_index=True)
        else:
            active_users_df = pd.DataFrame(columns=["user_id", "user_name"])

    # Drop rows with null values in critical fields (user_id or user_name)
    active_users_df = active_users_df.dropna(subset=["user_id", "user_name"])

    if active_users_df.empty:
        logger.warning(
            "Active users dataset is empty after filtering nulls. Returning empty report."
        )
        return "Name,Number of lessons completed,Date\n"

    # Ensure user_id is of integer type to match completions database schema join key
    active_users_df["user_id"] = pd.to_numeric(active_users_df["user_id"], errors="coerce").astype(
        "Int64"
    )
    active_users_df = active_users_df.dropna(subset=["user_id"])

    # Normalize input completions into an iterable of chunks
    if isinstance(completions, list):
        if completions and isinstance(completions[0], dict):
            chunks = [completions]
        else:
            chunks = completions
    else:
        chunks = completions

    chunk_aggregates = []
    for chunk in chunks:
        if not chunk:
            continue

        chunk_df = pd.DataFrame(chunk)

        # Drop rows with missing user_id or completion_date
        chunk_df = chunk_df.dropna(subset=["user_id", "completion_date"])
        if chunk_df.empty:
            continue

        # Ensure user_id is integer type
        chunk_df["user_id"] = pd.to_numeric(chunk_df["user_id"], errors="coerce").astype("Int64")
        chunk_df = chunk_df.dropna(subset=["user_id"])

        # to handle duplicate data entries gracefully
        if "lesson_id" in chunk_df.columns:
            chunk_df = chunk_df.drop_duplicates(subset=["user_id", "lesson_id", "completion_date"])
        else:
            chunk_df = chunk_df.drop_duplicates(subset=["user_id", "completion_date"])

        # Merge to filter out inactive/orphaned users
        merged = pd.merge(chunk_df, active_users_df, on="user_id", how="inner")
        if merged.empty:
            continue

        # Normalize and format date, filtering out malformed dates using errors="coerce"
        merged["Date"] = pd.to_datetime(merged["completion_date"], errors="coerce").dt.strftime(
            "%Y-%m-%d"
        )
        merged = merged.dropna(subset=["Date"])
        if merged.empty:
            continue

        # Aggregate within this chunk. Group by user_id and user_name to keep users with identical names distinct.
        agg = merged.groupby(["user_id", "user_name", "Date"]).size().reset_index(name="count")
        chunk_aggregates.append(agg)

    if chunk_aggregates:
        # Combine all chunk aggregates and perform the final aggregation
        final_df = pd.concat(chunk_aggregates)
        final_report = (
            final_df.groupby(["user_id", "user_name", "Date"])["count"].sum().reset_index()
        )
    else:
        final_report = pd.DataFrame(columns=["user_id", "user_name", "Date", "count"])

    # Rename columns to match requirements
    final_report = final_report.rename(
        columns={"user_name": "Name", "count": "Number of lessons completed"}
    )

    # Ensure all required columns are present and in the correct order (dropping user_id)
    final_report = final_report[["Name", "Number of lessons completed", "Date"]]

    # Sort by Date ascending, then Name ascending
    final_report = final_report.sort_values(by=["Date", "Name"])

    # pandas automatically handles quotes, commas, and newlines in Name properly per RFC 4180
    csv_content = final_report.to_csv(index=False, lineterminator="\n")

    logger.info(f"Report compiled successfully with {len(final_report)} rows")
    return csv_content
