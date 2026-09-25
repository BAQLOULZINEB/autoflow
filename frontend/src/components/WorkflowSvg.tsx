/**
 * Dark-themed workflow diagram (diagram-design / Cocoon-AI palette) of the real
 * LangGraph graph. `path` lights up the nodes a request went through; `waiting`
 * pulses the human_review gate. Pure inline SVG — no runtime layout engine.
 */
type Node = { id: string; x: number; y: number; w: number; h: number; label: string; sub: string; kind: 'agent' | 'orch' | 'human' | 'cond' | 'io' }

const N: Node[] = [
  { id: 'start', x: 20, y: 150, w: 90, h: 44, label: 'Demande', sub: 'WA · form · n8n', kind: 'io' },
  { id: 'intake', x: 140, y: 142, w: 120, h: 60, label: 'Intake', sub: 'structure + preuves', kind: 'agent' },
  { id: 'route_after_intake', x: 290, y: 142, w: 120, h: 60, label: 'Routage 1', sub: 'seuils rules.json', kind: 'cond' },
  { id: 'escalate', x: 440, y: 30, w: 120, h: 52, label: 'Escalade', sub: 'réclamation → manager', kind: 'human' },
  { id: 'clarify', x: 440, y: 100, w: 120, h: 52, label: 'Clarifier', sub: 'question courte', kind: 'agent' },
  { id: 'availability', x: 440, y: 190, w: 120, h: 60, label: 'Disponibilité', sub: 'déterministe · 0 LLM', kind: 'agent' },
  { id: 'decide_after_availability', x: 590, y: 190, w: 120, h: 60, label: 'Matrice', sub: "d'escalade", kind: 'cond' },
  { id: 'sensitive', x: 740, y: 130, w: 120, h: 52, label: 'Sensible', sub: 'remise · VIP · > 14 j', kind: 'human' },
  { id: 'draft', x: 740, y: 210, w: 120, h: 52, label: 'Brouillon', sub: 'prix injecté', kind: 'agent' },
  { id: 'human_review', x: 620, y: 320, w: 160, h: 64, label: 'Validation humaine', sub: 'interrupt() · équipe / manager', kind: 'human' },
  { id: 'finalize', x: 820, y: 326, w: 120, h: 52, label: 'Finaliser', sub: 'envoi · relance +24 h', kind: 'orch' },
  { id: 'sweep', x: 820, y: 410, w: 120, h: 52, label: 'Relances', sub: '24 h · max 2 · 72 h', kind: 'orch' },
]
const E: [string, string, string?][] = [
  ['start', 'intake'], ['intake', 'route_after_intake'],
  ['route_after_intake', 'escalate', 'complaint'], ['route_after_intake', 'clarify', 'incomplet'], ['route_after_intake', 'availability', 'ok'],
  ['availability', 'decide_after_availability'], ['decide_after_availability', 'sensitive', 'oui'], ['decide_after_availability', 'draft', 'non'],
  ['escalate', 'human_review'], ['clarify', 'human_review'], ['sensitive', 'human_review'], ['draft', 'human_review'],
  ['human_review', 'finalize', 'approve'], ['human_review', 'availability', 'complete'], ['finalize', 'sweep'],
]
const STYLE: Record<Node['kind'], { fill: string; stroke: string }> = {
  agent: { fill: 'rgba(6, 78, 59, 0.4)', stroke: '#34d399' },
  orch: { fill: 'rgba(8, 51, 68, 0.4)', stroke: '#22d3ee' },
  human: { fill: 'rgba(136, 19, 55, 0.4)', stroke: '#fb7185' },
  cond: { fill: 'rgba(76, 29, 149, 0.4)', stroke: '#a78bfa' },
  io: { fill: 'rgba(30, 41, 59, 0.5)', stroke: '#94a3b8' },
}
const byId = Object.fromEntries(N.map(n => [n.id, n]))
const cx = (n: Node) => n.x + n.w / 2, cy = (n: Node) => n.y + n.h / 2

function edgePath(a: Node, b: Node): string {
  // orthogonal-ish: leave from right/bottom, enter on left/top
  if (b.id === 'availability' && a.id === 'human_review') return `M ${a.x} ${cy(a)} L ${cx(b)} ${cy(a)} L ${cx(b)} ${b.y + b.h}`
  if (b.id === 'human_review') {
    // left column (escalate / clarify) leaves by the right edge through the x=575 corridor; right column drops straight down
    if (a.x + a.w <= 575) return `M ${a.x + a.w} ${cy(a)} L 575 ${cy(a)} L 575 ${b.y - 20} L ${cx(b)} ${b.y - 20} L ${cx(b)} ${b.y}`
    return `M ${cx(a)} ${a.y + a.h} L ${cx(a)} ${b.y - 20} L ${cx(b)} ${b.y - 20} L ${cx(b)} ${b.y}`
  }
  if (Math.abs(cy(a) - cy(b)) < 4) return `M ${a.x + a.w} ${cy(a)} L ${b.x} ${cy(b)}`
  if (a.id === 'finalize') return `M ${cx(a)} ${a.y + a.h} L ${cx(b)} ${b.y}`
  const mx = a.x + a.w + (b.x - a.x - a.w) / 2
  return `M ${a.x + a.w} ${cy(a)} L ${mx} ${cy(a)} L ${mx} ${cy(b)} L ${b.x} ${cy(b)}`
}

