import { useEffect, useState } from 'react'
import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { actorStore, api, tokenStore, type Scenario } from '../lib/api'
import { Banner } from './ui'
import { IconActivity, IconCar, IconClock, IconDashboard, IconFlask, IconInbox, IconLayers, IconList, IconLogout, IconPlus, IconPresent, IconRefresh, Logo } from './Icons'

/* Extra SVG icons for new pages */
const IconChart = ({ size = 16 }: { size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
    <line x1="18" y1="20" x2="18" y2="10" /><line x1="12" y1="20" x2="12" y2="4" /><line x1="6" y1="20" x2="6" y2="14" />
  </svg>
)
const IconTable = ({ size = 16 }: { size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="3" width="18" height="18" rx="2" /><line x1="3" y1="9" x2="21" y2="9" /><line x1="3" y1="15" x2="21" y2="15" /><line x1="9" y1="3" x2="9" y2="21" />
  </svg>
)
const IconCalendar = ({ size = 16 }: { size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="4" width="18" height="18" rx="2" /><line x1="16" y1="2" x2="16" y2="6" /><line x1="8" y1="2" x2="8" y2="6" /><line x1="3" y1="10" x2="21" y2="10" />
  </svg>
)
const IconUpload = ({ size = 16 }: { size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" /><polyline points="17 8 12 3 7 8" /><line x1="12" y1="3" x2="12" y2="15" />
  </svg>
)

const presentStore = {
  get: () => { try { return localStorage.getItem('autoflow_present') === '1' } catch { return false } },
  set: (v: boolean) => { try { localStorage.setItem('autoflow_present', v ? '1' : '0') } catch {} },
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
    try { const r = await api.live(0); setOpen(r.open_reviews); setClock(r.clock) } catch {}
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
        <div className="brand">
          <Logo />
          <div>
            AutoFlow <span style={{ color: '#0e9c99', fontWeight: 800 }}>Pro</span>
            <small>Plateforme IA · Location de voitures</small>
          </div>
        </div>

        <nav className="nav" aria-label="Navigation principale">
          {/* ─── Analyse & Aide à la décision ─── */}
          <div className="nav-section">Analyse & Décision</div>
          <NavLink to="/" end><IconDashboard size={16} /><span>Tableau de bord</span></NavLink>
          <NavLink to="/data"><IconTable size={16} /><span>Données</span></NavLink>
          <NavLink to="/appointments"><IconCalendar size={16} /><span>Rendez-vous</span></NavLink>
          <NavLink to="/excel"><IconUpload size={16} /><span>Import Excel</span></NavLink>

          {/* ─── Opérations & Logistique ─── */}
          <div className="nav-section">Opérations</div>
          <NavLink to="/queue"><IconInbox size={16} /><span>File à valider</span>{open > 0 && <span className="pill">{open}</span>}</NavLink>
          <NavLink to="/live"><IconActivity size={16} /><span>Suivi en direct</span><span className="live-dot" /></NavLink>
          <NavLink to="/requests"><IconList size={16} /><span>Demandes</span></NavLink>
          <NavLink to="/new"><IconPlus size={16} /><span>Nouvelle demande</span></NavLink>
          <NavLink to="/fleet"><IconCar size={16} /><span>Flotte & règles</span></NavLink>

          {/* ─── Ingénierie ─── */}
          <div className="nav-section">Ingénierie</div>
          <NavLink to="/architecture"><IconLayers size={16} /><span>Architecture</span></NavLink>
          <NavLink to="/simulations"><IconFlask size={16} /><span>Simulations</span></NavLink>
        </nav>

        <div className="side-block">
          <label htmlFor="actor">Utilisateur</label>
          <select id="actor" value={actor} onChange={e => { setActor(e.target.value); actorStore.set(e.target.value) }}>
            <option value="staff:Salma">Salma — équipe</option>
            <option value="staff:Youssef">Youssef — équipe</option>
            <option value="manager:Omar">Omar — manager</option>
          </select>
          <button className={`btn ghost sm full ${present ? 'on' : ''}`} onClick={() => setPresent(p => !p)} aria-pressed={present}>
            <IconPresent size={14} /> Présentation {present ? '✓' : ''}
          </button>
        </div>

        {!present && (
          <div className="side-block demo">
            <h3>Démo</h3>
            <div className="small clock"><IconClock size={12} /> {clock ? new Date(clock).toLocaleString('fr-FR', { dateStyle: 'short', timeStyle: 'short' }) : '…'}</div>
            <div className="row-actions" style={{ marginTop: 6 }}>
              {scen.map(s => (
                <button key={s.key} className="btn ghost sm" disabled={busy} title={s.title}
                  onClick={() => run(() => api.loadScenario(s.key), '/queue')}>{s.key}</button>
              ))}
            </div>
            <div className="row-actions">
              <button className="btn ghost sm" disabled={busy} onClick={() => run(() => api.advance(24))}>+24h</button>
              <button className="btn ghost sm" disabled={busy} onClick={() => run(() => api.advance(72))}>+72h</button>
              {confirmReset
                ? <button className="btn danger sm" disabled={busy}
                    onClick={() => { setConfirmReset(false); run(() => api.reset(), '/') }}>Confirmer</button>
                : <button className="btn ghost sm" disabled={busy}
                    onClick={() => setConfirmReset(true)}><IconRefresh size={12} /> Reset</button>}
            </div>
          </div>
        )}

        <button className="btn ghost sm full" style={{ marginTop: 'auto' }}
          onClick={() => { tokenStore.clear(); nav('/login') }}>
          <IconLogout size={14} /> Déconnexion
        </button>
      </aside>

      <main className="main">
        <Banner />
        <Outlet />
      </main>
    </div>
  )
}
