import { useCallback, useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { actorStore, api, fmtDate, fmtDay, INTENT_FR, STATE_FR, type Option, type ReqDetail } from '../lib/api'
import { Flag, LevelBadge, StateBadge } from '../components/ui'
import Trace from '../components/Trace'
import { Channel } from '../components/Icons'

const TABS = ['Raisonnement', 'Structurée', 'Disponibilité', 'Brouillon', 'Relance', 'Journal'] as const

export default function RequestDetail() {
  const { id = '' } = useParams()
  const [r, setR] = useState<ReqDetail | null>(null)
  const [tab, setTab] = useState<typeof TABS[number]>('Raisonnement')
  const [tick, setTick] = useState(0)
  const [body, setBody] = useState('')
  const [note, setNote] = useState('')
  const [fields, setFields] = useState<Record<string, string>>({})
  const [err, setErr] = useState('')
  const [busy, setBusy] = useState(false)

  const load = useCallback(async () => {
    const d = await api.request(id); setR(d)
    setBody(d.followup?.draft_fr || d.drafts.at(-1)?.body_fr || '')
    setFields({ pickup_date: d.structured.pickup_date || '', return_date: d.structured.return_date || '',
      vehicle_category: d.structured.vehicle_category || '', pickup_location: d.structured.pickup_location || '' })
  }, [id])
  useEffect(() => { load() }, [load])

  const act = async (action: string, extra: Record<string, unknown> = {}) => {
    setBusy(true); setErr('')
    try {
      const actor = actorStore.get()
      if (action === 'customer_yes' || action === 'customer_no') await api.customerReply(id, action === 'customer_yes', actor)
      else await api.decide(id, { action, actor, note, ...extra })
      await load(); setTick(t => t + 1)
    } catch (e) { setErr((e as Error).message) } finally { setBusy(false) }
  }

  if (!r) return <p className="muted">Chargement…</p>
  const s = r.structured, a = r.availability, f = r.followup
  const waiting = !!r.pending_interrupt
  const reminderDue = r.follow_ups.some(x => x.status === 'due')
  const isManagerNeeded = r.review_level === 'manager'
  const actor = actorStore.get()
  const canDecide = !isManagerNeeded || actor.startsWith('manager')
  const conf = (k: string) => { const v = s.field_confidence?.[k]; return v == null ? '' : ` (${Math.round(v * 100)} %)` }

  const OptRow = ({ o, alt }: { o: Option; alt?: boolean }) => (
    <tr><td className="mono">{o.vehicle_id}</td><td>{o.model}<br /><span className="muted small">{o.category} · {o.transmission} · {o.location}</span></td>
      <td className="small">{fmtDay(o.pickup_date)} → {fmtDay(o.return_date)}<br /><span className="muted">{o.days} j</span></td>
      <td><b>{o.total_mad} MAD</b><br /><span className="muted small">{o.daily_rate_mad} MAD/j</span></td>
      <td className="small">{alt ? <span className="tag warn">{o.note || 'alternative'}</span> : <span className="tag">disponible</span>}</td></tr>
  )

  return (
    <>
      <div className="topbar">
        <div>
          <h1>Demande {r.id} <StateBadge s={r.state} /> <LevelBadge l={r.review_level} /> {r.priority === 'high' && <span className="tag bad">priorité haute</span>}</h1>
          <div className="sub"><Channel id={r.channel} size={16} withLabel /> · {r.customer_name || 'Client'} · reçue {fmtDate(r.received_at)} · {INTENT_FR[r.intent || ''] || '—'} · extraction <code>{s.engine}</code></div>
        </div>
      </div>
      {err && <div className="alert">{err}</div>}

      <div className="grid c2" style={{ alignItems: 'start' }}>
        <div>
          <div className="card" style={{ marginBottom: 14 }}>
            <h2>Message client</h2>
            <div className="draft">{r.raw_message}</div>
          </div>

          <div className="card">
            <div className="tabs">{TABS.map(t => <button key={t} className={tab === t ? 'active' : ''} onClick={() => setTab(t)}>{t}</button>)}</div>

            {tab === 'Raisonnement' && <Trace id={id} compact refreshKey={tick} />}

            {tab === 'Structurée' && (
              <>
                <table>
                  <tbody>
                    <tr><th>Intention</th><td>{INTENT_FR[s.intent || ''] || s.intent}{conf('intent')}</td></tr>
                    <tr><th>Prise en charge</th><td>{fmtDay(s.pickup_date)}{conf('pickup_date')}</td></tr>
                    <tr><th>Retour</th><td>{fmtDay(s.return_date)}{conf('return_date')}</td></tr>
                    <tr><th>Catégorie</th><td>{s.vehicle_category || <span className="tag bad">manquante</span>}{conf('vehicle_category')}</td></tr>
                    <tr><th>Boîte</th><td>{s.transmission || '—'}</td></tr>
                    <tr><th>Lieu</th><td>{s.pickup_location || '—'} → {s.return_location || '—'}</td></tr>
                    <tr><th>Budget</th><td>{s.budget_mad ? `${s.budget_mad} MAD` : '—'}</td></tr>
                    <tr><th>Confiance globale</th><td><b>{Math.round((s.confidence || 0) * 100)} %</b></td></tr>
                    <tr><th>Signaux</th><td>{(s.flags || []).map(x => <Flag key={x} f={x} />)}{(s.flags || []).length === 0 && '—'}</td></tr>
                    <tr><th>Manquants</th><td>{(s.missing_fields || []).join(', ') || 'aucun'}</td></tr>
                  </tbody>
                </table>
                {s.evidence && Object.keys(s.evidence).length > 0 && (
                  <p className="small muted" style={{ marginTop: 10 }}>Preuves dans le texte : {Object.entries(s.evidence).map(([k, v]) => <span className="tag" key={k}>{k} = « {v} »</span>)}</p>
                )}
              </>
            )}

            {tab === 'Disponibilité' && (
              a?.status ? (
                <>
                  <p>Résultat : <b>{{ available: 'Disponible', alternative: 'Alternative proposée', unavailable: 'Indisponible', invalid: 'Demande invalide' }[a.status] || a.status}</b> · {a.days} jour(s) · calcul déterministe, aucun LLM.</p>
                  <table>
                    <thead><tr><th>Véhicule</th><th>Modèle</th><th>Dates</th><th>Total</th><th></th></tr></thead>
                    <tbody>
                      {(a.options || []).map(o => <OptRow key={o.vehicle_id + o.pickup_date} o={o} />)}
                      {(a.alternatives || []).map(o => <OptRow key={'alt' + o.vehicle_id + o.pickup_date} o={o} alt />)}
                    </tbody>
                  </table>
                  {(a.reasons || []).length > 0 && <><h3 style={{ marginTop: 12 }}>Pourquoi ces exclusions</h3><ul className="small muted">{a.reasons!.map((x, i) => <li key={i}>{x}</li>)}</ul></>}
                </>
              ) : <p className="muted">Pas encore vérifiée (demande incomplète ou réclamation).</p>
            )}

            {tab === 'Brouillon' && (
              <>
                {r.drafts.length === 0 && <p className="muted">Aucun brouillon généré automatiquement pour ce cas.</p>}
                {r.drafts.map(d => (
                  <div key={d.id} style={{ marginBottom: 12 }}>
                    <div className="small muted"><span className="tag">{d.kind}</span> {fmtDate(d.generated_at)} {d.sent_at && <span className="tag">envoyé par {d.sent_by} · {fmtDate(d.sent_at)}</span>} {d.edited && <span className="tag warn">modifié</span>}</div>
                    <div className="draft">{d.body_fr}</div>
                  </div>
                ))}
                {f?.rationale && <p className="small muted">Justification : {f.rationale}</p>}
              </>
            )}

            {tab === 'Relance' && (
              <>
                <p>Action recommandée : <b>{{ reply: 'Répondre', remind: 'Relancer', call: 'Appeler', escalate: 'Escalader', close: 'Clôturer' }[f?.action || ''] || '—'}</b>{f?.next_check_at && <> · prochaine vérification {fmtDate(f.next_check_at)}</>}</p>
                <table>
                  <thead><tr><th>#</th><th>Échéance</th><th>Statut</th><th>Issue</th></tr></thead>
                  <tbody>{r.follow_ups.map(x => <tr key={x.id}><td>{x.reminder_no}</td><td>{fmtDate(x.due_at)}</td><td><span className="tag">{x.status}</span></td><td className="muted small">{x.outcome || '—'}</td></tr>)}
                    {r.follow_ups.length === 0 && <tr><td colSpan={4} className="muted">Aucune relance planifiée (planifiée à l'envoi de la réponse).</td></tr>}</tbody>
                </table>
              </>
            )}

            {tab === 'Journal' && (
              <ul className="timeline">
                {r.events.map(e => (
                  <li key={e.id}><span className="muted">{fmtDate(e.ts)}</span><span className="actor">{e.actor}</span>
                    <span>{e.from !== e.to && e.to ? <span className="arrow">{STATE_FR[e.from || ''] || e.from} → {STATE_FR[e.to] || e.to} · </span> : null}{e.reason}</span></li>
                ))}
              </ul>
            )}
          </div>
        </div>

        {/* ---- decision panel ---- */}
        <div className="card" style={{ position: 'sticky', top: 16 }}>
          <h2>Décision humaine</h2>
          {r.review_reason && <p><b>Pourquoi ici :</b> {r.review_reason}</p>}
          {isManagerNeeded && !actor.startsWith('manager') && <div className="alert">Cette décision est réservée au manager. Changez d'utilisateur dans la barre latérale pour la démo.</div>}

          {waiting && (
            <>
              {(s.missing_fields?.length || s.flags?.includes('ambiguous_dates')) && (
                <details open style={{ marginBottom: 10 }}>
                  <summary style={{ fontWeight: 700, cursor: 'pointer' }}>Compléter les champs (relance la vérification)</summary>
                  <div className="grid c2">
                    <div><label>Prise en charge</label><input type="date" value={fields.pickup_date} onChange={e => setFields({ ...fields, pickup_date: e.target.value })} /></div>
                    <div><label>Retour</label><input type="date" value={fields.return_date} onChange={e => setFields({ ...fields, return_date: e.target.value })} /></div>
                    <div><label>Catégorie</label><select value={fields.vehicle_category} onChange={e => setFields({ ...fields, vehicle_category: e.target.value })}>
                      <option value="">—</option>{['citadine', 'berline', 'suv', '4x4', 'utilitaire'].map(c => <option key={c}>{c}</option>)}</select></div>
                    <div><label>Lieu</label><select value={fields.pickup_location} onChange={e => setFields({ ...fields, pickup_location: e.target.value })}>
                      {['Agdal', 'Hay Riad', 'Aeroport Rabat-Sale'].map(c => <option key={c}>{c}</option>)}</select></div>
                  </div>
                  <button className="btn navy sm" style={{ marginTop: 8 }} disabled={busy || !canDecide} onClick={() => act('complete', { fields })}>Compléter & revérifier</button>
                </details>
              )}
              <label>Message à envoyer au client (modifiable)</label>
              <textarea value={body} onChange={e => setBody(e.target.value)} placeholder="Aucun brouillon — rédigez la réponse ou clôturez." />
              <label>Note interne</label>
              <input value={note} onChange={e => setNote(e.target.value)} placeholder="ex. remise 10 % accordée" />
              <div className="row-actions">
                <button className="btn primary" disabled={busy || !canDecide || !body} onClick={() => act(body === (f?.draft_fr || '') ? 'approve' : 'edit', { body })}>
                  {body === (f?.draft_fr || '') ? 'Approuver & envoyer' : 'Modifier & envoyer'}
                </button>
                <button className="btn danger" disabled={busy || !canDecide} onClick={() => act('reject')}>Refuser</button>
                <button className="btn" disabled={busy || !canDecide} onClick={() => act('close')}>Clôturer</button>
              </div>
              <p className="small muted" style={{ marginTop: 10 }}>« Envoyer » est simulé dans le pilote : le système ne contacte jamais un client seul.</p>
            </>
          )}

          {!waiting && reminderDue && (
            <>
              <label>Relance à envoyer</label>
              <textarea value={body} onChange={e => setBody(e.target.value)} />
              <div className="row-actions">
                <button className="btn primary" disabled={busy} onClick={() => act('send_reminder', { body })}>Envoyer la relance</button>
                <button className="btn" disabled={busy} onClick={() => act('customer_yes')}>Le client a accepté</button>
                <button className="btn" disabled={busy} onClick={() => act('customer_no')}>Le client a décliné</button>
              </div>
            </>
          )}

          {!waiting && !reminderDue && r.state === 'pending_customer' && (
            <>
              <p className="muted">En attente d'une réponse client. Relance automatique planifiée.</p>
              <div className="row-actions">
                <button className="btn primary" disabled={busy} onClick={() => act('customer_yes')}>Le client a accepté → confirmer</button>
                <button className="btn" disabled={busy} onClick={() => act('customer_no')}>Le client a décliné</button>
              </div>
            </>
          )}

          {!waiting && r.state === 'needs_human' && !reminderDue && (
            <>
              <p>{f?.rationale}</p>
              <label>Note</label><input value={note} onChange={e => setNote(e.target.value)} />
              <div className="row-actions">
                <button className="btn primary" disabled={busy} onClick={() => act('call_done')}>Client appelé → relancer le suivi</button>
                <button className="btn" disabled={busy} onClick={() => act('close')}>Clôturer (perdu)</button>
              </div>
            </>
          )}

          {(r.state === 'confirmed' || r.state === 'closed') && <div className="ok">Demande {STATE_FR[r.state].toLowerCase()} — plus aucune action requise.</div>}
        </div>
      </div>
    </>
  )
}
