"""Render the dossier's dark-themed HTML+SVG diagrams from the diagram-design template.

Keeps the template's export toolbar (Copy / PNG / PDF) and SRI-pinned scripts intact;
only the title, subtitle, SVG body, cards and footer are replaced.
Run:  python docs/diagrams/build_diagrams.py
"""
from __future__ import annotations

import re
from pathlib import Path

TEMPLATE = Path.home() / ".claude/skills/diagram-design/resources/template.html"
OUT = Path(__file__).resolve().parent

C = {  # diagram-design palette
    "fe": ("rgba(8, 51, 68, 0.4)", "#22d3ee"), "be": ("rgba(6, 78, 59, 0.4)", "#34d399"),
    "db": ("rgba(76, 29, 149, 0.4)", "#a78bfa"), "cloud": ("rgba(120, 53, 15, 0.3)", "#fbbf24"),
    "sec": ("rgba(136, 19, 55, 0.4)", "#fb7185"), "bus": ("rgba(251, 146, 60, 0.3)", "#fb923c"),
    "ext": ("rgba(30, 41, 59, 0.5)", "#94a3b8"),
}


def box(x, y, w, h, kind, label, sub="", lines=(), dashed=False):
    fill, stroke = C[kind]
    dash = ' stroke-dasharray="4,4"' if dashed else ""
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="#0f172a"/>\n'
    s += f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{fill}" stroke="{stroke}" stroke-width="1.5"{dash}/>\n'
    s += f'<text x="{x + w / 2}" y="{y + 20}" fill="white" font-size="11" font-weight="600" text-anchor="middle">{label}</text>\n'
    if sub:
        s += f'<text x="{x + w / 2}" y="{y + 35}" fill="#94a3b8" font-size="9" text-anchor="middle">{sub}</text>\n'
    for i, ln in enumerate(lines):
        s += f'<text x="{x + w / 2}" y="{y + 50 + i * 13}" fill="#94a3b8" font-size="8" text-anchor="middle">{ln}</text>\n'
    return s


def arrow(pts, color="#64748b", label="", dashed=False, lx=None, ly=None):
    d = "M " + " L ".join(f"{x} {y}" for x, y in pts)
    dash = ' stroke-dasharray="5,5"' if dashed else ""
    s = f'<path d="{d}" fill="none" stroke="{color}" stroke-width="1.5" marker-end="url(#arrowhead)"{dash}/>\n'
    if label:
        (x0, y0), (x1, y1) = pts[0], pts[-1]
        s += f'<text x="{lx if lx is not None else (x0 + x1) / 2}" y="{ly if ly is not None else (y0 + y1) / 2 - 5}" fill="#94a3b8" font-size="8" text-anchor="middle">{label}</text>\n'
    return s


def region(x, y, w, h, label, color="#fbbf24"):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="rgba(251, 191, 36, 0.04)" stroke="{color}" stroke-width="1" stroke-dasharray="8,4"/>\n'
            f'<text x="{x + 12}" y="{y + 18}" fill="{color}" font-size="10" font-weight="600">{label}</text>\n')


def legend(x, y, items):
    s = f'<text x="{x}" y="{y}" fill="white" font-size="10" font-weight="600">Légende</text>\n'
    for i, (kind, txt) in enumerate(items):
        fill, stroke = C[kind]
        yy = y + 12 + i * 16
        s += f'<rect x="{x}" y="{yy}" width="16" height="10" rx="2" fill="{fill}" stroke="{stroke}" stroke-width="1"/><text x="{x + 22}" y="{yy + 8}" fill="#94a3b8" font-size="8">{txt}</text>\n'
    return s


def card(color, title, items):
    lis = "".join(f"<li>• {i}</li>" for i in items)
    return f'<div class="card"><div class="card-header"><div class="card-dot {color}"></div><h3>{title}</h3></div><ul>{lis}</ul></div>'


