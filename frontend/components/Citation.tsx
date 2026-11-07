import type { Citation as Source } from '../lib/contracts';
export function Citation({ source, onNavigate }: { source: Source; onNavigate: (source: Source) => void }) {
  return <button className="citation" onClick={() => onNavigate(source)} aria-label={`Open ${source.file_path}, lines ${source.start_line} to ${source.end_line}`}>{source.file_path} <span>L{source.start_line}–{source.end_line}</span> ↗</button>;
}
