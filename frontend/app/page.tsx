'use client';
import { FormEvent, useEffect, useRef, useState } from 'react';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
// Accept either the backend origin or its /api root; avoid malformed URLs
// when the Vercel environment value has a trailing slash.
const API = (() => {
  const base = API_BASE.trim().replace(/\/+$/, '');
  return base.endsWith('/api') ? base : `${base}/api`;
})();
type Msg = { role: string; content: string; message_type?: string };
type History = { id: string; created_at?: string; updated_at?: string; messages: Msg[] };

export default function Home() {
  const [id, setId] = useState('');
  const [mediaIds, setMediaIds] = useState<number[]>([]);
  const [messages, setMessages] = useState<Msg[]>([]);
  const [text, setText] = useState('');
  const [diagnosis, setDiagnosis] = useState<any>(null);
  const [busyConversationId, setBusyConversationId] = useState<string | null>(null);
  const [error, setError] = useState('');
  const [historyOpen, setHistoryOpen] = useState(false);
  const [history, setHistory] = useState<History[]>([]);
  const chatRef = useRef<HTMLDivElement>(null);
  const busy = busyConversationId !== null && busyConversationId === id;

  useEffect(() => {
    const chat = chatRef.current;
    if (chat) chat.scrollTo({ top: chat.scrollHeight, behavior: 'smooth' });
  }, [messages, busy, diagnosis]);

  useEffect(() => {
    const saved = localStorage.getItem('mechanic_conversation_id');
    if (saved) loadConversation(saved);
    else setMessages([{ role: 'assistant', content: 'Hello — I’m your virtual car mechanic. Tell me what your vehicle is doing, and I’ll help narrow it down.' }]);
    loadHistory();
  }, []);

  async function loadConversation(conversationId: string) {
    try {
      const r = await fetch(`${API}/conversations/${conversationId}/`);
      if (!r.ok) throw new Error('Conversation not found');
      const d = await r.json(); setId(conversationId); setMessages(d.messages || []);
    } catch { localStorage.removeItem('mechanic_conversation_id'); setMessages([{ role: 'assistant', content: 'Hello — I’m your virtual car mechanic. Tell me what your vehicle is doing, and I’ll help narrow it down.' }]); }
  }
  async function loadHistory() {
    // The history endpoint is intentionally conversation-specific; retain known IDs locally.
    const ids = JSON.parse(localStorage.getItem('mechanic_conversation_ids') || '[]') as string[];
    const records = await Promise.all(ids.map(async (conversationId) => { try { const r = await fetch(`${API}/conversations/${conversationId}/`); return r.ok ? await r.json() : null; } catch { return null; } }));
    setHistory(records.filter(Boolean));
  }
  function rememberConversation(conversationId: string) {
    localStorage.setItem('mechanic_conversation_id', conversationId);
    const ids = JSON.parse(localStorage.getItem('mechanic_conversation_ids') || '[]') as string[];
    localStorage.setItem('mechanic_conversation_ids', JSON.stringify([conversationId, ...ids.filter(x => x !== conversationId)].slice(0, 10)));
  }
  function newConversation() { setId(''); setBusyConversationId(null); setMediaIds([]); setDiagnosis(null); setError(''); setText(''); setMessages([{ role: 'assistant', content: 'Hello — I’m your virtual car mechanic. Tell me what your vehicle is doing, and I’ll help narrow it down.' }]); localStorage.removeItem('mechanic_conversation_id'); }
  async function upload(file: File) {
    if (file.size > 50 * 1024 * 1024) { setError('Files must be 50MB or smaller.'); return; }
    const f = new FormData(); f.append('file', file); if (id) f.append('conversation_id', id); setError('Uploading media…');
    try { const r = await fetch(`${API}/upload/`, { method: 'POST', body: f }); const d = await r.json(); if (!r.ok) throw Error(d.error?.message || 'Upload failed'); setId(d.conversation_id); setMediaIds(x => [...x, d.media_id]); rememberConversation(d.conversation_id); setError(`${file.name} uploaded and attached to your next message.`); } catch (x: any) { setError(x.message); }
  }
  async function send(e: FormEvent) {
    e.preventDefault(); if (!text.trim() || busy) return; const value = text.trim(); const requestId = id; setText(''); setMessages(m => [...m, { role: 'user', content: value }]); setBusyConversationId(requestId || '__new__'); setError('');
    try { const r = await fetch(`${API}/chat/`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ conversation_id: requestId || null, message: value, media_ids: mediaIds }) }); const d = await r.json(); if (!r.ok) throw Error(d.error?.message || 'Request failed'); rememberConversation(d.conversation_id); setMediaIds([]); loadHistory(); if ((!requestId && !id) || id === requestId) { setId(d.conversation_id); setMessages(m => [...m, { role: 'assistant', content: d.reply }]); } } catch (x: any) { if (id === requestId) setError(x.message); } finally { setBusyConversationId(current => current === (requestId || '__new__') ? null : current); }
  }
  async function diagnose() { const diagnosisId = id; setBusyConversationId(diagnosisId); try { const r = await fetch(`${API}/diagnosis/`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ conversation_id: diagnosisId, media_ids: mediaIds }) }); const d = await r.json(); if (!r.ok) throw Error(d.error?.message || 'More information is needed'); if (id === diagnosisId) setDiagnosis(d); } catch (x: any) { if (id === diagnosisId) setError(x.message); } finally { setBusyConversationId(current => current === diagnosisId ? null : current); } }

  return <main><header><div className="brand">AI CAR MECHANIC</div><div className="sub">Practical automotive troubleshooting</div></header><section className="shell"><div className="intro"><span>● ONLINE</span><h1>A calmer way to understand<br />what your car is telling you.</h1><p>Describe the symptom in plain language. Get useful next questions and a preliminary assessment — never a substitute for a qualified inspection.</p></div><div className="chat" ref={chatRef}>{messages.map((m, i) => <div key={i} className={`bubble ${m.role}`}>{m.content}</div>)}{busy && <div className="bubble assistant">Thinking…</div>}{diagnosis && <div className="diagnosis"><small>PRELIMINARY ASSESSMENT</small><h2>{diagnosis.probable_issue}</h2><p>{diagnosis.recommended_action}</p><b>Severity: {diagnosis.severity} · Confidence: {Math.round(diagnosis.confidence * 100)}%</b><button onClick={() => document.getElementById('booking')?.scrollIntoView()}>Book a mechanic</button></div>}</div>{error && <div className="error">{error}</div>}<form onSubmit={send}><textarea value={text} onChange={e => setText(e.target.value)} placeholder="Describe your car problem…" rows={3} /><div className="actions"><label className="upload">＋ Add media<input type="file" accept="image/*,audio/*,video/*" hidden onChange={e => e.target.files?.[0] && upload(e.target.files[0])} /></label><button disabled={busy || !text.trim()}>Send message ↗</button></div></form><div className="tools"><button onClick={diagnose} disabled={!id || busy}>Generate preliminary diagnosis</button><button onClick={() => setHistoryOpen(x => !x)}>{historyOpen ? 'Hide history' : 'Show history'}</button><button onClick={newConversation}>New conversation</button></div>{historyOpen && <aside className="history"><h3>Conversation history</h3>{history.length ? history.map(c => <button key={c.id} onClick={() => { loadConversation(c.id); setHistoryOpen(false); }}>{new Date(c.messages?.[0] ? Date.now() : Date.now()).toLocaleDateString()} · {c.messages?.find(m => m.role === 'user')?.content?.slice(0, 55) || 'Empty conversation'}</button>) : <p>No saved conversations yet.</p>}</aside>}<Booking id={id} diagnosis={diagnosis?.diagnosis_id} /></section></main>;
}
function Booking({ id, diagnosis }: { id: string; diagnosis?: number }) { const [open, setOpen] = useState(false); const [done, setDone] = useState(''); async function submit(e: FormEvent) { e.preventDefault(); const body = Object.fromEntries(new FormData(e.currentTarget as HTMLFormElement)); const r = await fetch(`${API}/booking/`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ ...body, conversation_id: id, diagnosis_id: diagnosis, vehicle_year: Number(body.vehicle_year) }) }); const d = await r.json(); setDone(r.ok ? `Booking confirmed — #${d.id}` : (d.error?.message || 'Unable to book')); } return <div id="booking" className="booking"><button onClick={() => setOpen(!open)}>{open ? 'Close booking form' : 'Book a mechanic'}</button>{open && <form onSubmit={submit} className="booking-form">{['customer_name', 'phone', 'email', 'vehicle_make', 'vehicle_model', 'vehicle_year', 'preferred_date', 'preferred_time'].map(n => <input key={n} name={n} required placeholder={n.replaceAll('_', ' ')} type={n === 'email' ? 'email' : n.includes('date') ? 'date' : n.includes('time') ? 'time' : 'text'} />)}<textarea name="problem_summary" required placeholder="Problem summary" /><button>Confirm booking</button>{done && <p>{done}</p>}</form>}</div>; }
