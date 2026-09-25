# Rapport de stage

## AutoFlow — système d'automatisation intelligent des workflows d'entreprise
### Conception et réalisation d'un système multi-agents supervisé pour le traitement des demandes d'une agence de location de voitures (Rabat)

**Intitulé du stage :** AI Engineer — automatisation des workflows métier
**Année universitaire :** 2026-2027
**Auteur :** *[Nom Prénom]* · **Encadrant académique :** *[Nom]* · **Tuteur entreprise :** *[Nom, gérant de l'agence]*
**Mots-clés :** systèmes multi-agents, LangGraph, human-in-the-loop, orchestration de workflows, extraction d'information, PME, automatisation supervisée

> Les champs entre crochets sont à compléter. Les chiffres cités sont ceux du dépôt au 21 septembre 2026 et sont reproductibles (`pytest -q`, `python -m eval.eval_intake`). Les figures renvoient aux fichiers de `docs/diagrams/` et `docs/assets/`.

---

## Remerciements

*[À rédiger : encadrant académique, tuteur entreprise, équipe de l'agence qui a accepté d'être observée, établissement.]*

---

## Résumé

Les petites et moyennes entreprises de services reçoivent leurs demandes clients par des canaux dispersés — WhatsApp, réseaux sociaux, téléphone, formulaire, comptoir — et les traitent manuellement. Il en résulte des re-saisies, des vérifications lentes, des relances oubliées et une faible visibilité pour le dirigeant. Ce stage étudie ce problème dans le cas d'une agence de location de voitures à Rabat et propose *AutoFlow*, un système d'automatisation **supervisé** : le système structure chaque demande, vérifie la disponibilité selon des règles, prépare réponses et relances, trace chaque décision, et transmet à une personne tout cas ambigu ou sensible. L'architecture est volontairement compacte — un orchestrateur LangGraph, trois agents spécialisés (comprendre, vérifier, préparer) et un point de contrôle humain — et privilégie la fiabilité à l'autonomie : aucune disponibilité n'est inventée, aucun message n'est envoyé sans clic humain, tout indicateur est calculé depuis un journal d'événements. Le prototype, livré avec un espace d'administration, un jeu de données réaliste et sept simulations métier automatisées, est évalué sur 45 messages étiquetés : 89 à 91 % d'exactitude par champ pour l'extraction, et surtout 100 % des extractions erronées interceptées par la validation humaine. Les gains métier sont cadrés pour une mesure avant/après en pilote, sans chiffre promis à l'avance.

## Abstract

Service SMEs receive customer requests through scattered channels and process them by hand, which causes re-typing, slow checks, forgotten follow-ups and poor managerial visibility. This internship studies the problem for a car-rental agency in Rabat and proposes *AutoFlow*, a **supervised** workflow-automation system: it structures every request, checks availability deterministically, drafts replies and reminders, traces every decision and hands any ambiguous or sensitive case to a human. The architecture is deliberately compact — one LangGraph orchestrator, three narrow agents (understand, verify, prepare) and a human-in-the-loop gate — and favours reliability over autonomy. The prototype ships with an admin dashboard, a realistic generated dataset and seven automated business simulations. On 45 labelled messages the intake agent reaches 89–91 % per-field accuracy, and 100 % of its errors are caught by the human gate. Business KPIs are framed for before/after measurement during a pilot, with no figure claimed in advance.

---

## Table des matières

1. Introduction
2. Contexte de l'entreprise et problématique
3. État de l'art
4. Analyse des besoins et cahier des charges
5. Conception de l'architecture
6. Réalisation
7. Évaluation
8. Discussion et perspectives
9. Conclusion
Bibliographie · Annexes

---

## 1. Introduction

### 1.1 Cadre du stage
Le stage s'inscrit dans une démarche d'*ingénieur IA et architecte d'automatisation* : identifier une friction opérationnelle réelle dans une entreprise, concevoir une architecture de workflow simple et fiable, construire un prototype fonctionnel, puis traduire le travail technique en valeur métier compréhensible par un dirigeant non technique. Le terrain choisi est une agence de location de voitures à Rabat, représentative des PME de services marocaines : forte présence sur WhatsApp et les réseaux sociaux, outils dispersés (tableur, carnet, messagerie), équipe réduite, décisions commerciales fréquentes (remises, clients réguliers, réclamations).

### 1.2 Problématique
Comment automatiser le traitement des demandes clients d'une PME **sans retirer la décision aux humains ni inventer d'information**, et comment prouver — à un jury comme à un gérant — que le système est fiable, explicable et mesurable ?

### 1.3 Objectifs
1. Reconstruire le problème métier sous forme d'hypothèses d'audit vérifiables.
2. Concevoir une architecture multi-agents supervisée, explicite et testable.
3. Réaliser un prototype de bout en bout (agents, orchestrateur, API, espace admin, déploiement).
4. Évaluer honnêtement : tests, exactitude, robustesse, et cadre de mesure des indicateurs métier.
5. Produire un dossier réutilisable : kit commercial, architecture, choix techniques, portfolio.

### 1.4 Démarche
La démarche suit six phases (`kit_prospection/09_execution_plan.md`) : cadrage et hypothèses → audit → données et machine à états → agents et espace admin → démonstration et retours → mesure pilote. Le principe directeur a été « le métier d'abord, le code ensuite » : la machine à états et les données de test existaient avant la première ligne d'agent.

## 2. Contexte de l'entreprise et problématique

### 2.1 L'agence et son marché
Une agence de location de taille moyenne à Rabat gère une flotte de deux à trois dizaines de véhicules (citadines Dacia, Renault, Hyundai ; berlines ; SUV ; utilitaires) répartis sur plusieurs sites (Agdal, Hay Riad, aéroport Rabat-Salé), avec des tarifs journaliers de 230 à 800 MAD. La demande est saisonnière et arrive majoritairement par WhatsApp, puis Facebook/Instagram, téléphone et comptoir. Les messages sont courts, en français et en darija, avec des dates exprimées de multiples façons (« du 12 au 15 octobre », « 20/10 au 27/10 », « le week-end prochain »).

### 2.2 Une journée type (hypothèse)
Une demande arrive sur WhatsApp pendant qu'un client est au comptoir ; un collègue note les dates sur un carnet ; un autre ouvre le tableur des véhicules ; on vérifie si le SUV est revenu de maintenance ; un devis part ; le client ne répond pas ; personne n'a le temps de relancer ; trois jours plus tard il a loué ailleurs ; le gérant demande « on en est où ? » et la réponse dépend de la mémoire de chacun.

### 2.3 Frictions et coûts cachés
Les six frictions F1–F6 (canaux dispersés, vérification manuelle, questions répétitives, relances oubliées, statut flou, visibilité limitée) n'apparaissent dans aucun bilan : elles se paient en minutes perdues, en clients silencieux et en charge mentale. Elles sont présentées à l'agence comme des hypothèses à valider par un audit court, jamais comme des faits (`kit_prospection/01_prospect_brief_fr.md`).

## 3. État de l'art

### 3.1 Automatisation des workflows d'entreprise
Les approches classiques — RPA, plateformes low-code (n8n, Make, Zapier) — excellent pour relier des applications et déclencher des actions sur des événements structurés. Elles restent faibles dès que l'entrée est du langage naturel et que l'état métier (« cette demande attend le client depuis 48 h ») doit être tenu et raisonné. n8n, avec ses centaines de modèles communautaires, est retenu ici comme *colle* périphérique (webhooks, notifications), pas comme cœur de décision.

### 3.2 Agents fondés sur les LLM et orchestration
Depuis 2024, les cadres d'orchestration d'agents se sont structurés autour de graphes d'états persistants. **LangGraph** (LangChain) modélise un workflow comme un graphe dont les nœuds sont des fonctions et les arêtes des décisions ; il offre le *checkpointing* (reprise après arrêt), l'*interruption* pour validation humaine et la reprise par commande. En septembre 2026 il est le cadre le plus adopté (≈ 42 k étoiles, 44 k projets dépendants). **Microsoft Agent Framework** (2025-2026) apporte des graphes de workflows, l'observabilité et le checkpointing en Python/.NET/Go, mais son intégration à l'écosystème Azure en fait un candidat pour une version « entreprise », pas pour un pilote de PME. CrewAI et AutoGen privilégient la conversation entre agents plutôt qu'une machine à états explicite. Les standards émergents **MCP** (outils exposés aux modèles) et **A2A** (communication entre agents) sont notés en veille.

### 3.3 Extraction d'information structurée et confiance
Les LLM produisent des sorties structurées fiables lorsqu'un schéma est imposé (*structured output*), mais restent sujets à l'hallucination. Deux garde-fous sont retenus : l'**ancrage par la preuve** (un champ n'est accepté que s'il cite un passage exact du texte source) et la **calibration de la confiance** (des scores dont on vérifie qu'ils prédisent réellement la justesse). L'approche de Jev AI — « des décisions typées avec une probabilité, pas de la prose » — inspire la représentation des sorties de l'agent Intake sous forme de *signaux* numériques comparés à des seuils.

