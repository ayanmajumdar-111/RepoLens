export interface Citation { chunk_id: string; file_path: string; start_line: number; end_line: number }
export interface Repository { id: string; github_url: string; full_name: string; default_branch: string; indexed_commit_sha: string | null; indexing_status: 'pending' | 'processing' | 'ready' | 'failed' }
export interface ChatResponse { session_id: string; message_id: string; answer: string; citations: Citation[] }
