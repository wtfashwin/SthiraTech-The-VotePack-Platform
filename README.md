# SthiraTech — VotePack

VotePack helps groups plan trips, compare itinerary ideas, vote on activities, and track shared expenses.

The repository is an application prototype. It includes a React/TypeScript frontend, a FastAPI backend, and PostgreSQL models with pgvector support. Payment collection in the frontend is still a placeholder; provider integrations and hosted operation need separate verification.

## Capabilities

- Register and log in with JWT authentication and bcrypt password hashing.
- Create trips with dates and a destination, add participants and itinerary activities, and record polls and expenses.
- Generate recommendation embeddings and consensus proposals through optional Gemini configuration.
- Handle Stripe Connect onboarding, commitment deposit intents, and webhooks in the backend.
- Optionally use Redis caching, Brevo email, and Sentry monitoring.

## How it works

The browser sends requests to FastAPI under `/api/v1`. Routers validate input, apply authentication where defined, and use SQLAlchemy to read or write PostgreSQL. The application creates ORM tables on startup. Optional services are configured through backend environment settings; they need your own accounts and may incur charges.

## Getting started

The check workflows use Python 3.10 and Node.js 20. You also need npm and PostgreSQL with pgvector. Docker can provide the included local database; Supabase is an optional hosted alternative.

From a new terminal:

```bash
git clone https://github.com/wtfashwin/SthiraTech-The-VotePack-Platform.git
cd SthiraTech-The-VotePack-Platform
python -m venv .venv
source .venv/bin/activate
python -m pip install -r packages/api/requirements.txt
docker compose -f packages/docker-compose.yml up -d db
```

On Windows, activate `.venv\Scripts\activate` instead. The included database uses host port `5433`; its database name and local credentials are in `packages/docker-compose.yml`.

Create `.env` at the repository root, replacing the placeholders, and keep it out of Git:

```env
DATABASE_URL=postgresql://<user>:<password>@localhost:5433/packvote
SECRET_KEY=<a-random-secret-at-least-32-characters-long>
FRONTEND_URL=http://localhost:5173
```

The database user needs permission to create the `vector` extension. Optional settings are `GEMINI_API_KEY`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `REDIS_URL`, `BREVO_API_KEY`, and `SENTRY_DSN`.

Start the API from the repository root with the virtual environment active:

```bash
uvicorn packages.api.main:app --reload --port 8000
```

In another terminal, starting at the repository root:

```bash
cd packages/web
npm ci
npm run dev
```

Open `http://localhost:5173`. For a first check, register an account, create a trip, and inspect it through `http://localhost:8000/docs`. The `/` API response is a liveness check; it does not verify external integrations.

## Checks

Pull requests and pushes to `main` or `develop` run checks when the relevant application or workflow files change. Documentation edits do not trigger deployment. Validation does not use production credentials.

Backend tests need an explicitly configured disposable PostgreSQL/pgvector database. For example, from the repository root:

```bash
docker run --rm -d --name votepack-test-db \
  -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=votepack_test -p 127.0.0.1:5434:5432 pgvector/pgvector:pg16
docker exec votepack-test-db pg_isready -U postgres
```

Wait until `pg_isready` reports that connections are accepted, then run with the virtual environment active:

```bash
export TEST_DATABASE_URL=postgresql://postgres:postgres@127.0.0.1:5434/votepack_test
python -m pip install -r packages/api/requirements-dev.txt
ruff check packages/api --select E,F,W,I --ignore E501
mypy packages/api --ignore-missing-imports
python -m pytest packages/api/tests -v --cov=packages/api --cov-report=term-missing
python -m unittest discover -s scripts/tests -v
```

API tests use an explicitly mapped disposable schema per test and disable optional providers. The isolation regression creates and removes its own database to prove that existing public tables stay untouched, so the test role needs permission to create databases. Deployment-helper tests replace the HTTP boundary and send no provider requests. Stop the example test database with `docker stop votepack-test-db` when finished.

From `packages/web`:

```bash
npm run lint
npm run typecheck
npm test
npm run build
```

Frontend tests render authentication controls and the loading button. They do not cover a complete browser journey. The build writes `packages/web/dist/`.

Backend CI also runs Bandit over application code and `pip-audit` over the installed environment. Dependency advisories remain unresolved; the security job reports failures instead of swallowing them. These commands are available locally:

```bash
bandit -r packages/api --exclude packages/api/tests
pip-audit --progress-spinner off
```

## Manual deployment

The **Request Render deployment** workflow runs only through **Actions → Run workflow**. Select `main` after reviewing its validation results. Configure the repository Actions secret `RENDER_DEPLOY_HOOK_URL` with the actual service hook from Render settings before running it.

Missing or malformed hook configuration fails before any request. The helper sends one bounded POST and fails on HTTP errors. An accepted hook means Render started or queued a deployment; inspect the service’s deployment status before claiming it is live. [Render deploy-hook documentation](https://render.com/docs/deploy-hooks).

Frontend hosting is configured separately. CI produces a build artifact; it does not claim a Vercel deployment.

## Project layout

- `packages/api/` — settings, models, database operations, routers, and tests.
- `packages/web/` — frontend pages, components, API client, and rendering tests.
- `packages/docker-compose.yml` — local PostgreSQL/pgvector service.
- `scripts/request_render_deploy.sh` — manual Render request guard.
- `.github/workflows/` — backend/frontend validation and manual deployment.

## Known limits and contributions

Frontend API URLs currently point to `localhost:8000`; `VITE_API_BASE_URL` is not consumed. The first Alembic revision adds indexes to existing tables and is not a fresh-schema bootstrap. The older host startup scripts contain Render-specific paths and database-host assumptions. Dependency advisories and broader provider/browser integration work remain open.

For a change, describe the user-visible problem, keep the diff focused, run the relevant checks above, and include their results. Keep credentials and private data out of code, logs, issues, and pull requests. Use Stripe test configuration when working on payment behavior.

## Manual deployment

Use **Actions → Request Render deployment → Run workflow** on `main` to request a backend deployment. The repository needs the real service hook configured as the `RENDER_DEPLOY_HOOK_URL` Actions secret. Missing or malformed configuration fails before any request.

The helper reports whether Render accepted the request; check Render's service status to confirm the deployment completed. The workflow does not deploy the frontend. Its five guard tests run without provider requests:

```bash
python -m unittest discover -s scripts/tests -v
```

## License

The original README states: “Do whatever you want with it.” No standalone license file is included; that wording is retained without choosing a new license.
