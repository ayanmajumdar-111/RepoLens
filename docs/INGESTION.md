# Day 1 ingestion

Provisional Person 1 locations: `backend/app/services/ingestion/` and
`backend/tests/ingestion/`. Person 2 should confirm these locations.

Use `GitHubClient` as a context manager. `ingest(url)` returns metadata, the
resolved commit SHA, tree, accepted source text and skip reasons. Metadata is
the GitHub response, not a database repository record. Callers supply the UUID
when calling `chunk_source`. Storage continues to assign chunk UUIDs.

Only public HTTPS github.com repository URLs are accepted. Requests use a fixed
API host, no redirects, timeouts and bounded response bodies. Rate limits surface
as typed errors with retry metadata; retries and job scheduling are caller-owned.
The default branch is resolved once and files are read by immutable blob SHA.
Truncated trees and aggregate limits fail explicitly instead of reporting a
complete import. Symlinks and submodules are not downloaded. No code is executed.

Defaults: 200 KB per file, 500 accepted files, 5 MB accepted content. UTF-8 text
only; null-containing or invalid UTF-8 files are skipped. Exclusions are a
conservative filename/directory policy, not a general secret scanner. More
generated-file patterns and encodings can be added later.

Python parsing extracts qualified symbols, including decorators in starting
lines. Invalid Python raises SyntaxError for callers to record per file. Parsing
does not execute decorators or imports. Chunking currently uses bounded line
windows, retains original text and uses one-based inclusive locations; it does
not yet use AST boundaries or a token budget. Symbol names and embeddings are
null in these initial chunks. Empty source produces no chunks.

## Integration decisions

- Confirm strict repository-relative POSIX paths; unsafe paths are rejected,
  rather than silently normalized.
- Confirm service interfaces and map GitHub metadata to repository records.
- Persist the resolved commit with the repository; agree atomic publication of
  a completed index and behavior if an import fails midway.
- Database-generated UUIDs follow the proposed contract. Stable IDs,
  deduplication, reindexing and retention of historical citations remain open.
- Pin embedding revision and preprocessing with Person 2 before indexing.
  Embedding generation, database writes, retrieval and HTTP import routes are
  intentionally not implemented here.
- Agree API error mapping, ownership, import scheduling and production limits.

## Tests

From `backend`, run `.venv/Scripts/python -m pytest -q`. GitHub tests use
HTTPX MockTransport and require no network or credentials. The local isolated
environment uses the available Python 3.14 interpreter; no Python 3.12 was
installed on this machine. Database migrations and frontend are unchanged.
