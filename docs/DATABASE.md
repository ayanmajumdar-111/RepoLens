# Database design

database/migrations/001_initial.sql is a transactional, one-time initial migration for PostgreSQL with pgvector and pgcrypto available. Apply using a migration runner that tracks versions, or manually once on a new development database: `psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f database/migrations/001_initial.sql`. A migration runner is not yet implemented. Never rerun this initial migration on an existing schema.

Users are identity-provider IDs; repositories belong to a user. Chunks store source metadata and nullable vector(384) embeddings so incomplete indexing is representable. Skip null embeddings during retrieval. Sessions belong to repositories; messages and citations use composite foreign keys to keep their referenced data in the same repository. Reindexing and citation retention need a team decision: deleting chunks currently cascades to citations.

Use the same model revision and preprocessing for document and query vectors; model name alone does not enforce compatibility. Cosine distance is planned, with exact search initially. Filter by authorized repository first, order by embedding <=> query vector, exclude null and zero vectors, and define score as 1 - cosine distance. Validate finite nonzero vectors before storage and queries; these checks and search are not implemented.

**Security:** ownership columns and foreign keys do not enforce authorization. No RLS policies, grants, Supabase Auth integration, or authorization checks exist. Do not expose these tables through Supabase's client API or deploy with untrusted access until access rules are implemented and tested. Service-role credentials bypass RLS and must stay server-side. Citation line containment and assistant-only citations also require application validation.
