"""Source validation, filtering, AST symbols and line-preserving chunks."""
import ast
from dataclasses import dataclass
from pathlib import PurePosixPath
from uuid import UUID

LANGUAGES = {'.py': 'python', '.js': 'javascript', '.ts': 'typescript',
             '.tsx': 'typescript', '.jsx': 'javascript', '.java': 'java',
             '.c': 'c', '.h': 'c', '.cpp': 'cpp', '.go': 'go', '.rs': 'rust'}
EXCLUDED = {'node_modules', 'vendor', '.git', '.venv', 'venv', 'dist', 'build',
            '__pycache__', '.next', 'coverage', '.aws', '.ssh'}


def validate_path(path: str) -> str:
    if (not path or '\\' in path or ':' in path or
            any(ord(c) < 32 for c in path) or
            any(part in {'', '.', '..'} for part in path.split('/'))):
        raise ValueError('Expected a safe repository-relative POSIX path')
    return path


@dataclass(frozen=True)
class Limits:
    max_file_bytes: int = 200_000
    max_files: int = 500
    max_total_bytes: int = 5_000_000

    def __post_init__(self):
        if min(self.max_file_bytes, self.max_files, self.max_total_bytes) <= 0:
            raise ValueError('Limits must be positive')


def skip_reason(path: str, size: int, limits: Limits) -> str | None:
    validate_path(path)
    p = PurePosixPath(path.lower())
    if any(part in EXCLUDED for part in p.parts):
        return 'excluded_directory'
    if (p.name.startswith('.env') or p.stem in {'credentials', 'secrets', 'id_rsa', 'id_ed25519'}
            or p.suffix in {'.pem', '.key', '.p12', '.pfx'}):
        return 'credential_file'
    if any(marker in p.name for marker in ('.min.', '.generated.', '_pb2.', '_pb2_grpc.')):
        return 'generated_file'
    if size < 0 or size > limits.max_file_bytes:
        return 'file_size'
    if p.suffix not in LANGUAGES:
        return 'unsupported_language'
    return None


def decode_source(content: bytes) -> str:
    if b'\x00' in content:
        raise ValueError('Binary source rejected')
    # UTF-8 is the initial supported encoding; do not silently replace bytes.
    return content.decode('utf-8')


@dataclass(frozen=True)
class Symbol:
    file_path: str
    symbol_name: str
    kind: str
    start_line: int
    end_line: int


def parse_python(path: str, content: str) -> list[Symbol]:
    validate_path(path)
    tree = ast.parse(content, filename=path)
    result = []

    def visit(node, parents=(), parent_kind=None):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            name = '.'.join((*parents, node.name))
            kind = 'class' if isinstance(node, ast.ClassDef) else ('method' if parent_kind == 'class' else 'function')
            start = min([node.lineno] + [d.lineno for d in node.decorator_list])
            result.append(Symbol(path, name, kind, start, node.end_lineno))
            parents, parent_kind = (*parents, node.name), kind
        for child in ast.iter_child_nodes(node):
            visit(child, parents, parent_kind)

    visit(tree)
    return result


@dataclass(frozen=True)
class Chunk:
    repository_id: str
    file_path: str
    start_line: int
    end_line: int
    symbol_name: str | None
    language: str
    content: str
    embedding_model: str = 'sentence-transformers/all-MiniLM-L6-v2'
    embedding: None = None


def chunk_source(repository_id: str, path: str, content: str, max_lines: int = 100) -> list[Chunk]:
    UUID(repository_id)
    validate_path(path)
    if max_lines <= 0:
        raise ValueError('max_lines must be positive')
    language = LANGUAGES[PurePosixPath(path).suffix.lower()]
    lines = content.splitlines(keepends=True)
    # Initial bounded line windows retain imports, comments and module-level code.
    return [Chunk(repository_id, path, i + 1, min(i + max_lines, len(lines)),
                  None, language, ''.join(lines[i:i + max_lines]))
            for i in range(0, len(lines), max_lines)]
