import { useEffect, useState } from 'react'
import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { actorStore, api, tokenStore, type Scenario } from '../lib/api'
import { Banner } from './ui'
import { IconActivity, IconCar, IconClock, IconDashboard, IconFlask, IconInbox, IconLayers, IconList, IconLogout, IconPlus, IconPresent, IconRefresh, Logo } from './Icons'

const presentStore = {
  get: () => { try { return localStorage.getItem('autoflow_present') === '1' } catch { return false } },
  set: (v: boolean) => { try { localStorage.setItem('autoflow_present', v ? '1' : '0') } catch { /* ignore */ } },
}

export default function Layout() {
  const nav = useNavigate()
  const [open, setOpen] = useState(0)
  const [scen, setScen] = useState<Scenario[]>([])
  const [clock, setClock] = useState('')
  const [busy, setBusy] = useState(false)
  const [actor, setActor] = useState(actorStore.get())
  const [present, setPresent] = useState(presentStore.get())
  const [confirmReset, setConfirmReset] = useState(false)

  const refresh = async () => {
    try { const r = await api.live(0); setOpen(r.open_reviews); setClock(r.clock) } catch { /* 401 handled by api */ }
  }
  useEffect(() => { refresh(); api.scenarios().then(setScen).catch(() => {}) }, [])
  useEffect(() => { const t = setInterval(refresh, 15000); return () => clearInterval(t) }, [])
  useEffect(() => { document.documentElement.classList.toggle('present', present); presentStore.set(present) }, [present])

  const run = async (fn: () => Promise<unknown>, go?: string) => {
    setBusy(true)
    try { await fn(); await refresh(); if (go) nav(go); else nav(0) } finally { setBusy(false) }
  }

  return (
    <div className="shell">
      <aside className="side">
        <div className="brand"><Logo /><div>AutoFlow<small>Espace admin · agence de location</small></div></div>
        <nav className="nav" aria-label="Navigation principale">
          <NavLink to="/" end><IconDashboard size={16} /><span>Tableau de bord</span></NavLink>
          <NavLink to="/queue"><IconInbox size={16} /><span>File à valider</span>{open > 0 && <span className="pill">{open}</span>}</NavLink>
          <NavLink to="/live"><IconActivity size={16} /><span>Suivi en direct</span><span className="live-dot" /></NavLink>
          <NavLink to="/simulations"><IconFlask size={16} /><span>Simulations</span></NavLink>
          <NavLink to="/requests"><IconList size={16} /><span>Demandes</span></NavLink>
          <NavLink to="/new"><IconPlus size={16} /><span>Nouvelle demande</span></NavLink>
          <NavLink to="/fleet"><IconCar size={16} /><span>Flotte & règles</span></NavLink>
          <NavLink to="/architecture"><IconLayers size={16} /><span>Architecture</span></NavLink>
        </nav>

        <div className="side-block">
          <label htmlFor="actor">Je suis</label>
          <select id="actor" value={actor} onChange={e => { setActor(e.target.value); actorStore.set(e.target.value) }}>
            <option value="staff:Salma">Salma — équipe</option>
            <option value="staff:Youssef">Youssef — équipe</option>
            <option value="manager:Omar">Omar — manager</option>
          </select>
          <button className={`btn ghost sm full ${present ? 'on' : ''}`} onClick={() => setPresent(p => !p)} aria-pressed={present}>
            <IconPresent size={14} /> Mode présentation {present ? 'activé' : ''}
          </button>
        </div>

        {!present && (
          <div className="side-block demo">
            <h3>Contrôles démo</h3>
            <div className="small clock"><IconClock size={12} /> {clock ? new Date(clock).toLocaleString('fr-FR', { dateStyle: 'short', timeStyle: 'short' }) : '…'}</div>
            <div className="row-actions" style={{ marginTop: 6 }}>
              {scen.map(s => <button key={s.key} className="btn ghost sm" disabled={busy} title={s.title} onClick={() => run(() => api.loadScenario(s.key), '/queue')}>Scénario {s.key}</button>)}
            </div>
            <div className="row-actions">
              <button className="btn ghost sm" disabled={busy} onClick={() => run(() => api.advance(24))}>+24 h</button>
              <button className="btn ghost sm" disabled={busy} onClick={() => run(() => api.advance(72))}>+72 h</button>
              {confirmReset
                ? <button className="btn danger sm" disabled={busy} onClick={() => { setConfirmReset(false); run(() => api.reset(), '/') }}>Confirmer le reset</button>
                : <button className="btn ghost sm" disabled={busy} onClick={() => setConfirmReset(true)}><IconRefresh size={12} /> Reset</button>}
            </div>
          </div>
        )}
        <button className="btn ghost sm full" style={{ marginTop: 'auto' }} onClick={() => { tokenStore.clear(); nav('/login') }}><IconLogout size={14} /> Déconnexion</button>
      </aside>
      <main className="main">
        <Banner />
        <Outlet />
      </main>
    </div>
  )
}
