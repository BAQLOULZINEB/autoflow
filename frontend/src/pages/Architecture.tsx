import { useEffect, useRef, useState } from 'react'
import mermaid from 'mermaid'
import { api } from '../lib/api'
import WorkflowSvg from '../components/WorkflowSvg'

mermaid.initialize({ startOnLoad: false, theme: 'base', themeVariables: {
  fontFamily: 'Manrope, Inter, system-ui', lineColor: '#0E9C99', primaryColor: '#FFFFFF',
  primaryBorderColor: '#D8DCE3', primaryTextColor: '#111827', background: '#FAF8F4' } })

const OVERVIEW = `flowchart TD
  classDef human fill:#0B1F3A,color:#FFFFFF,stroke:#0B1F3A;
  classDef system fill:#DDF3F2,color:#0B1F3A,stroke:#0E9C99,stroke-width:1.5px;
  classDef orch fill:#0B1F3A,color:#FFFFFF,stroke:#0E9C99,stroke-width:2px;
  classDef neutral fill:#FFFFFF,color:#111827,stroke:#D8DCE3;
  C[Demande client<br/>WhatsApp · Facebook · formulaire · n8n]:::neutral
  I[Agent Intake<br/>structure + champs manquants + preuves]:::system
  O{{Orchestrateur LangGraph<br/>états · règles · journal · interrupt · escalade}}:::orch
  A[Agent Disponibilité<br/>déterministe, aucun LLM]:::system
  F[Agent Suivi<br/>brouillon · relance · prochaine action]:::system
  H[File de validation<br/>équipe / manager]:::human
  D[Dashboard admin<br/>statuts · KPI · journal]:::neutral
  C --> I --> O
  O -->|complète & confiante| A --> O
  O -->|résultat validé| F --> O
  O -.->|toujours : une personne envoie| H
  H -.->|approuver · modifier · refuser · compléter| O
  O --> D`

function Diagram({ code, id }: { code: string; id: string }) {
  const ref = useRef<HTMLDivElement>(null)
  useEffect(() => {
    let alive = true
    mermaid.render(id, code).then(({ svg }) => { if (alive && ref.current) ref.current.innerHTML = svg }).catch(e => { if (ref.current) ref.current.textContent = String(e) })
    return () => { alive = false }
  }, [code, id])
  return <div className="mermaid" ref={ref} />
}

export default function Architecture() {
  const [graph, setGraph] = useState('')
  useEffect(() => { api.graph().then(g => setGraph(g.mermaid)) }, [])
  return (
    <>
      <div className="topbar"><div><h1>Architecture</h1><div className="sub">1 orchestrateur + 3 agents spécialisés + humain dans la boucle. Le graphe de droite est généré par LangGraph à partir du code réel.</div></div></div>
      <div className="card" style={{ marginBottom: 14 }}>
        <h2>Workflow d'orchestration (vue technique)</h2>
        <WorkflowSvg />
        <p className="small muted" style={{ marginTop: 8 }}>Même diagramme que dans « Suivi en direct » : là-bas, le chemin réellement suivi par chaque demande s'allume.</p>
      </div>
      <div className="grid c2" style={{ alignItems: 'start' }}>
        <div className="card">
          <h2>Vue métier</h2>
          <Diagram code={OVERVIEW} id="ov" />
          <div className="legend"><span><span className="dot" style={{ background: '#DDF3F2', border: '1px solid #0E9C99' }} />agent</span><span><span className="dot" style={{ background: '#0B1F3A' }} />orchestrateur / humain</span><span>— flux nominal · ┄ contrôle humain</span></div>
        </div>
        <div className="card">
          <h2>Graphe LangGraph (source : <code>GET /api/graph</code>)</h2>
          {graph ? <Diagram code={graph} id="lg" /> : <p className="muted">Chargement…</p>}
          <p className="small muted">Le nœud <code>human_review</code> est un <code>interrupt()</code> : l'exécution est suspendue et persistée (checkpointer SQLite) jusqu'à la décision dans cet espace admin. « Compléter » renvoie vers <code>availability</code> via <code>Command(goto=…)</code>.</p>
        </div>
      </div>
      <div className="card" style={{ marginTop: 14 }}>
        <h2>Couche BI & Import de données</h2>
        <div className="grid c3">
          <div>
            <h3>Pipeline Excel → SQLite</h3>
            <p className="small muted">Import atomique d'un classeur .xlsx (5 feuilles : Flotte, Clients, Locations, Dépenses, RendezVous). Validation CIN marocain, détection doublons, correction automatique des dates inversées. Parsing via <code>openpyxl</code>.</p>
          </div>
          <div>
            <h3>Moteur d'analytique temps réel</h3>
            <p className="small muted">15+ endpoints BI calculés à la volée via SQLAlchemy (jamais de KPI stockés). CA journalier/mensuel, répartition dépenses, taux d'occupation par véhicule, ranking clients, canaux d'acquisition.</p>
          </div>
          <div>
            <h3>Visualisation Chart.js</h3>
            <p className="small muted">6 types de graphiques (area, bar, doughnut, horizontal bar). Palette 12 couleurs, tooltips en MAD, responsive. Données formatées côté client avec <code>react-chartjs-2</code>.</p>
          </div>
        </div>
      </div>
      <div className="card" style={{ marginTop: 14 }}>
        <h2>Principes de conception</h2>
        <div className="grid c3">
          <div><h3>Les agents proposent, l'orchestrateur route, l'humain décide</h3><p className="small muted">Aucune décision commerciale (prix, confirmation, réclamation) n'est prise par le système. Le routage suit une matrice d'escalade explicite.</p></div>
          <div><h3>Aucune disponibilité inventée</h3><p className="small muted">L'agent Disponibilité est du code déterministe sur la table flotte + règles. L'agent Intake ne garde un champ que s'il cite un passage exact du message.</p></div>
          <div><h3>Tout est tracé, tout est mesurable</h3><p className="small muted">Chaque transition écrit un événement (acteur, raison, horodatage). Les KPI sont calculés depuis le journal, jamais stockés.</p></div>
        </div>
      </div>
      <div className="card" style={{ marginTop: 14 }}>
        <h2>Stack technique</h2>
        <div className="grid c2">
          <div>
            <h3>Backend</h3>
            <ul className="small muted" style={{ paddingLeft: 16, lineHeight: 1.8 }}>
              <li><strong>FastAPI</strong> — API REST async, 25+ endpoints</li>
              <li><strong>LangGraph</strong> — orchestration multi-agents avec état persistant</li>
              <li><strong>SQLAlchemy + SQLite</strong> — ORM, migrations, checkpointing</li>
              <li><strong>openpyxl</strong> — parsing et validation Excel</li>
              <li><strong>3 agents</strong> : Intake (extraction), Disponibilité (déterministe), Suivi (relance)</li>
            </ul>
          </div>
          <div>
            <h3>Frontend</h3>
            <ul className="small muted" style={{ paddingLeft: 16, lineHeight: 1.8 }}>
              <li><strong>React 18 + TypeScript</strong> — SPA avec Vite</li>
              <li><strong>Chart.js + react-chartjs-2</strong> — graphiques BI interactifs</li>
              <li><strong>React Router v6</strong> — navigation 3 sections</li>
              <li><strong>Design system</strong> : Inter, densité dashboard, tokens CSS</li>
              <li><strong>Mermaid.js</strong> — diagrammes d'architecture générés</li>
            </ul>
          </div>
        </div>
      </div>
    </>
  )
}
