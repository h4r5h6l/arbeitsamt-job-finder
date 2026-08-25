# REST API Consumption in Python — A Hands-On Guide

Learn how to call a real HTTP API from Python, parse the JSON it returns, and print
results to your terminal. We'll use the **Bundesagentur für Arbeit Jobsuche API**
(the one documented in [`bundesAPI/jobsuche-api`](https://github.com/bundesAPI/jobsuche-api))
as our live subject, because it needs no registration or OAuth — just one public header.

Every section has a matching runnable script in `app/scripts/` (currently
`api_demo.py`, which puts it all together). Run it, read its output, then read the
source — that's the fastest way to learn this.

---

## 0. Setup

```bash
cd arbeitsamt-job-finder
source venv/bin/activate        # or: python3 -m venv venv && source venv/bin/activate
pip install requests
```

`requests` is *the* de-facto standard HTTP library for Python. Everything below uses it.
(Section 9 shows the same thing with only the standard library, so you know what
`requests` is doing for you.)

---

## 1. HTTP in 60 seconds

A REST API is just a set of URLs you talk to over HTTP. Each interaction is:

```
REQUEST                                RESPONSE
─────────────────────────────          ─────────────────────────────
GET /pc/v6/jobs?wo=Berlin HTTP/1.1     HTTP/1.1 200 OK
Host: rest.arbeitsagentur.de           Content-Type: application/json
X-API-Key: jobboerse-jobsuche
                                       {"ergebnisliste": [...], ...}
```

The four things you must understand:

| Concept | What it is | In our API |
|---|---|---|
| **Method** | What you want to do | `GET` = read data (we only need GET here) |
| **URL + query string** | Which resource | `/pc/v6/jobs?was=python&wo=Berlin` |
| **Headers** | Metadata about the request | `X-API-Key: jobboerse-jobsuche` (auth) |
| **Status code** | Outcome of the request | `200` ok · `404` not found · `429` too many requests |

The response body is usually **JSON** — a text format that maps directly onto Python
dicts/lists once parsed.

### This API's three endpoints

| Purpose | Method & URL |
|---|---|
| Search jobs | `GET https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v6/jobs` |
| Job details | `GET .../pc/v4/jobdetails/{base64(refnr)}` |
| Employer logo | `GET https://rest.arbeitsagentur.de/vermittlung/ag-darstellung-service/ct/v1/arbeitgeberlogo/{hash}` |

Every request needs the auth header:

```
X-API-Key: jobboerse-jobsuche
```

This is a *public constant* baked into the official app — there's no signup. But note
the pattern, because most APIs you'll use later work the same way, just with a secret key.

---

## 2. Your first GET → terminal


The minimal program: build the URL, send the request, inspect what came back.

```python
import requests

url = "https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v6/jobs"
headers = {"X-API-Key": "jobboerse-jobsuche"}

resp = requests.get(url, headers=headers, timeout=15)

print(resp.status_code)      # 200 means "OK"
print(resp.headers["Content-Type"])
print(resp.text[:500])       # raw body — first 500 chars
```

Key points:

- `requests.get(...)` sends a GET request and returns a `Response` object.
- **Always pass `timeout=`.** Without it, a hanging server hangs your program forever.
- `resp.status_code` — check this before trusting the body.
- `resp.text` is the raw body as a string; useful for a first look.

Run it:

```bash
python app/scripts/api_demo.py
```

---

## 3. Query parameters — done right


Query strings like `?was=python&wo=Berlin&size=5` filter results. Don't paste them into
the URL by hand — special characters (`&`, spaces, umlauts) would break it. Let
`requests` encode them via the `params=` argument:

```python
params = {
    "was": "Python",        # free-text job title search
    "wo": "Berlin",         # location
    "umkreis": 50,          # radius around `wo` in km
    "size": 5,              # results per page
    "page": 1,
}
resp = requests.get(url, headers=headers, params=params, timeout=15)
print(resp.url)             # see the final URL requests built
```

`requests` turns that dict into `...?was=Python&wo=Berlin&umkreis=50&size=5&page=1`,
percent-encoding anything unsafe automatically.

Useful filters from the [API docs](https://github.com/bundesAPI/jobsuche-api#filter):

| Param | Meaning | Example values |
|---|---|---|
| `was` | job title free text | `"Softwareentwickler"` |
| `wo` | location free text | `"Leipzig"` |
| `umkreis` | radius around `wo`, km | `25`, `200` |
| `arbeitszeit` | work time; semicolon-separated | `vz` full-time, `tz` part-time, `ho` home office, `mj` minijob |
| `angebotsart` | 1=job, 2=self-employed, 4=apprenticeship, 34=internship | `1` |
| `veroeffentlichtseit` | published within N days (0–100) | `30` |
| `zeitarbeit` / `pav` | include temp agency / private placement jobs | `false` |
| `page`, `size` | pagination | `2`, `25` |

---

## 4. Parsing JSON → formatted terminal output


Raw JSON is hard to read. Two steps fix that:

```python
data = resp.json()           # JSON text -> Python dict/list (raises if body isn't JSON)
```

Now `data` is an ordinary Python object. The live search endpoint wraps results in
`ergebnisliste`; each entry looks roughly like:

```jsonc
{
  "stellenangebotsTitel": "Programmierung mit Python",
  "firma": "alfatraining Bildungszentrum GmbH",
  "referenznummer": "10000-1183300826-S",     // ← you need this for step 5!
  "eintrittszeitraum": {"von": "2026-08-31"},
  "stellenlokationen": [{"adresse": {"ort": "Berlin", "plz": "10247"}}],
  "arbeitszeitVollzeit": true,
  "homeofficemoeglich": true,
  "entfernung": 3
}
```

Turn that into human-friendly output with f-strings:

```python
for i, job in enumerate(data.get("ergebnisliste", []), start=1):
    titel = job.get("stellenangebotsTitel", "?")
    firma = job.get("firma", "?")
    ort   = job["stellenlokationen"][0]["adresse"]["ort"] if job.get("stellenlokationen") else "?"
    print(f"{i:>2}. {titel} @ {firma} ({ort})")

total = data.get("maxErgebnisse", "?")
print(f"\n{total} total hits")
```

Tips for robust parsing:

- Use `.get("key", default)` instead of `["key"]` when a field might be missing —
  APIs change, and a `None` beats a crash mid-loop.
- For quick debugging, pretty-print the whole payload:
  `print(json.dumps(data, indent=2, ensure_ascii=False))`.
- ⚠️ **Spec drift gotcha:** the official OpenAPI spec calls these fields
  `stellenangebote`/`refnr`/`titel`, but the live v6 endpoint returns
  `ergebnisliste`/`referenznummer`/`stellenangebotsTitel`/`firma`. When a documented
  field seems missing, print the raw JSON and look at reality.

---

## 5. The real flow: search → details (base64!)


Real APIs are rarely one request. Here the workflow is two steps chained together:

1. Search → grab a job's `referenznummer` (a.k.a. `refnr`), e.g. `10001-1002716922-S`.
2. Details endpoint wants that refnr **base64-encoded** in the URL path:
   `10001-1002716922-S` → `MTAwMDEtMTAwMjcxNjkyMi1T`.

```python
import base64

refnr = "10000-1183300826-S"
encoded = base64.b64encode(refnr.encode()).decode()

detail_url = f"https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v4/jobdetails/{encoded}"
resp = requests.get(detail_url, headers=headers, timeout=15)
resp.raise_for_status()

d = resp.json()
print(d["stellenangebotsTitel"])
print(d["firma"])
print(d["stellenangebotsBeschreibung"][:800])
```

Lessons hiding in this example:

- **Chaining requests:** output of one call (refnr) becomes input of the next (path param).
- **Encoding data for transport:** base64 isn't encryption — just a way to put an
  arbitrary string safely inside a URL path.
- Path parameters go *in the URL*; filters go in *query params*. Different tools:
  f-string vs `params=`.

---

## 6. Error handling — expect failure


Network code fails in predictable ways. Handle them explicitly:

| Failure | Example cause | Defense |
|---|---|---|
| Connection error | offline, DNS broken | catch `requests.exceptions.ConnectionError` |
| Timeout | slow server | `timeout=` + catch `Timeout` |
| HTTP error status | `404`, `429`, `500` | `resp.raise_for_status()` + catch `HTTPError` |
| Bad JSON | HTML error page instead of JSON | `.json()` raises `JSONDecodeError` |

The idiomatic wrapper:

```python
try:
    resp = requests.get(url, headers=headers, params=params, timeout=15)
    resp.raise_for_status()                 # turns 4xx/5xx into exceptions
    data = resp.json()
except requests.exceptions.Timeout:
    print("Server too slow — try again later.")
except requests.exceptions.HTTPError as e:
    print(f"API said no: {e}")              # e.g. 429 = rate limited
except requests.exceptions.RequestException as e:
    print(f"Network problem: {e}")          # parent class of all requests errors
else:
    print("Success:", len(data.get("ergebnisliste", [])), "jobs")
```

`RequestException` is the base class of everything `requests` raises — catching it last
is your safety net.

---

## 7. Pagination — fetching many pages

Search results are paginated (`page`, `size`). Loop until fewer than `size` results
come back:

```python
page = 1
while True:
    resp = requests.get(url, headers=headers,
                        params={"was": "Entwickler", "page": page, "size": 50},
                        timeout=15)
    resp.raise_for_status()
    hits = resp.json().get("ergebnisliste", [])
    if len(hits) < 50:            # short page = last page
        break
    page += 1                     # next iteration
```

Be polite: add `time.sleep(1)` between pages. Public APIs rate-limit aggressive clients
(you'd see HTTP `429 Too Many Requests`).

---

## 8. Quick reference

| Task | Code |
|---|---|
| Simple GET | `requests.get(url, timeout=10)` |
| Query params | `requests.get(url, params={"wo": "Berlin"}, timeout=10)` |
| Auth header | `headers={"X-API-Key": "jobboerse-jobsuche"}` |
| Status code | `resp.status_code` |
| Body as text | `resp.text` |
| Body as JSON | `resp.json()` |
| Throw on 4xx/5xx | `resp.raise_for_status()` |
| Final URL built | `resp.url` |
| Response headers | `resp.headers` |
| Base64-encode a string | `base64.b64encode(s.encode()).decode()` |

---

## 9. Bonus: same thing with zero libraries (`urllib`)

`requests` is convenience, not magic. This stdlib version of script 01 does the same job:

```python
import json
from urllib.request import Request, urlopen

req = Request(
    "https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v6/jobs?wo=Berlin&size=2",
    headers={"X-API-Key": "jobboerse-jobsuche"},
)
with urlopen(req, timeout=15) as r:          # raises HTTPError on 4xx/5xx
    data = json.load(r)                       # parses body straight into Python objects

print(len(data["ergebnisliste"]), "jobs")
```

Notice how much `requests` absorbs: automatic percent-encoding, `.status_code`
inspection before reading, friendlier exceptions, `timeout` on every call. Now you
understand both layers.

---

## 10. Where to go next in this repo

Once the fundamentals click, look at the working example in this project:
`app/scripts/api_demo.py`. It combines everything above into one script — it
paginates through **all** pages of a search, prints each result's complete raw
JSON with `json.dumps(..., indent=2)`, and saves the whole collection to
`all_jobs_raw.json` with `json.dump()`:

```python
all_jobs = []
page = 1
while True:
    resp = requests.get(BASE, headers=HEADERS,
                        params={"was": "...", "wo": "Leipzig", "size": 100, "page": page},
                        timeout=15)
    resp.raise_for_status()
    batch = resp.json().get("ergebnisliste") or []
    if not batch:
        break
    all_jobs.extend(batch)
    if len(batch) < 100:
        break
    page += 1

with open("all_jobs_raw.json", "w", encoding="utf-8") as f:
    json.dump(all_jobs, f, ensure_ascii=False, indent=2)
```

Run it yourself:

```bash
python app/scripts/api_demo.py
```

Also worth knowing beyond `requests`: [`httpx`](https://www.python-httpx.org/) (modern,
async-capable, near-identical API) and session reuse (`requests.Session()`) when making
many calls to the same host.
