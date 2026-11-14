# Demo checklist

1. Start Ollama with `ollama serve`.
2. Start Docker with `docker compose up -d --build`.
3. Confirm `docker compose ps` reports PostgreSQL and API as healthy.
4. Run `./scripts/docker_smoke_test.ps1` in PowerShell.
5. Open `http://localhost:8501`.
6. Ask `List customers in Mumbai.` and verify two rows are returned.
7. Ask `What is our revenue?` and verify a clarification is returned.
8. Mark a completed query Correct or Incorrect, then inspect `/v1/history`.
9. Run `python -m pytest -q` with `DATABASE_URL` set to include database tests.
10. Run the repeated independent evaluation and report its mean, minimum, and maximum.

The current repeated independent measurement is 20/20 for three runs on this
small local dataset. It is evidence for this configuration, not a general
accuracy claim.
