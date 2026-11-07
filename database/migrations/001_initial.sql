-- Apply once to a new PostgreSQL database with pgvector installed.
BEGIN;
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- IDs are supplied by the identity provider; authentication is not implemented.
CREATE TABLE users (
    id uuid PRIMARY KEY,
    created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE repositories (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    github_url text NOT NULL,
    full_name text NOT NULL,
    default_branch text,
    indexed_commit_sha text,
    indexing_status text NOT NULL DEFAULT 'pending'
        CHECK (indexing_status IN ('pending', 'processing', 'ready', 'failed')),
    indexing_error text,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (owner_id, github_url)
);
CREATE INDEX repositories_owner_idx ON repositories(owner_id);
CREATE TABLE code_chunks (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    repository_id uuid NOT NULL REFERENCES repositories(id) ON DELETE CASCADE,
    file_path text NOT NULL CHECK (length(file_path) > 0),
    start_line integer NOT NULL CHECK (start_line > 0),
    end_line integer NOT NULL CHECK (end_line >= start_line),
    symbol_name text,
    language text,
    content text NOT NULL,
    embedding vector(384),
    embedding_model text NOT NULL DEFAULT 'sentence-transformers/all-MiniLM-L6-v2',
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (id, repository_id)
);
CREATE INDEX code_chunks_repository_idx ON code_chunks(repository_id);
-- Exact cosine search is the baseline; add an ANN index after measuring recall.
CREATE TABLE chat_sessions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    repository_id uuid NOT NULL REFERENCES repositories(id) ON DELETE CASCADE,
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (id, repository_id)
);
CREATE INDEX chat_sessions_repository_idx ON chat_sessions(repository_id);
CREATE TABLE chat_messages (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id uuid NOT NULL,
    repository_id uuid NOT NULL,
    role text NOT NULL CHECK (role IN ('user', 'assistant')),
    content text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    FOREIGN KEY (session_id, repository_id) REFERENCES chat_sessions(id, repository_id) ON DELETE CASCADE,
    UNIQUE (id, repository_id)
);
CREATE INDEX chat_messages_session_idx ON chat_messages(session_id, created_at);
CREATE TABLE citations (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id uuid NOT NULL,
    chunk_id uuid NOT NULL,
    repository_id uuid NOT NULL,
    start_line integer NOT NULL CHECK (start_line > 0),
    end_line integer NOT NULL CHECK (end_line >= start_line),
    FOREIGN KEY (message_id, repository_id) REFERENCES chat_messages(id, repository_id) ON DELETE CASCADE,
    FOREIGN KEY (chunk_id, repository_id) REFERENCES code_chunks(id, repository_id) ON DELETE CASCADE
);
CREATE INDEX citations_message_idx ON citations(message_id);
COMMIT;
