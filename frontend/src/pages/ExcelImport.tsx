import { useRef, useState } from 'react'
import { api, type ExcelImportResult } from '../lib/api'

export default function ExcelImport() {
  const [result, setResult] = useState<ExcelImportResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [dragOver, setDragOver] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  const upload = async (file: File) => {
    setLoading(true); setError(''); setResult(null)
    try {
      const r = await api.excelImport(file)
      setResult(r)
    } catch (e: any) {
      setError(e.message || 'Erreur lors de l\'import')
    } finally {
      setLoading(false)
    }
  }

  const seedDemo = async () => {
    setLoading(true); setError(''); setResult(null)
    try {
      const r = await api.excelSeed()
      setResult(r)
    } catch (e: any) {
      setError(e.message || 'Erreur')
    } finally {
      setLoading(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault(); setDragOver(false)
    const f = e.dataTransfer.files[0]
    if (f && f.name.endsWith('.xlsx')) upload(f)
    else setError('Seuls les fichiers .xlsx sont acceptés.')
  }

  return (
    <>
      <div className="topbar">
        <div>
          <h1>Importer un fichier Excel</h1>
          <div className="sub">Ajoutez vos données depuis un fichier Excel</div>
        </div>
      </div>

      <div className="grid c2">
        <div
          className={`card ${dragOver ? 'drag-over' : ''}`}
          style={{
            border: dragOver ? '2px dashed var(--teal)' : '2px dashed var(--line)',
            textAlign: 'center', padding: '40px 24px', cursor: 'pointer',
            transition: 'border-color .2s, background .2s',
            background: dragOver ? 'var(--teal-soft)' : 'var(--paper)',
          }}
          onClick={() => inputRef.current?.click()}
          onDragOver={e => { e.preventDefault(); setDragOver(true) }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
        >
          <div style={{ marginBottom: 12 }}><svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#0e9c99" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg></div>
          <h2>Glissez votre fichier ici</h2>
          <p className="muted">ou cliquez pour choisir un fichier</p>
          <p className="muted small">Feuilles attendues : Locations, Flotte, Clients, Depenses, RendezVous</p>
          <input ref={inputRef} type="file" accept=".xlsx,.xlsm" hidden
            onChange={e => { const f = e.target.files?.[0]; if (f) upload(f) }} />
        </div>

        <div className="card">
          <h2>Données de démonstration</h2>
          <p className="muted" style={{ marginBottom: 16 }}>
            Charger le fichier <code>autoflow_agence.xlsx</code> généré avec des données fictives réalistes
            basées sur les tarifs réels du marché marocain (Juillet–Septembre 2026).
          </p>
          <p className="muted small" style={{ marginBottom: 16 }}>
            38 véhicules · 200 clients · ~530 locations · ~220 dépenses · ~24 rendez-vous
          </p>
          <button className="btn primary" onClick={seedDemo} disabled={loading}>
            {loading ? 'Import en cours…' : 'Charger les données démo'}
          </button>
        </div>
      </div>

      {loading && <div className="progress-bar indeterminate" style={{ marginTop: 16 }} />}

      {error && (
        <div className="banner error" style={{ marginTop: 16 }}>
          {error}
        </div>
      )}

      {result && (
        <div className="card" style={{ marginTop: 16 }}>
          <h2 style={{ color: result.ok ? 'var(--green)' : 'var(--rose)' }}>
            {result.ok ? 'Import réussi' : 'Import avec erreurs'}
          </h2>

          <div className="grid c3" style={{ marginTop: 12 }}>
            {Object.entries(result.sheets).map(([name, stats]) => (
              <div key={name} className="kpi card">
                <div className="label">{name}</div>
                <div className="value" style={{ fontSize: 20 }}>{(stats as any).importés ?? 0}</div>
                <div className="hint">{(stats as any).ignorés > 0 ? `${(stats as any).ignorés} ignorés` : 'Complet'}</div>
              </div>
            ))}
          </div>

          {result.warnings.length > 0 && (
            <details style={{ marginTop: 16 }}>
              <summary className="muted" style={{ cursor: 'pointer', fontWeight: 600 }}>
                {result.warnings.length} avertissement(s)
              </summary>
              <ul style={{ marginTop: 8, fontSize: 12, color: 'var(--muted)' }}>
                {result.warnings.slice(0, 30).map((w, i) => <li key={i}>{w}</li>)}
                {result.warnings.length > 30 && <li>… et {result.warnings.length - 30} de plus</li>}
              </ul>
            </details>
          )}

          {result.errors.length > 0 && (
            <div style={{ marginTop: 12, color: 'var(--rose)' }}>
              {result.errors.map((e, i) => <p key={i}>{e}</p>)}
            </div>
          )}
        </div>
      )}
    </>
  )
}
