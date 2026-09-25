import { useState } from 'react'
import { api } from '../lib/api'

/** Customer-facing form (no auth). Same endpoint an n8n / WhatsApp webhook would hit. */
export default function PublicIntake() {
  const [name, setName] = useState('')
  const [msg, setMsg] = useState('')
  const [done, setDone] = useState<string | null>(null)
  const [err, setErr] = useState('')
  const [busy, setBusy] = useState(false)
  const submit = async (e: React.FormEvent) => {
    e.preventDefault(); setBusy(true); setErr('')
    try { const r = await api.publicIntake({ message: msg, channel: 'form', customer_name: name }); setDone(r.message) }
    catch (x) { setErr((x as Error).message) } finally { setBusy(false) }
  }
  return (
    <div className="public">
      <div className="card">
        <h1>Demande de location</h1>
        <p className="muted">Décrivez votre besoin (dates, type de véhicule, lieu). Un membre de l'agence vous répond rapidement.</p>
        {done ? <div className="ok">{done}</div> : (
          <form onSubmit={submit}>
            {err && <div className="alert">{err}</div>}
            <label>Votre nom</label><input value={name} onChange={e => setName(e.target.value)} required />
            <label>Votre demande</label>
            <textarea value={msg} onChange={e => setMsg(e.target.value)} required placeholder="Ex. : une citadine du 12 au 15 octobre, prise à Agdal." />
            <button className="btn primary" style={{ marginTop: 12 }} disabled={busy}>{busy ? 'Envoi…' : 'Envoyer ma demande'}</button>
          </form>
        )}
        <p className="small muted" style={{ marginTop: 14 }}>Démonstration — aucune donnée réelle. Vos informations ne sont utilisées que pour traiter cette demande.</p>
      </div>
    </div>
  )
}
