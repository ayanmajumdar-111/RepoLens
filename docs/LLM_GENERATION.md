# Proposed LLM generation architecture

Person 3 owns generation; Person 2 owns repository-scoped retrieval. No provider calls or backend changes are included in Day 1. Agree module paths with Person 2 before implementation.

Flow: authorized chat request → repository readiness check → retrieval → bounded context → provider adapter → citation validation → persisted assistant response.

The adapter receives a question, bounded conversation context, and retrieved chunks with IDs, paths, inclusive 1-based lines, and repository snapshot identity. Keep provider/model settings and keys on the backend. Enforce timeouts, token budgets, cancellation, and bounded retries for transient failures.

Treat source code and previous messages as untrusted data, never instructions. Delimit evidence in the prompt, request structured answer text and chunk-ID/line references, and never execute model output. Empty retrieval returns an explicit insufficient-evidence response without fabricated citations.

Validate every citation against the retrieved set: same repository and snapshot, known chunk ID, exact stored path, integer start/end with start <= end, and containment within that chunk. Resolve paths from stored metadata rather than trusting model paths. Reject invalid output and either retry once or return a transparent failure. Render plain text safely; add sanitized Markdown only deliberately.

Return the proposed CONTRACTS.md chat response. Confirm an insufficient-evidence field, response validation, error codes, authorization, conversation ownership, persistence, streaming policy, and immutable file-content/tree endpoints with the team before live integration. Reindexing must not silently redirect old citations to changed code.

Tests should cover empty evidence, unknown IDs, cross-repository references, invalid ranges, malicious repository instructions, timeouts, and valid cited answers. Evaluate factual grounding separately from citation validity.

## Day 1 implementation

The frontend contains a landing page, URL validation, fixture workspace, expandable explorer, numbered source viewer, mock chat, failure simulation, and clickable citations. `frontend/lib/mock.ts` is the only demo data source. `frontend/lib/api.ts` is an unused proposed API adapter; it needs runtime response validation before live use. No user repository is fetched. Chat history lives only in memory. The interface uses responsive CSS with Tailwind available through the existing build.

Remaining: live import/index status, repository lists, file APIs, history persistence, authentication, real retrieval/generation, syntax highlighting, and agreed schemas. Lint tooling is not configured in the existing foundation.
