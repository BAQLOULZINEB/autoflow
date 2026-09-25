import { useEffect, useState } from 'react'
import { api, fmtDay } from '../lib/api'

type Fleet = Awaited<ReturnType<typeof api.fleet>>

export default function Fleet() {
  const [f, setF] = useState<Fleet | null>(null)
  const [rules, setRules] = useState<Record<string, unknown> | null>(null)
  useEffect(() => { api.fleet().then(setF); api.rules().then(setRules) }, [])
  if (!f || !rules) return <p className="muted">Chargement…</p>
  const fu = rules.follow_up as Record<string, number>
  const ag = rules.agency as Record<string, unknown>
  return (
    <>
      <div className="topbar"><div><h1>Flotte & règles</h1><div className="sub">La source de vérité de l'agent de disponibilité. Données fictives.</div></div></div>
      <div className="grid c2" style={{ alignItems: 'start' }}>
        <div>
          <div className="card" style={{ marginBottom: 14 }}>
            <h2>Véhicules ({f.vehicles.length})</h2>
            <table>
              <thead><tr><th>ID</th><th>Modèle</th><th>Cat. · boîte</th><th>Lieu</th><th>Statut</th><th>MAD/j</th></tr></thead>
              <tbody>{f.vehicles.map(v => (
                <tr key={String(v.id)}><td className="mono">{v.id}</td><td>{v.model}</td><td className="small">{v.category} · {v.transmission}</td><td>{v.location}</td>
                  <td>{v.status === 'maintenance' ? <span className="tag bad">maintenance → {fmtDay(v.maintenance_until as string)}</span> : <span className="tag">{v.status}</span>}</td><td>{v.daily_rate_mad}</td></tr>))}</tbody>
            </table>
          </div>
          <div className="card">
            <h2>Réservations ({f.bookings.length})</h2>
            <table>
              <thead><tr><th>ID</th><th>Véhicule</th><th>Du</th><th>Au</th><th>Origine</th></tr></thead>
              <tbody>{f.bookings.map(b => (
                <tr key={String(b.id)}><td className="mono">{b.id}</td><td className="mono">{b.vehicle_id}</td><td>{fmtDay(b.start_date)}</td><td>{fmtDay(b.end_date)}</td><td className="small muted">{b.request_id || 'existante'}</td></tr>))}</tbody>
            </table>
          </div>
        </div>
        <div>
          <div className="card" style={{ marginBottom: 14 }}>
            <h2>Règles métier (v{String(rules.version)})</h2>
            <table><tbody>
              <tr><th>Durée</th><td>{String(rules.min_days)} à {String(rules.max_days)} jours · auto jusqu'à {String(rules.max_auto_days)} j, au-delà : manager</td></tr>
              <tr><th>Tampon entre locations</th><td>{String(rules.buffer_hours)} h</td></tr>
              <tr><th>Décalage de dates proposé</th><td>± {String(rules.shift_days_allowed)} j</td></tr>
              <tr><th>Valeur élevée</th><td>&gt; {String(rules.high_value_threshold_mad)} MAD → manager</td></tr>
              <tr><th>Seuil de confiance</th><td>{String(rules.confidence_threshold)} global · {String(rules.critical_field_threshold)} par champ critique</td></tr>
              <tr><th>Relances</th><td>1re après {fu.first_reminder_after_h} h · max {fu.max_reminders} · sans réponse après {fu.stale_after_h} h</td></tr>
              <tr><th>Confirmation automatique</th><td><b>{rules.auto_confirm ? 'oui' : 'jamais dans le pilote'}</b></td></tr>
              <tr><th>Agence</th><td>{String(ag.name)} · caution {String(ag.deposit_mad)} MAD · {String(ag.km_per_day)} km/j</td></tr>
            </tbody></table>
            <h3 style={{ marginTop: 12 }}>Catégories de repli</h3>
            <pre className="draft">{JSON.stringify(rules.category_fallbacks, null, 2)}</pre>
            <p className="small muted" style={{ marginTop: 8 }}>Modifiables dans <code>backend/data/rules.json</code> — versionnées, jamais codées en dur dans les agents.</p>
          </div>
          <div className="card">
            <h2>Clients ({f.customers.length})</h2>
            <table><tbody>{f.customers.map(c => <tr key={String(c.id)}><td>{c.name}</td><td className="mono small">{c.phone_masked}</td><td>{c.is_vip && <span className="tag warn">régulier</span>}</td></tr>)}</tbody></table>
          </div>
        </div>
      </div>
    </>
  )
}
