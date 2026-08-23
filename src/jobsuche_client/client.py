"""JobsucheClient — search_jobs(), get_job_details(), get_logo()."""
from __future__ import annotations

import base64
from typing import Iterable, Optional, Union
from urllib.parse import quote

import requests

from .config import Config
from .exceptions import ApiError, NotFoundError, RateLimitError
from .models import JobDetails, JobSearchResponse


class JobsucheClient:
    """Typed client for the unofficial BA Jobsuche API.

    Example
    -------
    >>> from jobsuche_client import JobsucheClient
    >>> client = JobsucheClient()               # reads env if present
    >>> resp = client.search_jobs(was="DevOps", wo="Berlin", size=3)
    >>> client.get_job_details(resp.results[0].referenznummer)
    """

    def __init__(
        self,
        config: Optional[Config] = None,
        session: Optional[requests.Session] = None,
    ) -> None:
        self.config = config or Config.from_env()
        self.session = session or requests.Session()

    # ------------------------------------------------------------------ #
    # public API
    # ------------------------------------------------------------------ #

    def search_jobs(
        self,
        was: Optional[str] = None,            # free-text job title
        wo: Optional[str] = None,             # free-text location
        umkreis: Optional[int] = None,        # radius km around `wo`
        page: int = 1,
        size: int = 50,
        arbeitgeber: Optional[str] = None,
        berufsfeld: Optional[str] = None,
        veroeffentlichtseit: Optional[int] = None,   # 0..100 days
        angebotsart: Optional[int] = None,    # 1 job, 2 self-emp., 4 ausbildung, 34 internship
        arbeitszeit: Union[str, Iterable[str], None] = None,  # vz tz snw ho mj
        befristung: Union[str, Iterable[str], None] = None,  # 1 fixed, 2 permanent
        zeitarbeit: Optional[bool] = None,
        behinderung: Optional[bool] = None,
    ) -> JobSearchResponse:
        """Search `/pc/v6/jobs`. Multi-value params are semicolon-joined."""
        params: dict[str, Union[str, int, bool]] = {"page": page, "size": size}
        optional = {
            "was": was, "wo": wo, "umkreis": umkreis, "arbeitgeber": arbeitgeber,
            "berufsfeld": berufsfeld, "veroeffentlichtseit": veroeffentlichtseit,
            "angebotsart": angebotsart, "zeitarbeit": zeitarbeit,
            "behinderung": behinderung,
        }
        params.update({k: v for k, v in optional.items() if v is not None})
        if arbeitszeit:
            params["arbeitszeit"] = self._join_multi(arbeitszeit)
        if befristung:
            params["befristung"] = self._join_multi(befristung)

        resp = self.session.get(
            f"{self.config.jobsuche_base_url}/pc/v6/jobs",
            headers=self.config.headers, params=params,
            timeout=self.config.timeout,
        )
        data = self._handle(resp)
        return JobSearchResponse.from_api(data)

    def get_job_details(self, refnr: str) -> JobDetails:
        """Fetch details for a `referenznummer`; base64-encodes it internally
        and takes care of URL-encoding the `=` padding."""
        encoded = quote(base64.b64encode(refnr.encode("utf-8")).decode("ascii"), safe="")
        resp = self.session.get(
            f"{self.config.jobsuche_base_url}/pc/v4/jobdetails/{encoded}",
            headers=self.config.headers, timeout=self.config.timeout,
        )
        return JobDetails.from_api(self._handle(resp))

    def get_logo(self, kundennummer_hash: str) -> bytes:
        """Employer logo bytes (webp/png). Raises NotFoundError (404) if none."""
        url = (
            f"{self.config.logo_base_url}"
            f"/ct/v1/arbeitgeberlogo/{quote(kundennummer_hash, safe='')}"
        )
        resp = self.session.get(
            url, headers=self.config.headers, timeout=self.config.timeout,
        )
        if resp.status_code == 404:
            raise NotFoundError("No logo for this employer", status_code=404)
        self._handle(resp)
        return resp.content

    # ------------------------------------------------------------------ #
    # helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _join_multi(value: Union[str, Iterable[str]]) -> str:
        return value if isinstance(value, str) else ";".join(value)

    def _handle(self, resp: requests.Response) -> dict:
        if resp.status_code == 404:
            raise NotFoundError("Not found", status_code=404)
        if resp.status_code == 429:
            raise RateLimitError(
                "Rate limited — slow down and cache results", status_code=429
            )
        if resp.status_code >= 400:
            raise ApiError(
                f"HTTP {resp.status_code}: {resp.text[:200]}",
                status_code=resp.status_code,
            )
        return resp.json()
