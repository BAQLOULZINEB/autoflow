import { useEffect, useRef, useState } from 'react'
import { api, type GarageVehicle, fmtMAD, fmtDay } from '../lib/api'

const CAT_COLORS: Record<string, string> = {
  citadine: '#0e9c99', berline: '#2563eb', suv: '#f59e0b',
  '4x4': '#dc2626', utilitaire: '#6b7280', premium: '#7c3aed',
}

const STATUS_META: Record<string, { label: string; color: string; bg: string }> = {
  disponible: { label: 'Disponible', color: '#16a34a', bg: '#dcfce7' },
  en_location: { label: 'En location', color: '#d97706', bg: '#fef3c7' },
  maintenance: { label: 'En maintenance', color: '#dc2626', bg: '#fee2e2' },
}

const CAT_LABELS: Record<string, string> = {
  citadine: 'Citadine', berline: 'Berline', suv: 'SUV',
  '4x4': '4x4', utilitaire: 'Utilitaire', premium: 'Premium',
}

type OfficialPhoto = { url: string; source: string | null; year: number | null; provider: 'official' | 'agency' | 'kifal' | null }

const photoCache = new Map<string, OfficialPhoto | null>()
const photoRequests = new Map<string, Promise<OfficialPhoto | null>>()

async function findOfficialPhoto(model: string): Promise<OfficialPhoto | null> {
  if (photoCache.has(model)) return photoCache.get(model) || null
  if (photoRequests.has(model)) return photoRequests.get(model)!

  const request = (async () => {
    try {
      const result = await api.officialVehicleImage(model)
      const photo = result.image_url
        ? { url: result.image_url, source: result.source_url, year: result.model_year, provider: result.source_type }
        : null
      photoCache.set(model, photo)
      return photo
    } catch {
      photoCache.set(model, null)
      return null
    } finally {
      photoRequests.delete(model)
    }
  })()
  photoRequests.set(model, request)
  return request
}

function VehiclePhoto({ model, category, status }: Pick<GarageVehicle, 'model' | 'category' | 'status'>) {
  const holder = useRef<HTMLDivElement>(null)
  const [visible, setVisible] = useState(false)
  const [photo, setPhoto] = useState<OfficialPhoto | null | undefined>(undefined)

  useEffect(() => {
    const target = holder.current
    if (!target) return
    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) { setVisible(true); observer.disconnect() }
    }, { rootMargin: '240px' })
    observer.observe(target)
    return () => observer.disconnect()
  }, [])
  useEffect(() => { if (visible) void findOfficialPhoto(model).then(setPhoto) }, [model, visible])

  const meta = STATUS_META[status] || STATUS_META.disponible
  const sourceLabel = photo?.provider === 'kifal' ? 'Visuel Kifal · voir le modèle' : 'Visuel officiel · voir le modèle'
  return (
    <div className={`garage-photo ${photo ? 'has-photo' : ''}`} ref={holder}>
      {photo && <img src={photo.url} alt={`Photo d’une ${model}`} loading="lazy" onError={() => setPhoto(null)} />}
      <div className="garage-photo-shade" />
      <span className="garage-category">{CAT_LABELS[category] || category}{photo?.year ? ` · ${photo.year}+` : ''}</span>
      <span className="garage-status" style={{ background: meta.bg, color: meta.color }}>{meta.label}</span>
      {photo ? (photo.source
        ? <a className="garage-attribution" href={photo.source} target="_blank" rel="noreferrer" onClick={event => event.stopPropagation()}>{sourceLabel}</a>
        : <span className="garage-attribution">Visuel validé · agence</span>
      ) : <span className="garage-photo-loading">{visible ? 'Visuel officiel indisponible' : 'Chargement du visuel officiel…'}</span>}
    </div>
  )
}

