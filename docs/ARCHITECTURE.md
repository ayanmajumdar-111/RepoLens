# Architecture

This is a foundation; only the health endpoint exists today.

Indexing: GitHub URL → GitHub REST API → files/tree → parsing and line-preserving chunks → all-MiniLM-L6-v2 embeddings → PostgreSQL/pgvector. Person 1 owns ingestion, parsing, chunking, and document embeddings. Person 2 owns schema, storage, query embeddings and repository-filtered retrieval.

Questions: question → same embedding model and preprocessing → repository-scoped cosine similarity → top-k chunks with source metadata → LLM prompt and answer → validated citations in the interface. Person 3 owns the frontend, generation and citation presentation. All members review integration, testing and deployment.

FastAPI is the integration boundary; Next.js must not receive database or service-role credentials. Authentication, authorization, database connections, retrieval, ingestion and generation are not implemented. Contracts are proposals for team agreement.
