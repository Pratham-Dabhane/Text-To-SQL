# Safe Text-to-SQL

A free-first Text-to-SQL learning project. It uses a local PostgreSQL database,
SQLAlchemy, Ollama, SQLGlot, FastAPI, Streamlit, and pytest.

## What it does

```text
English question
  -> schema-aware prompt
  -> local Llama model
  -> SQL cleaning and SQLGlot validation
  -> row and EXPLAIN guardrails
  -> PostgreSQL read-only transaction
  -> results, sanity warnings, and history
```

Ambiguous questions can return clarification options. Questions requiring data
that is absent from the schema can be refused.

## Setup

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Create and seed the learning database:

```powershell
psql -U postgres -h localhost -d postgres -c "CREATE DATABASE text_to_sql_learning;"
psql -U postgres -h localhost -d text_to_sql_learning -f db/schema.sql
psql -U postgres -h localhost -d text_to_sql_learning -f db/seed.sql
```

Set the connection URL in the PowerShell process that starts the API:

```powershell
$env:DATABASE_URL = "postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/text_to_sql_learning"
```

Start Ollama and ensure `llama3.2:3b` is installed:

```powershell
ollama serve
ollama list
```

Create the SELECT-only database role using [db/readonly_role_setup.md](db/readonly_role_setup.md).

## Run the application

For a reproducible local stack, install Docker Desktop and run:

```powershell
docker compose up --build
```

Then open `http://localhost:8501`. The compose example uses development-only
passwords; change them before using any shared or public environment. To stop
the stack, run `docker compose down`.

PostgreSQL is intentionally not published to Windows; the API reaches it
internally at `postgres:5432`. This avoids conflicts with a local PostgreSQL
installation.

The Docker API reaches Ollama on Windows through
`host.docker.internal:11434`. Start Ollama before sending generated-query
requests.

Optional API protection can be enabled with `API_KEY` and
`RATE_LIMIT_PER_MINUTE` environment variables. Streamlit forwards `API_KEY`
automatically. Leave `API_KEY` unset for the local learning setup.

To run a quick Docker verification after startup:

```powershell
./scripts/docker_smoke_test.ps1
```

Terminal 1:

```powershell
uvicorn text_to_sql.api:app --app-dir src --reload
```

Terminal 2:

```powershell
streamlit run ui/streamlit_app.py
```

The API is at `http://localhost:8000`; the Streamlit UI is normally at
`http://localhost:8501`.

## Tests and evaluation

```powershell
python -m pytest -q
```

The project includes database tests, SQL safety tests, golden execution cases,
holdout cases, ambiguity cases, and mocked local-model tests.

The project has 10 golden cases, 40 prompt-tuned regression cases, and 20
independent cases. The regression suite checks known failure patterns. The
independent set is reserved for measuring model behavior without adding its
questions to the prompt. The independent set measured 20/20 on each of three
runs with `llama3.2:3b`. These are
measurements for this small local dataset and model configuration, not general
production accuracy claims.

API history and feedback are stored in `data/history.sqlite3` by default. Set
`HISTORY_DB_PATH` to choose another local path. This store is separate from the
PostgreSQL connection used for generated queries, which remains read-only.

## Safety design

- SQLGlot rejects malformed, multi-statement, DDL, and DML SQL.
- Generated queries receive a configurable row limit.
- PostgreSQL `EXPLAIN` estimates are checked before execution.
- Queries run in read-only transactions.
- The database role has SELECT permission only.
- Blocked and allowed decisions can be recorded in the audit log.

## Known limitations

The project uses a shared API-key check and in-memory per-client rate limit;
it does not provide user accounts, durable distributed rate limiting, or a
broader multi-schema evaluation suite. LLM alignment judgments are review
signals and are not probabilities or proof of correctness.

See [docs/demo_checklist.md](docs/demo_checklist.md) for a short end-to-end demo.
See [docs/portfolio_walkthrough.md](docs/portfolio_walkthrough.md) for an
interview-ready explanation of the system.
