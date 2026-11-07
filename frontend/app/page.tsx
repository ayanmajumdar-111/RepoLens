'use client';
import { useState } from 'react';
import { Citation } from '../components/Citation';
import type { Citation as Source } from '../lib/contracts';
import { files, mockAnswer } from '../lib/mock';
type Message = { role: 'You' | 'RepoLens'; text: string; citations?: Source[] };
export default function Home() {
  const [workspace, setWorkspace] = useState(false);
  const [url, setUrl] = useState('');
  const [error, setError] = useState('');
  const [file, setFile] = useState('app/main.py');
  const [range, setRange] = useState<Source | null>(null);
  const [question, setQuestion] = useState('');
  const [busy, setBusy] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  function openDemo() { setWorkspace(true); setError(''); }
  function select(path: string) { setFile(path); setRange(null); }
  function navigate(source: Source) {
    if (!files[source.file_path] || source.start_line < 1 || source.end_line > files[source.file_path].split('\n').length) return;
    setFile(source.file_path); setRange(source);
    setTimeout(() => document.getElementById(`line-${source.start_line}`)?.scrollIntoView({ block: 'center', behavior: 'smooth' }), 0);
  }
  async function ask() {
    if (!question.trim() || busy) return;
    const prompt = question.trim(); setBusy(true); setError('');
    setMessages(previous => [...previous, { role: 'You', text: prompt }]); setQuestion('');
    try { const result = await mockAnswer(prompt); setMessages(previous => [...previous, { role: 'RepoLens', text: result.answer, citations: result.citations }]); }
    catch (cause) { setError(cause instanceof Error ? cause.message : 'Unable to answer.'); setQuestion(prompt); }
    finally { setBusy(false); }
  }
  return <main className="min-h-screen antialiased">
    <header><button className="brand" onClick={() => setWorkspace(false)}><span className="mark">⌘</span> RepoLens</button><nav><span className="muted">Your code. In context.</span><button onClick={openDemo}>Open demo ↗</button></nav></header>
    {!workspace ? <section className="landing"><div className="eyebrow">CODEBASE INTELLIGENCE / DAY ONE</div><h1>Less searching.<br/><span>More understanding.</span></h1><p className="intro">Find your way through an unfamiliar repository. Explore the code, ask better questions, and follow every answer back to its source.</p>
      <form className="import" onSubmit={event => { event.preventDefault(); try { const parsed = new URL(url); if (parsed.protocol !== 'https:' || parsed.hostname !== 'github.com' || !/^\/[\w.-]+\/[\w.-]+\/?$/.test(parsed.pathname)) throw new Error(); setError('Live import is not connected yet. Open the demo workspace below.'); } catch { setError('Enter a repository URL such as https://github.com/owner/repository.'); } }}><label htmlFor="repository">GitHub repository URL</label><div className="input-row"><input id="repository" value={url} onChange={event => setUrl(event.target.value)} placeholder="https://github.com/owner/repository" required/><button className="primary">Check repository →</button></div></form>
      <p className="muted">Live indexing is coming next. <button className="text-button" onClick={openDemo}>Explore the interactive demo →</button></p>
      <div className="features">{[['01', 'Explore the structure', 'Navigate folders and read source code without losing your place.'], ['02', 'Ask with context', 'A conversational workspace built around repository evidence.'], ['03', 'Trace every answer', 'Jump from a citation straight to the supporting source lines.']].map(([number, title, text]) => <article key={number}><small>{number}</small><h2>{title}</h2><p>{text}</p></article>)}</div>
    </section> : <section className="workspace"><div className="workspace-title"><div><div className="eyebrow">REPOSITORY WORKSPACE</div><h1>repolens / demo</h1></div><span className="badge">● Demo fixtures ready</span></div><p className="notice">Demo mode · No repository imported, no live indexing, no LLM calls. Conversations last only in this page session.</p>
      <div className="panels"><aside><h2>Repositories</h2><div className="repo">◈ repolens / demo <span className="muted">main</span></div><h2>Files</h2><details open><summary>app</summary><button className={file === 'app/main.py' ? 'selected' : ''} onClick={() => select('app/main.py')}>main.py</button><details open><summary>api</summary><button className={file === 'app/api/router.py' ? 'selected' : ''} onClick={() => select('app/api/router.py')}>router.py</button></details></details><button onClick={() => select('README.md')}>README.md</button><p className="muted">3 fixture files<br/>Indexing status: demo ready</p></aside>
      <section className="code-panel" aria-label="Source code"><div className="panel-heading">{file}<span className="muted">read only</span></div><div className="code-scroll"><pre>{files[file].split('\n').map((line, index) => <div id={`line-${index + 1}`} key={index} className={range && index + 1 >= range.start_line && index + 1 <= range.end_line ? 'highlight' : ''}><span className="line-number">{index + 1}</span><code>{line || ' '}</code></div>)}</pre></div></section>
      <section className="chat"><div className="panel-heading">Ask RepoLens<span className="badge">MOCK</span></div><div className="messages" aria-live="polite">{messages.length === 0 && <div className="chat-empty"><span className="mark">✧</span><h2>Start with a question.</h2><p>Explore the demo API and follow its source citations.</p><button onClick={() => setQuestion('How does the health endpoint work?')}>How does the health endpoint work? ↗</button><p className="muted">Ask “simulate error” to preview failure handling.</p></div>}{messages.map((message, index) => <article className="message" key={index}><strong>{message.role}</strong><p>{message.text}</p>{message.citations?.map(source => <Citation key={source.chunk_id} source={source} onNavigate={navigate}/>)}</article>)}{busy && <p role="status">Reading demo context…</p>}</div><form className="composer" onSubmit={event => { event.preventDefault(); void ask(); }}><label htmlFor="question">Ask about this repository</label><textarea id="question" value={question} onChange={event => setQuestion(event.target.value)} placeholder="How does this application work?" maxLength={4000}/><button className="primary" disabled={busy || !question.trim()}>{busy ? 'Thinking…' : 'Send question ↑'}</button></form></section></div>
    </section>}{error && <div className="error" role="alert">{error}<button onClick={() => setError('')} aria-label="Dismiss error">×</button></div>}
    <footer>RepoLens <span>Built for curious developers.</span></footer>
  </main>;
}