### 3.4 Human-in-the-loop
La littérature sur l'automatisation sûre converge : les décisions à enjeu (argent, identité, émotion) doivent rester humaines, et l'escalade doit être une *fonctionnalité* explicite, pas un repli de l'IA faible. C'est le principe fondateur d'AutoFlow.

### 3.5 Synthèse
Le choix retenu est un **orchestrateur explicite + agents étroits + point de contrôle humain**, plutôt qu'un agent LLM libre équipé d'outils : il est testable, explicable au gérant, et fonctionne sans appel externe.

## 4. Analyse des besoins et cahier des charges

### 4.1 Utilisateurs et rôles
- **Client** : écrit en langage naturel ; ne voit jamais le système directement.
- **Équipe (agents commerciaux)** : relit, modifie, envoie, complète, relance, enregistre la réponse client.
- **Manager** : remises, réclamations, longues durées, valeurs élevées, refus.
- **Système** : structure, vérifie, prépare, route, journalise, rappelle.

### 4.2 Exigences fonctionnelles (extrait)
RF1 identifiant + état + événement pour toute demande · RF2 aucune disponibilité déclarée sans vérification déterministe · RF3 champ LLM sans preuve rejeté · RF4 réclamation escaladée sans brouillon · RF5 remise / > 14 j / > 6 000 MAD → manager · RF6 aucun envoi sans clic humain · RF7 relance planifiée à l'envoi, `stalled` après la politique · RF8 journal complet · RF9 KPI dérivés · RF10 authentification admin, formulaire public sans token. Chaque exigence est reliée à un test (`01-cahier-des-charges.md §4`).