def render(name, title, subtitle, svg, viewbox, cards, footer):
    t = TEMPLATE.read_text(encoding="utf-8")
    t = t.replace('<html lang="en">', '<html lang="fr">')
    t = t.replace("<title>[PROJECT NAME] Architecture Diagram</title>", f"<title>{title}</title>")
    t = t.replace("<h1>[PROJECT NAME] Architecture</h1>", f"<h1>{title}</h1>")
    t = t.replace("[Subtitle description]", subtitle)
    t = re.sub(r'<svg viewBox="0 0 1000 680">.*?</svg>', lambda m: f'<svg viewBox="{viewbox}">' + DEFS + svg + "</svg>", t, flags=re.S)
    t = re.sub(r'<div class="cards">.*?</div>\s*<!-- Footer -->', '<div class="cards">' + "".join(cards) + "</div>\n\n    <!-- Footer -->", t, flags=re.S)
    t = t.replace("[Project Name] • [Additional metadata]", footer)
    (OUT / name).write_text(t, encoding="utf-8")
    print("→", OUT / name)


DEFS = '''<defs>
  <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="#64748b"/></marker>
  <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M 40 0 L 0 0 0 40" fill="none" stroke="#1e293b" stroke-width="0.5"/></pattern>
</defs>
<rect width="100%" height="100%" fill="url(#grid)"/>
'''

# =========================================================================== #
# 01 — System context
# =========================================================================== #
svg = ""
svg += arrow([(150, 205), (378, 205)], "#22d3ee", "message texte · formulaire /demande", lx=264, ly=196)
svg += arrow([(150, 335), (378, 300)], "#fb7185", "valide · modifie · envoie", lx=250, ly=308)
svg += arrow([(150, 455), (378, 330)], "#fb7185", "prix · réclamations · escalades", lx=230, ly=420)
svg += arrow([(622, 205), (810, 120)], "#94a3b8", "texte du message seulement ?", dashed=True, lx=740, ly=150)
svg += arrow([(810, 250), (622, 250)], "#fb923c", "POST /api/public/intake ?", dashed=True, lx=726, ly=242)
svg += arrow([(900, 380), (900, 290)], "#94a3b8", "futur ?", dashed=True, lx=925, ly=340)
svg += arrow([(500, 350), (500, 430)], "#a78bfa", "brouillons · file · KPI · journal", lx=500, ly=395)
svg += box(10, 180, 140, 50, "ext", "Client", "WhatsApp · FB · comptoir")
svg += box(30, 310, 120, 50, "sec", "Équipe agence", "Salma · Youssef")
svg += box(30, 430, 120, 50, "sec", "Manager", "Omar")
svg += box(380, 150, 240, 200, "be", "AutoFlow", "workflow supervisé",
           ["Intake · Disponibilité · Suivi", "Orchestrateur LangGraph", "matrice d'escalade · interrupt()", "journal d'événements · KPI", "n'envoie JAMAIS au client seul"])
svg += box(810, 90, 180, 50, "ext", "Fournisseur LLM", "Anthropic · OpenAI · Ollama", dashed=True)
svg += box(810, 225, 180, 50, "bus", "n8n", "webhooks · notifications", dashed=True)
svg += box(810, 380, 180, 50, "ext", "WhatsApp Business", "via n8n (futur)", dashed=True)
svg += box(380, 430, 240, 60, "fe", "Espace admin", "React · Vercel / Netlify", ["/queue · /live · /requests/:id"])
svg += legend(700, 470, [("be", "système étudié"), ("fe", "interface admin"), ("sec", "humains dans la boucle"), ("ext", "externe / optionnel (pointillé = hypothèse)")])
render("01-contexte.html", "AutoFlow — Vue contexte", "Qui parle au système, et la frontière clé : aucune sortie vers le client sans clic humain.", svg, "0 0 1000 560",
       [card("emerald", "Frontière (FACT)", ["Le système produit des brouillons ; une personne envoie", "Aucune disponibilité inventée : code déterministe", "Chaque décision est tracée avec acteur et raison"]),
        card("rose", "Humains dans la boucle", ["Équipe : relit, modifie, envoie, complète", "Manager : remises, réclamations, longues durées", "Escalade = fonctionnalité, pas défaut"]),
        card("amber", "Hypothèses (pointillé)", ["LLM optionnel — rules-only par défaut, coût 0", "n8n pour brancher WhatsApp / Typeform / Slack", "Aucun connecteur client réel dans le pilote"])],
       "AutoFlow • Projet de stage AI Engineer • agence de location, Rabat • vue 1/4")

