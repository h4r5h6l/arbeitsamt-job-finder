"""Exceptions for the Jobsuche API client.

Hierarchy:
    JobsucheError            # base for everything
    ├── NotFoundError        # 404 (e.g. no logo for this employer)
    ├── RateLimitError        # 429 — slow down / cache more
    └── ApiError             # any other non-2xx
"""


class JobsucheError(Exception):
    """Base error for all API failures."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class NotFoundError(JobsucheError):
    """404 — a resource does not exist."""


class RateLimitError(JobsucheError):
    """429 — the API rate limit was hit; retry with backoff."""


class ApiError(JobsucheError):
    """Any other non-2xx response."""
