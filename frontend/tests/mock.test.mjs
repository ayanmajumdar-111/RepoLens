import { test } from 'node:test';
import assert from 'node:assert/strict';
import { files, mockAnswer } from '../lib/mock.ts';
test('demo answers cite existing fixture lines', async () => {
  const result = await mockAnswer('How does the health API work?');
  assert.ok(result.citations.length);
  for (const citation of result.citations) {
    assert.ok(files[citation.file_path]);
    assert.ok(citation.start_line >= 1);
    assert.ok(citation.end_line >= citation.start_line);
    assert.ok(citation.end_line <= files[citation.file_path].split('\n').length);
  }
});
test('unsupported questions do not fabricate citations', async () => {
  const result = await mockAnswer('Explain billing');
  assert.deepEqual(result.citations, []);
  assert.match(result.answer, /insufficient/);
});
test('demo failure is recoverable', async () => {
  await assert.rejects(mockAnswer('simulate error'), /Simulated request failure/);
  assert.ok((await mockAnswer('health')).citations.length);
});
