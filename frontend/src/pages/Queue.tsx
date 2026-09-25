import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api, fmtDate, INTENT_FR, type ReviewItem } from '../lib/api'
import { LevelBadge, StateBadge } from '../components/ui'
import { Channel } from '../components/Icons'

const ACTION_FR: Record<string, string> = { reply: 'Relire & envoyer', remind: 'Envoyer la relance', call: 'Appeler le client', escalate: 'Décision requise', close: 'Clôturer' }

export default function Queue() {
  const [items, setItems] = useState<ReviewItem[]>([])
  const nav = useNavigate()
  useEffect(() => { api.reviews().then(setItems) }, [])
  const manager = items.filter(i => i.level === 'manager')
  const staff = items.filter(i => i.level !== 'manager')
  const Table = ({ rows }: { rows: ReviewItem[] }) => (
    <table>
      <thead><tr><th>Demande</th><th>Client</th><th>État</th><th>Pourquoi une personne</th><th>Action attendue</th><th>Depuis</th></tr></thead>
      <tbody>
        {rows.map(i => (
          <tr key={i.review_id} className="row" onClick={() => nav(`/requests/${i.request_id}`)}>
            <td className="mono"><b>{i.request_id}</b><br /><span className="muted small">{INTENT_FR[i.intent || ''] || ''}</span></td>
            <td><Channel id={i.channel} size={16} /> {i.customer_name || '—'}</td>
            <td><StateBadge s={i.state} /> {i.priority === 'high' && <span className="tag bad">priorité</span>}</td>
            <td>{i.reason}</td>
            <td><LevelBadge l={i.level} /> <span className="small">{ACTION_FR[i.action || ''] || 'Valider'}</span></td>
            <td className="muted small">{fmtDate(i.opened_at)}</td>
          </tr>
        ))}
        {rows.length === 0 && <tr><td colSpan={6} className="muted">Rien à valider — la file est vide.</td></tr>}
      </tbody>
    </table>
  )
  return (
    <>
      <div className="topbar"><div><h1>File à valider</h1><div className="sub">Le système prépare ; une personne décide. Chaque ligne explique pourquoi elle est ici.</div></div></div>
      <div className="card" style={{ marginBottom: 16 }}><h2>Pour le manager ({manager.length})</h2><Table rows={manager} /></div>
      <div className="card"><h2>Pour l'équipe ({staff.length})</h2><Table rows={staff} /></div>
    </>
  )
}
