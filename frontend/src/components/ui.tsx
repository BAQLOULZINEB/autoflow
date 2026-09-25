import { STATE_FR } from '../lib/api'

export const StateBadge = ({ s }: { s: string }) => <span className={`badge s-${s}`}>{STATE_FR[s] || s}</span>
export const LevelBadge = ({ l }: { l: string | null }) => l ? <span className={`badge lvl-${l}`}>{l === 'manager' ? 'Manager' : 'Équipe'}</span> : null
export const Banner = () => <div className="banner">▌ Données de démonstration — aucun client réel. Le système prépare ; l'équipe décide.</div>

export function Kpi({ label, value, hint }: { label: string; value: string | number; hint?: string }) {
  return (
    <div className="card kpi">
      <div className="label">{label}</div>
      <div className="value">{value}</div>
      {hint && <div className="hint">{hint}</div>}
    </div>
  )
}

export const FLAG_FR: Record<string, string> = {
  discount_requested: 'Remise demandée', vip_claimed: 'Client régulier', ambiguous_dates: 'Dates ambiguës',
  location_defaulted: 'Lieu par défaut (Agdal)',
}
export const Flag = ({ f }: { f: string }) => {
  const bad = f === 'discount_requested' || f === 'ambiguous_dates'
  return <span className={`tag ${bad ? 'warn' : ''}`}>{FLAG_FR[f] || f}</span>
}