# =========================================================================== #
# 02 — Containers
# =========================================================================== #
svg = ""
svg += region(30, 40, 300, 150, "Vercel / Netlify — statique")
svg += region(30, 230, 940, 400, "Backend Python")
svg += arrow([(280, 150), (280, 268)], "#22d3ee", "HTTPS JSON · X-Admin-Token", lx=380, ly=215)
svg += arrow([(300, 300), (378, 300)], "#34d399")
svg += arrow([(498, 300), (578, 300)], "#34d399", "submit · resume")
svg += arrow([(700, 300), (700, 370)], "#34d399")
svg += arrow([(640, 400), (560, 400)], "#34d399")
svg += arrow([(760, 400), (840, 400)], "#34d399")
svg += arrow([(700, 430), (700, 500)], "#34d399")
svg += arrow([(820, 520), (900, 520)], "#a78bfa", "thread", lx=860, ly=580)
svg += arrow([(580, 520), (500, 520)], "#a78bfa", "events", lx=540, ly=580)
svg += arrow([(440, 440), (440, 500)], "#a78bfa", "rules.json", lx=470, ly=475)
svg += arrow([(560, 385), (570, 385), (570, 350), (930, 350), (930, 142)], "#94a3b8", "with_structured_output (optionnel)", dashed=True, lx=760, ly=344)
svg += box(60, 80, 240, 70, "fe", "Espace admin", "React 19 + Vite + TS", ["/login /queue /live /requests/:id", "/architecture /demande (public)"])
svg += box(60, 270, 240, 60, "be", "FastAPI", "app/main.py", ["auth · CORS · 20 routes"])
svg += box(380, 270, 118, 60, "be", "Service", "orchestrator.py", ["submit · sweep · kpis"])
svg += box(580, 270, 240, 60, "be", "Orchestrateur LangGraph", "workflow/graph.py", ["StateGraph · interrupt · Command"])
svg += box(440, 370, 120, 60, "be", "Agent Intake", "agents/intake.py", ["règles + LLM optionnel"])
svg += box(640, 370, 120, 60, "be", "Agent Dispo.", "availability.py", ["déterministe · 0 LLM"])
svg += box(840, 370, 120, 60, "be", "Agent Suivi", "followup.py", ["brouillons · relances"])
svg += box(380, 500, 120, 50, "db", "rules.json", "règles versionnées")
svg += box(580, 500, 240, 60, "db", "SQLite / PostgreSQL", "SQLAlchemy 2", ["requests · events · drafts · reviews", "follow_ups · vehicles · bookings"])
svg += box(900, 500, 60, 60, "db", "ckpt", "SqliteSaver")
svg += box(880, 90, 100, 50, "ext", "LLM API", "optionnel", dashed=True)
svg += legend(30, 660, [("fe", "frontend"), ("be", "backend Python"), ("db", "données / config"), ("ext", "externe optionnel")])
render("02-conteneurs.html", "AutoFlow — Vue conteneurs", "De quoi est fait le système : un frontend statique, une API, un graphe, trois agents, une base et un checkpointer.", svg, "0 0 1000 740",
       [card("cyan", "Frontend", ["Vite + React + TypeScript, aucun secret embarqué", "Token saisi à la connexion, stocké côté navigateur", "Déployable Vercel / Netlify en 1 commande"]),
        card("emerald", "Backend", ["FastAPI 0.141 · LangGraph 1.2 · Python 3.12+", "Fonctionne hors ligne (LLM_PROVIDER=none)", "Docker · Render · ou Vercel Python (/tmp)"]),
        card("violet", "Données", ["SQLite par défaut, PostgreSQL = 1 variable d'env", "KPI calculés depuis events, jamais stockés", "Checkpoints LangGraph = reprise après crash"])],
       "AutoFlow • vue 2/4 • trait pointillé = optionnel / hypothèse")

