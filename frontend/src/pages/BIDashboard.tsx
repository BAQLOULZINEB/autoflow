import { useEffect, useRef, useState } from 'react'
import { Bar, Doughnut, Line } from 'react-chartjs-2'
import type { ChartData, ChartOptions } from 'chart.js'
import {
  api, fmtMAD, fmtNum,
  type BiDashboard as BiData, type RevenuePoint,
  type MonthlyRevenue, type CategoryRevenue,
  type ExpenseCategory, type FleetCategory,
} from '../lib/api'
import { CHART_COLORS, COLORS, alpha, DEFAULTS } from '../lib/charts'

const MONTHS: Record<number, string> = { 7: 'Juillet', 8: 'Août', 9: 'Septembre' }

/* ─── Trend arrow component ──────────────────────────────────────────── */
function Trend({ value, suffix = '%' }: { value: number | null; suffix?: string }) {
  if (value == null) return <span className="hint">—</span>
  const up = value >= 0
  return (
    <span className={up ? 'trend-up' : 'trend-down'}>
      <svg width="12" height="12" viewBox="0 0 12 12" fill="none" style={{ marginRight: 2 }}>
        {up
          ? <path d="M6 2L10 7H2L6 2Z" fill="currentColor" />
          : <path d="M6 10L2 5H10L6 10Z" fill="currentColor" />}
      </svg>
      {Math.abs(value).toFixed(1)}{suffix}
    </span>
  )
}

/* ─── KPI Card ───────────────────────────────────────────────────────── */
function KPI({ label, value, hint, trend, color }: {
  label: string; value: string; hint?: string; trend?: number | null; color?: string
}) {
  return (
    <div className="card kpi">
      <div className="label">{label}</div>
      <div className="value" style={color ? { color } : undefined}>{value}</div>
      <div className="hint">
        {trend !== undefined && <Trend value={trend} />}
        {hint && <span style={{ marginLeft: trend !== undefined ? 8 : 0 }}>{hint}</span>}
      </div>
    </div>
  )
}

