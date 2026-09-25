import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api, fmtDate, INTENT_FR, STATE_FR, type Kpis, type Req } from '../lib/api'
import { Kpi, LevelBadge, StateBadge } from '../components/ui'
import { Channel, IconPlus } from '../components/Icons'

const COLS: [string, string[]][] = [
  ['Nouvelles / incomplètes', ['new', 'incomplete', 'checked']],
  ['Devis prêts', ['quote_ready']],
  ['Attente client', ['pending_customer', 'stalled']],
  ['À valider / escaladées', ['needs_human', 'escalated']],
  ['Confirmées / clôturées', ['confirmed', 'closed']],
]

export default function Dashboard() {
  const [k, setK] = useState<Kpis | null>(null)
  const [reqs, setReqs] = useState<Req[]>([])
  const [events, setEvents] = useState<{ id: number; request_id: string; from: string | null; to: string | null; actor: string; reason: string; ts: string }[]>([])
  const nav = useNavigate()
  useEffect(() => {
    api.kpis().then(setK); api.requests().then(setReqs); api.events(12).then(setEvents)
  }, [])
  if (!k) return <p className="muted">Chargement…</p>
  const s = k.by_state
  return (
    <>
      <div className="topbar">
        <div><h1>Tableau de bord</h1><div className="sub">Où en est chaque demande — en un écran. {k.label}.</div></div>
        <Link className="btn primary" to="/new"><IconPlus size={14} /> Nouvelle demande</Link>
      </div>

      <div className="grid c5" style={{ marginBottom: 16 }}>
        <Kpi label="Demandes" value={k.total_requests} hint="depuis le reset démo" />
        <Kpi label="À valider par une personne" value={k.reviews_open} hint={`${k.reviews_manager} pour le manager`} />
        <Kpi label="Transmissions à l'humain" value={k.human_handoffs} hint="c'est une fonctionnalité, pas un défaut" />
        <Kpi label="Relances envoyées" value={k.reminders_sent} hint={`${k.reminders_due} à envoyer`} />
        <Kpi label="Demandes complètes" value={k.complete_rate == null ? '—' : `${Math.round(k.complete_rate * 100)} %`} hint="dès le premier message" />
      </div>

      <div className="card" style={{ marginBottom: 16 }}>
        <h2>Statut des demandes</h2>
        <div className="board">
          {COLS.map(([title, states]) => {
            const items = reqs.filter(r => states.includes(r.state))
            return (
              <div className="col" key={title}>
                <h3>{title} <span>{states.reduce((a, st) => a + (s[st] || 0), 0)}</span></h3>
                {items.slice(0, 6).map(r => (
                  <div className="item" key={r.id} onClick={() => nav(`/requests/${r.id}`)}>
                    <Channel id={r.channel} size={14} /> <b>{r.id}</b> · {r.customer_name || 'Client'} <br />
                    <StateBadge s={r.state} /> <LevelBadge l={r.review_level} /> <span className="muted small">{INTENT_FR[r.intent || ''] || ''}</span>
                  </div>
                ))}
                {items.length === 0 && <div className="muted small" style={{ marginTop: 8 }}>—</div>}
              </div>
            )
          })}
        </div>
      </div>

      <div className="grid c2">
        <div className="card">
          <h2>Indicateurs — objectif pilote (à mesurer)</h2>
          <table>
            <thead><tr><th>Indicateur</th><th>Avant (audit)</th><th>Démo</th><th>Après (pilote)</th></tr></thead>
            <tbody>
              <tr><td>Temps jusqu'au 1er brouillon</td><td className="muted">à mesurer</td><td>{k.avg_seconds_to_first_draft == null ? '—' : `${k.avg_seconds_to_first_draft} s`}</td><td className="muted">à mesurer</td></tr>
              <tr><td>Demandes complètes au 1er message</td><td className="muted">à mesurer</td><td>{k.complete_rate == null ? '—' : `${Math.round(k.complete_rate * 100)} %`}</td><td className="muted">à mesurer</td></tr>
              <tr><td>Relances effectuées</td><td className="muted">à mesurer</td><td>{k.reminders_sent}</td><td className="muted">à mesurer</td></tr>
              <tr><td>Cas transmis à une personne</td><td className="muted">à mesurer</td><td>{k.human_handoffs}</td><td className="muted">à mesurer</td></tr>
              <tr><td>Événements tracés</td><td className="muted">—</td><td>{k.events}</td><td className="muted">—</td></tr>
            </tbody>
          </table>
          <p className="small muted" style={{ marginTop: 8 }}>Aucun gain chiffré n'est revendiqué avant mesure. Les compteurs viennent du journal d'événements.</p>
        </div>
        <div className="card">
          <h2>Journal récent</h2>
          <ul className="timeline">
            {events.map(e => (
              <li key={e.id}>
                <span className="muted">{fmtDate(e.ts)}</span>
                <span><Link to={`/requests/${e.request_id}`} className="mono" style={{ color: 'var(--teal)' }}>{e.request_id}</Link> <span className="actor small">{e.actor}</span></span>
                <span>{e.from !== e.to && e.to ? <><span className="arrow">→ {STATE_FR[e.to] || e.to}</span> · </> : null}{e.reason}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </>
  )
}