# =========================================================================== #
# 03 — Workflow (same layout as the admin's live panel)
# =========================================================================== #
svg = ""
svg += arrow([(110, 172), (138, 172)], "#22d3ee")
svg += arrow([(260, 172), (288, 172)], "#22d3ee")
svg += arrow([(410, 172), (425, 172), (425, 56), (438, 56)], "#64748b", "complaint", lx=425, ly=110)
svg += arrow([(410, 172), (425, 172), (425, 126), (438, 126)], "#64748b", "incomplet", lx=425, ly=150)
svg += arrow([(410, 172), (425, 172), (425, 220), (438, 220)], "#64748b", "ok", lx=430, ly=205)
svg += arrow([(560, 220), (588, 220)], "#64748b")
svg += arrow([(710, 220), (725, 220), (725, 156), (738, 156)], "#64748b", "oui", lx=725, ly=180)
svg += arrow([(710, 220), (725, 220), (725, 236), (738, 236)], "#64748b", "non", lx=725, ly=252)
for x0, y0 in ((560, 56), (560, 126)):
    svg += arrow([(x0, y0), (575, y0), (575, 300), (700, 300), (700, 318)], "#fb7185", dashed=True)
for x0 in (800,):
    svg += arrow([(x0, 182), (x0, 300), (700, 300), (700, 318)], "#fb7185", dashed=True)
    svg += arrow([(x0, 262), (x0, 300)], "#fb7185", dashed=True)
svg += arrow([(780, 352), (818, 352)], "#22d3ee", "approve / edit", lx=799, ly=344)
svg += arrow([(620, 352), (500, 352), (500, 252)], "#22d3ee", "complete + fields", dashed=True, lx=560, ly=344)
svg += arrow([(880, 378), (880, 408)], "#22d3ee")
svg += box(20, 150, 90, 44, "ext", "Demande", "WA · form · n8n")
svg += box(140, 142, 120, 60, "be", "Intake", "structure + preuves")
svg += box(290, 142, 120, 60, "db", "Routage 1", "seuils rules.json")
svg += box(440, 30, 120, 52, "sec", "Escalade", "réclamation → manager")
svg += box(440, 100, 120, 52, "be", "Clarifier", "question courte")
svg += box(440, 190, 120, 60, "be", "Disponibilité", "déterministe · 0 LLM")
svg += box(590, 190, 120, 60, "db", "Matrice", "d'escalade")
svg += box(740, 130, 120, 52, "sec", "Sensible", "remise · VIP · > 14 j")
svg += box(740, 210, 120, 52, "be", "Brouillon", "prix injecté")
svg += box(620, 320, 160, 64, "sec", "Validation humaine", "interrupt() · équipe / manager")
svg += box(820, 326, 120, 52, "fe", "Finaliser", "envoi · relance +24 h")
svg += box(820, 410, 120, 52, "fe", "Relances", "24 h · max 2 · 72 h")
svg += legend(20, 400, [("be", "agent spécialisé"), ("db", "décision orchestrateur (règles)"), ("sec", "point de contrôle humain"), ("fe", "orchestrateur / suivi")])
render("03-workflow.html", "AutoFlow — Workflow d'orchestration", "Le graphe LangGraph réel : agents en vert, décisions par règles en violet, contrôle humain en rose. Identique au panneau « Suivi en direct ».", svg, "0 0 960 480",
       [card("violet", "Routage 1 (après Intake)", ["complaint → escalade manager, aucun brouillon", "manquants · champ < 0.7 · global < 0.75 → clarifier", "sinon → disponibilité"]),
        card("rose", "Matrice d'escalade", ["remise demandée → manager", "VIP + alternative · > 14 j · > 6000 MAD", "invalide / indisponible / hops > 8 → humain"]),
        card("cyan", "Après la décision", ["approve/edit : envoi simulé, relance +24 h", "complete : retour à Disponibilité (Command goto)", "reject/close : clôture tracée"])],
       "AutoFlow • vue 3/4 • généré depuis le même modèle que l'espace admin")

