# Contributing

Thanks for contributing. Quick guide:

- Fork the repo and create feature branches from `main`.
- Run unit tests and lint before opening a PR.
- E2E tests run on Pull Requests (Playwright). Keep PRs small and focused.
- If your change requires heavy ML deps, add a note and use the `ML Optional` workflow to validate.

Local checks:

```bash
# backend
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements-base.txt
pytest -q

# frontend
cd frontend
npm ci
npx playwright install
npx playwright test
```
