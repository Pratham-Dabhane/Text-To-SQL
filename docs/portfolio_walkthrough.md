# Portfolio walkthrough

## Problem

Text-to-SQL systems translate English into database queries. A generated query
can be wrong, unsafe, or expensive, so this project treats model output as
untrusted input.

## Architecture

```text
Streamlit UI -> FastAPI -> prompt with inspected schema -> Ollama
                         -> SQLGlot validation -> query guardrails
                         -> PostgreSQL SELECT-only role -> results
```

Docker Compose runs Streamlit, FastAPI, and PostgreSQL. Ollama stays local on
the Windows host and is reached from the API container through
`host.docker.internal`.

## Safety controls

- SQLGlot accepts one read-only `SELECT` statement and rejects DDL/DML.
- A row limit is added to generated queries.
- PostgreSQL `EXPLAIN` estimates are checked before execution.
- Queries run inside read-only transactions.
- The generated-query role has `SELECT` permission only.
- Optional API-key checks and per-client rate limiting protect the API.

Each control covers a different failure mode. Database permissions remain the
last line of defense if application validation has a defect.

## Evaluation evidence

The project has 10 golden cases and 20 holdout cases. Golden cases help verify
the evaluation pipeline. Holdout cases test questions outside the initial
manual SQL exercises.

The latest measured holdout result was 20/20 on each of three runs with the
local `llama3.2:3b` configuration. This is a small, fixed dataset result. It
does not establish general model accuracy or a confidence probability.

## Demo flow

1. Start Ollama and `docker compose up -d --build`.
2. Run `./scripts/docker_smoke_test.ps1`.
3. Show a normal query such as `List customers in Mumbai.`
4. Show an ambiguous question such as `What is our revenue?`
5. Show the generated SQL, results, feedback, and query history.
6. Explain that destructive SQL is rejected and the database role is read-only.
7. Show the evaluation command and its recorded results.

## Current limits

- The test database is intentionally small and fictional.
- The API key is shared, rather than a full user identity system.
- Rate limiting is stored in API memory and does not coordinate across replicas.
- The evaluation suite needs 50+ cases and broader schemas for stronger evidence.
- Alignment judgments are review signals only; execution against expected data is
  the actual correctness evidence used here.