function MiniKPI({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return (
    <div className="garage-mini-kpi">
      <div className="garage-mini-label">{label}</div>
      <div className="garage-mini-value">{value}</div>
      {sub && <div className="garage-mini-sub">{sub}</div>}
    </div>
  )
}

function OccupancyBar({ pct }: { pct: number }) {
  const color = pct > 70 ? '#16a34a' : pct > 40 ? '#f59e0b' : '#dc2626'
  return (
    <div style={{ width: '100%', height: 6, borderRadius: 3, background: 'var(--line)', overflow: 'hidden' }}>
      <div style={{ width: `${Math.min(100, pct)}%`, height: '100%', borderRadius: 3, background: color, transition: 'width .4s ease' }} />
    </div>
  )
}

function VehicleCard({ v, onClick, expanded }: { v: GarageVehicle; onClick: () => void; expanded: boolean }) {
  const catColor = CAT_COLORS[v.category] || '#64748b'

  return (
    <div
      className="card garage-vehicle-card"
      onClick={onClick}
      style={{
        cursor: 'pointer',
        border: expanded ? `2px solid ${catColor}` : '1px solid var(--line)',
        transition: 'all .25s ease',
        padding: 0,
        overflow: 'hidden',
      }}
    >
      <VehiclePhoto model={v.model} category={v.category} status={v.status} />

      <div className="garage-vehicle-head" style={{ background: `linear-gradient(135deg, ${catColor}14, ${catColor}05)` }}>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ fontWeight: 800, fontSize: 17, color: 'var(--ink)' }}>{v.model}</div>
          <div style={{ fontSize: 12, color: 'var(--muted)', marginTop: 2 }}>
            {v.plate} · {CAT_LABELS[v.category] || v.category} · {v.transmission}
          </div>
          <div style={{ fontSize: 12, color: 'var(--muted)' }}>
            {v.location} · {fmtMAD(v.daily_rate)}/jour
          </div>
        </div>
      </div>

      {/* Quick stats row */}
      <div className="garage-stat-grid">
        <MiniKPI label="Revenus" value={fmtMAD(v.revenue)} />
        <MiniKPI label="Depenses" value={fmtMAD(v.expenses)} />
        <MiniKPI label="Profit" value={fmtMAD(v.profit)} />
        <MiniKPI label="Locations" value={String(v.rental_count)} />
      </div>

      {/* Occupancy bar */}
      <div style={{ padding: '0 20px 12px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, color: 'var(--muted)', marginBottom: 4 }}>
          <span>Taux d'occupation</span>
          <span style={{ fontWeight: 600 }}>{v.occupancy_pct}%</span>
        </div>
        <OccupancyBar pct={v.occupancy_pct} />
      </div>

      {/* Expanded details */}
      {expanded && (
        <div style={{
          borderTop: '1px solid var(--line)',
          padding: '16px 20px',
          animation: 'fadeSlideDown .25s ease',
        }}>
          {v.maintenance_until && (
            <div style={{ fontSize: 12, color: '#dc2626', marginBottom: 12, padding: '6px 10px', background: '#fee2e2', borderRadius: 6 }}>
              Maintenance jusqu'au {fmtDay(v.maintenance_until)}
            </div>
          )}

          {/* Recent rentals */}
          {v.recent_rentals.length > 0 && (
            <div style={{ marginBottom: 16 }}>
              <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--ink)', marginBottom: 8 }}>
                Dernieres locations
              </div>
              <table style={{ width: '100%', fontSize: 11, borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ color: 'var(--muted)', borderBottom: '1px solid var(--line)' }}>
                    <th style={{ textAlign: 'left', padding: '4px 0', fontWeight: 500 }}>Client</th>
                    <th style={{ textAlign: 'left', padding: '4px 0', fontWeight: 500 }}>Sortie</th>
                    <th style={{ textAlign: 'left', padding: '4px 0', fontWeight: 500 }}>Retour</th>
                    <th style={{ textAlign: 'right', padding: '4px 0', fontWeight: 500 }}>Montant</th>
                  </tr>
                </thead>
                <tbody>
                  {v.recent_rentals.map(r => (
                    <tr key={r.id} style={{ borderBottom: '1px solid var(--line)' }}>
                      <td style={{ padding: '6px 0', color: 'var(--ink)' }}>{r.cin}</td>
                      <td style={{ padding: '6px 0', color: 'var(--muted)' }}>{fmtDay(r.date_out)}</td>
                      <td style={{ padding: '6px 0', color: 'var(--muted)' }}>{fmtDay(r.date_in)}</td>
                      <td style={{ padding: '6px 0', textAlign: 'right', fontWeight: 600, color: 'var(--ink)' }}>{fmtMAD(r.amount)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Upcoming appointments */}
          {v.appointments.length > 0 && (
            <div>
              <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--ink)', marginBottom: 8 }}>
                Prochains rendez-vous
              </div>
              {v.appointments.map((a, i) => (
                <div key={i} style={{
                  display: 'flex', gap: 12, alignItems: 'center', fontSize: 12,
                  padding: '6px 0', borderBottom: i < v.appointments.length - 1 ? '1px solid var(--line)' : 'none',
                }}>
                  <span style={{ color: 'var(--teal)', fontWeight: 600, minWidth: 75 }}>{fmtDay(a.date)}</span>
                  <span style={{ color: 'var(--muted)' }}>{a.time}</span>
                  <span style={{ color: 'var(--ink)' }}>{a.type}</span>
                  {a.note && <span style={{ color: 'var(--muted)', fontSize: 11 }}>— {a.note}</span>}
                </div>
              ))}
            </div>
          )}

          {v.recent_rentals.length === 0 && v.appointments.length === 0 && (
            <div style={{ fontSize: 12, color: 'var(--muted)', textAlign: 'center', padding: 12 }}>
              Aucune activite recente pour ce vehicule
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default function Garage() {
  const [vehicles, setVehicles] = useState<GarageVehicle[]>([])
  const [loading, setLoading] = useState(true)
  const [expanded, setExpanded] = useState<string | null>(null)
  const [filter, setFilter] = useState<string>('all')
  const [catFilter, setCatFilter] = useState<string>('all')
  const [search, setSearch] = useState('')

  useEffect(() => {
    api.biFleetGarage()
      .then(items => {
        setVehicles(items)
        void api.warmVehicleImages()
      })
      .finally(() => setLoading(false))
  }, [])

  const categories = [...new Set(vehicles.map(v => v.category))]
  const statusCounts = vehicles.reduce((acc, v) => {
    acc[v.status] = (acc[v.status] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  const filtered = vehicles.filter(v => {
    if (filter !== 'all' && v.status !== filter) return false
    if (catFilter !== 'all' && v.category !== catFilter) return false
    if (search) {
      const q = search.toLowerCase()
      return v.model.toLowerCase().includes(q) || v.plate.toLowerCase().includes(q) || v.code.toLowerCase().includes(q)
    }
    return true
  })

  const totalRevenue = vehicles.reduce((s, v) => s + v.revenue, 0)
  const totalProfit = vehicles.reduce((s, v) => s + v.profit, 0)
  const avgOccupancy = vehicles.length ? Math.round(vehicles.reduce((s, v) => s + v.occupancy_pct, 0) / vehicles.length) : 0

  return (
    <>
      <div className="topbar">
        <div>
          <h1>Mes voitures</h1>
          <div className="sub">Vue d'ensemble de votre flotte et de l'activite de chaque vehicule</div>
        </div>
      </div>

      {/* Fleet summary KPIs */}
      <div className="grid c4" style={{ marginBottom: 24 }}>
        <div className="card kpi" style={{ borderLeft: '4px solid var(--teal)' }}>
          <div className="label">Vehicules au total</div>
          <div className="value">{vehicles.length}</div>
        </div>
        <div className="card kpi" style={{ borderLeft: '4px solid #16a34a' }}>
          <div className="label">Revenus totaux</div>
          <div className="value">{fmtMAD(totalRevenue)}</div>
        </div>
        <div className="card kpi" style={{ borderLeft: '4px solid #2563eb' }}>
          <div className="label">Profit total</div>
          <div className="value">{fmtMAD(totalProfit)}</div>
        </div>
        <div className="card kpi" style={{ borderLeft: '4px solid #f59e0b' }}>
          <div className="label">Occupation moyenne</div>
          <div className="value">{avgOccupancy}%</div>
        </div>
      </div>

      {/* Filters */}
      <div className="card" style={{ marginBottom: 20, padding: '12px 20px', display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap' }}>
        {/* Status pills */}
        <button className={`btn ${filter === 'all' ? 'primary' : ''}`} onClick={() => setFilter('all')}
          style={{ fontSize: 12, padding: '4px 12px' }}>
          Toutes ({vehicles.length})
        </button>
        {Object.entries(STATUS_META).map(([key, meta]) => (
          <button key={key} className={`btn ${filter === key ? 'primary' : ''}`} onClick={() => setFilter(key)}
            style={{ fontSize: 12, padding: '4px 12px', borderColor: meta.color, color: filter === key ? '#fff' : meta.color,
              background: filter === key ? meta.color : 'transparent' }}>
            {meta.label} ({statusCounts[key] || 0})
          </button>
        ))}

        <div style={{ width: 1, height: 24, background: 'var(--line)', margin: '0 4px' }} />

        {/* Category filter */}
        <select value={catFilter} onChange={e => setCatFilter(e.target.value)}
          style={{ fontSize: 12, padding: '4px 8px', border: '1px solid var(--line)', borderRadius: 6,
            background: 'var(--paper)', color: 'var(--ink)' }}>
          <option value="all">Toutes les categories</option>
          {categories.map(c => (
            <option key={c} value={c}>{CAT_LABELS[c] || c}</option>
          ))}
        </select>

        {/* Search */}
        <input type="text" placeholder="Rechercher un vehicule..." value={search}
          onChange={e => setSearch(e.target.value)}
          style={{ fontSize: 12, padding: '5px 12px', border: '1px solid var(--line)', borderRadius: 6,
            background: 'var(--paper)', color: 'var(--ink)', flex: 1, minWidth: 160 }} />
      </div>

      {/* Vehicle grid */}
      {loading ? (
        <div className="progress-bar indeterminate" />
      ) : filtered.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: 40, color: 'var(--muted)' }}>
          Aucun vehicule ne correspond aux filtres selectionnes
        </div>
      ) : (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))',
          gap: 16,
        }}>
          {filtered.map(v => (
            <VehicleCard
              key={v.code}
              v={v}
              expanded={expanded === v.code}
              onClick={() => setExpanded(expanded === v.code ? null : v.code)}
            />
          ))}
        </div>
      )}

      <style>{`
        @keyframes fadeSlideDown {
          from { opacity: 0; transform: translateY(-8px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </>
  )
}