/* ─── Main Dashboard ─────────────────────────────────────────────────── */
export default function BIDashboard() {
  const [month, setMonth] = useState(9)
  const [loading, setLoading] = useState(true)
  const [bi, setBi] = useState<BiData | null>(null)
  const [revDaily, setRevDaily] = useState<RevenuePoint[]>([])
  const [revMonthly, setRevMonthly] = useState<MonthlyRevenue[]>([])
  const [expCat, setExpCat] = useState<ExpenseCategory[]>([])
  const [fleetCat, setFleetCat] = useState<FleetCategory[]>([])
  const [revByCat, setRevByCat] = useState<CategoryRevenue[]>([])
  const areaRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    setLoading(true)
    Promise.all([
      api.biDashboard(),
      api.biRevenueDaily(month),
      api.biRevenueMonthly(),
      api.biExpensesCategory(month),
      api.biFleetCategories(),
      api.biRevenueByCategory(month),
    ]).then(([d, rd, rm, ec, fc, rc]) => {
      setBi(d); setRevDaily(rd); setRevMonthly(rm)
      setExpCat(ec); setFleetCat(fc); setRevByCat(rc)
    }).catch(console.error).finally(() => setLoading(false))
  }, [month])

  if (loading && !bi) {
    return <div className="topbar"><h1>Chargement…</h1></div>
  }

  /* ─── Chart data builders ─────────────────────────────────────────── */
  const dailyData: ChartData<'line'> = {
    labels: revDaily.map(p => {
      const d = new Date(p.date + 'T00:00:00')
      return d.getDate().toString()
    }),
    datasets: [{
      label: 'CA (MAD)',
      data: revDaily.map(p => p.revenue),
      borderColor: COLORS.teal,
      backgroundColor: (ctx) => {
        const chart = ctx.chart
        const { ctx: c, chartArea } = chart
        if (!chartArea) return alpha(COLORS.teal, 0.15)
        const grad = c.createLinearGradient(0, chartArea.top, 0, chartArea.bottom)
        grad.addColorStop(0, alpha(COLORS.teal, 0.35))
        grad.addColorStop(1, alpha(COLORS.teal, 0.02))
        return grad
      },
      fill: true,
      tension: 0.4,
      pointRadius: 2,
      pointHoverRadius: 5,
      pointBackgroundColor: COLORS.teal,
      borderWidth: 2.5,
    }],
  }
  const dailyOpts: ChartOptions<'line'> = {
    ...DEFAULTS,
    plugins: {
      ...DEFAULTS.plugins,
      tooltip: {
        ...DEFAULTS.plugins.tooltip,
        callbacks: {
          label: (ctx) => `${fmtMAD(ctx.parsed.y)}`,
        },
      },
    },
    scales: {
      x: { ...DEFAULTS.scales.x },
      y: {
        ...DEFAULTS.scales.y,
        ticks: { ...DEFAULTS.scales.y.ticks, callback: (v) => fmtMAD(Number(v)) },
      },
    },
  }

  const catBarData: ChartData<'bar'> = {
    labels: revByCat.map(c => c.category),
    datasets: [{
      label: 'CA',
      data: revByCat.map(c => c.revenue),
      backgroundColor: revByCat.map((_, i) => CHART_COLORS[i % CHART_COLORS.length]),
      borderRadius: 6,
      barThickness: 22,
    }],
  }
  const catBarOpts: ChartOptions<'bar'> = {
    ...DEFAULTS,
    indexAxis: 'y',
    plugins: {
      ...DEFAULTS.plugins,
      tooltip: {
        ...DEFAULTS.plugins.tooltip,
        callbacks: { label: (ctx) => ` ${fmtMAD(ctx.parsed.x)}` },
      },
    },
    scales: {
      x: { ...DEFAULTS.scales.x, ticks: { ...DEFAULTS.scales.x.ticks, callback: v => fmtMAD(Number(v)) } },
      y: { ...DEFAULTS.scales.y, grid: { display: false } },
    },
  }

  const donutOpts: ChartOptions<'doughnut'> = {
    responsive: true,
    maintainAspectRatio: false,
    cutout: '65%',
    plugins: {
      legend: { position: 'bottom', labels: { padding: 12, usePointStyle: true, pointStyle: 'circle', font: { size: 11, family: 'Inter, system-ui' } } },
      tooltip: {
        ...DEFAULTS.plugins.tooltip,
        callbacks: { label: (ctx) => ` ${ctx.label}: ${fmtMAD(ctx.parsed)}` },
      },
    },
  }
  const expDonutData: ChartData<'doughnut'> = {
    labels: expCat.map(e => e.category),
    datasets: [{
      data: expCat.map(e => e.amount),
      backgroundColor: expCat.map((_, i) => CHART_COLORS[i % CHART_COLORS.length]),
      borderWidth: 0,
      hoverOffset: 6,
    }],
  }
  const fleetDonutData: ChartData<'doughnut'> = {
    labels: fleetCat.map(f => f.category.charAt(0).toUpperCase() + f.category.slice(1)),
    datasets: [{
      data: fleetCat.map(f => f.count),
      backgroundColor: fleetCat.map((_, i) => CHART_COLORS[i % CHART_COLORS.length]),
      borderWidth: 0,
      hoverOffset: 6,
    }],
  }

  const monthlyBarData: ChartData<'bar'> = {
    labels: revMonthly.map(m => m.month),
    datasets: [{
      label: 'CA (MAD)',
      data: revMonthly.map(m => m.revenue),
      backgroundColor: revMonthly.map((_, i) => [COLORS.teal, COLORS.amber, COLORS.violet][i % 3]),
      borderRadius: 8,
      barThickness: 48,
    }],
  }
  const monthlyBarOpts: ChartOptions<'bar'> = {
    ...DEFAULTS,
    plugins: {
      ...DEFAULTS.plugins,
      tooltip: {
        ...DEFAULTS.plugins.tooltip,
        callbacks: {
          label: (ctx) => ` ${fmtMAD(ctx.parsed.y)} · ${revMonthly[ctx.dataIndex]?.count ?? 0} locations`,
        },
      },
    },
    scales: {
      x: { ...DEFAULTS.scales.x },
      y: {
        ...DEFAULTS.scales.y,
        ticks: { ...DEFAULTS.scales.y.ticks, callback: v => fmtMAD(Number(v)) },
      },
    },
  }

  const channelBarData: ChartData<'bar'> = bi ? {
    labels: bi.channels.map(c => c.name),
    datasets: [{
      label: 'Locations',
      data: bi.channels.map(c => c.count),
      backgroundColor: bi.channels.map((_, i) => CHART_COLORS[i % CHART_COLORS.length]),
      borderRadius: 6,
      barThickness: 20,
    }],
  } : { labels: [], datasets: [] }
  const channelOpts: ChartOptions<'bar'> = {
    ...DEFAULTS,
    indexAxis: 'y',
    scales: {
      x: { ...DEFAULTS.scales.x },
      y: { ...DEFAULTS.scales.y, grid: { display: false } },
    },
  }

  const profitColor = bi && bi.profit_month >= 0 ? COLORS.green : COLORS.rose
  const expDelta = bi && bi.expenses_prev_month
    ? ((bi.expenses_month - bi.expenses_prev_month) / bi.expenses_prev_month) * 100
    : null

  return (
    <>
      {/* ── Header ─────────────────────────────────────────────────────── */}
      <div className="topbar">
        <div>
          <h1>Tableau de bord</h1>
          <div className="sub">Vue d'ensemble · Agence Mobilité Rabat</div>
        </div>
        <div className="row-actions" style={{ gap: 10, alignItems: 'center' }}>
          <select
            className="month-select"
            value={month}
            onChange={e => setMonth(Number(e.target.value))}
            aria-label="Mois"
          >
            {Object.entries(MONTHS).map(([k, v]) => (
              <option key={k} value={k}>{v} 2026</option>
            ))}
          </select>
          {bi && <span className="tag">📊 {fmtNum(bi.rentals_month)} locations ce mois</span>}
        </div>
      </div>

      {/* ── KPI Row ────────────────────────────────────────────────────── */}
      {bi && (
        <div className="grid c5" style={{ marginBottom: 16 }}>
          <KPI
            label="Chiffre d'affaires"
            value={fmtMAD(bi.revenue_month)}
            trend={bi.revenue_delta_pct}
            hint="vs mois précédent"
          />
          <KPI
            label="Locations actives"
            value={String(bi.active_rentals)}
            hint={`${bi.rented_today} / ${bi.total_vehicles} véhicules`}
          />
          <KPI
            label="Taux d'occupation"
            value={`${bi.occupancy_pct}%`}
            hint={`${bi.in_maintenance} en maintenance`}
            color={bi.occupancy_pct > 70 ? COLORS.green : bi.occupancy_pct > 40 ? COLORS.amber : COLORS.rose}
          />
          <KPI
            label="Dépenses"
            value={fmtMAD(bi.expenses_month)}
            trend={expDelta}
            hint="vs mois précédent"
          />
          <KPI
            label="Résultat net"
            value={fmtMAD(bi.profit_month)}
            color={profitColor}
            hint={bi.profit_month >= 0 ? 'Bénéfice' : 'Déficit'}
          />
        </div>
      )}

      {/* ── Revenue Area Chart ─────────────────────────────────────────── */}
      <div className="card chart-card" style={{ marginBottom: 16 }}>
        <h2>Évolution du chiffre d'affaires — {MONTHS[month]} 2026</h2>
        <div style={{ height: 260 }}>
          <Line data={dailyData} options={dailyOpts} />
        </div>
      </div>

      {/* ── 3 Charts Row ───────────────────────────────────────────────── */}
      <div className="grid c3" style={{ marginBottom: 16 }}>
        <div className="card chart-card">
          <h2>CA par segment</h2>
          <div style={{ height: 220 }}>
            <Bar data={catBarData} options={catBarOpts} />
          </div>
        </div>
        <div className="card chart-card">
          <h2>Répartition des dépenses</h2>
          <div style={{ height: 220 }}>
            <Doughnut data={expDonutData} options={donutOpts} />
          </div>
        </div>
        <div className="card chart-card">
          <h2>Flotte par catégorie</h2>
          <div style={{ height: 220 }}>
            <Doughnut data={fleetDonutData} options={donutOpts} />
          </div>
        </div>
      </div>

      {/* ── Monthly Bar Chart ──────────────────────────────────────────── */}
      <div className="card chart-card" style={{ marginBottom: 16 }}>
        <h2>Chiffre d'affaires mensuel</h2>
        <div style={{ height: 220 }}>
          <Bar data={monthlyBarData} options={monthlyBarOpts} />
        </div>
      </div>

      {/* ── Bottom Row ─────────────────────────────────────────────────── */}
      <div className="grid c2">
        <div className="card chart-card">
          <h2>Canaux d'acquisition</h2>
          <div style={{ height: 200 }}>
            <Bar data={channelBarData} options={channelOpts} />
          </div>
        </div>

        {bi && (
          <div className="card" style={{ padding: 20 }}>
            <h2>Indicateurs clés</h2>
            <div className="grid c2" style={{ gap: 12, marginTop: 12 }}>
              <div className="mini-kpi">
                <div className="mini-label">Durée moy.</div>
                <div className="mini-value">{bi.avg_rental_days ?? '—'} <small>jours</small></div>
              </div>
              <div className="mini-kpi">
                <div className="mini-label">Tarif moy.</div>
                <div className="mini-value">{bi.avg_daily_rate ? fmtMAD(bi.avg_daily_rate) : '—'} <small>/jour</small></div>
              </div>
              <div className="mini-kpi">
                <div className="mini-label">Clients ce mois</div>
                <div className="mini-value">{fmtNum(bi.clients_month)}</div>
              </div>
              <div className="mini-kpi">
                <div className="mini-label">RDV aujourd'hui</div>
                <div className="mini-value">{bi.appointments_today} <small>+ {bi.appointments_week} cette semaine</small></div>
              </div>
            </div>
          </div>
        )}
      </div>
    </>
  )
}