### 4.3 Exigences non fonctionnelles
Fonctionnement hors ligne ; explicabilité de chaque routage ; reprise après redémarrage ; minimisation des données (téléphones masqués, données fictives, seul le texte du message vers un LLM si activé, loi 09-08 à cadrer) ; simplicité (< 1 500 lignes de Python métier).

### 4.4 Indicateurs
Temps de première réponse, délai de devis, taux de demandes complètes, taux de relances effectuées, minutes manuelles par demande, nombre de cas escaladés. Tous sont mesurés avant (audit) et après (pilote) avec la même méthode ; aucun n'est promis.

## 5. Conception de l'architecture

### 5.1 Vue d'ensemble
*(Figure 1 — `diagrams/01-contexte.html` ; Figure 2 — `diagrams/02-conteneurs.html`.)*
Le client, l'équipe et le manager interagissent avec AutoFlow ; le fournisseur LLM, n8n et WhatsApp Business sont externes et optionnels. Le système se compose d'un frontend statique (React), d'une API (FastAPI), d'un graphe d'orchestration (LangGraph), de trois agents, d'une base relationnelle (SQLite → PostgreSQL) et d'un checkpointer.

### 5.2 Le graphe d'orchestration
*(Figure 3 — `diagrams/03-workflow.html`.)*

```
START → intake → routage 1 ─┬─ complaint → escalate ─────────┐
                            ├─ incomplet / peu sûr → clarify ─┤
                            └─ ok → availability → matrice ─┬─ sensible ─┤
                                                            └─ draft ────┤
                                                    human_review (interrupt) ← ─┘
                                                    → finalize → END  |  → availability (complete)
```

Le **routage 1** compare les sorties de l'Intake aux seuils de `rules.json` : réclamation, champs manquants, confiance de champ critique < 0,7, confiance globale < 0,75. La **matrice d'escalade** décide après la disponibilité : remise demandée, client régulier avec alternative, durée > 14 jours, valeur > 6 000 MAD, statut invalide ou indisponible, plus de 8 sauts. Le nœud `human_review` est un `interrupt()` réel : l'exécution est suspendue et persistée jusqu'à la décision (`approve`, `edit`, `reject`, `close`, `complete`) ; `complete` renvoie vers `availability` par `Command(goto=…)`.

