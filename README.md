# RepoLens

### Understand any GitHub repository with AI

RepoLens aims to help developers explore public GitHub repositories using retrieval-augmented generation. The current project is a foundation: only the health endpoint and a minimal frontend are implemented. Repository ingestion, retrieval, chat, authentication and citations are planned.

## Stack

Next.js, TypeScript and Tailwind CSS; Python and FastAPI; PostgreSQL, Supabase and pgvector; Sentence Transformers; a configurable LLM provider; GitHub REST API.

## Local setup

Requirements: Python 3.12+, Node.js 20.9+ and pnpm. PostgreSQL with pgvector is only needed to apply the optional initial migration; no database credentials are needed to run the applications.

From the repository root, copy `.env.example` to `.env` if you want to change defaults. Never commit secrets. The backend reads the root `.env` and environment variables; `CORS_ORIGINS` is a comma-separated list. The frontend skeleton does not yet consume the API URL.

Backend (commands shown for PowerShell):
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m uvicorn app.main:app --reload
```
Open http://localhost:8000/health or http://localhost:8000/docs. In another terminal, from `backend/`, run `python -m pytest -q`.

Frontend, in a separate terminal:
```powershell
cd frontend
pnpm install --frozen-lockfile
pnpm dev
```
Open http://localhost:3000. Run `pnpm build` for a production build.

The initial SQL migration and its limitations are described in [docs/DATABASE.md](docs/DATABASE.md). Do not expose the database to untrusted clients until authorization is implemented.

## Documentation

- [Architecture and team responsibilities](docs/ARCHITECTURE.md)
- [Database design](docs/DATABASE.md)
- [Proposed shared contracts](docs/CONTRACTS.md)
- [Development log](docs/DEVELOPMENT_LOG.md)

## Contributors and license

Developed by Computer Science students at Manipal Institute of Technology. License to be finalized by the contributors.