export default function WorkflowSvg({ path = [], waiting = false, compact = false }: { path?: string[]; waiting?: boolean; compact?: boolean }) {
  const on = new Set(path.length ? ['start', ...path] : [])
  const edgeOn = (a: string, b: string) => on.has(a) && on.has(b) && (path.indexOf(b) > path.indexOf(a) || a === 'start' || (a === 'human_review' && b === 'availability'))
  return (
    <svg viewBox="0 0 960 480" style={{ width: '100%', display: 'block', background: '#020617', borderRadius: 12, border: '1px solid #1e293b', maxHeight: compact ? 300 : undefined }}
      fontFamily="'JetBrains Mono', ui-monospace, Menlo, monospace">
      <defs>
        <marker id="ah" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="#64748b" /></marker>
        <marker id="ah-on" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="#22d3ee" /></marker>
        <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M 40 0 L 0 0 0 40" fill="none" stroke="#1e293b" strokeWidth="0.5" /></pattern>
        <filter id="glow"><feGaussianBlur stdDeviation="3" result="b" /><feMerge><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge></filter>
        <style>{`@keyframes pz{0%,100%{opacity:1}50%{opacity:.35}} .pz{animation:pz 1.4s infinite}`}</style>
      </defs>
      <rect width="100%" height="100%" fill="url(#grid)" />
      <text x="16" y="20" fill="#94a3b8" fontSize="9">LangGraph StateGraph · chemin suivi en cyan · nœud rose = décision humaine</text>
      {E.map(([a, b, lbl]) => {
        const A = byId[a], B = byId[b]; const active = edgeOn(a, b)
        const d = edgePath(A, B)
        return (
          <g key={a + b}>
            <path d={d} fill="none" stroke={active ? '#22d3ee' : '#334155'} strokeWidth={active ? 2 : 1.2} markerEnd={active ? 'url(#ah-on)' : 'url(#ah)'} strokeDasharray={b === 'human_review' || a === 'human_review' ? '5,4' : undefined} />
            {lbl && <text x={(A.x + A.w + B.x) / 2 + (b === 'availability' && a === 'human_review' ? -80 : 0)} y={(cy(A) + cy(B)) / 2 - 4} fill={active ? '#22d3ee' : '#64748b'} fontSize="8" textAnchor="middle">{lbl}</text>}
          </g>
        )
      })}
      {N.map(n => {
        const st = STYLE[n.kind]; const active = on.has(n.id); const isWait = waiting && n.id === 'human_review'
        return (
          <g key={n.id} opacity={path.length && !active ? 0.45 : 1} className={isWait ? 'pz' : undefined}>
            <rect x={n.x} y={n.y} width={n.w} height={n.h} rx="6" fill="#0f172a" />
            <rect x={n.x} y={n.y} width={n.w} height={n.h} rx="6" fill={st.fill} stroke={isWait ? '#fbbf24' : st.stroke} strokeWidth={active ? 2.2 : 1.5} filter={active ? 'url(#glow)' : undefined} />
            <text x={cx(n)} y={n.y + (n.h > 50 ? 24 : 21)} fill="white" fontSize="11" fontWeight="600" textAnchor="middle">{n.label}</text>
            <text x={cx(n)} y={n.y + (n.h > 50 ? 40 : 36)} fill="#94a3b8" fontSize="8" textAnchor="middle">{n.sub}</text>
          </g>
        )
      })}
      {/* legend */}
      <g transform="translate(16 400)">
        {(['agent', 'cond', 'human', 'orch'] as const).map((k, i) => (
          <g key={k} transform={`translate(0 ${i * 16})`}>
            <rect width="16" height="10" rx="2" fill={STYLE[k].fill} stroke={STYLE[k].stroke} strokeWidth="1" />
            <text x="22" y="8" fill="#94a3b8" fontSize="8">{{ agent: 'agent spécialisé', cond: 'décision orchestrateur (règles)', human: 'point de contrôle humain', orch: 'orchestrateur / suivi' }[k]}</text>
          </g>
        ))}
      </g>
    </svg>
  )
}