### 5.3 Machine à états et journal
Dix états (`new`, `incomplete`, `checked`, `quote_ready`, `pending_customer`, `stalled`, `needs_human`, `escalated`, `confirmed`, `closed`) et une table de transitions légales. Toute transition passe par `store.transition()` qui refuse un mouvement illégal et écrit un événement `{request_id, from, to, actor, reason, ts}`. C'est ce journal qui rend le système auditable et les KPI calculables.

### 5.4 Les agents
**Intake.** Normalisation Unicode, grammaire de dates française (six formes, dont les formes ambiguës notées à 0,55), lexiques d'intention, de catégorie, de lieu, de signaux (remise, client régulier). Sortie : `StructuredRequest` avec confiance par champ, preuves textuelles, champs manquants, question de clarification en français, et `signals` (probabilités). Le moteur LLM, s'il est activé, produit un schéma typé dont chaque champ doit citer un passage exact du message ; les deux moteurs sont fusionnés (accord → confiance 0,95 ; désaccord → valeur du LLM avec preuve, sinon règles).
**Disponibilité.** Chevauchement de dates avec tampon de 4 h, maintenance, statut ; classement par site puis boîte puis prix ; replis par catégorie ; décalage ± 3 jours ; raisons d'exclusion. Aucun appel LLM.
**Suivi.** Brouillons français à prix injecté (jamais généré), planification de la première relance à +24 h, maximum deux relances, détection d'un lead sans réponse à 72 h depuis la première réponse envoyée (un appel de l'équipe remet l'horloge à zéro), recommandation d'appel puis de clôture.

### 5.5 Modèle de données
`customers`, `vehicles`, `bookings`, `requests` (message brut, structuré, disponibilité, suivi, état, niveau de revue), `drafts`, `follow_ups`, `reviews`, `events`, `settings` (horloge démo). *(Figure — `02-architecture.md §2.4`.)*

### 5.6 Vue défaillances
LLM indisponible → règles seules, confiance × 0,9 · champ sans preuve → rejeté · dates ambiguës → humain · table flotte périmée → horodatage affiché · crash → reprise au dernier checkpoint · boucle → cap de sauts · transition illégale → HTTP 409 · trop de relances → plafond puis appel recommandé. *(Tableau complet : `02-architecture.md §2.7`.)*

### 5.7 Vue déploiement
*(Figure 4 — `diagrams/04-deploiement.html`.)* Laptop (démo hors ligne) ; frontend Vercel/Netlify + backend Docker sur Render/Railway/Fly avec volume ; ou tout-Vercel (Python serverless, base éphémère → Postgres Neon/Supabase). Secrets uniquement en variables d'environnement.

## 6. Réalisation

### 6.1 Organisation du code
`backend/app/` : `main.py` (24 routes), `db.py`, `clock.py`, `rules.py`, `agents/`, `workflow/` (`graph.py`, `orchestrator.py`, `store.py`, `explain.py`, `state.py`), `simulations.py` ; `backend/data/` (générateur et fichiers) ; `backend/tests/` ; `backend/eval/`. `frontend/src/` : `lib/api.ts`, `components/` (Layout, WorkflowSvg, Trace, Icons, ui), `pages/` (Dashboard, Queue, Live, Simulations, Requests, RequestDetail, NewRequest, Fleet, Architecture, PublicIntake, Login).

### 6.2 L'orchestrateur en pratique
Chaque demande est un *thread* LangGraph (`thread_id = request_id`). `submit()` crée la ligne, écrit l'événement initial et invoque le graphe ; celui-ci s'arrête sur `interrupt()` avec un *payload* (raison, niveau, brouillon, actions permises) que l'API expose comme `pending_interrupt`. `resume()` rejoue le graphe avec `Command(resume=décision)`. Le checkpointer SQLite garantit que la validation en attente survit à un redémarrage.

