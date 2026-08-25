# Arbeitsamt Job Finder

A minimal script that consumes the (unofficial) **Bundesagentur für Arbeit — Jobsuche API** and dumps job search results as **raw JSON** — to the terminal and to a file.

This project talks to the REST API documented by [`bundesAPI/jobsuche-api`](https://github.com/bundesAPI/jobsuche-api) — an unofficial, reverse-engineered spec of the API behind the [Jobsuche](https://www.arbeitsagentur.de/jobsuche/) portal. Credit to the `bundesAPI` community for documenting it; this repo is not affiliated with the Bundesagentur für Arbeit.

## What it does

- Searches job listings (`was`, `wo`, plus pagination via `page`/`size`)
- Loops through **every page** until all results are fetched
- Prints each result's **complete raw JSON** to the terminal
- Saves everything as a single JSON array in `all_jobs_raw.json`

## API

| Purpose | Method & URL |
|---|---|
| Search jobs | `GET https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v6/jobs` |

**Auth:** no OAuth or registration required — every request needs the header:

```
X-API-Key: jobboerse-jobsuche
```

> ⚠️ **Spec vs. live API:** the [`bundesAPI` OpenAPI spec (v2.1.0)](https://github.com/bundesAPI/jobsuche-api) documents results under `stellenangebote`. The **live** `/pc/v6/jobs` endpoint returns them under `ergebnisliste`. The script reads `ergebnisliste` first with a `stellenangebote` fallback, so both work.

## Project structure

```
arbeitsamt-job-finder/
├── app/
│   └── scripts/
│       └── api_demo.py     # fetch-all-pages demo, prints + saves raw JSON
├── docs/
│   └── rest-api-guide.md   # hands-on REST/Python tutorial using this API
└── venv/
```

## Setup

```bash
git clone <your-repo-url>
cd arbeitsamt-job-finder
python -m venv venv && source venv/bin/activate
pip install requests
```

## Usage

```bash
python app/scripts/api_demo.py
```

Example output:

```
Fetching all raw JSON data...

  page 1: fetched 6 jobs (total so far: 6)

Found 6 jobs total.

--- Job 1 ---
{
  "stellenangebotsart": "ARBEIT",
  "stellenangebotsTitel": "Wissenschaftliche*r Mitarbeiter*in ...",
  ...
}

Saved all raw data to all_jobs_raw.json
```

The current demo searches `was="Wissenschaftliche Mitarbeiterin"`, `wo="Leipzig"` — edit those arguments inside `fetch_all_jobs_raw(...)` / `main()` to change the query.

## Notes

- This is an **unofficial** API with no formal SLA from the Bundesagentur für Arbeit — endpoints and parameters may change without notice.
- The `X-API-Key` value is a public constant used by the official app/website, not a personal secret.
- Be a good citizen: cache results where reasonable and avoid hammering the endpoints (`time.sleep()` between pages if you scale this up).

## License

MIT