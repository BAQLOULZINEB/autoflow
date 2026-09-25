import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api, fmtDate, fmtDay, INTENT_FR, STATE_FR, type Req } from '../lib/api'
import { LevelBadge, StateBadge } from '../components/ui'
import { Channel } from '../components/Icons'

export default function Requests() {
  const [rows, setRows] = useState<Req[]>([])
  const [state, setState] = useState('')
  const nav = useNavigate()
  useEffect(() => { api.requests(state || undefined).then(setRows) }, [state])
  return (
    <>
      <div className="topbar">
        <div><h1>Demandes</h1><div className="sub">{rows.length} demande(s)</div></div>
        <select style={{ width: 220 }} value={state} onChange={e => setState(e.target.value)}>
          <option value="">Tous les états</option>
          {Object.entries(STATE_FR).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
        </select>
      </div>
      <div className="card">
        <table>
          <thead><tr><th>ID</th><th>Reçue</th><th>Client · canal</th><th>Intention</th><th>Dates · catégorie</th><th>État</th><th>Message</th></tr></thead>
          <tbody>
            {rows.map(r => (
              <tr key={r.id} className="row" onClick={() => nav(`/requests/${r.id}`)}>
                <td className="mono"><b>{r.id}</b></td>
                <td className="small muted">{fmtDate(r.received_at)}</td>
                <td>{r.customer_name || '—'}<br /><Channel id={r.channel} size={16} withLabel /></td>
                <td>{INTENT_FR[r.intent || ''] || '—'}</td>
                <td className="small">{r.structured?.pickup_date ? `${fmtDay(r.structured.pickup_date)} → ${fmtDay(r.structured.return_date)}` : '—'}<br /><span className="muted">{r.structured?.vehicle_category || ''}</span></td>
                <td><StateBadge s={r.state} /> <LevelBadge l={r.review_level} /></td>
                <td className="small muted" style={{ maxWidth: 320 }}>{r.raw_message.slice(0, 90)}{r.raw_message.length > 90 ? '…' : ''}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  )
}
