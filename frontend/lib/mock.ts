import type { Citation } from './contracts';
export const files: Record<string, string> = {
  'app/main.py': 'from fastapi import FastAPI\nfrom app.api.router import router\n\napp = FastAPI(title="RepoLens API")\napp.include_router(router)',
  'app/api/router.py': 'from fastapi import APIRouter\n\nrouter = APIRouter()\n\n@router.get("/health")\ndef health():\n    return {"status": "ok"}',
  'README.md': '# RepoLens demo\n\nAn illustrative repository for exploring the interface.\nThese files are fixtures, not imported GitHub contents.',
};
export async function mockAnswer(question: string): Promise<{ answer: string; citations: Citation[] }> {
  await new Promise(resolve => setTimeout(resolve, 700));
  if (question.toLowerCase().includes('simulate error')) throw new Error('Simulated request failure. Edit your question and retry.');
  if (!/health|api|route|app|fastapi/i.test(question)) return { answer: 'The demo evidence is insufficient to answer that question. Try asking how the health endpoint works.', citations: [] };
  return { answer: 'In this demo, FastAPI creates the application and attaches an API router. The router exposes GET /health, returning a status response. This is a fixture-based explanation, not an LLM answer.', citations: [{ chunk_id: 'demo-router', file_path: 'app/api/router.py', start_line: 5, end_line: 7 }] };
}
