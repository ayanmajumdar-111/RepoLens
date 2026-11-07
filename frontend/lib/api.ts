import type { Repository, ChatResponse } from './contracts';
// Proposed endpoints only. Demo mode never calls this client.
export function createApiClient(baseUrl: string) {
  async function request<T>(path: string, body?: unknown): Promise<T> {
    const response = await fetch(`${baseUrl.replace(/\/$/, '')}${path}`, { method: body ? 'POST' : 'GET', headers: { 'Content-Type': 'application/json' }, body: body ? JSON.stringify(body) : undefined, signal: AbortSignal.timeout(30000) });
    if (!response.ok) throw new Error(`Request failed (${response.status}). Please try again.`);
    return response.json() as Promise<T>; // Runtime validation required before enabling live mode.
  }
  return {
    health: () => request<{ status: string }>('/health'),
    importRepository: (github_url: string) => request<Repository>('/api/repositories', { github_url }),
    repository: (id: string) => request<Repository>(`/api/repositories/${encodeURIComponent(id)}`),
    chat: (id: string, question: string, session_id: string | null) => request<ChatResponse>(`/api/repositories/${encodeURIComponent(id)}/chat`, { question, session_id }),
  };
}
