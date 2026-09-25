import { useEffect, useState } from 'react'
import { api, fmtMAD, fmtDate, fmtDay, type LocationRow, type ExpenseRow } from '../lib/api'

type Tab = 'locations' | 'expenses'

export default function DataExplorer() {
  const [tab, setTab] = useState<Tab>('locations')
  const [month, setMonth] = useState(9)
  const [locations, setLocations] = useState<LocationRow[]>([])
  const [expenses, setExpenses] = useState<ExpenseRow[]>([])
  const [loading, setLoading] = useState(true)

  /* Fetch both datasets when month changes so tab counts are always accurate */
  useEffect(() => {
    setLoading(true)
    Promise.all([
      api.biLocations(month, 2026, 500),
      api.biExpensesList(month, 2026, 500),
    ]).then(([loc, exp]) => { setLocations(loc); setExpenses(exp) })
      .finally(() => setLoading(false))
  }, [month])

  const totalLoc = locations.reduce((s, l) => s + l.amount, 0)
  const totalExp = expenses.reduce((s, e) => s + e.amount, 0)

  return (
    <>
      <div className="topbar">
        <div>
          <h1>Explorateur de données</h1>
          <div className="sub">Historique complet des locations et dépenses — filtrable par mois</div>
        </div>
        <div className="row-actions" style={{ marginTop: 0, gap: 8 }}>
          <select value={month} onChange={e => setMonth(+e.target.value)} style={{ minWidth: 130 }}>
            <option value={7}>Juillet 2026</option>
            <option value={8}>Août 2026</option>
            <option value={9}>Septembre 2026</option>
          </select>
        </div>
      </div>

      <div className="tab-bar">
        <button className={tab === 'locations' ? 'active' : ''} onClick={() => setTab('locations')}>
          📋 Locations ({locations.length})
        </button>
        <button className={tab === 'expenses' ? 'active' : ''} onClick={() => setTab('expenses')}>
          💰 Dépenses ({expenses.length})
        </button>
      </div>

      {loading && <div className="progress-bar indeterminate" />}

      {tab === 'locations' && !loading && (
        <div className="card" style={{ padding: 0 }}>
          <div style={{ padding: '12px 16px', borderBottom: '1px solid var(--line)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="muted">{locations.length} locations</span>
            <span style={{ fontWeight: 700 }}>Total : {fmtMAD(totalLoc)}</span>
          </div>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>N°</th><th>Matricule</th><th>CIN</th><th>Prix/jour</th>
                  <th>Date sortie</th><th>Date entrée</th><th>Jours</th>
                  <th>Montant</th><th>Canal</th><th>Statut</th>
                </tr>
              </thead>
              <tbody>
                {locations.map(l => (
                  <tr key={l.id}>
                    <td className="mono">{l.id}</td>
                    <td className="mono">{l.plate}</td>
                    <td className="mono">{l.cin}</td>
                    <td>{fmtMAD(l.price_per_day)}</td>
                    <td>{fmtDay(l.date_out)}</td>
                    <td>{fmtDay(l.date_in)}</td>
                    <td style={{ textAlign: 'center' }}>{l.days}</td>
                    <td style={{ fontWeight: 600 }}>{fmtMAD(l.amount)}</td>
                    <td><span className="tag">{l.channel}</span></td>
                    <td><span className={`badge s-${l.status}`}>{l.status === 'terminee' ? 'Terminée' : l.status === 'en_cours' ? 'En cours' : 'Réservée'}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {tab === 'expenses' && !loading && (
        <div className="card" style={{ padding: 0 }}>
          <div style={{ padding: '12px 16px', borderBottom: '1px solid var(--line)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="muted">{expenses.length} dépenses</span>
            <span style={{ fontWeight: 700 }}>Total : {fmtMAD(totalExp)}</span>
          </div>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Date</th><th>Matricule</th><th>Catégorie</th>
                  <th>Montant</th><th>Fournisseur</th><th>Note</th>
                </tr>
              </thead>
              <tbody>
                {expenses.map(e => (
                  <tr key={e.id}>
                    <td>{fmtDay(e.date)}</td>
                    <td className="mono">{e.plate || '—'}</td>
                    <td><span className="tag">{e.category}</span></td>
                    <td style={{ fontWeight: 600 }}>{fmtMAD(e.amount)}</td>
                    <td>{e.supplier}</td>
                    <td className="muted">{e.note}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </>
  )
}
