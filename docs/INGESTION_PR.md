# Add Day 1 public GitHub ingestion and parsing foundation

Adds URL validation, a bounded HTTPX GitHub client, source filtering, Python AST
symbol extraction and line-preserving chunks. Imports resolve a default-branch
commit and read immutable blobs, so subsequent branch changes cannot mix file
versions within an import.

HTTPX is now a runtime dependency. Tests use mocked GitHub responses. The work
does not add import API endpoints, embeddings, database writes or retrieval.
Database migrations and frontend files are unchanged.

Review requested from Person 2: provisional service directories, metadata-to-DB
mapping, storage interface, path rules, atomic index publication, and the open
decisions documented in INGESTION.md. Chunk UUIDs remain storage-owned.

Validation: backend pytest suite on isolated Python 3.14. Dependencies installed
successfully; no Python compatibility failure observed. An upstream Starlette
TestClient deprecation warning remains.