# =========================================================================== #
# 04 — Deployment
# =========================================================================== #
svg = ""
svg += region(30, 40, 290, 230, "Laptop — dev / démo à l'agence")
svg += region(360, 40, 610, 230, "Cloud — pilote distant (gratuit ou ~0 MAD/mois)")
svg += region(360, 300, 610, 150, "Option tout-Vercel (serverless)")
svg += arrow([(175, 130), (175, 170)], "#22d3ee", "proxy /api", lx=210, ly=152)
svg += arrow([(175, 230), (175, 250)], "#a78bfa")
svg += arrow([(520, 130), (520, 170)], "#22d3ee", "HTTPS + X-Admin-Token", lx=600, ly=152)
svg += arrow([(640, 200), (760, 200)], "#a78bfa", "DATABASE_URL ?", dashed=True)
svg += arrow([(520, 230), (520, 250)], "#a78bfa")
svg += box(60, 80, 230, 50, "fe", "vite dev :5173", "npm run dev")
svg += box(60, 170, 230, 60, "be", "uvicorn :8000", "python -m uvicorn app.main:app", ["LLM_PROVIDER=none · 0 appel externe"])
svg += box(60, 250, 230, 14, "db", "", "")
svg += '<text x="175" y="261" fill="#a78bfa" font-size="8" text-anchor="middle">autoflow.db · checkpoints.db</text>\n'
svg += box(400, 80, 240, 50, "fe", "Vercel / Netlify", "frontend/dist · VITE_API_URL")
svg += box(400, 170, 240, 60, "cloud", "Render / Railway / Fly", "Docker backend/", ["volume /data · ADMIN_TOKEN · CORS_ORIGINS"])
svg += box(760, 170, 200, 60, "db", "Neon / Supabase", "PostgreSQL (optionnel)", ["1 variable d'env, 0 changement de code"], dashed=True)
svg += box(400, 250, 240, 14, "db", "", "")
svg += '<text x="520" y="261" fill="#a78bfa" font-size="8" text-anchor="middle">/data/autoflow.db (volume persistant)</text>\n'
svg += box(400, 340, 240, 60, "cloud", "Vercel Python", "backend/api/index.py", ["DB dans /tmp = éphémère → Postgres conseillé"])
svg += box(700, 340, 240, 60, "sec", "Secrets", "variables d'environnement", ["ADMIN_TOKEN · clés LLM · jamais dans le code"])
svg += legend(30, 480, [("fe", "frontend statique"), ("be", "processus Python"), ("cloud", "hébergeur"), ("db", "stockage"), ("sec", "sécurité")])
render("04-deploiement.html", "AutoFlow — Vue déploiement", "Trois façons de faire tourner le pilote, de la démo sur laptop au cloud gratuit.", svg, "0 0 1000 580",
       [card("emerald", "Coût pour l'agence", ["Laptop : 0 MAD, fonctionne hors ligne", "Cloud : offres gratuites Vercel + Render + Neon", "LLM : optionnel ; ~0,01 MAD par demande si activé"]),
        card("amber", "Déploiement", ["frontend : vercel --prod (ou netlify deploy)", "backend : docker build / render.yaml", "docker compose up pour tout lancer localement"]),
        card("rose", "Sécurité pilote", ["Token admin par en-tête, formulaire public sans token", "Téléphones masqués, données fictives", "Seul le texte du message part vers un LLM (si activé)"])],
       "AutoFlow • vue 4/4")
