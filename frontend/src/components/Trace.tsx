import { useEffect, useState } from 'react'
import { api, type Trace as TraceT } from '../lib/api'
import WorkflowSvg from './WorkflowSvg'

const fmtVal = (v: unknown) => v == null ? '—' : typeof v === 'object' ? JSON.stringify(v) : String(v)

/** Reasoning panel: lit-up graph path + every rule the orchestrator evaluated. */
export default function Trace({ id, compact = false, refreshKey = 0 }: { id: string; compact?: boolean; refreshKey?: number }) {
  const [t, setT] = useState<TraceT | null>(null)
  useEffect(() => { api.trace(id).then(setT).catch(() => setT(null)) }, [id, refreshKey])
  if (!t) return <p className="muted">Chargement du raisonnement…</p>
  return (
    <div>
      <WorkflowSvg path={t.path} waiting={t.waiting} compact={compact} />
      <div className="steps">
        {t.steps.map((s, i) => (
          <div className={`step ${s.waiting ? 'wait' : ''}`} key={i}>
            <div className="step-head"><span className="step-no">{i + 1}</span><b>{s.title}</b><span className="muted small mono">{s.node}</span></div>
            <div className="verdict">{s.verdict}</div>
            {s.checks.length > 0 && (
              <table className="checks">
                <tbody>
                  {s.checks.map((c, j) => (
                    <tr key={j} className={c.effect && c.passed ? 'fired' : ''}>
                      <td className="rule">{c.rule}</td>
                      <td className="mono">{fmtVal(c.value)}</td>
                      <td className="muted small">{c.threshold ? `seuil : ${fmtVal(c.threshold)}` : ''}</td>
                      <td className="small">{c.effect ? (c.passed ? <span className="tag warn">{c.effect}</span> : <span className="tag">{c.effect} ✗</span>) : ''}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
