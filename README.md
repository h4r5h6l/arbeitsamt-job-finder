# Arbeitsamt Job Finder

A client for the (unofficial) **Bundesagentur für Arbeit — Jobsuche API**, used to search job listings and streamline the job application process.

This project consumes the REST API documented by [`bundesAPI/jobsuche-api`](https://github.com/bundesAPI/jobsuche-api) — an unofficial, reverse-engineered spec of the API that powers the [Jobsuche](https://www.arbeitsagentur.de/jobsuche/) portal. Credit to the `bundesAPI` community for documenting it; this repo is not affiliated with the Bundesagentur für Arbeit.

## What it does

- Searches job listings (`was`, `wo`, `berufsfeld`, `arbeitszeit`, and other filters)
- Fetches full job details from a search result's reference number
- Fetches employer logos where available
- Provides a thin, typed client others can build application-tracking or auto-apply features on top of

## API overview

| Purpose | Method & URL |
|---|---|
| Search jobs | `GET https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v6/jobs` |
| Job details | `GET https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v4/jobdetails/{base64(refnr)}` |
| Employer logo | `GET https://rest.arbeitsagentur.de/vermittlung/ag-darstellung-service/ct/v1/arbeitgeberlogo/{kundennummerHash}` |

**Auth:** no OAuth or registration required — every request needs the header:

```
X-API-Key: jobboerse-jobsuche
```

**Typical flow:**

1. Search jobs → each result's `referenznummer` (the spec calls it `refnr`).
2. Base64-encode the `referenznummer` and fetch job details from `/pc/v4/jobdetails/{base64(refnr)}`.
3. If the details response includes `arbeitgeberKundennummerHash`, fetch the employer logo from the **separate** logo host.

> ⚠️ **Spec vs. live API:** the [`bundesAPI` OpenAPI spec (v2.1.0)](https://github.com/bundesAPI/jobsuche-api) documents the search results under `stellenangebote` with fields `refnr`/`titel`/`arbeitgeber`. The **live** `/pc/v6/jobs` endpoint actually returns `ergebnisliste` with `referenznummer`/`stellenangebotsTitel`/`firma`. The client models handle both via a tolerant field lookup, so callers never see the drift.

## Project structure

```
arbeitsamt-job-finder/
├── README.md
├── .gitignore
├── .env.example
├── pyproject.toml
├── src/
│   └── jobsuche_client/
│       ├── __init__.py
│       ├── client.py        # search_jobs(), get_job_details(), get_logo()
│       ├── models.py        # response models
│       ├── config.py        # base URLs, headers, timeouts
│       └── exceptions.py
├── app/                      # optional: expose via your own API
│   ├── main.py
│   └── routers/
│       └── jobs.py
├── scripts/
│   └── fetch_jobs.py         # example CLI usage
└── tests/
    ├── test_client.py
    └── fixtures/
```

## Setup

```bash
git clone <your-repo-url>
cd arbeitsamt-job-finder
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt   # or: pip install -e .
cp .env.example .env
```

## Usage

```bash
python scripts/fetch_jobs.py --was "Softwareentwickler" --wo "Leipzig" --umkreis 50
```

```python
from jobsuche_client import JobsucheClient

client = JobsucheClient()
resp = client.search_jobs(was="Softwareentwickler", wo="Leipzig", umkreis=50)
details = client.get_job_details(resp.results[0].referenznummer)
print(details.beschreibung)
```

## Notes

- This is an **unofficial** API with no formal SLA or documentation from the Bundesagentur für Arbeit — endpoints and parameters may change without notice.
- The `X-API-Key` value is a public constant used by the official app/website, not a personal secret. It's still kept in config rather than hardcoded, in case it changes.
- Be a good citizen: cache results where reasonable and avoid hammering the endpoints.

## License

MIT