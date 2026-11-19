<div align="center">

# 🛡️🔍 TextQL

### Safe Text-to-SQL with Guardrails

**Ask questions in English. Get SQL that is validated, guarded, and executed read-only — never trusted blindly.**

![Tests](https://github.com/Pratham-Dabhane/Text-To-SQL/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)
![Model](https://img.shields.io/badge/Model-llama3.2%3A3b%20via%20Ollama-orange)

</div>

---

A free-first Text-to-SQL **learning project** built entirely with local tools. It uses a local PostgreSQL database, SQLAlchemy, Ollama, SQLGlot, FastAPI, Streamlit, and pytest.

The core idea is simple: **model output is treated as untrusted input.** Every generated query is cleaned, parsed, validated, row-limited, estimate-checked, and only then executed inside a PostgreSQL read-only transaction against a SELECT-only database role.

> This is a small, local learning project with a fictional dataset — not a production system. The evaluation numbers below are measurements for this dataset and model configuration only, not general accuracy claims.

---

## ✨ What it does

```text
English question
  -> question router (clarify / refuse obvious schema gaps)
  -> schema inspection (SQLAlchemy) + schema-aware prompt
  -> local Llama model via Ollama (llama3.2:3b)
  -> SQL cleaning + SQLGlot validation (one read-only SELECT only)
  -> row-limit + EXPLAIN estimate guardrails
  -> PostgreSQL read-only transaction (SELECT-only role)
  -> results + sanity warnings + saved history & feedback
```

- **Ambiguous questions can return clarification options** instead of a guessed query — e.g. `What is our revenue?` asks whether you mean all orders or delivered orders only.
- **Questions requiring data absent from the schema can be refused** — e.g. questions about profit or cost, which the schema has no data for.
- **If execution fails with a database error,** the app and evaluator make **one bounded repair attempt**, then reapply the normal SQL guardrails.

### Try questions like

| Question | What happens |
|---|---|
| `List customers in Mumbai.` | Generates SQL, executes it, returns 2 rows |
| `What is our revenue?` | Returns a clarification instead of guessing |
| `What is the most expensive product? Return its name and price.` | Generates SQL with ordering + `LIMIT 1` |

---

## 🧱 Tech stack

| Layer | Technology |
|---|---|
| UI | Streamlit (`ui/streamlit_app.py`) |
| API | FastAPI + Uvicorn (`src/text_to_sql/api.py`) |
| Model | Ollama — `llama3.2:3b` by default, temperature `0.0` |
| Database | PostgreSQL 16 |
| DB access | SQLAlchemy 2.x + psycopg 3 |
| SQL validation | SQLGlot |
| History store | SQLite (separate from PostgreSQL) |
| Tests / evaluation | pytest, golden / regression / independent datasets in `eval/` |
| Local stack | Docker Compose — PostgreSQL, API, and Streamlit |

*Exact version ranges are in [`requirements.txt`](requirements.txt). Python 3.11 is used in the `Dockerfile` and CI.*

---

## 🗄️ Learning database

Defined in [`db/schema.sql`](db/schema.sql), seeded by [`db/seed.sql`](db/seed.sql). Each order contains one product in this model.

| Table | Columns |
|---|---|
| `customers` | `customer_id` (PK), `full_name`, `email` (unique), `city`, `created_at` |
| `products` | `product_id` (PK), `product_name` (unique), `category`, `unit_price` |
| `orders` | `order_id` (PK), `customer_id` (FK → customers), `product_id` (FK → products), `quantity`, `ordered_at`, `status` (`pending` / `shipped` / `delivered` / `cancelled`) |

An alternate schema for evaluation lives in `db/alternate_schema.sql` / `db/alternate_seed.sql`: `departments`, `employees`, `projects`, and the `employee_projects` bridge table.

---

## 🚀 Setup

### Prerequisites

- Python 3.11 (for the local, non-Docker route)
- PostgreSQL (for the local route) **or** Docker Desktop (for the Compose route)
- [Ollama](https://ollama.com/) running locally, with `llama3.2:3b` installed

```powershell
ollama serve
ollama list   # confirm llama3.2:3b is present
```

### Option A — Docker Compose (reproducible local stack)

```powershell
docker compose up --build
```

Then open **http://localhost:8501**.

- API: `http://localhost:8000` · Streamlit UI: `http://localhost:8501`
- PostgreSQL is **intentionally not published to Windows**; the API reaches it internally at `postgres:5432`. This avoids conflicts with a local PostgreSQL installation.
- The Docker API reaches Ollama on Windows through `host.docker.internal:11434`. Start Ollama before sending generated-query requests.
- The Compose example uses **development-only passwords; change them before using any shared or public environment.**
- Stop the stack with `docker compose down`.

Quick verification after startup:

```powershell
./scripts/docker_smoke_test.ps1
```

### Option B — Run locally

**1. Install dependencies**

```powershell
python -m pip install -r requirements.txt
```

**2. Create and seed the learning database**

```powershell
psql -U postgres -h localhost -d postgres -c "CREATE DATABASE text_to_sql_learning;"
psql -U postgres -h localhost -d text_to_sql_learning -f db/schema.sql
psql -U postgres -h localhost -d text_to_sql_learning -f db/seed.sql
```

**3. Create the SELECT-only database role**

Follow [`db/readonly_role_setup.md`](db/readonly_role_setup.md) — it runs `db/create_readonly_role.sql` and sets the `text_to_sql_reader` password interactively. No password is stored in the repository.

**4. Set the connection URL** in the PowerShell process that starts the API:

```powershell
$env:DATABASE_URL = "postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/text_to_sql_learning"
```

**5. Start the API and UI** in two terminals:

```powershell
# Terminal 1
uvicorn text_to_sql.api:app --app-dir src --reload
```

```powershell
# Terminal 2
streamlit run ui/streamlit_app.py
```

---

## ⚙️ Configuration

All settings are environment variables, loaded in `src/text_to_sql/settings.py`.

| Variable | Default | Used by | Purpose |
|---|---|---|---|
| `DATABASE_URL` | — (required for queries) | API | PostgreSQL connection for generated queries |
| `HISTORY_DB_PATH` | `data/history.sqlite3` | API | SQLite file for query history & feedback |
| `OLLAMA_URL` | `http://localhost:11434` | API | Base URL of the local Ollama server |
| `API_KEY` | unset | API + Streamlit | Optional shared API key. Leave unset for the local learning setup; Streamlit forwards it automatically when set |
| `RATE_LIMIT_PER_MINUTE` | `60` | API | In-memory, per-client rate limit |
| `API_URL` | `http://localhost:8000` | Streamlit only | Where the UI reaches the API |

API history and feedback are stored in `data/history.sqlite3` by default. This store is **separate** from the PostgreSQL connection used for generated queries, which remains read-only.

---

## 🔌 API endpoints

Defined in `src/text_to_sql/api.py`. All `/v1/` routes go through the API-key and rate-limit middleware.

| Method & path | Description |
|---|---|
| `GET /health` | Returns `{"status": "ok"}` |
| `GET /v1/schema` | Returns inspected tables, columns, primary keys, and foreign keys |
| `POST /v1/query` | Body: `{"question": "..."}` — routes, generates, validates, and executes, or returns a clarification / refusal |
| `GET /v1/history` | Returns saved query history as `{"items": [...]}` |
| `POST /v1/feedback` | Body: `{"query_id": "...", "is_correct": true/false}` — records Correct / Incorrect feedback from the UI |

---

## 📁 Project structure

```text
.
├── db/
│   ├── schema.sql / seed.sql            # Main learning database
│   ├── alternate_schema.sql / alternate_seed.sql
│   ├── create_readonly_role.sql         # SELECT-only role
│   ├── readonly_role_setup.md
│   └── docker-init/                     # Docker DB initialisation
├── docs/
│   ├── demo_checklist.md                # Short end-to-end demo
│   └── portfolio_walkthrough.md         # Interview-ready system explanation
├── eval/                                # Datasets + evaluation utilities
│   ├── golden_questions.json            # 10 cases
│   ├── regression_questions.json        # 40 cases
│   ├── independent_questions.json       # 20 cases
│   ├── second_schema_questions.json     # 10 cases, alternate schema
│   ├── clarification_cases.json         # 3 cases
│   ├── safety_cases.json                # 7 cases
│   ├── evaluator.py / llm_evaluator.py
│   └── alignment.py / complexity.py / multi_query.py
├── exercises/                           # Phase 1 SQL practice + answers
├── scripts/
│   └── docker_smoke_test.ps1
├── src/text_to_sql/
│   ├── api.py                           # FastAPI app + middleware
│   ├── query_pipeline.py                # Route → generate → execute → record
│   ├── question_router.py               # Pre-generation clarify / refuse rules
│   ├── schema.py / schema_prompt.py     # Schema inspection + prompt formatting
│   ├── prompt.py / prompt_examples.py   # Schema-aware prompt + curated examples
│   ├── generation.py                    # Generation, validation, one repair attempt
│   ├── ollama_client.py                 # Local Ollama /api/generate client
│   ├── sql_response.py                  # Strips Markdown fences from model output
│   ├── sql_validation.py                # SQLGlot read-only validation
│   ├── sql_guardrails.py                # Row limit + EXPLAIN estimate check
│   ├── execution.py                     # Read-only transaction execution
│   ├── sanity.py                        # Post-execution result warnings
│   ├── audit.py                         # In-memory audit log for decisions
│   ├── security.py                      # API-key check + rate limiting
│   ├── settings.py                      # Environment-based settings
│   └── history_store.py                 # SQLite history & feedback
├── tests/                               # 31 test files
├── ui/
│   └── streamlit_app.py                 # Streamlit client for the API
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

---

## 🔒 Safety design

Each control covers a different failure mode. Database permissions remain the last line of defence if application validation has a defect.

| Control | Where | What it does |
|---|---|---|
| **Question router** | `question_router.py` | Before generation: refuses profit/cost questions (no such data in the schema) and asks for clarification on ambiguous revenue / “valuable” questions. It is intentionally conservative and domain-specific — a baseline, not a general ambiguity detector |
| **SQL cleaning** | `sql_response.py` | Strips optional Markdown fences from model output; rejects blank output |
| **SQLGlot validation** | `sql_validation.py` | Requires exactly **one** statement; allows only `SELECT` / `UNION` / `INTERSECT` / `EXCEPT` roots; rejects `INSERT`, `UPDATE`, `DELETE`, `CREATE`, `ALTER`, `DROP` anywhere in the tree, plus malformed SQL |
| **Row limit** | `sql_guardrails.py` | Adds / caps a `LIMIT` — `max_rows = 1000` by default in `execution.py` |
| **EXPLAIN estimate check** | `sql_guardrails.py` | Runs `EXPLAIN (FORMAT JSON)` first and rejects queries estimated above `max_estimated_rows = 100_000` by default |
| **Read-only transaction** | `execution.py` | Executes with `SET TRANSACTION READ ONLY` |
| **SELECT-only role** | `db/create_readonly_role.sql` | The generated-query role has `SELECT` permission only |
| **Sanity warnings** | `sanity.py` | Warns (without rejecting results) on empty results or a column that is `NULL` for every returned row |
| **Audit log** | `audit.py` | Blocked and allowed decisions **can be recorded** in the in-memory audit log |
| **API protection** | `security.py`, `api.py` | Optional shared `X-API-Key` check (`401` on mismatch) and in-memory per-client rate limit (`429` when exceeded) |

---

## 🧪 Tests and evaluation

```powershell
python -m pytest -q
```

The project includes database tests, SQL safety tests, golden cases, regression cases, independent cases, ambiguity cases, and mocked local-model tests.

> The latest local run passed **67 tests**, including PostgreSQL integration tests when `DATABASE_URL` was configured. Runs without database configuration skip only those integration checks.
> — *as recorded in the previous README; this is a local run result, not a CI guarantee.*

### Evaluation datasets

| Dataset | Cases | Purpose |
|---|---:|---|
| Golden (`eval/golden_questions.json`) | 10 | Verify the evaluation pipeline |
| Regression (`eval/regression_questions.json`) | 40 | Prompt-tuned cases that check known failure patterns from returning |
| Independent (`eval/independent_questions.json`) | 20 | Reserved for measuring model behaviour — its questions are **not** added to the prompt |
| Second schema (`eval/second_schema_questions.json`) | 10 | Alternate departments / employees / projects database |
| Clarification (`eval/clarification_cases.json`) | 3 | Expected clarify / refuse behaviour |
| Safety (`eval/safety_cases.json`) | 7 | SQL that must be rejected, e.g. `DELETE FROM customers` |

### Measured results — `llama3.2:3b`, this local dataset only

| Measurement | Result |
|---|---|
| Regression suite | **40/40 on each of three runs** — *not* an independent accuracy claim, because the prompt was tuned using these cases |
| Independent set | **20/20 on each of three runs** |
| Second schema — deterministic reference queries | **10/10** |
| Second schema — local Llama model | **7/10 on each of three runs** — measures limited generalisation to an unfamiliar schema, not global accuracy |

Evaluation utilities in `eval/` also include alignment judgments (`alignment.py`), a complexity heuristic (`complexity.py`), and multi-query result comparison (`multi_query.py`). **LLM alignment judgments are review signals only — not probabilities or proof of correctness.** Execution against expected data is the correctness evidence used here.

---

## ⚠️ Known limitations

- The test database is intentionally **small and fictional**; results do not establish general model accuracy.
- The project uses a **shared API-key check** and an **in-memory, per-client rate limit** — it does not provide user accounts, durable distributed rate limiting, or coordination across replicas.
- It does not provide a broader multi-schema evaluation suite; the alternate-schema check is a single, limited generalisation test.
- LLM alignment judgments are review signals and are **not** probabilities or proof of correctness.

---

## 📚 Further reading

- [`docs/demo_checklist.md`](docs/demo_checklist.md) — short end-to-end demo: start the stack, ask `List customers in Mumbai.`, ask `What is our revenue?`, give feedback, inspect `/v1/history`
- [`docs/portfolio_walkthrough.md`](docs/portfolio_walkthrough.md) — interview-ready explanation of the problem, architecture, safety controls, and evaluation evidence
- [`exercises/phase1_queries.md`](exercises/phase1_queries.md) — Phase 1 SQL practice questions for the learning schema, with answers in `exercises/phase1_answers.sql`
