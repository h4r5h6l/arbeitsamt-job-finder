"""Base URLs, auth header and request settings."""
from __future__ import annotations

import os
from dataclasses import dataclass

# Public clientId used by the official BA app/website. Not a personal secret.
DEFAULT_API_KEY = "jobboerse-jobsuche"
DEFAULT_JOBSUCHE_BASE_URL = (
    "https://rest.arbeitsagentur.de/jobboerse/jobsuche-service"
)
DEFAULT_LOGO_BASE_URL = (
    "https://rest.arbeitsagentur.de/vermittlung/ag-darstellung-service"
)
DEFAULT_TIMEOUT = 15.0


@dataclass(frozen=True)
class Config:
    api_key: str = DEFAULT_API_KEY
    jobsuche_base_url: str = DEFAULT_JOBSUCHE_BASE_URL
    logo_base_url: str = DEFAULT_LOGO_BASE_URL
    timeout: float = DEFAULT_TIMEOUT

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            api_key=os.getenv("JOBSUCHE_API_KEY", DEFAULT_API_KEY),
            jobsuche_base_url=os.getenv(
                "JOBSUCHE_BASE_URL", DEFAULT_JOBSUCHE_BASE_URL
            ).rstrip("/"),
            logo_base_url=os.getenv(
                "JOBSUCHE_LOGO_BASE_URL", DEFAULT_LOGO_BASE_URL
            ).rstrip("/"),
        )

    @property
    def headers(self) -> dict[str, str]:
        return {"X-API-Key": self.api_key, "Accept": "application/json"}
