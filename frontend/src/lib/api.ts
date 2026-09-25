// Thin fetch wrapper. Token lives in localStorage (pilot: one shared admin token).
const BASE = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '')

export const tokenStore = {
  get: () => { try { return localStorage.getItem('autoflow_token') || '' } catch { return '' } },
  set: (t: string) => { try { localStorage.setItem('autoflow_token', t) } catch { /* private mode */ } },
  clear: () => { try { localStorage.removeItem('autoflow_token') } catch { /* ignore */ } },
}
export const actorStore = {
  get: () => { try { return localStorage.getItem('autoflow_actor') || 'staff:Salma' } catch { return 'staff:Salma' } },
  set: (a: string) => { try { localStorage.setItem('autoflow_actor', a) } catch { /* ignore */ } },
}

export class ApiError extends Error { status: number; constructor(s: number, m: string) { super(m); this.status = s } }

async function call<T>(method: string, path: string, body?: unknown, auth = true): Promise<T> {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  if (auth) headers['X-Admin-Token'] = tokenStore.get()
  const res = await fetch(`${BASE}${path}`, { method, headers, body: body ? JSON.stringify(body) : undefined })
  if (!res.ok) {
    let msg = res.statusText
    try { msg = (await res.json()).detail || msg } catch { /* not json */ }
    if (res.status === 401 && auth) { tokenStore.clear(); window.location.assign('/login') }
    throw new ApiError(res.status, msg)
  }
  return res.json()
}

// ---- types (mirror backend schemas) -------------------------------------
export type Structured = {
  intent: string; pickup_date: string | null; return_date: string | null; vehicle_category: string | null
  transmission: string | null; pickup_location: string | null; return_location: string | null; budget_mad: number | null
  flags: string[]; field_confidence: Record<string, number>; confidence: number; missing_fields: string[]
  clarification_fr: string | null; evidence: Record<string, string>; engine: string
}
export type Option = { vehicle_id: string; model: string; category: string; transmission: string; location: string
  daily_rate_mad: number; days: number; total_mad: number; pickup_date: string; return_date: string; note: string }
export type Availability = { status: string; options: Option[]; alternatives: Option[]; reasons: string[]; days: number; computed_at: string }
export type FollowUp = { draft_kind: string; draft_fr: string; action: string; next_check_at: string | null; reminder_no: number; rationale: string }
export type Req = {
  id: string; customer_name: string; channel: string; raw_message: string; received_at: string; state: string
  intent: string | null; structured: Partial<Structured>; availability: Partial<Availability>; followup: Partial<FollowUp>
  review_reason: string | null; review_level: string | null; priority: string; hops: number; updated_at: string
}
export type ReqDetail = Req & {
  drafts: { id: number; kind: string; body_fr: string; generated_at: string; edited: boolean; sent_by: string | null; sent_at: string | null }[]
  events: { id: number; from: string | null; to: string | null; actor: string; reason: string; ts: string }[]
  reviews: { id: number; reason: string; level: string; priority: string; decision: string | null; actor: string | null; note: string; opened_at: string; closed_at: string | null }[]
  follow_ups: { id: number; due_at: string; reminder_no: number; status: string; outcome: string | null }[]
  pending_interrupt: { allowed: string[]; review: { level: string; priority: string; reason: string } } | null
}
export type ReviewItem = { review_id: number; request_id: string; customer_name: string; channel: string; state: string; level: string
  priority: string; reason: string; opened_at: string; intent: string | null; draft_kind: string | null; action: string | null }
export type Kpis = { total_requests: number; by_state: Record<string, number>; complete_rate: number | null
  avg_seconds_to_first_draft: number | null; reviews_open: number; reviews_manager: number; human_handoffs: number
  reminders_sent: number; reminders_due: number; events: number; clock: string; label: string }
