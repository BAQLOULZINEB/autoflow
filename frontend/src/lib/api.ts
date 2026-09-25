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

async function uploadFile<T>(path: string, file: File): Promise<T> {
  const headers: Record<string, string> = { 'X-Admin-Token': tokenStore.get() }
  const fd = new FormData()
  fd.append('file', file)
  const res = await fetch(`${BASE}${path}`, { method: 'POST', headers, body: fd })
  if (!res.ok) {
    let msg = res.statusText
    try { msg = (await res.json()).detail || msg } catch { /* not json */ }
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

// ---- BI / analytics types ------------------------------------------------
export type BiDashboard = {
  revenue_month: number; revenue_prev_month: number; revenue_delta_pct: number | null
  active_rentals: number; rentals_month: number; rentals_prev_month: number
  total_vehicles: number; in_maintenance: number; occupancy_pct: number; rented_today: number
  expenses_month: number; expenses_prev_month: number; profit_month: number
  avg_rental_days: number | null; avg_daily_rate: number | null
  appointments_today: number; appointments_week: number
  channels: { name: string; count: number }[]
  clients_month: number; today: string
}
export type RevenuePoint = { date: string; revenue: number; count: number }
export type MonthlyRevenue = { month: string; revenue: number; count: number }
export type CategoryRevenue = { category: string; revenue: number; count: number }
export type ExpenseCategory = { category: string; amount: number }
export type ExpenseVehicle = { plate: string; amount: number }
export type FleetCategory = { category: string; count: number }
export type OccupancyItem = { vehicle_id: string; model: string; category: string; rented_days: number; occupancy_pct: number }
export type AppointmentItem = { id: number; date: string; time: string; type: string; plate: string | null; cin: string | null; status: string; note: string }
export type ClientRank = { cin: string; total: number; rentals: number }
export type LocationRow = { id: string; plate: string; cin: string; price_per_day: number; date_out: string; date_in: string; days: number; amount: number; channel: string; status: string }
export type ExpenseRow = { id: number; date: string; plate: string | null; category: string; amount: number; supplier: string; note: string }
export type ExcelImportResult = { ok: boolean; sheets: Record<string, { importés: number; ignorés: number }>; warnings: string[]; errors: string[] }

export type GarageRental = { id: string; cin: string; date_out: string; date_in: string; days: number; amount: number; channel: string; status: string }
export type GarageAppointment = { date: string; time: string; type: string; note: string }
export type GarageVehicle = {
  code: string; plate: string; model: string; category: string; transmission: string
  location: string; daily_rate: number; status: 'disponible' | 'en_location' | 'maintenance'
  maintenance_until: string | null; revenue: number; expenses: number; profit: number
  rental_count: number; rented_days: number; occupancy_pct: number
  recent_rentals: GarageRental[]; appointments: GarageAppointment[]
}
export type OfficialVehicleImage = {
  image_url: string | null
  source_url: string | null
  model_year: number | null
  source_type: 'official' | 'agency' | 'kifal' | null
}

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

  // BI / Analytics
  biDashboard: () => call<BiDashboard>('GET', '/api/bi/dashboard'),
  biRevenueDaily: (month?: number, year?: number) => {
    const p = new URLSearchParams()
    if (month !== undefined) p.set('month', String(month))
    if (year !== undefined) p.set('year', String(year))
    const qs = p.toString()
    return call<RevenuePoint[]>('GET', `/api/bi/revenue/daily${qs ? '?' + qs : ''}`)
  },
  biRevenueMonthly: () => call<MonthlyRevenue[]>('GET', '/api/bi/revenue/monthly'),
  biRevenueByCategory: (month?: number, year?: number) => {
    const p = new URLSearchParams()
    if (month !== undefined) p.set('month', String(month))
    if (year !== undefined) p.set('year', String(year))
    const qs = p.toString()
    return call<CategoryRevenue[]>('GET', `/api/bi/revenue/category${qs ? '?' + qs : ''}`)
  },
  biExpensesCategory: (month?: number, year?: number) => {
    const p = new URLSearchParams()
    if (month !== undefined) p.set('month', String(month))
    if (year !== undefined) p.set('year', String(year))
    const qs = p.toString()
    return call<ExpenseCategory[]>('GET', `/api/bi/expenses/category${qs ? '?' + qs : ''}`)
  },
  biExpensesVehicle: (month?: number, year?: number) => {
    const p = new URLSearchParams()
    if (month !== undefined) p.set('month', String(month))
    if (year !== undefined) p.set('year', String(year))
    const qs = p.toString()
    return call<ExpenseVehicle[]>('GET', `/api/bi/expenses/vehicle${qs ? '?' + qs : ''}`)
  },
  biFleetCategories: () => call<FleetCategory[]>('GET', '/api/bi/fleet/categories'),
  biFleetOccupancy: (month?: number, year?: number) => {
    const p = new URLSearchParams()
    if (month !== undefined) p.set('month', String(month))
    if (year !== undefined) p.set('year', String(year))
    const qs = p.toString()
    return call<OccupancyItem[]>('GET', `/api/bi/fleet/occupancy${qs ? '?' + qs : ''}`)
  },
  biAppointments: (days?: number) => call<AppointmentItem[]>('GET', `/api/bi/appointments${days ? '?days=' + days : ''}`),
  biTopClients: (limit?: number) => call<ClientRank[]>('GET', `/api/bi/clients/top${limit ? '?limit=' + limit : ''}`),
  biLocations: (month?: number, year?: number, limit?: number) => {
    const p = new URLSearchParams()
    if (month !== undefined) p.set('month', String(month))
    if (year !== undefined) p.set('year', String(year))
    if (limit !== undefined) p.set('limit', String(limit))
    const qs = p.toString()
    return call<LocationRow[]>('GET', `/api/bi/locations${qs ? '?' + qs : ''}`)
  },
  biExpensesList: (month?: number, year?: number, limit?: number) => {
    const p = new URLSearchParams()
    if (month !== undefined) p.set('month', String(month))
    if (year !== undefined) p.set('year', String(year))
    if (limit !== undefined) p.set('limit', String(limit))
    const qs = p.toString()
    return call<ExpenseRow[]>('GET', `/api/bi/expenses${qs ? '?' + qs : ''}`)
  },
  biAppointmentsList: (days?: number) => call<AppointmentItem[]>('GET', `/api/bi/appointments/list${days ? '?days=' + days : ''}`),
  biFleetGarage: (month?: number, year?: number) => {
    const p = new URLSearchParams()
    if (month !== undefined) p.set('month', String(month))
    if (year !== undefined) p.set('year', String(year))
    const qs = p.toString()
    return call<GarageVehicle[]>('GET', `/api/bi/fleet/garage${qs ? '?' + qs : ''}`)
  },
  officialVehicleImage: (model: string) => call<OfficialVehicleImage>('GET', `/api/media/vehicle-image?model=${encodeURIComponent(model)}`),
  warmVehicleImages: () => call<{ queued: number }>('POST', '/api/media/vehicle-images/warm'),

  // Excel import
  excelImport: (file: File) => uploadFile<ExcelImportResult>('/api/excel/import', file),
  excelSeed: () => call<ExcelImportResult>('POST', '/api/excel/seed'),
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
export const fmtMAD = (n: number) => new Intl.NumberFormat('fr-MA', { style: 'currency', currency: 'MAD', minimumFractionDigits: 0 }).format(n)
export const fmtPct = (n: number) => `${n > 0 ? '+' : ''}${n.toFixed(1)}%`
export const fmtNum = (n: number) => new Intl.NumberFormat('fr-MA').format(n)
