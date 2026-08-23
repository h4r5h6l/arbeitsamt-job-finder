# AGENTS.md

Logging convention for AI coding agents working in this repo (Claude Code, Codex, Cursor, etc).

Read this file before making changes. Applies to any agent or sub-agent working here.

---

## 1. Log file

Path: `./logs/session.log` (relative to repo root)

- Create the file (and `logs/` dir) if missing.
- Add `logs/` to `.gitignore` — never commit the log.
- Append only. Never rewrite or delete earlier entries.
- Never log secrets — API keys, tokens, credentials get `[REDACTED]`.

## 2. When to log

Append one entry after every user turn where you took an action (edited a file, ran a command, made a decision worth remembering). Skip pure Q&A with no changes.

## 3. Entry format

```text
## [YYYY-MM-DDTHH:MM:SSZ] <short title>

Prompt: <user's request, verbatim, secrets redacted>

Summary: <1-3 sentences — what you did and why>

Changed: <files edited / commands run, comma-separated>

Notes: <anything else worth remembering — a decision, a blocker, a TODO — omit if none>
```

## 4. Example

```text
## [2026-08-22T14:03:11Z] Add job search client

Prompt: build the JobsucheClient with search_jobs and get_job_details

Summary: Added src/jobsuche_client/client.py with search_jobs() and
get_job_details(), wired to the public X-API-Key header per the API docs.

Changed: src/jobsuche_client/client.py, src/jobsuche_client/config.py

Notes: base64-encoding of refnr happens inside get_job_details(), not the caller.
```

## 5. Session start

At the start of a new session, append a short marker before the first real entry:

```text
## [YYYY-MM-DDTHH:MM:SSZ] SESSION START — <agent name>
```