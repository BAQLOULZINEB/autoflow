import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { api, type SimCatalogue, type SimResult, type Trace } from '../lib/api'
import { Channel, IconBot, IconCheck, IconPlay, IconSpinner, IconUser, IconX } from '../components/Icons'
import { StateBadge } from '../components/ui'
import WorkflowSvg from '../components/WorkflowSvg'

const WHO: Record<string, { label: string; cls: string; Icon: typeof IconUser }> = {
  client: { label: 'Client', cls: 'who-client', Icon: IconUser },
  staff: { label: 'Équipe', cls: 'who-staff', Icon: IconUser },
  manager: { label: 'Manager', cls: 'who-manager', Icon: IconUser },
  system: { label: 'Système', cls: 'who-system', Icon: IconBot },
}
const REVEAL_MS = 700

type RunPanel = {
  title: string
  phase: 'processing' | 'replaying' | 'done' | 'error'
  result?: SimResult
  trace?: Trace
  visibleNodes: number
  error?: string
}

function WorkflowPanel({ panel, onClose }: { panel: RunPanel; onClose: () => void }) {
  const path = panel.trace?.path || []
  const litPath = path.slice(0, panel.visibleNodes)
  const currentNode = litPath.at(-1)
  const isWorking = panel.phase === 'processing' || panel.phase === 'replaying'

  return (
    <div className="modal-overlay workflow-overlay" role="dialog" aria-modal="true" aria-label="Workflow en direct">
      <section className="modal workflow-panel">
        <div className="workflow-panel-head">
          <div>
            <div className="eyebrow"><span className={`live-dot ${isWorking ? '' : 'done'}`} /> WORKFLOW EN DIRECT</div>
            <h2>{panel.title}</h2>
            <p className="muted small">
              {panel.phase === 'processing' && 'La demande entre dans le workflow…'}
              {panel.phase === 'replaying' && 'Le chemin réellement suivi s’affiche étape par étape.'}
              {panel.phase === 'done' && 'Traitement terminé. Vous pouvez consulter la demande complète.'}
              {panel.phase === 'error' && 'Le scénario n’a pas pu être traité.'}
            </p>
          </div>
          <button className="btn sm" onClick={onClose}>Masquer</button>
        </div>

        <div className="workflow-live-layout">
          <div className="workflow-map">
            <WorkflowSvg path={litPath} waiting={isWorking && currentNode === 'human_review'} compact />
            {isWorking && <div className="workflow-now"><IconSpinner size={14} /> {currentNode ? `Étape active : ${currentNode.replaceAll('_', ' ')}` : 'Initialisation du workflow'}</div>}
          </div>
          <ol className="workflow-node-list">
            {!panel.trace && <li className="workflow-node active"><IconSpinner size={14} /> Réception et préparation de la demande</li>}
            {panel.trace?.steps.map(step => {
              const active = litPath.includes(step.node)
              const pending = !active
              return (
                <li key={step.node} className={`workflow-node ${active ? 'complete' : pending ? 'pending' : ''}`}>
                  <span className="workflow-node-mark">{active ? <IconCheck size={14} /> : <span className="dot-idle" />}</span>
                  <span><b>{step.title}</b><small>{active ? step.verdict : 'En attente'}</small></span>
                </li>
              )
            })}
          </ol>
        </div>

        {panel.error && <p className="alert">{panel.error}</p>}
        <div className="workflow-panel-foot">
          <span className={`tag ${panel.phase === 'done' && panel.result?.ok ? 'good' : panel.phase === 'error' ? 'bad' : ''}`}>
            {isWorking ? 'Traitement en cours' : panel.result?.ok ? 'Scénario conforme' : 'Terminé'}
          </span>
          {panel.result && <div className="row-actions" style={{ marginTop: 0 }}>
            <Link className="btn sm" to={`/requests/${panel.result.request_id}`}>Voir la demande →</Link>
            <Link className="btn primary sm" to="/live">Voir le suivi en direct →</Link>
          </div>}
        </div>
      </section>
    </div>
  )
}

/** Built-in business cases: each runs through the real API and asserts every step. */
export default function Simulations() {
  const [cat, setCat] = useState<SimCatalogue[]>([])
  const [results, setResults] = useState<Record<string, SimResult>>({})
  const [revealed, setRevealed] = useState<Record<string, number>>({})
  const [running, setRunning] = useState<string | null>(null)
  const [runningAll, setRunningAll] = useState(false)
  const [open, setOpen] = useState<string | null>(null)
  const [panel, setPanel] = useState<RunPanel | null>(null)
  const timers = useRef<number[]>([])
  useEffect(() => { api.simulations().then(setCat); return () => timers.current.forEach(clearTimeout) }, [])

  const play = async (key: string) => {
    const scenario = cat.find(s => s.key === key)
    setRunning(key); setOpen(key); setRevealed(r => ({ ...r, [key]: 0 }))
    setPanel({ title: scenario?.title || 'Scénario', phase: 'processing', visibleNodes: 0 })
    try {
      const res = await api.runSimulation(key)
      setResults(r => ({ ...r, [key]: res }))
      let trace: Trace | undefined
      try { trace = await api.trace(res.request_id) } catch { /* The simulation result remains available. */ }
      const nodeCount = trace?.path.length || 0
      setPanel({ title: res.title, phase: 'replaying', result: res, trace, visibleNodes: 0 })
      // Replay the verified execution so the workflow remains readable during a live presentation.
      await new Promise<void>(resolve => {
        const frames = Math.max(res.steps.length, nodeCount, 1)
        Array.from({ length: frames }, (_, i) => i).forEach(i => {
          timers.current.push(window.setTimeout(() => {
            setRevealed(r => ({ ...r, [key]: i + 1 }))
            setPanel(current => current?.result?.request_id === res.request_id
              ? { ...current, visibleNodes: Math.min(nodeCount, i + 1), phase: i === frames - 1 ? 'done' : 'replaying' }
              : current)
            if (i === frames - 1) resolve()
          }, REVEAL_MS * (i + 1)))
        })
      })
    } catch (error) {
      setPanel(current => current ? { ...current, phase: 'error', error: error instanceof Error ? error.message : 'Erreur inconnue.' } : current)
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
      {panel && <WorkflowPanel panel={panel} onClose={() => setPanel(null)} />}
      <p className="small muted" style={{ marginTop: 14 }}>Ces mêmes scénarios servent aussi de tests automatiques pour garantir que le système fonctionne correctement.</p>
    </>
  )
}
