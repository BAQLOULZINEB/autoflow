import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api, tokenStore } from '../lib/api'

export default function Login() {
  const [token, setToken] = useState('')
  const [err, setErr] = useState('')
  const nav = useNavigate()
  const submit = async (e: React.FormEvent) => {
    e.preventDefault(); setErr('')
    try { await api.login(token); tokenStore.set(token); nav('/') }
    catch { setErr('Token invalide. Vérifiez ADMIN_TOKEN côté backend.') }
  }
  return (
    <div className="login">
      <form className="card" onSubmit={submit}>
        <h1>AutoFlow <span style={{ color: '#0e9c99', fontWeight: 800 }}>Pro</span></h1>
        <p className="muted">Espace admin — système d'automatisation supervisé des workflows d'une agence de location.</p>
        <label>Token administrateur</label>
        <input type="password" value={token} onChange={e => setToken(e.target.value)} placeholder="change-me-admin" autoFocus />
        {err && <p className="alert" style={{ marginTop: 10 }}>{err}</p>}
        <button className="btn primary" style={{ width: '100%', marginTop: 14 }}>Entrer</button>
        <p className="small muted" style={{ marginTop: 12 }}>Démo : le token par défaut est <code>change-me-admin</code>. Formulaire client public : <a href="/demande" style={{ color: 'var(--teal)' }}>/demande</a></p>
      </form>
    </div>
  )
}
