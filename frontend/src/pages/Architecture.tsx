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
        <h2>Principes de conception</h2>
        <div className="grid c3">
          <div><h3>Les agents proposent, l'orchestrateur route, l'humain décide</h3><p className="small muted">Aucune décision commerciale (prix, confirmation, réclamation) n'est prise par le système. Le routage suit une matrice d'escalade explicite.</p></div>
          <div><h3>Aucune disponibilité inventée</h3><p className="small muted">L'agent Disponibilité est du code déterministe sur la table flotte + règles. L'agent Intake ne garde un champ que s'il cite un passage exact du message.</p></div>
          <div><h3>Tout est tracé, tout est mesurable</h3><p className="small muted">Chaque transition écrit un événement (acteur, raison, horodatage). Les KPI sont calculés depuis le journal, jamais stockés.</p></div>
        </div>
      </div>
    </>
  )
}
