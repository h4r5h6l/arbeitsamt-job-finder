import json

import requests

BASE = "https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v6/jobs"
HEADERS = {"X-API-Key": "jobboerse-jobsuche"}
OUTPUT_FILE = "all_jobs_raw.json"


def fetch_all_jobs_raw(was: str, wo: str = "", size: int = 100) -> list[dict]:
    """Paginate through every page and return ALL jobs as their raw JSON dicts."""
    all_jobs: list[dict] = []
    page = 1
    while True:
        params = {"was": was, "wo": wo, "size": size, "page": page}
        response = requests.get(BASE, headers=HEADERS, params=params)
        response.raise_for_status()
        data = response.json()
        batch = data.get("ergebnisliste") or data.get("stellenangebote") or []
        if not batch:
            break
        all_jobs.extend(batch)
        print(f"  page {page}: fetched {len(batch)} jobs (total so far: {len(all_jobs)})")
        if len(batch) < size:
            break
        page += 1
    return all_jobs


def main():
    print("Fetching all raw JSON data...\n")
    jobs = fetch_all_jobs_raw(was="Wissenschaftliche Mitarbeiterin", wo="Leipzig")
    print(f"\nFound {len(jobs)} jobs total.\n")

    # Print the complete raw JSON of every job
    for i, job in enumerate(jobs, start=1):
        print(f"--- Job {i} ---")
        print(json.dumps(job, ensure_ascii=False, indent=2))

    # Also save everything to a single JSON file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)
    print(f"\nSaved all raw data to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
