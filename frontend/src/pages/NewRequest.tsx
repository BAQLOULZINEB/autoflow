import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api, type Scenario } from '../lib/api'
import { Channel } from '../components/Icons'

export default function NewRequest() {
  const [msg, setMsg] = useState('')
  const [name, setName] = useState('')
  const [channel, setChannel] = useState('whatsapp')
  const [scen, setScen] = useState<Scenario[]>([])
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState('')
  const nav = useNavigate()
  useEffect(() => { api.scenarios().then(setScen) }, [])
  const submit = async (e: React.FormEvent) => {
    e.preventDefault(); setBusy(true); setErr('')
    try { const d = await api.createRequest({ message: msg, channel, customer_name: name }); nav(`/requests/${d.id}`) }
    catch (x) { setErr((x as Error).message) } finally { setBusy(false) }
  }
  return (
    <>
      <div className="topbar"><div><h1>Nouvelle demande</h1><div className="sub">Collez un message WhatsApp / Facebook / formulaire tel quel — le workflow s'en charge.</div></div></div>
      <div className="grid c2" style={{ alignItems: 'start' }}>
        <form className="card" onSubmit={submit}>
          {err && <div className="alert">{err}</div>}
          <label>Message client</label>
          <textarea value={msg} onChange={e => setMsg(e.target.value)} placeholder="Salam, je voudrais louer une citadine du 12 au 15 octobre…" required />
          <div className="grid c2">
            <div><label>Nom client (optionnel)</label><input value={name} onChange={e => setName(e.target.value)} placeholder="Karim B." /></div>
            <div><label>Canal</label><select value={channel} onChange={e => setChannel(e.target.value)}>
              {[['whatsapp', 'WhatsApp'], ['facebook', 'Facebook'], ['instagram', 'Instagram'], ['form', 'Site web'], ['phone', 'Téléphone'], ['walk-in', 'Comptoir'], ['email', 'E-mail']].map(([v, l]) => <option key={v} value={v}>{l}</option>)}</select></div>
          </div>
          <button className="btn primary" style={{ marginTop: 14 }} disabled={busy}>{busy ? 'Analyse…' : 'Analyser la demande'}</button>
        </form>
        <div className="card">
          <h2>Scénarios de démonstration</h2>
          {scen.map(s => (
            <div key={s.key} style={{ borderBottom: '1px solid var(--line)', padding: '8px 0' }}>
              <Channel id={s.channel} size={16} /> <b>{s.key} — {s.title}</b> <button className="btn sm" type="button" onClick={() => { setMsg(s.message); setName(s.customer); setChannel(s.channel) }}>Utiliser</button>
              <div className="draft small" style={{ margin: '6px 0' }}>{s.message}</div>
              <div className="small muted">Attendu : {s.expected}</div>
            </div>
          ))}
        </div>
      </div>
    </>
  )
}
