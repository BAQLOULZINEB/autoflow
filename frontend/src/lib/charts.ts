/**
 * Chart.js configuration + AutoFlow Pro color palette.
 * Based on UI/UX Pro Max design system: Data-Dense Dashboard style.
 */
import {
  Chart as ChartJS,
  CategoryScale, LinearScale, PointElement, LineElement,
  BarElement, ArcElement, Filler, Tooltip, Legend,
} from 'chart.js'

ChartJS.register(
  CategoryScale, LinearScale, PointElement, LineElement,
  BarElement, ArcElement, Filler, Tooltip, Legend,
)

// Color palette — matching the agency's brand + BI best practices
export const COLORS = {
  teal:   '#0e9c99',
  navy:   '#0b1f3a',
  amber:  '#f59e0b',
  rose:   '#e11d48',
  violet: '#7c3aed',
  green:  '#059669',
  sky:    '#0ea5e9',
  orange: '#f97316',
  indigo: '#6366f1',
  pink:   '#ec4899',
  lime:   '#84cc16',
  cyan:   '#06b6d4',
}

export const CHART_COLORS = [
  COLORS.teal, COLORS.amber, COLORS.violet, COLORS.rose,
  COLORS.sky, COLORS.green, COLORS.orange, COLORS.indigo,
  COLORS.pink, COLORS.lime, COLORS.cyan, COLORS.navy,
]

export const alpha = (hex: string, a: number) => {
  const r = parseInt(hex.slice(1, 3), 16)
  const g = parseInt(hex.slice(3, 5), 16)
  const b = parseInt(hex.slice(5, 7), 16)
  return `rgba(${r},${g},${b},${a})`
}

// Default chart options (dense dashboard style)
export const DEFAULTS = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: {
      backgroundColor: '#0b1f3a',
      titleFont: { family: 'Inter, system-ui', size: 12, weight: '600' as const },
      bodyFont: { family: 'Inter, system-ui', size: 11 },
      padding: 10,
      cornerRadius: 8,
      displayColors: true,
      boxPadding: 4,
    },
  },
  scales: {
    x: {
      grid: { display: false },
      ticks: { font: { size: 11, family: 'Inter, system-ui' }, color: '#6b7280' },
      border: { display: false },
    },
    y: {
      grid: { color: '#f0f0f0' },
      ticks: { font: { size: 11, family: 'Inter, system-ui' }, color: '#6b7280' },
      border: { display: false },
    },
  },
} as const
