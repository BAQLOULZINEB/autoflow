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
      <div className="topbar"><div><h1>Comment fonctionne le système</h1><div className="sub">Le système traite chaque demande automatiquement, mais c'est toujours vous qui décidez. Voici comment il fonctionne étape par étape.</div></div></div>
      <div className="card" style={{ marginBottom: 14 }}>
        <h2>Parcours d'une demande client</h2>
        <WorkflowSvg />
        <p className="small muted" style={{ marginTop: 8 }}>Ce diagramme montre le chemin que suit chaque demande dans le système. Les nœuds roses nécessitent votre validation.</p>
      </div>
      <div className="grid c2" style={{ alignItems: 'start' }}>
        <div className="card">
          <h2>Vue d'ensemble simplifiée</h2>
          <Diagram code={OVERVIEW} id="ov" />
          <div className="legend"><span><span className="dot" style={{ background: '#DDF3F2', border: '1px solid #0E9C99' }} />agent</span><span><span className="dot" style={{ background: '#0B1F3A' }} />orchestrateur / humain</span><span>— flux nominal · ┄ contrôle humain</span></div>
        </div>
        <div className="card">
          <h2>Graphe technique détaillé</h2>
          {graph ? <Diagram code={graph} id="lg" /> : <p className="muted">Chargement…</p>}
          <p className="small muted">Quand le système arrive à l'étape « validation humaine », il s'arrête et attend votre décision. Vous pouvez approuver, modifier ou refuser depuis la page « À traiter ».</p>
        </div>
      </div>
      <div className="card" style={{ marginTop: 14 }}>
        <h2>Vos données, vos graphiques</h2>
        <div className="grid c3">
          <div>
            <h3>Import depuis Excel</h3>
            <p className="small muted">Chargez votre fichier Excel avec les feuilles Flotte, Clients, Locations, Dépenses et Rendez-vous. Le système vérifie automatiquement les erreurs (dates inversées, doublons, CIN invalides).</p>
          </div>
          <div>
            <h3>Calcul automatique des chiffres</h3>
            <p className="small muted">Tous les graphiques et indicateurs sont calculés en temps réel à partir de vos données. Revenus, dépenses, taux d'occupation, classement clients — tout est mis à jour automatiquement.</p>
          </div>
          <div>
            <h3>Graphiques visuels</h3>
            <p className="small muted">6 types de graphiques interactifs pour visualiser vos données : courbes, barres, camemberts. Survolez chaque élément pour voir les détails en dirhams (MAD).</p>
          </div>
        </div>
      </div>
      <div className="card" style={{ marginTop: 14 }}>
        <h2>Principes de conception</h2>
        <div className="grid c3">
          <div><h3>Le système propose, vous décidez</h3><p className="small muted">Le système ne prend jamais de décision commerciale à votre place (prix, confirmation, réclamation). Il prépare le dossier, vous validez.</p></div>
          <div><h3>Données toujours fiables</h3><p className="small muted">La vérification des disponibilités est basée sur vos données réelles, jamais sur des estimations. Chaque information est vérifiable.</p></div>
          <div><h3>Tout est enregistré</h3><p className="small muted">Chaque action est tracée avec l'utilisateur, la raison et la date. Vous pouvez toujours retrouver qui a fait quoi et quand.</p></div>
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
