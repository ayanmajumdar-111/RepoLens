import base64
import httpx
import pytest
from app.services.ingestion.github import GitHubClient, GitHubError, validate_url
from app.services.ingestion.source import Limits, skip_reason, parse_python, chunk_source, decode_source, validate_path


@pytest.mark.parametrize('suffix', ['', '/', '.git', '.git/'])
def test_urls(suffix):
    assert validate_url('https://github.com/owner/repo' + suffix) == ('owner', 'repo')


@pytest.mark.parametrize('url', ['http://github.com/a/b', 'https://evil.com/a/b',
    'https://github.com@evil.com/a/b', 'https://github.com/a/b/issues',
    'https://github.com/a/b?token=x', 'https://github.com/a/..', 'garbage'])
def test_bad_urls(url):
    with pytest.raises(ValueError):
        validate_url(url)


@pytest.mark.parametrize('path', ['node_modules/a.py', '.env', 'secrets.py',
    'build/a.py', 'a.generated.py', 'a.min.js', 'image.png', '.aws/a.py'])
def test_filter(path):
    assert skip_reason(path, 1, Limits()) is not None


def test_limits_and_binary():
    assert skip_reason('a.py', 201, Limits(max_file_bytes=200)) == 'file_size'
    assert skip_reason('src/a.py', 10, Limits()) is None
    with pytest.raises(ValueError):
        decode_source(b'abc\x00def')
    for path in ['../a.py', '/a.py', 'a\\b.py', 'a//b.py']:
        with pytest.raises(ValueError):
            validate_path(path)


def test_symbols_and_lines():
    code = '@decorate\nclass A:\n    async def run(self):\n        return 1\n\ndef f():\n    pass\n'
    symbols = parse_python('a.py', code)
    assert [(s.symbol_name, s.kind, s.start_line, s.end_line) for s in symbols] == [
        ('A', 'class', 1, 4), ('A.run', 'method', 3, 4), ('f', 'function', 6, 7)]
    chunks = chunk_source('11111111-1111-4111-8111-111111111111', 'a.py', code, 3)
    assert ''.join(c.content for c in chunks) == code
    for c in chunks:
        assert c.content == ''.join(code.splitlines(keepends=True)[c.start_line-1:c.end_line])
    with pytest.raises(SyntaxError):
        parse_python('a.py', 'def broken(')


@pytest.mark.parametrize('status,headers,expected', [
    (404, {}, 'not_found'), (500, {}, 'http_500'), (401, {}, 'http_401'),
    (429, {'retry-after': '10'}, 'rate_limited'),
    (403, {'x-ratelimit-remaining': '0'}, 'rate_limited')])
def test_api_errors(status, headers, expected):
    with GitHubClient(transport=httpx.MockTransport(lambda r: httpx.Response(status, headers=headers))) as client:
        with pytest.raises(GitHubError, match=expected):
            client.metadata('https://github.com/a/b')


def test_network_error():
    def fail(request):
        raise httpx.ConnectError('secret detail', request=request)
    with GitHubClient(transport=httpx.MockTransport(fail)) as client:
        with pytest.raises(GitHubError, match='^network_error$'):
            client.metadata('https://github.com/a/b')


def fixture_transport(truncated=False):
    def handler(request):
        path = request.url.path
        if path.endswith('/git/blobs/' + 'a'*40):
            return httpx.Response(200, json={'encoding': 'base64', 'content': base64.b64encode(b'x=1\n').decode()})
        if '/git/trees/' in path:
            return httpx.Response(200, json={'truncated': truncated, 'tree': [
                {'path': 'a.py', 'type': 'blob', 'mode': '100644', 'sha': 'a'*40, 'size': 4},
                {'path': 'secrets.py', 'type': 'blob', 'mode': '100644', 'size': 5}]})
        if '/commits/' in path:
            return httpx.Response(200, json={'sha': 'b'*40, 'commit': {'tree': {'sha': 'c'*40}}})
        return httpx.Response(200, json={'private': False, 'default_branch': 'main'})
    return httpx.MockTransport(handler)


def test_snapshot_ingestion():
    with GitHubClient(transport=fixture_transport()) as client:
        result = client.ingest('https://github.com/a/b')
    assert result['files'] == {'a.py': 'x=1\n'}
    assert result['indexed_commit_sha'] == 'b'*40
    assert result['skipped']['secrets.py'] == 'credential_file'


def test_truncation_and_total_limits():
    with GitHubClient(transport=fixture_transport(True)) as client:
        with pytest.raises(GitHubError, match='truncated_tree'):
            client.ingest('https://github.com/a/b')


def test_private_and_invalid_json():
    for response, code in [(httpx.Response(200, json={'private': True}), 'public_repositories_only'),
                           (httpx.Response(200, text='bad json'), 'invalid_response')]:
        with GitHubClient(transport=httpx.MockTransport(lambda r: response)) as client:
            with pytest.raises(GitHubError, match=code):
                client.metadata('https://github.com/a/b')


def test_file_count_limit():
    original = fixture_transport()
    def handler(request):
        response = original.handle_request(request)
        if '/git/trees/' in request.url.path:
            data = response.json()
            data['tree'].append({**data['tree'][0], 'path': 'b.py'})
            return httpx.Response(200, json=data)
        return response
    with GitHubClient(limits=Limits(max_files=1), transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(GitHubError, match='repository_limit_exceeded'):
            client.ingest('https://github.com/a/b')
    with GitHubClient(limits=Limits(max_total_bytes=3), transport=fixture_transport()) as client:
        with pytest.raises(GitHubError, match='repository_limit_exceeded'):
            client.ingest('https://github.com/a/b')
