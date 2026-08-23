"""jobsuche_client — typed client for the unofficial BA Jobsuche API."""
from __future__ import annotations

from .client import JobsucheClient
from .config import Config
from .exceptions import ApiError, JobsucheError, NotFoundError, RateLimitError
from .models import JobDetails, JobSearchResponse, JobSearchResult

__all__ = [
    "JobsucheClient",
    "Config",
    "JobsucheError",
    "ApiError",
    "NotFoundError",
    "RateLimitError",
    "JobDetails",
    "JobSearchResponse",
    "JobSearchResult",
]
