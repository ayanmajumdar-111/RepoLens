# Shared contracts (proposed)

Only GET /health is implemented. All other paths and examples below are proposed for team review; no authentication, persistence, retrieval, or chat API is implemented. IDs are UUID strings, lines are 1-based and inclusive. Paths are repository-relative and should be validated to prevent traversal. Errors must not leak secrets.

## Repository and indexing

POST /api/repositories request:
```json
{"github_url":"https://github.com/example/project"}
```
Proposed response:
```json
{"id":"11111111-1111-4111-8111-111111111111","github_url":"https://github.com/example/project","full_name":"example/project","default_branch":"main","indexed_commit_sha":null,"indexing_status":"pending"}
```
GET /api/repositories/{repository_id} returns metadata and pending, processing, ready or failed status. Define ownership and access control before implementation.

## Ingestion chunk

Person 1 supplies this structure to Person 2; embedding is an array of exactly 384 finite numbers, not the shortened illustrative array below. The model revision and preprocessing must match at indexing and query time.
```json
{"repository_id":"11111111-1111-4111-8111-111111111111","file_path":"src/auth.py","start_line":10,"end_line":20,"symbol_name":"login","language":"python","content":"def login():\n    pass","embedding_model":"sentence-transformers/all-MiniLM-L6-v2","embedding":"<384 floating-point values>"}
```
Storage assigns a chunk UUID; null embeddings represent incomplete work and must not be retrieved. Pin model revision and preprocessing as a team before indexing.

## Retrieval

POST /api/repositories/{repository_id}/retrieve request:
```json
{"question":"How does login work?","top_k":5}
```
Proposed response:
```json
{"chunks":[{"chunk_id":"22222222-2222-4222-8222-222222222222","repository_id":"11111111-1111-4111-8111-111111111111","file_path":"src/auth.py","start_line":10,"end_line":20,"symbol_name":"login","language":"python","content":"def login():\n    pass","score":0.82}]}
```
Score is planned as 1 minus cosine distance: larger means more similar, normally in [-1, 1]; it is not a probability. Empty matches return an empty array. Agree top_k limits before implementation.

## Chat and citations

POST /api/repositories/{repository_id}/chat request:
```json
{"session_id":null,"question":"How does login work?"}
```
Proposed response:
```json
{"session_id":"33333333-3333-4333-8333-333333333333","message_id":"44444444-4444-4444-8444-444444444444","answer":"Login is defined in auth.py.","citations":[{"chunk_id":"22222222-2222-4222-8222-222222222222","file_path":"src/auth.py","start_line":10,"end_line":20}]}
```
Citations must refer to retrieved chunks and lines within them. The generator must acknowledge insufficient evidence instead of inventing citations.

## Errors

Proposed consistent error response, to be implemented:
```json
{"error":{"code":"repository_not_found","message":"Repository not found.","details":null}}
```
FastAPI currently uses its default error format. GET /health currently returns HTTP 200 and `{"status":"ok"}`; it checks process availability, not the database.
