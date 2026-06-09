class ReportingPipelineError(Exception):
    """Base exception for the ETL pipeline."""

    pass


class DatabaseError(ReportingPipelineError):
    """Raised when a database connection or query fails."""

    pass


class EmailDispatchError(ReportingPipelineError):
    """Raised when sending the report email fails."""

    pass
