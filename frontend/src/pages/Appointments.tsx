import { useEffect, useState } from 'react'
import { api, fmtDay, type AppointmentItem } from '../lib/api'

const TYPE_COLORS: Record<string, string> = {
  'Entretien garage': '#f59e0b',
  'Visite technique': '#7c3aed',
  'Renouvellement assurance': '#0ea5e9',
  'Expertise sinistre': '#e11d48',
  'Rendez-vous client': '#059669',
  'Fournisseur': '#6366f1',
}

export default function Appointments() {
  const [items, setItems] = useState<AppointmentItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.biAppointmentsList(60).then(setItems).finally(() => setLoading(false))
  }, [])

  const today = new Date().toISOString().slice(0, 10)
  const todayItems = items.filter(a => a.date === today)
  const upcoming = items.filter(a => a.date > today)

  return (
    <>
      <div className="topbar">
        <div>
          <h1>Rendez-vous & Planning</h1>
          <div className="sub">Agenda de l'agence — entretiens, visites techniques, clients</div>
        </div>
        <div className="row-actions" style={{ marginTop: 0 }}>
          <span className="tag" style={{ background: '#059669', color: '#fff' }}>{todayItems.length} aujourd'hui</span>
          <span className="tag">{upcoming.length} à venir</span>
        </div>
      </div>

      {loading && <div className="progress-bar indeterminate" />}

      {todayItems.length > 0 && (
        <div className="card" style={{ marginBottom: 16, borderLeft: '4px solid #059669' }}>
          <h2 style={{ color: '#059669', marginBottom: 12 }}>📅 Aujourd'hui</h2>
          <div className="grid c2" style={{ gap: 8 }}>
            {todayItems.map(a => (
              <div key={a.id} className="card" style={{ padding: '10px 14px', display: 'flex', gap: 12, alignItems: 'center' }}>
                <div style={{ fontWeight: 800, fontSize: 18, color: 'var(--teal)', minWidth: 50 }}>{a.time}</div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 700 }}>{a.type}</div>
                  <div className="muted small">{a.plate && `🚗 ${a.plate}`} {a.cin && `· ${a.cin}`} {a.note && `— ${a.note}`}</div>
                </div>
                <span className={`badge ${a.status === 'fait' ? 's-confirmed' : 's-pending_customer'}`}>
                  {a.status === 'fait' ? '✓ Fait' : '⏳ Prévu'}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="card" style={{ padding: 0 }}>
        <div style={{ padding: '12px 16px', borderBottom: '1px solid var(--line)' }}>
          <h2 style={{ margin: 0 }}>Tous les rendez-vous</h2>
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr><th>Date</th><th>Heure</th><th>Type</th><th>Véhicule</th><th>Client</th><th>Statut</th><th>Note</th></tr>
            </thead>
            <tbody>
              {items.map(a => (
                <tr key={a.id} style={a.date === today ? { background: 'var(--green-soft)' } : undefined}>
                  <td>{fmtDay(a.date)}</td>
                  <td style={{ fontWeight: 700 }}>{a.time}</td>
                  <td>
                    <span className="tag" style={{ background: TYPE_COLORS[a.type] || '#94a3b8', color: '#fff' }}>
                      {a.type}
                    </span>
                  </td>
                  <td className="mono">{a.plate || '—'}</td>
                  <td className="mono">{a.cin || '—'}</td>
                  <td>
                    <span className={`badge ${a.status === 'fait' ? 's-confirmed' : 's-pending_customer'}`}>
                      {a.status === 'fait' ? 'Fait' : 'Prévu'}
                    </span>
                  </td>
                  <td className="muted">{a.note}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </>
  )
}
