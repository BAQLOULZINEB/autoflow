import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { api, type SimCatalogue, type SimResult } from '../lib/api'
import { Channel, IconBot, IconCheck, IconFlask, IconPlay, IconSpinner, IconUser, IconX } from '../components/Icons'
import { StateBadge } from '../components/ui'

const WHO: Record<string, { label: string; cls: string; Icon: typeof IconUser }> = {
  client: { label: 'Client', cls: 'who-client', Icon: IconUser },
  staff: { label: 'Équipe', cls: 'who-staff', Icon: IconUser },
  manager: { label: 'Manager', cls: 'who-manager', Icon: IconUser },
  system: { label: 'Système', cls: 'who-system', Icon: IconBot },
}
const REVEAL_MS = 700

/** Built-in business cases: each runs through the real API and asserts every step. */
export default function Simulations() {
  const [cat, setCat] = useState<SimCatalogue[]>([])
  const [results, setResults] = useState<Record<string, SimResult>>({})
  const [revealed, setRevealed] = useState<Record<string, number>>({})
  const [running, setRunning] = useState<string | null>(null)
  const [runningAll, setRunningAll] = useState(false)
  const [open, setOpen] = useState<string | null>(null)
  const timers = useRef<number[]>([])
  useEffect(() => { api.simulations().then(setCat); return () => timers.current.forEach(clearTimeout) }, [])

  const play = async (key: string) => {
    setRunning(key); setOpen(key); setRevealed(r => ({ ...r, [key]: 0 }))
    try {
      const res = await api.runSimulation(key)
      setResults(r => ({ ...r, [key]: res }))
      // reveal steps one by one so the audience follows the story
      await new Promise<void>(resolve => {
        res.steps.forEach((_, i) => {
          timers.current.push(window.setTimeout(() => {
            setRevealed(r => ({ ...r, [key]: i + 1 }))
            if (i === res.steps.length - 1) resolve()
          }, REVEAL_MS * (i + 1)))
        })
      })
    } finally { setRunning(null) }
  }
  const playAll = async () => {
    setRunningAll(true)
    for (const s of cat) await play(s.key)
    setRunningAll(false)
  }

  const passed = Object.values(results).filter(r => r.ok).length
  const total = Object.keys(results).length

  return (
    <>
      <div className="topbar">
        <div><h1>Tester le système</h1><div className="sub">Lancez des scénarios réalistes pour voir comment le système traite chaque type de demande. Chaque étape est vérifiée automatiquement.</div></div>
        <div className="row-actions" style={{ marginTop: 0 }}>
          {total > 0 && <span className={`tag ${passed === total ? 'good' : 'bad'}`}>{passed}/{total} cas conformes</span>}
          <button className="btn primary" disabled={runningAll || running !== null} onClick={playAll}><IconPlay size={14} /> Tout jouer</button>
        </div>
      </div>

      <div className="sim-grid">
        {cat.map(s => {
          const res = results[s.key]; const shown = revealed[s.key] ?? 0
          const isOpen = open === s.key
          const status = running === s.key ? 'running' : res ? (shown < res.steps.length ? 'running' : res.ok ? 'ok' : 'fail') : 'idle'
          return (
            <div className={`card sim ${isOpen ? 'open' : ''} ${status}`} key={s.key}>
              <div className="sim-head" onClick={() => setOpen(isOpen ? null : s.key)}>
                <Channel id={s.channel} size={30} />
                <div style={{ flex: 1 }}>
                  <h2 style={{ marginBottom: 2 }}>{s.title}</h2>
                  <div className="muted small">{s.customer} · {s.steps.length} étapes</div>
                </div>
                <span className={`sim-status s-${status}`}>
                  {status === 'running' ? <><IconSpinner size={14} /> en cours</> : status === 'ok' ? <><IconCheck size={14} /> conforme</> : status === 'fail' ? <><IconX size={14} /> écart</> : 'prêt'}
                </span>
                <button className="btn primary sm" disabled={running !== null} onClick={e => { e.stopPropagation(); play(s.key) }}><IconPlay size={12} /> Jouer</button>
              </div>
              <p className="small" style={{ margin: '8px 0 4px' }}>{s.summary}</p>
              <div className="proves">{s.proves.map(p => <span className="tag" key={p}>{p}</span>)}</div>

              {isOpen && (
                <ol className="sim-steps">
                  {(res ? res.steps : s.steps.map((st, i) => ({ ...st, i: i + 1, checks: [], ok: undefined as boolean | undefined, state: undefined, error: null, ms: 0, detail: '' }))).map((st, i) => {
                    const w = WHO[st.who] || WHO.system
                    const visible = res ? i < shown : false
                    const pending = res && !visible
                    return (
                      <li key={i} className={`sim-step ${visible ? (st.ok ? 'ok' : 'fail') : pending ? 'pending' : 'idle'}`}>
                        <span className={`who ${w.cls}`}><w.Icon size={13} /> {w.label}</span>
                        <div style={{ flex: 1 }}>
                          <div className="sim-label">{st.label}{st.detail && <code className="muted"> · {st.detail}</code>}</div>
                          {visible && (
                            <div className="sim-checks">
                              {st.state && <StateBadge s={st.state} />}
                              {st.checks.map((c, j) => (
                                <span key={j} className={`chk ${c.ok ? 'ok' : 'ko'}`} title={`attendu : ${JSON.stringify(c.expected)} · observé : ${JSON.stringify(c.observed)}`}>
                                  {c.ok ? <IconCheck size={11} /> : <IconX size={11} />} {c.check.replace(/_/g, ' ')}{!c.ok && <> → {String(c.observed)}</>}
                                </span>
                              ))}
                              {st.error && <span className="chk ko"><IconX size={11} /> {st.error}</span>}
                              <span className="muted small">{st.ms} ms</span>
                            </div>
                          )}
                        </div>
                        <span className="sim-mark">{visible ? (st.ok ? <IconCheck size={16} /> : <IconX size={16} />) : pending ? <IconSpinner size={14} /> : <span className="dot-idle" />}</span>
                      </li>
                    )
                  })}
                </ol>
              )}
              {res && shown >= res.steps.length && (
                <div className="sim-foot">
                  <span>Demande <Link to={`/requests/${res.request_id}`} className="mono link">{res.request_id}</Link> · état final <StateBadge s={res.steps.at(-1)?.state || ''} /></span>
                  <Link className="btn sm" to="/live">Voir le raisonnement →</Link>
                </div>
              )}
            </div>
          )
        })}
      </div>
      <p className="small muted" style={{ marginTop: 14 }}>Ces mêmes scénarios servent aussi de tests automatiques pour garantir que le système fonctionne correctement.</p>
    </>
  )
}