export type Check = { rule: string; value: unknown; threshold: unknown; passed: boolean; effect: string }
export type Trace = { path: string[]; steps: { node: string; title: string; verdict: string; checks: Check[]; waiting?: boolean }[]; state: string; waiting: boolean }
export type LiveEvent = { id: number; request_id: string; from: string | null; to: string | null; actor: string; reason: string; ts: string }
export type SimCheck = { check: string; expected: unknown; observed: unknown; ok: boolean }
export type SimStep = { i: number; label: string; who: string; do: string; detail: string; state?: string; checks: SimCheck[]; ok?: boolean; error: string | null; ms: number }
export type SimResult = { key: string; title: string; channel: string; request_id: string; ok: boolean; steps: SimStep[]; started_at: string; clock: string }
export type SimCatalogue = { key: string; title: string; channel: string; customer: string; message: string; summary: string; proves: string[]; steps: { label: string; who: string }[] }
export type Scenario = { key: string; title: string; customer: string; channel: string; message: string; expected: string }

// ---- endpoints -----------------------------------------------------------
export const api = {
  health: () => call<{ ok: boolean; llm: string; clock: string }>('GET', '/api/health', undefined, false),
  login: (token: string) => call<{ ok: boolean }>('POST', '/api/auth/login', { token }, false),
  publicIntake: (b: { message: string; channel: string; customer_name: string }) =>
    call<{ request_id: string; message: string }>('POST', '/api/public/intake', b, false),
  requests: (state?: string) => call<Req[]>('GET', `/api/requests${state ? `?state=${state}` : ''}`),
  request: (id: string) => call<ReqDetail>('GET', `/api/requests/${id}`),
  createRequest: (b: { message: string; channel: string; customer_name: string }) => call<ReqDetail>('POST', '/api/requests', b),
  decide: (id: string, b: { action: string; actor: string; body?: string; note?: string; fields?: Record<string, string> }) =>
    call<ReqDetail>('POST', `/api/requests/${id}/decision`, b),
  customerReply: (id: string, accepted: boolean, actor: string) => call<ReqDetail>('POST', `/api/requests/${id}/customer-reply`, { accepted, actor }),
  trace: (id: string) => call<Trace>('GET', `/api/requests/${id}/trace`),
  live: (since = 0) => call<{ events: LiveEvent[]; last_id: number; open_reviews: number; clock: string }>('GET', `/api/live?since=${since}`),
  reviews: () => call<ReviewItem[]>('GET', '/api/reviews'),
  fleet: () => call<{ vehicles: Record<string, string | number | null>[]; bookings: Record<string, string | null>[]; customers: Record<string, string | boolean>[] }>('GET', '/api/fleet'),
  rules: () => call<Record<string, unknown>>('GET', '/api/rules'),
  kpis: () => call<Kpis>('GET', '/api/kpis'),
  events: (limit = 40) => call<{ id: number; request_id: string; from: string | null; to: string | null; actor: string; reason: string; ts: string }[]>('GET', `/api/events?limit=${limit}`),
  graph: () => call<{ mermaid: string }>('GET', '/api/graph'),
  simulations: () => call<SimCatalogue[]>('GET', '/api/simulations'),
  runSimulation: (key: string) => call<SimResult>('POST', `/api/simulations/${key}/run`),
  scenarios: () => call<Scenario[]>('GET', '/api/demo/scenarios'),
  loadScenario: (k: string) => call<ReqDetail>('POST', `/api/demo/load/${k}`),
  reset: () => call<{ ok: boolean }>('POST', '/api/demo/reset'),
  advance: (hours: number) => call<{ clock: string }>('POST', '/api/demo/advance', { hours }),
}

export const STATE_FR: Record<string, string> = {
  new: 'Nouvelle', incomplete: 'Incomplète', checked: 'Vérifiée', quote_ready: 'Devis prêt',
  pending_customer: 'Attente client', stalled: 'Sans réponse', needs_human: 'À valider',
  escalated: 'Escaladée', confirmed: 'Confirmée', closed: 'Clôturée',
}
export const INTENT_FR: Record<string, string> = {
  quote: 'Devis', reservation: 'Réservation', info: 'Information', modification: 'Modification', complaint: 'Réclamation', other: 'Autre',
}
export const fmtDate = (iso?: string | null) => iso ? new Date(iso).toLocaleString('fr-FR', { dateStyle: 'short', timeStyle: 'short' }) : '—'
export const fmtDay = (iso?: string | null) => iso ? new Date(iso + 'T00:00:00').toLocaleDateString('fr-FR') : '—'
