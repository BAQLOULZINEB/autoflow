# IMAGES.md — Guide des figures du rapport LaTeX

Ce fichier accompagne `rapport_autoflow.tex`. Chaque figure référencée dans le `.tex` est listée ici avec : **nom exact du fichier attendu** dans le dossier de compilation (même répertoire que le `.tex` sur Overleaf), **type**, **description précise** de ce qu'il faut voir, **source recommandée** pour l'obtenir, et **placement** dans le rapport.

> Astuce Overleaf : placer toutes les images dans le même dossier que le `.tex`, en `.png` (ou `.pdf` vectoriel pour les schémas). Résolution recommandée : 1600 px de large minimum pour un rendu net en PDF.

---

## 0. Logos (page de garde)

### `logoEmsi.png`
- **Type** : logo institutionnel EMSI.
- **Source** : logo officiel EMSI Rabat (déjà en ta possession).
- **Placement** : page de garde, à gauche.

### `honoris_logo.png`
- **Type** : logo institutionnel Honoris United Universities.
- **Source** : logo officiel Honoris (déjà en ta possession).
- **Placement** : page de garde, à droite.

---

## 1. Infographie problème → système → résultat

### `fig_infographie_probleme_solution.png`
- **Type** : infographie hero (bandeau visuel).
- **Description** : trois blocs horizontaux — (1) **Chaos** : icônes WhatsApp/Facebook/formulaire/téléphone/comptoir en désordre, mention « re-saisie, dates floues, relances oubliées » ; (2) **Système AutoFlow** au centre : cercle avec 1 orchestrateur + 3 agents + un humain ; (3) **Résultat** : file à valider claire, brouillons prêts, KPI auditables.
- **Source recommandée** : réutiliser `docs/assets/infographie_probleme_systeme_resultat.png` **ou** `docs/assets/infographie_flux_operationnel.png` (déjà présents dans le repo — les renommer/copier).
- **Placement** : section 1 (Introduction), après la démarche.

---

## 2. Diagrammes C4 (architecture)

