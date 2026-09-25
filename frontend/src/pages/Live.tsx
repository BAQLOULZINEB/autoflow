import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { api, fmtDate, STATE_FR, type LiveEvent } from '../lib/api'
import Trace from '../components/Trace'
import { IconPause, IconPlay } from '../components/Icons'

const ACTOR_COLOR: Record<string, string> = { intake: '#34d399', availability: '#34d399', followup: '#34d399', orchestrator: '#a78bfa', system: '#94a3b8' }
const actorColor = (a: string) => a.startsWith('staff') || a.startsWith('manager') ? '#fb7185' : ACTOR_COLOR[a] || '#22d3ee'

/** Live panel: what the system is doing right now + the reasoning behind any decision. */
export default function Live() {
  const [events, setEvents] = useState<LiveEvent[]>([])
  const [selected, setSelected] = useState<string>('')
  const [open, setOpen] = useState(0)
  const [clock, setClock] = useState('')
  const [tick, setTick] = useState(0)
  const [paused, setPaused] = useState(false)
  const lastId = useRef(0)
  const fresh = useRef<Set<number>>(new Set())

  const poll = async () => {
    const r = await api.live(lastId.current)
    if (r.events.length) {
      fresh.current = new Set(r.events.map(e => e.id))
      setEvents(prev => [...r.events, ...prev].slice(0, 80))
      lastId.current = r.last_id
      setTick(t => t + 1)
      if (!selected) setSelected(r.events[0].request_id)
    }
    setOpen(r.open_reviews); setClock(r.clock)
  }
  useEffect(() => { poll() }, []) // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => { if (paused) return; const t = setInterval(poll, 4000); return () => clearInterval(t) }, [paused, selected]) // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <>
      <div className="topbar">
        <div><h1>Suivi en direct</h1><div className="sub">Chaque action du système et de l'équipe, en temps réel. Cliquez un événement pour voir le raisonnement complet de la décision.</div></div>
        <div className="row-actions" style={{ marginTop: 0 }}>
          <span className="tag">{open} à valider</span>
          <span className="tag">horloge {clock ? new Date(clock).toLocaleTimeString('fr-FR') : '…'}</span>
          <button className="btn sm" onClick={() => setPaused(p => !p)}>{paused ? <><IconPlay size={12} /> Reprendre</> : <><IconPause size={12} /> Pause</>}</button>
        </div>
      </div>
      <div className="live-grid">
        <div className="card feed">
          <h2><span className="live-dot" /> Flux d'activité</h2>
          <ul className="timeline live">
            {events.map(e => (
              <li key={e.id} className={`${fresh.current.has(e.id) ? 'new' : ''} ${selected === e.request_id ? 'sel' : ''}`} onClick={() => setSelected(e.request_id)}>
                <span className="muted small">{fmtDate(e.ts)}</span>
                <span><b className="mono">{e.request_id}</b><br /><span style={{ color: actorColor(e.actor), fontWeight: 700, fontSize: 11 }}>{e.actor}</span></span>
                <span className="small">{e.from !== e.to && e.to ? <span className="arrow">→ {STATE_FR[e.to] || e.to} · </span> : null}{e.reason}</span>
              </li>
            ))}
            {events.length === 0 && <li className="muted">En attente d'activité… chargez un scénario dans la barre latérale.</li>}
          </ul>
        </div>
        <div className="card">
          <div className="topbar" style={{ marginBottom: 8 }}>
            <h2>Raisonnement — {selected ? <Link to={`/requests/${selected}`} style={{ color: 'var(--teal)' }}>{selected}</Link> : '…'}</h2>
            {selected && <Link className="btn sm" to={`/requests/${selected}`}>Ouvrir la demande →</Link>}
          </div>
          {selected ? <Trace id={selected} refreshKey={tick} /> : <p className="muted">Sélectionnez un événement.</p>}
        </div>
      </div>
    </>
  )
}
