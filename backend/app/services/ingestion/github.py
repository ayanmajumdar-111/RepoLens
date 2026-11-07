"""Fixed-host GitHub REST client with bounded responses and snapshot reads."""
import base64
import re
from urllib.parse import quote, urlsplit
import httpx
from .source import Limits, skip_reason, decode_source


class GitHubError(Exception):
    def __init__(self, code: str, retry_after: str | None = None):
        super().__init__(code)
        self.code = code
        self.retry_after = retry_after


def validate_url(url: str) -> tuple[str, str]:
    try:
        parts = urlsplit(url)
        if (any(ord(c) < 32 for c in url) or url != url.strip() or parts.scheme != 'https' or parts.netloc.lower() != 'github.com'
                or parts.query or parts.fragment):
            raise ValueError
        path = parts.path.rstrip('/')
        if path.endswith('.git'):
            path = path[:-4]
        match = re.fullmatch(r'/([A-Za-z0-9][A-Za-z0-9-]{0,38})/([A-Za-z0-9_.-]+)', path)
        if not match or match[2] in {'.', '..'}:
            raise ValueError
        return match[1], match[2]
    except ValueError:
        raise ValueError('Expected https://github.com/owner/repository') from None


class GitHubClient:
    def __init__(self, token: str | None = None, *, limits: Limits = Limits(), transport=None):
        self.limits = limits
        headers = {'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}
        if token:
            headers['Authorization'] = f'Bearer {token}'
        self.client = httpx.Client(base_url='https://api.github.com', headers=headers,
                                   timeout=20, follow_redirects=False, transport=transport)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.client.close()

    def _get(self, path: str, cap: int = 8_000_000):
        try:
            with self.client.stream('GET', path) as response:
                if response.status_code == 429 or (response.status_code == 403 and
                        (response.headers.get('x-ratelimit-remaining') == '0' or 'retry-after' in response.headers)):
                    raise GitHubError('rate_limited', response.headers.get('retry-after') or response.headers.get('x-ratelimit-reset'))
                if response.status_code == 404:
                    raise GitHubError('not_found')
                if response.status_code != 200:
                    raise GitHubError(f'http_{response.status_code}')
                data = bytearray()
                for block in response.iter_bytes():
                    data.extend(block)
                    if len(data) > cap:
                        raise GitHubError('response_too_large')
                import json
                return json.loads(data)
        except httpx.RequestError:
            raise GitHubError('network_error') from None
        except ValueError:
            raise GitHubError('invalid_response') from None

    def metadata(self, url: str) -> dict:
        owner, repo = validate_url(url)
        data = self._get(f'/repos/{owner}/{repo}')
        if data.get('private', True):
            raise GitHubError('public_repositories_only')
        return data

    def snapshot(self, url: str) -> tuple[dict, str, list[dict]]:
        owner, repo = validate_url(url)
        metadata = self.metadata(url)
        branch = quote(metadata['default_branch'], safe='')
        commit = self._get(f'/repos/{owner}/{repo}/commits/{branch}')
        sha = commit['sha']
        tree_sha = commit['commit']['tree']['sha']
        tree = self._get(f'/repos/{owner}/{repo}/git/trees/{tree_sha}?recursive=1')
        if tree.get('truncated'):
            raise GitHubError('truncated_tree')
        return metadata, sha, tree['tree']

    def source(self, url: str, entry: dict) -> str:
        owner, repo = validate_url(url)
        if entry.get('mode') not in {'100644', '100755'} or entry.get('type') != 'blob':
            raise GitHubError('unsupported_entry')
        reason = skip_reason(entry['path'], entry['size'], self.limits)
        if reason:
            raise GitHubError(reason)
        sha = entry['sha']
        if not re.fullmatch('[0-9a-f]{40}', sha):
            raise GitHubError('invalid_blob_sha')
        blob = self._get(f'/repos/{owner}/{repo}/git/blobs/{sha}', self.limits.max_file_bytes * 2 + 4096)
        try:
            if blob['encoding'] != 'base64':
                raise ValueError
            raw = base64.b64decode(''.join(blob['content'].split()), validate=True)
            if len(raw) > self.limits.max_file_bytes or len(raw) != entry['size']:
                raise ValueError
            return decode_source(raw)
        except (ValueError, KeyError):
            raise GitHubError('invalid_source') from None

    def ingest(self, url: str) -> dict:
        metadata, sha, tree = self.snapshot(url)
        files, skipped, total = {}, {}, 0
        for entry in tree:
            path = entry['path']
            if entry.get('type') != 'blob' or entry.get('mode') not in {'100644', '100755'}:
                continue
            reason = skip_reason(path, entry.get('size', -1), self.limits)
            if reason:
                skipped[path] = reason
                continue
            if len(files) >= self.limits.max_files or total + entry['size'] > self.limits.max_total_bytes:
                raise GitHubError('repository_limit_exceeded')
            try:
                content = self.source(url, entry)
            except GitHubError as exc:
                if exc.code != 'invalid_source':
                    raise
                skipped[path] = exc.code
                continue
            total += entry['size']
            files[path] = content
        return {'metadata': metadata, 'indexed_commit_sha': sha, 'tree': tree,
                'files': files, 'skipped': skipped}