### `fig_c4_contexte.png` — Vue contexte
- **Type** : diagramme C4 niveau 1 (contexte système).
- **Description** : au centre AutoFlow (workflow supervisé) ; autour, les acteurs humains (Client, Équipe agence, Manager) et les systèmes externes en pointillés (LLM Anthropic/OpenAI/Ollama, n8n, WhatsApp Business API). Flèches étiquetées « message texte », « valide/modifie/envoie », « escalades », « extraction optionnelle ». **Mention frontière clé** : *AutoFlow n'envoie jamais un message au client*.
- **Source recommandée** : ouvrir `docs/diagrams/01-contexte.html` dans Chrome → export PNG via impression PDF ou capture haute résolution. Alternativement : re-générer avec `python docs/diagrams/build_diagrams.py`.
- **Placement** : section 5.1 (Vue d'ensemble).

### `fig_c4_conteneurs.png` — Vue conteneurs
- **Type** : diagramme C4 niveau 2 (conteneurs techniques).
- **Description** : trois zones — Vercel/Netlify (React + Vite + TS, écrans /login, /queue, /requests/:id, /architecture, /demande) ; Backend Python (FastAPI + Orchestrateur LangGraph + 3 Agents + Service orchestrator + rules.json + SQLite/Postgres + checkpoints.db) ; LLM externe en pointillés. Flèches : HTTPS JSON /api/*, appel with_structured_output, store.transition → Event, thread_id = request_id.
- **Source recommandée** : `docs/diagrams/02-conteneurs.html` → export PNG.
- **Placement** : section 5.2 (Vue conteneurs).

### `fig_graphe_langgraph.png` — Graphe d'orchestration
- **Type** : diagramme de workflow (nœuds + arêtes conditionnelles).
- **Description** : nœuds `START → intake → route_after_intake → {escalate | clarify | availability} → decide_after_availability → {sensitive | draft} → human_review [interrupt] → finalize → END`. Bien marquer les deux gardes en losange, le nœud `human_review` en style « gate » (fond navy), et la flèche de retour `Command(goto=availability)` depuis `human_review`. Palette navy/teal/crème.
- **Source recommandée** : `docs/diagrams/03-workflow.html` → export PNG. Alternative : capture depuis l'onglet **Architecture** de l'espace admin (le graphe est exposé par `GET /api/graph`).
- **Placement** : section 5.3 (Le graphe LangGraph).

### `fig_sequence_scenario_c.png` — Diagramme de séquence scénario C
- **Type** : diagramme UML de séquence (interactions dans le temps).
- **Description** : 6 participants en colonnes (Espace admin, FastAPI, LangGraph, Intake, Availability, DB, Manager). Séquence : POST /demo/load/C → INSERT Request → invoke(thread=A-0003) → run_intake → `dates conf 0.55, discount_requested` → route clarify → interrupt(payload) → **Manager complète dates 24→26/10** → Command(resume) → Command(goto=availability) → check_availability → sensitive (remise) → interrupt → **Manager approuve avec note** → transition escalated→quote_ready→pending_customer → END. Deux `interrupt()` bien visibles.
- **Source recommandée** : reprendre le mermaid `sequenceDiagram` de `docs/02-architecture.md §2.5` → coller dans mermaid.live → export PNG. Ou générer via draw.io.
- **Placement** : chapitre 4, section 4.8 (Vue séquence).

### `fig_c4_deploiement.png` — Vue déploiement
- **Type** : diagramme C4 niveau 4 (déploiement).
- **Description** : trois zones — (1) Dev/démo laptop : Vite dev :5173 + uvicorn :8000 + fichiers SQLite ; (2) Cloud pilote distant : Vercel/Netlify (frontend) + Render/Railway/Fly (Docker backend, volume /data) + Neon/Supabase Postgres optionnel ; (3) Serverless tout-Vercel : Vercel Python + backend/api/index.py + DB éphémère → Neon. Flèches HTTPS + X-Admin-Token.
- **Source recommandée** : `docs/diagrams/04-deploiement.html` → export PNG.
- **Placement** : section 5.7 (Vue déploiement).

---

## 3. Machine à états

### `fig_machine_etats.png`
- **Type** : diagramme de machine à états (bulles + transitions).
- **Description** : 10 états en cercles reliés par des flèches étiquetées : `new → incomplete → checked → quote_ready → pending_customer → stalled → needs_human → escalated → confirmed → closed`. Colorier les 3 états « alerte » (`needs_human`, `escalated`, `stalled`) en orange, les 2 états terminaux (`confirmed`, `closed`) en vert, les autres en bleu clair. Ajouter les principales transitions inverses (ex : `pending_customer → confirmed`, `needs_human → checked`).
- **Source recommandée** : dessiner à Mermaid.live avec `stateDiagram-v2` puis export SVG/PNG ; ou utiliser draw.io ; ou générer avec la skill **diagram-design** en réutilisant la palette du projet.
- **Placement** : section 5.4 (Machine à états).

---

## 4. Screenshots de l'espace admin

### `fig_admin_queue.png` — File à valider
- **Type** : capture d'écran de l'espace admin.
- **Description** : page `/queue`. On doit y voir : bandeau supérieur « File à valider », deux onglets (Équipe / Manager), liste de 5–7 demandes avec pour chacune : identifiant (ex. A-0003), niveau (badge), priorité (haute/normale), **raison lisible** (ex. « Remise demandée — validation manager »), aperçu du brouillon, boutons *Approuver · Modifier · Refuser*.
- **Source recommandée** : lancer `npm run dev` dans `frontend/`, se connecter avec `change-me-admin`, aller sur `/queue`, faire capture d'écran (F12 device mode 1440×900 pour un rendu propre).
- **Placement** : section 6.6 (Espace d'administration).

### `fig_admin_live_trace.png` — Suivi en direct + raisonnement
- **Type** : capture d'écran (idéalement 2 panneaux côte à côte).
- **Description** : page `/live` OU onglet *Raisonnement* d'une fiche demande. Deux zones : (1) **flux d'événements** en temps quasi réel (liste horodatée) ; (2) **graphe du workflow avec chemin allumé** — nœuds réellement traversés en teal, autres en gris — et à côté un tableau listant chaque règle évaluée (nom, valeur mesurée, seuil, branche déclenchée). Choisir un cas riche (scénario C avec ambiguité + remise = manager).
- **Source recommandée** : dans l'admin, jouer le scénario C via **Simulations**, puis ouvrir sa fiche → onglet *Raisonnement*. Capture d'écran.
- **Placement** : section 6.6 (Espace d'administration), juste après `fig_admin_queue.png`.

### `fig_admin_simulations.png` — Menu Simulations
- **Type** : capture d'écran.
- **Description** : page `/simulations`. On doit voir 7 cartes/lignes avec le **logo du canal** (WhatsApp, Facebook, Instagram, site web, téléphone, comptoir), le titre du cas, un résumé (1 ligne), un bouton *Jouer*, et en bas un bouton *Tout jouer*. Si possible, capturer un cas en cours d'exécution (étapes révélées avec ✓/✗).
- **Source recommandée** : capture directe depuis l'admin `/simulations`.
- **Placement** : section 6.8 (Simulations métier).

---

## 5. (Optionnel — bonus créatif)

Si tu veux ajouter du bonus visuel « out of the box » pour le jury sans surcharger, ajoute UNE des figures suivantes en annexe (elles ne sont pas référencées par le `.tex` actuel — il faudra insérer un `\includegraphics` supplémentaire) :

- **Timeline projet (8 semaines)** : diagramme Gantt allégé avec les 6 phases.
- **Radar des compétences AI Engineer** : LangGraph, HITL, RAG, prompt engineering, MLOps, API design, front, tests, comm métier — auto-évaluation avant/après stage.
- **Comparatif LangGraph vs MS Agent Framework vs CrewAI vs AutoGen** : tableau visuel (icônes + badges) sur 5 critères (HITL, checkpointing, courbe d'apprentissage, dépendance cloud, communauté).

---

## Récapitulatif — checklist avant compilation Overleaf

- [ ] `logoEmsi.png`
- [ ] `honoris_logo.png`
- [ ] `fig_infographie_probleme_solution.png`
- [ ] `fig_c4_contexte.png`
- [ ] `fig_c4_conteneurs.png`
- [ ] `fig_graphe_langgraph.png`
- [ ] `fig_c4_deploiement.png`
- [ ] `fig_machine_etats.png`
- [ ] `fig_admin_queue.png`
- [ ] `fig_admin_live_trace.png`
- [ ] `fig_sequence_scenario_c.png`
- [ ] `fig_admin_simulations.png`

**Total : 12 fichiers image** (2 logos + 9 figures). Tous à déposer dans le même dossier que `rapport_autoflow.tex` sur Overleaf.

Si une figure manque au moment de la compilation, LaTeX ne bloquera pas nécessairement (le `\includegraphics` échouera pour cette figure uniquement) — mais préfère avoir toutes les images prêtes pour un rendu final propre.
