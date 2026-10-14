# SthiraTech — VotePack

A group-travel planning application prototype for trips, itinerary activities, polls, and shared expenses.

## What it does

The repository contains a React/TypeScript frontend and a FastAPI backend with:

- Account registration and login using JWTs and bcrypt password hashing.
- Trips, participants, itinerary days, activities, polls, votes, and expense balances.
- Gemini-backed embeddings and recommendation/consensus code.
- Stripe Connect onboarding, commitment deposits, and payment webhooks.
- Optional Redis caching, Brevo email, and Sentry monitoring.

External integrations need your own provider accounts and configuration. They may incur charges. Their availability and a complete hosted workflow are not established by the repository alone.

## Local setup

The CI files use Python 3.10 and Node.js 20. You also need PostgreSQL with pgvector and permission to create the `vector` extension. Supabase is an optional hosted PostgreSQL provider; a local database definition is included.

```bash
git clone https://github.com/wtfashwin/SthiraTech-The-VotePack-Platform.git
cd SthiraTech-The-VotePack-Platform
python -m venv .venv
source .venv/bin/activate
python -m pip install -r packages/api/requirements.txt
```

On Windows, activate the environment with `.venv\Scripts\activate` instead. `ai_service.py` directly imports NumPy but the requirements file does not list it explicitly; ensure it is installed in the environment and record a compatible version when completing setup.

For the included local database:

```bash
docker compose -f packages/docker-compose.yml up -d db
```

It exposes PostgreSQL on port `5433`. Use the database name and local credentials defined in that file. Alternatively, supply your own PostgreSQL/pgvector connection.

Create `.env` at the repository root for the root-level startup command below:

```env
DATABASE_URL=postgresql://<user>:<password>@localhost:5433/packvote
SECRET_KEY=<a-random-secret-at-least-32-characters-long>
FRONTEND_URL=http://localhost:5173
```

Replace the placeholders. Optional settings are `GEMINI_API_KEY`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `REDIS_URL`, `BREVO_API_KEY`, and `SENTRY_DSN`.

From the repository root, start the API:

```bash
uvicorn packages.api.main:app --reload --port 8000
```

This package-qualified entry point matches the backend’s relative imports. Startup creates ORM tables and initializes caching. API documentation is at `http://localhost:8000/docs`.

In another terminal:

```bash
cd packages/web
npm ci
npm run dev
```

Open `http://localhost:5173`. The frontend API URLs currently point directly to `http://localhost:8000/api/v1` in `src/api/apiClient.ts`; setting `VITE_API_BASE_URL` does not change them.

## Usage and source guide

For local exploration, register an account, create a trip, add participants and itinerary activities, then inspect poll and expense flows. Use Stripe test configuration when exploring payment code.

- `packages/api/main.py` — application setup and router registration.
- `packages/api/routers/` — authentication, trips, itinerary, polls, expenses, AI, and payments.
- `packages/api/models.py` and `crud.py` — data models and database operations.
- `packages/api/config.py` — environment settings.
- `packages/web/src/` — pages, components, API client, and state stores.
- `packages/api/tests/` — backend tests.
- `scripts/` — host-specific startup scripts.

## Available checks and limitations

From `packages/web`, `npm run lint` and `npm run build` are defined; no frontend test script is present. Backend CI uses `pytest tests/ -v --cov=. --cov-report=term-missing --cov-report=xml` from `packages/api`, with pytest, pytest-cov, pytest-asyncio, and httpx installed separately.

Backend tests need repair: `tests/conftest.py` imports `Base` from `database.py`, while it is defined in `models.py`. The initial Alembic revision adds indexes to existing tables, so it is not a standalone schema bootstrap. The startup scripts contain host-specific paths and database-host assumptions. `config.py` prints the database connection string; remove that logging before using shared logs.

## License

The original README states: “Do whatever you want with it.” No standalone license file is included; that wording is retained here without choosing a new license.