### 6.3 L'espace d'administration
Dix écrans en React + TypeScript, charte navy / teal / crème héritée du kit de prospection (continuité avec les documents déjà remis à l'agence), icônes SVG, transitions courtes, anneaux de focus, respect de `prefers-reduced-motion`, mode présentation. Deux écrans méritent une mention :
- **Suivi en direct** : flux d'événements en temps quasi réel (4 s) et, pour toute demande, le **graphe allumé** sur le chemin réellement suivi accompagné de chaque règle évaluée (valeur, seuil, branche déclenchée). Le raisonnement du système est ainsi *inspectable*, condition d'un système supervisé crédible.
- **Simulations** : sept cas métier scriptés (WhatsApp, Facebook, Instagram, site, téléphone, comptoir) joués à travers la vraie API, révélés étape par étape avec l'acteur, l'état atteint et les vérifications ✓/✗. La même définition sert de suite de tests d'acceptation.

### 6.4 Données réalistes et rejeu d'historique
Un générateur déterministe produit 24 véhicules, 80 réservations sans chevauchement, 40 clients et 45 messages étiquetés répartis sur six semaines, avec un comportement humain scénarisé (accepté, décliné, sans réponse, refusé, réclamation). Au premier démarrage, l'horloge de démonstration est reculée message par message et chaque demande **traverse le vrai graphe** ; aucune ligne n'est écrite « à la main ». Les fenêtres de dates utilisées par les scénarios de démonstration sont protégées pour rester déterministes.

### 6.5 Intégrations et déploiement
Workflow n8n d'entrée (webhook → `POST /api/public/intake` → notification équipe ou manager selon `review_level`) ; Dockerfile ; `docker-compose.yml` ; `vercel.json` et `netlify.toml` (frontend) ; `backend/api/index.py` (Vercel Python).

### 6.6 Difficultés rencontrées et solutions
- **Dates françaises** : la forme « du 27 août au 17 septembre » prenait le second mois pour les deux dates ; corrigée par une capture optionnelle du premier mois, détectée par l'évaluation.
- **Horloge de lead sans réponse** : elle repartait à chaque relance envoyée, rendant l'état `stalled` inatteignable après la deuxième relance ; détectée par la simulation « lead silencieux », corrigée en prenant pour référence la première réponse envoyée.
- **Priorité d'intention** : « je passerai réserver plus tard » faisait primer *réservation* sur une question d'information ; règle ajoutée (question sans date + mots d'information → `info`).
- **Fichiers SQLite verrouillés sous Windows** dans les tests : libération explicite de l'engine et du cache du graphe.
- **Diagrammes** : chevauchements d'arêtes et de libellés dans les rendus SVG, résolus par des corridors fixes et une vérification visuelle en navigateur.

## 7. Évaluation

### 7.1 Tests automatisés
Seize tests, tous verts : huit tests de bout en bout (scénarios A–E, relances par voyage dans le temps, réservation créée à l'acceptation, KPI et graphe exposés) et sept simulations métier paramétrées plus le catalogue. Chaque exécution rejoue également l'historique de 45 messages (≈ 8 s).

### 7.2 Exactitude de l'agent Intake
Sur 45 messages étiquetés (moteur règles, hors ligne) : intention 100 % (45/45) ; date de prise 89 % (39/44) ; date de retour 82 % (36/44) ; catégorie 91 % (40/44). **Huit extractions comportent au moins une erreur ; les huit sont routées vers un humain** par les seuils. La calibration confirme la place des seuils : confiance ≥ 0,8 → 94 % d'extractions entièrement correctes ; < 0,8 → 0 %. *(Détail : `backend/eval/report.md`.)*

### 7.3 Robustesse
Comportements vérifiés : LLM indisponible, champ sans preuve, transition illégale, redémarrage pendant une validation, boucle, plafond de relances (`05-evaluation.md §5.3`).

### 7.4 Cadre de mesure des indicateurs métier
Pour chaque indicateur, la source dans le journal, la valeur « avant » (audit), l'objectif et la valeur « après » (pilote) ; résultats en fourchettes si n < 30 ; effet Hawthorne déclaré ; distinction entre temps gagné, tâches déplacées vers l'humain et cas exigeant toujours une intervention. Les compteurs affichés dans la démonstration sont de l'activité simulée, jamais des gains.

### 7.5 Limites de l'évaluation
Les étiquettes proviennent du même générateur que les messages (résultat optimiste) ; le moteur LLM n'a pas été évalué avec une clé réelle ; aucune mesure métier n'a encore été prise sur site.

## 8. Discussion et perspectives

### 8.1 Ce que le système fait bien, et ce qu'il ne fait pas
Il rend le traitement des demandes **lisible** (un état, un propriétaire, une raison), **sûr** (rien d'inventé, rien d'envoyé seul) et **mesurable**. Il ne comprend pas les formulations libres rares (« vers la fin du mois ») — elles tombent en validation humaine, ce qui est le comportement voulu — et il ne remplace aucune relation client.

### 8.2 Où est l'IA ?
Dans la compréhension du langage (règles, LLM optionnel), dans la représentation des décisions (signaux calibrés → seuils), et surtout dans la *conception* : l'IA sert le workflow, elle ne le remplace pas. Un jury peut suivre chaque décision ; un gérant peut dire exactement ce que le système peut et ne peut pas faire.

### 8.3 Valeur économique pour une PME
Infrastructure proche de zéro (laptop ou offres gratuites), LLM optionnel à quelques centimes par demande ou modèle local, licences libres. La valeur facturable est le temps d'audit et d'adaptation ; les gains se mesurent en pilote.

### 8.4 Généralisation
Le squelette *intake → vérification déterministe → brouillon → validation → suivi* s'applique à un cabinet, une clinique, un artisan, une agence immobilière : c'est le sens du nom *AutoFlow*. Seuls changent les lexiques, la table de « disponibilité » et les règles.

### 8.5 Perspectives
Audit et base « avant » ; jeu de 30 messages réels annotés ; connecteur WhatsApp Business via n8n (notification seulement) ; outils exposés en MCP si un LLM avec outils est retenu ; pilote de 2 à 4 semaines et tableau avant/après ; étude d'une version « entreprise » sur Microsoft Agent Framework.

## 9. Conclusion

Ce stage a transformé une friction banale — des demandes WhatsApp traitées à la main — en un système d'automatisation supervisé, compact et explicable, livré de bout en bout : agents, orchestrateur LangGraph avec validation humaine persistée, API, espace d'administration avec suivi en direct du raisonnement, jeu de données réaliste, simulations jouables doublées de tests, dossier d'architecture et kit commercial. La contribution principale n'est pas un modèle, mais une **discipline d'architecture** : les agents proposent, l'orchestrateur route selon des règles versionnées, l'humain décide, tout est tracé, rien n'est promis avant d'être mesuré. Les compétences mobilisées couvrent l'ingénierie des workflows et des systèmes multi-agents, l'extraction d'information ancrée par la preuve, la conception d'API et d'interfaces, les tests et l'évaluation, ainsi que la communication métier auprès d'un dirigeant non technique.

---

## Bibliographie

1. LangChain Inc., *LangGraph — documentation : StateGraph, persistence, human-in-the-loop, interrupts*, 2026. https://github.com/langchain-ai/langgraph
2. Microsoft, *Agent Framework — workflows, checkpointing, observability*, 2026. https://github.com/microsoft/agent-framework
3. A. Perritano, *LangGraph Customer Support Agent*, 2025. https://github.com/aperritano/langgraph-customer-support-agent
4. E. Surovtsev, *LangGraph HITL FastAPI demo*, 2025. https://github.com/esurovtsev/langgraph-hitl-fastapi-demo
5. E. Cingöz, *Awesome n8n Templates*, 2026. https://github.com/enescingoz/awesome-n8n-templates
6. TypeSafe, *Jev AI — typed decisions with calibrated confidence*, 2026. https://jev-ai.pro
7. Anthropic, *Model Context Protocol specification*, 2025-2026.
8. FastAPI, SQLAlchemy 2.0, React 19, Vite — documentations officielles.
9. Cocoon AI, *Architecture Diagram Generator*, 2026. https://github.com/Cocoon-AI/architecture-diagram-generator
10. Royaume du Maroc, *Loi n° 09-08 relative à la protection des personnes physiques à l'égard du traitement des données à caractère personnel*, 2009.

## Annexes

- **A.** Cahier des charges — `01-cahier-des-charges.md`
- **B.** Architecture, sept vues et inventaire — `02-architecture.md` ; diagrammes exportables — `diagrams/`
- **C.** Choix techniques et decision records — `03-choix-techniques.md`
- **D.** Démo, données, déploiement — `04-demo-et-deploiement.md`
- **E.** Évaluation et rapport d'exactitude — `05-evaluation.md`, `backend/eval/report.md`
- **F.** Règles métier — `backend/data/rules.json`
- **G.** Catalogue des simulations — `backend/app/simulations.py`
- **H.** Extrait de journal d'événements d'une demande (à insérer depuis l'onglet *Journal*)
- **I.** Kit de prospection complet — `kit_prospection/` ; visuels — `assets/`
- **J.** Workflow n8n — `integrations/n8n/autoflow_intake_webhook.json`
