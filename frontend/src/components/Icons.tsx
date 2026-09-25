/* Inline SVG icons — channel logos + UI glyphs (Lucide-style, 24px grid). No emoji. */
import type { ReactElement, SVGProps } from 'react'

type P = SVGProps<SVGSVGElement> & { size?: number }
const base = (size = 18): SVGProps<SVGSVGElement> => ({ width: size, height: size, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', strokeWidth: 2, strokeLinecap: 'round', strokeLinejoin: 'round', 'aria-hidden': true })

/* ---- channel logos (simplified marks, brand colours) ---- */
export const WhatsApp = ({ size = 18, ...p }: P) => (
  <svg width={size} height={size} viewBox="0 0 24 24" aria-hidden {...p}>
    <circle cx="12" cy="12" r="11" fill="#25D366" />
    <path d="M6.5 17.5l.9-3.1a6.2 6.2 0 1 1 2.3 2.3l-3.2.8z" fill="#fff" />
    <path d="M9.6 8.8c.2-.4.4-.4.6-.4h.5c.2 0 .3.1.4.3l.6 1.4c.1.2 0 .3-.1.5l-.4.5c-.1.1-.2.2-.1.4.4.8 1.3 1.7 2.2 2.1.2.1.3 0 .4-.1l.5-.6c.1-.2.3-.2.5-.1l1.4.7c.2.1.3.2.3.4 0 .5-.3 1.3-.9 1.5-.5.2-1.2.3-2.5-.3a7 7 0 0 1-3-2.7c-.6-1-.7-1.9-.5-2.6.1-.5.3-.8.6-1z" fill="#25D366" />
  </svg>
)
export const Facebook = ({ size = 18, ...p }: P) => (
  <svg width={size} height={size} viewBox="0 0 24 24" aria-hidden {...p}>
    <circle cx="12" cy="12" r="11" fill="#1877F2" />
    <path d="M13.3 20v-6.2h2.1l.3-2.5h-2.4V9.7c0-.7.2-1.2 1.2-1.2h1.3V6.3c-.2 0-1-.1-1.9-.1-1.9 0-3.2 1.2-3.2 3.3v1.8H8.6v2.5h2.1V20h2.6z" fill="#fff" />
  </svg>
)
export const Instagram = ({ size = 18, ...p }: P) => (
  <svg width={size} height={size} viewBox="0 0 24 24" aria-hidden {...p}>
    <defs><linearGradient id="ig" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stopColor="#F9CE34" /><stop offset=".5" stopColor="#EE2A7B" /><stop offset="1" stopColor="#6228D7" /></linearGradient></defs>
    <rect x="2" y="2" width="20" height="20" rx="6" fill="url(#ig)" />
    <rect x="6.5" y="6.5" width="11" height="11" rx="3.5" fill="none" stroke="#fff" strokeWidth="1.8" />
    <circle cx="12" cy="12" r="2.6" fill="none" stroke="#fff" strokeWidth="1.8" />
    <circle cx="15.6" cy="8.4" r=".9" fill="#fff" />
  </svg>
)
export const Site = ({ size = 18, ...p }: P) => (
  <svg width={size} height={size} viewBox="0 0 24 24" aria-hidden {...p}>
    <circle cx="12" cy="12" r="11" fill="#0E9C99" />
    <g fill="none" stroke="#fff" strokeWidth="1.6"><circle cx="12" cy="12" r="6.5" /><path d="M5.5 12h13M12 5.5c2.2 2 2.2 11 0 13M12 5.5c-2.2 2-2.2 11 0 13" /></g>
  </svg>
)
export const Phone = ({ size = 18, ...p }: P) => (
  <svg width={size} height={size} viewBox="0 0 24 24" aria-hidden {...p}>
    <circle cx="12" cy="12" r="11" fill="#0B1F3A" />
    <path d="M8.2 7.2l1.6-.4 1.3 2.6-1 1a7 7 0 0 0 3.5 3.5l1-1 2.6 1.3-.4 1.6c-.1.5-.6.9-1.1.8A9.6 9.6 0 0 1 7.4 8.3c-.1-.5.3-1 .8-1.1z" fill="#fff" />
  </svg>
)
export const WalkIn = ({ size = 18, ...p }: P) => (
  <svg width={size} height={size} viewBox="0 0 24 24" aria-hidden {...p}>
    <circle cx="12" cy="12" r="11" fill="#7C3AED" />
    <g fill="none" stroke="#fff" strokeWidth="1.6"><path d="M6.5 10.5v6.5h11v-6.5M5.5 10.5l1.2-3.5h10.6l1.2 3.5c0 1-.9 1.5-1.7 1.5s-1.6-.5-1.6-1.5c0 1-.8 1.5-1.6 1.5s-1.6-.5-1.6-1.5c0 1-.8 1.5-1.6 1.5s-1.6-.5-1.6-1.5c0 1-.9 1.5-1.7 1.5S5.5 11.5 5.5 10.5z" /><path d="M10 17v-3.5h4V17" /></g>
  </svg>
)
export const Mail = ({ size = 18, ...p }: P) => (
  <svg width={size} height={size} viewBox="0 0 24 24" aria-hidden {...p}>
    <circle cx="12" cy="12" r="11" fill="#F59E0B" />
    <g fill="none" stroke="#fff" strokeWidth="1.6"><rect x="6" y="8" width="12" height="9" rx="1.5" /><path d="M6 9l6 4 6-4" /></g>
  </svg>
)

export const CHANNEL_META: Record<string, { label: string; Icon: (p: P) => ReactElement }> = {
  whatsapp: { label: 'WhatsApp', Icon: WhatsApp }, facebook: { label: 'Facebook', Icon: Facebook },
  instagram: { label: 'Instagram', Icon: Instagram }, form: { label: 'Site web', Icon: Site }, site: { label: 'Site web', Icon: Site },
  phone: { label: 'Téléphone', Icon: Phone }, 'walk-in': { label: 'Comptoir', Icon: WalkIn }, email: { label: 'E-mail', Icon: Mail },
}
export function Channel({ id, size = 18, withLabel = false }: { id: string; size?: number; withLabel?: boolean }) {
  const m = CHANNEL_META[id] || { label: id, Icon: Site }
  return <span className="chan" title={m.label}><m.Icon size={size} />{withLabel && <span>{m.label}</span>}</span>
}

/* ---- UI glyphs ---- */
export const IconDashboard = (p: P) => <svg {...base(p.size)} {...p}><rect x="3" y="3" width="7" height="9" rx="1.5" /><rect x="14" y="3" width="7" height="5" rx="1.5" /><rect x="14" y="12" width="7" height="9" rx="1.5" /><rect x="3" y="16" width="7" height="5" rx="1.5" /></svg>
export const IconInbox = (p: P) => <svg {...base(p.size)} {...p}><path d="M22 12h-6l-2 3h-4l-2-3H2" /><path d="M5.5 5h13l3.5 7v7H2v-7z" /></svg>
export const IconActivity = (p: P) => <svg {...base(p.size)} {...p}><path d="M22 12h-4l-3 9L9 3l-3 9H2" /></svg>
export const IconList = (p: P) => <svg {...base(p.size)} {...p}><path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01" /></svg>
export const IconPlus = (p: P) => <svg {...base(p.size)} {...p}><path d="M12 5v14M5 12h14" /></svg>
export const IconCar = (p: P) => <svg {...base(p.size)} {...p}><path d="M5 17h14M3 12l2-5h14l2 5v5H3z" /><circle cx="7.5" cy="17" r="1.5" /><circle cx="16.5" cy="17" r="1.5" /></svg>
export const IconLayers = (p: P) => <svg {...base(p.size)} {...p}><path d="M12 2l10 5-10 5L2 7z" /><path d="M2 12l10 5 10-5M2 17l10 5 10-5" /></svg>
export const IconPlay = (p: P) => <svg {...base(p.size)} {...p}><path d="M6 4l14 8-14 8z" fill="currentColor" stroke="none" /></svg>
export const IconPause = (p: P) => <svg {...base(p.size)} {...p}><rect x="6" y="4" width="4" height="16" fill="currentColor" stroke="none" /><rect x="14" y="4" width="4" height="16" fill="currentColor" stroke="none" /></svg>
export const IconCheck = (p: P) => <svg {...base(p.size)} {...p}><path d="M20 6L9 17l-5-5" /></svg>
export const IconX = (p: P) => <svg {...base(p.size)} {...p}><path d="M18 6L6 18M6 6l12 12" /></svg>
export const IconClock = (p: P) => <svg {...base(p.size)} {...p}><circle cx="12" cy="12" r="9" /><path d="M12 7v5l3 2" /></svg>
export const IconRefresh = (p: P) => <svg {...base(p.size)} {...p}><path d="M3 12a9 9 0 0 1 15.5-6.3L21 8M21 3v5h-5M21 12a9 9 0 0 1-15.5 6.3L3 16M3 21v-5h5" /></svg>
export const IconLogout = (p: P) => <svg {...base(p.size)} {...p}><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9" /></svg>
export const IconUser = (p: P) => <svg {...base(p.size)} {...p}><circle cx="12" cy="8" r="4" /><path d="M4 21a8 8 0 0 1 16 0" /></svg>
export const IconBot = (p: P) => <svg {...base(p.size)} {...p}><rect x="4" y="8" width="16" height="12" rx="3" /><path d="M12 4v4M8 14h.01M16 14h.01M9 18h6" /></svg>
export const IconFlask = (p: P) => <svg {...base(p.size)} {...p}><path d="M9 3h6M10 3v6L4.5 19a1.5 1.5 0 0 0 1.3 2.2h12.4a1.5 1.5 0 0 0 1.3-2.2L14 9V3" /><path d="M7 15h10" /></svg>
export const IconPresent = (p: P) => <svg {...base(p.size)} {...p}><rect x="3" y="4" width="18" height="12" rx="2" /><path d="M12 16v4M8 20h8" /></svg>
export const IconSpinner = (p: P) => <svg {...base(p.size)} {...p} className="spin"><path d="M21 12a9 9 0 1 1-6.2-8.6" /></svg>
export const Logo = ({ size = 28 }: { size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 32 32" aria-hidden>
    <rect width="32" height="32" rx="8" fill="#0E9C99" />
    <path d="M7 21l5-10 5 10M9.3 17.5h5.4" fill="none" stroke="#fff" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" />
    <path d="M19 11h6M19 16h6M19 21h4" stroke="#fff" strokeWidth="2.4" strokeLinecap="round" opacity=".9" />
  </svg>
)
