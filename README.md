# AI Tutor Beta

AI Tutor Beta is a local-first study-planning prototype for the CUET General Test section. The project is designed to validate a deterministic feedback loop that prioritizes weak concepts, respects prerequisites, and surfaces review-heavy study paths based on learner state.

This repository is currently structured around:
- a FastAPI backend
- a PostgreSQL database for learner state and concept metadata
- a data-seeding pipeline for curated content
- a placeholder frontend structure for the future web app

## Project status

The backend and database foundation are in place, but the app is still under active development. The current web app directory is a placeholder and the backend API is the main runtime surface to work on.

## Prerequisites

Before starting, make sure you have:
- Python 3.11+
- Docker Desktop or Docker Engine with Docker Compose
- Git
- Optional: psql client for direct PostgreSQL checks

## Repository structure

```text
.
├── apps/
│   ├── backend/
│   │   ├── app/
│   │   │   ├── api/
│   │   │   ├── core/
│   │   │   ├── db/
│   │   │   ├── models/
│   │   │   └── services/
│   │   ├── main.py
│   │   └── requirements.txt
│   └── web/
│       └── README.md
├── pipelines/
│   └── content_seeding/
├── scripts/
│   └── seed_postgres.sql
├── docker-compose.yml
├── README.md
└── .gitignore
```

## Local environment setup

### 1) Start PostgreSQL

From the project root:

```bash
docker compose up -d
```

This starts a local PostgreSQL instance using the config in [docker-compose.yml](docker-compose.yml).

Default local connection values:
- Host: localhost
- Port: 5432
- User: aitutor_user
- Password: aitutor_secure_pass
- Database: aitutor_beta_state

## Backend setup

### 2) Create and activate a virtual environment

```bash
cd apps/backend
python -m venv .venv
```

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

### 3) Install Python dependencies

```bash
pip install -r requirements.txt
```

The backend dependencies currently include FastAPI, Uvicorn, psycopg, Pydantic, and python-dotenv as defined in [apps/backend/requirements.txt](apps/backend/requirements.txt).

### 4) Run the API

From [apps/backend](apps/backend):

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

You should then be able to access:
- API root: http://localhost:8000
- Health check: http://localhost:8000/health

The health endpoint is defined in [apps/backend/main.py](apps/backend/main.py).

## Environment variables

The app loads settings from an environment file via [apps/backend/app/core/config.py](apps/backend/app/core/config.py). If you want to override defaults, create a `.env` file in [apps/backend](apps/backend) with values like:

```env
POSTGRES_USER=aitutor_user
POSTGRES_PASSWORD=aitutor_secure_pass
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=aitutor_beta_state
```

## Database initialization and seeding

The project includes a bootstrap SQL file at [scripts/seed_postgres.sql](scripts/seed_postgres.sql). This creates the base tables and seeds example concepts and resources.

To apply it locally:

```bash
docker exec -i aitutor_beta_postgres psql -U aitutor_user -d aitutor_beta_state < scripts/seed_postgres.sql
```

If the database is not yet up, start it first with `docker compose up -d`.

## Backend architecture

Some of the main backend modules are:
- [apps/backend/main.py](apps/backend/main.py): application entrypoint
- [apps/backend/app/api](apps/backend/app/api): route modules such as plan and quiz endpoints
- [apps/backend/app/core/config.py](apps/backend/app/core/config.py): configuration and environment settings
- [apps/backend/app/db/postgres.py](apps/backend/app/db/postgres.py): PostgreSQL connection factory
- [apps/backend/app/services](apps/backend/app/services): priority logic and async business services
- [apps/backend/app/models/schemas.py](apps/backend/app/models/schemas.py): request/response models

## Content pipeline

The curated content and question seed workflow lives under [pipelines/content_seeding](pipelines/content_seeding). That folder is used for structured content generation and resource ingestion rather than the web runtime itself.

## Frontend status

The current frontend area at [apps/web](apps/web) is still a placeholder. The project is not yet ready for a full web app onboarding flow until the frontend is implemented.

## Typical development workflow

1. Start PostgreSQL with Docker.
2. Activate the backend virtual environment.
3. Install backend requirements.
4. Run the FastAPI app with Uvicorn.
5. Hit the health endpoint to confirm the service is live.
6. Add or verify seeded data in Postgres.
7. Implement backend features in the API/service layers.
8. Extend the content seed pipeline when new study resources or concepts are needed.

## Current feature direction

The project intentionally focuses on a verification-first learning loop, where concept priority is derived from a deterministic rule. The backend service layer is the best place to work on the ranking logic and stateful study recommendation system.

## Troubleshooting

### Database connection errors

Check that Docker is running and that PostgreSQL is listening on port 5432. Verify the database and credentials match the config in [apps/backend/app/core/config.py](apps/backend/app/core/config.py).

### Module import errors

Make sure you are running inside the backend virtual environment and installed the dependencies from [apps/backend/requirements.txt](apps/backend/requirements.txt).

### Frontend missing

The UI is not yet implemented; treat [apps/web](apps/web) as a reserved area for future work rather than a running application.

## Next steps

A contributor to this project should first:
- get the Postgres container running
- verify the FastAPI health endpoint works
- inspect the app API modules and service logic
- then add new routes, state transitions, or planning behavior in the backend

This README is intended to be the starting point for local engineering work on the project.
