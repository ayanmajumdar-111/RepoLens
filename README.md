# RepoLens# RepoLens

### Understand any GitHub repository with AI

RepoLens is a full-stack, AI-powered codebase intelligence platform
that uses Retrieval-Augmented Generation (RAG) to help developers
explore and understand GitHub repositories.

> Status: In active development

## The Problem

Understanding an unfamiliar codebase can be time-consuming,
especially when navigating multiple files, functions, and modules.

## Our Solution

RepoLens aims to let developers import public GitHub repositories,
ask natural-language questions, and receive answers grounded
in the repository's source code.

## Planned Features

- Import and index public GitHub repositories
- Ask natural-language questions about codebases
- Semantic code search using vector embeddings
- AI-generated explanations with source citations
- File viewer with relevant source references
- Repository dashboard and query history

## Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | Next.js, TypeScript, Tailwind CSS |
| Backend | Python, FastAPI |
| Database | PostgreSQL, Supabase |
| Vector Search | pgvector |
| Embeddings | Sentence Transformers |
| AI | Configurable LLM API |
| Integration | GitHub REST API |

## Architecture

GitHub Repository
      |
Repository Ingestion
      |
Code Chunking
      |
Embedding Generation
      |
Vector Database
      |
Semantic Retrieval
      |
LLM Answer Generation
      |
Web Interface + Source Citations

## Getting Started

Installation and local development instructions will be
added as the application is implemented.

## Roadmap

- [ ] Repository ingestion
- [ ] Embedding generation and vector storage
- [ ] RAG question-answering backend
- [ ] Frontend dashboard
- [ ] Source citations and file viewer
- [ ] Authentication and query history
- [ ] Testing and deployment

## Contributors

Developed by a team of Computer Science students
at Manipal Institute of Technology.

## License

To be finalized by the project contributors.
