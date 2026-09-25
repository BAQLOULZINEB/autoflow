# AutoFlow — Deck de soutenance

> Fichier source pour générer la présentation visuelle (HTML slides ou .pptx).
> **Contenu = data.** Un autre assistant s'occupera du rendu visuel avec le prompt fourni en fin de fichier.

---

## Méta

- **Projet** : AutoFlow — système d'automatisation intelligent des workflows d'entreprise
- **Stage** :systeme automatisation des workflows métier
- **Cas** : Agence de location de voitures — Rabat
- **Nombre de slides** : 16 (+ 2 optionnels)
- **Ton** : ingénieur AI qui a diagnostiqué, conçu et livré — pas étudiant qui récite
- **Fil rouge narratif** : *chaos observé → problème diagnostiqué → architecture décidée → système livré → preuves → et maintenant ?*

---

## Slide 1 — Cover / Hook

**Titre** : AutoFlow
**Baseline** : *Le système prépare. L'équipe décide.*
**Sous-titre** : Automatisation supervisée des workflows métier — cas d'une agence de location à Rabat
**Meta bas de page** : AI Engineer · EMSI 4IASD · [Année]

**Visual note** : plein écran dark navy, un seul mot "AutoFlow" en grand, la baseline en teal juste en dessous. Rien d'autre. On accroche par la sobriété.

---

## Slide 2 — Le chaos observé (Problème, partie 1)

**Titre** : Une matinée dans une agence de location, en 2026

**Narration (courte)** :
> *WhatsApp qui vibre pendant un client au comptoir. Le tableur Excel des véhicules ouvert dans un onglet. Un SUV peut-être libre. Un devis part. Le client ne répond plus. Trois jours après, il a loué ailleurs. Le gérant demande « on en est où ? » — la réponse dépend de la mémoire de chacun.*

**Visual note** : timeline horizontale 5 étapes avec micro-icônes (WhatsApp, Excel, message envoyé, silence, gérant qui demande). Faire ressentir la friction.

---

## Slide 3 — Les 6 frictions structurantes (Problème, partie 2)

**Titre** : Ce que ça coûte — 6 frictions, aucune ligne dans un bilan

| # | Friction | Coût réel |
|---|---|---|
| F1 | Demandes dispersées sur 5+ canaux | Re-saisie, oublis silencieux |
| F2 | Disponibilité vérifiée à la main | Réponses lentes, doubles réservations |
| F3 | Questions répétitives (prix, caution, km) | Attention consommée |
| F4 | Relances oubliées après devis | Devis perdus invisibles |
| F5 | Statut des demandes flou | Coordination par mémoire |
| F6 | Visibilité gérant limitée | Pilotage à l'instinct |

**Insight à prononcer** : *« Ces frictions n'apparaissent nulle part. Elles se paient en minutes perdues, en charge mentale, en clients silencieux. »*

**Visual note** : 6 cartes grid 3×2, chaque carte = une icône + friction + coût. Couleur d'accent orange sur "coût réel".

---

## Slide 4 — Problématique centrale (Problème, partie 3)

**Titre** : Le vrai défi

**Boîte encadrée (couleur navy)** :
> Comment automatiser le traitement des demandes clients d'une PME **sans retirer la décision aux humains ni inventer d'information** — et prouver au jury *comme* au gérant que c'est fiable, explicable, mesurable ?

**3 puces contre-intuitives (accent teal)** :
- ❌ **Pas** un agent LLM autonome qui envoie tout seul
- ❌ **Pas** une IA qui hallucine des disponibilités
- ❌ **Pas** une boîte noire inexplicable

**Visual note** : une seule grande boîte au centre, les 3 anti-patterns en dessous barrés.

---

## Slide 5 — Solution envisagée (le pivot)

**Titre** : Le contre-pied — un workflow supervisé

**Formule signature** :
> **1 orchestrateur · 3 agents · 1 humain**

**3 invariants non négociables** :
1. 🚫 Le système **n'envoie jamais** un message client seul → l'envoi = un clic humain
2. 🚫 Le système **n'invente jamais** une disponibilité (code déterministe) ni un champ (evidence gate)
3. ✅ **Tout est tracé** — chaque décision = un événement (acteur, raison, horodatage)

**Punchline à prononcer** : *« La confiance n'est pas une promesse marketing. C'est une propriété structurelle du code. »*

**Visual note** : les 3 invariants comme 3 badges/pastilles verticales. Style contrat d'assurance.

---

## Slide 6 — Architecture en une phrase (Vue macro)

**Titre** : L'ossature

**Schéma central** (à générer visuellement, pas texte) :
```
Client (WhatsApp / Facebook / formulaire / n8n)
     │
     ▼
┌─────────────────────────────────────────────┐
│  🧠 Agent Intake        (comprendre)         │
│         evidence-gated · signaux calibrés    │
├─────────────────────────────────────────────┤
│  ⚙️  Orchestrateur LangGraph                 │
│         10 états · matrice d'escalade        │
├─────────────────────────────────────────────┤
│  🔍 Agent Disponibilité (vérifier)           │
│         déterministe · 0 LLM                 │
├─────────────────────────────────────────────┤
│  ✍️  Agent Suivi        (préparer)           │
│         brouillon FR · relance +24h          │
└─────────────────────────────────────────────┘
     │
     ▼
  👤 Validation humaine (interrupt persistant)
     │
     ▼
  📊 Espace admin (file · trace live · KPI)
```

**Visual note** : diagramme vertical en 4 couches avec code-couleur cohérent. Le nœud "humain" doit se démarquer visuellement (couleur dorée/accent).

---

## Slide 7 — Architecture C4 (Vue technique)

**Titre** : Les 4 vues qui comptent

**Grid 2×2** — chaque case = une vue :
1. **Contexte** — Qui parle au système ? Frontière-clé : aucun message client direct
2. **Conteneurs** — Frontend React sur Vercel · Backend FastAPI + LangGraph · SQLite→Postgres · Checkpointer
3. **Workflow** — 7 nœuds · 2 gardes conditionnelles · `interrupt()` humain persisté
4. **Déploiement** — 3 topologies : laptop offline · cloud Docker · serverless Vercel

**Visual note** : 4 miniatures d'architectures cliquables (dans le vrai deck : screenshots des HTML `docs/diagrams/`).

---

## Slide 8 — Le cerveau : le graphe LangGraph

**Titre** : 7 nœuds, 2 gardes, 1 interruption humaine

**Diagramme** (screenshot de `docs/diagrams/03-workflow.html` ou re-render) :
```
START → intake → [route_after_intake]
                    ├─ complaint    → escalate ──┐
                    ├─ incomplet    → clarify ───┤
                    └─ ok → availability → [decide_after_availability]
                                             ├─ remise/>14j/>6k → sensitive ──┤
                                             └─ ok             → draft ──────┤
                                                          human_review ◄─────┘
                                                          [interrupt persisté]
                                                          │
                                                          ▼
                                                    finalize → END
                                                     │
                                                     └─ ou Command(goto=availability)
```

**Une phrase clé** : *« Le graphe est exposé par `GET /api/graph`. Le code et le schéma ne peuvent pas diverger. »*

---

## Slide 9 — La matrice d'escalade (le contrat métier)

**Titre** : Qui décide quoi — et pourquoi

**Table courte, dense visuellement** :
| Déclencheur | → | Niveau |
|---|---|---|
| Réclamation | → | 🚨 Manager |
| Champs manquants / conf < 0.75 | → | 👥 Équipe |
| Remise demandée | → | 🚨 Manager |
| Durée > 14 j · Valeur > 6000 MAD | → | 🚨 Manager |
| Client régulier + alternative | → | 👥 Équipe |
| Boucle (> 8 sauts) | → | 👥 Équipe |

**Punchline** : *« Le gérant ne signe pas un chèque en blanc. La matrice est versionnée dans `rules.json`. »*

---

## Slide 10 — Exploitation : les 3 agents en 60 secondes

**Titre** : Trois responsabilités, une par agent

**3 colonnes** :

### 🧠 Intake — *comprendre*
- Regex FR + darija + LLM optionnel
- **Evidence gate** : un champ LLM sans passage exact du message = rejeté
- Signaux calibrés : `discount_requested: 0.92`, `dates_ambiguous: 0.55`
- Sortie : `StructuredRequest` typée

### 🔍 Disponibilité — *vérifier*
- **0 LLM** — pur SQL + comparaison de dates
- Chevauchement + tampon 4h + maintenance + replis
- Alternatives : catégorie de repli, décalage ±3 jours
- Chaque exclusion porte une **raison lisible**

### ✍️ Suivi — *préparer*
- Brouillon FR à **prix injecté depuis la table** (jamais généré)
- Politique : relance +24h, max 2 relances, `stalled` à 72h
- Templates : devis · alternative · clarification · relance

**Punchline** : *« Un LLM là où il apporte de la valeur — pas là où il apporte du risque. »*

---

## Slide 11 — Exploitation : l'espace admin (démo statique)

**Titre** : Ce que voit l'équipe

**3 screenshots côte à côte** :
1. **File à valider** — badges niveau/priorité, raison lisible, brouillon prêt, boutons Approuver/Modifier/Refuser
2. **Suivi en direct** — graphe allumé sur le chemin réel + tableau de règles évaluées
3. **Simulations** — 7 cas métier jouables live, doublés par 7 tests d'intégration

**Une phrase clé** : *« Le raisonnement est inspectable. Pas de boîte noire. »*

---

## Slide 12 — Évaluation (les chiffres)

**Titre** : Ce qu'on mesure — ce qu'on ne promet pas

**Grid stats — 4 gros nombres** :
- ✅ **16 / 16** tests d'intégration verts
- 🎯 **89–91 %** exactitude par champ (Intake)
- 🛡️ **100 %** des extractions erronées rattrapées par l'humain
- 📊 **94 % vs 0 %** — calibration : ce qui a confiance ≥ 0.8 est correct dans 94 % des cas ; en dessous, 0 %

**Petit encadré honnête** :
> **Ce qu'on ne promet pas** : les KPI métier (temps de 1re réponse, minutes économisées, taux de conversion). Ils seront **mesurés** en pilote avant/après, jamais annoncés à l'avance.

**Punchline** : *« La rigueur commence par ce qu'on refuse d'affirmer. »*

---

## Slide 13 — Robustesse (le stress-test)

**Titre** : Que fait le système quand ça casse ?

**Table 2 colonnes** :
| Défaillance | Comportement |
|---|---|
| LLM indisponible | Règles seules · confiance × 0.9 · flag `llm_failed` |
| LLM hallucine un champ | Champ rejeté (evidence gate) · question de clarification |
| Redémarrage pendant validation | Checkpoint SQLite → validation retrouvée intacte |
| Boucle agents (> 8 sauts) | Route forcée vers humain |
| Trop de relances | Cap `max_reminders=2` → `stalled` → appel recommandé |
| Transition d'état illégale | `HTTP 409` · rien n'est écrit |

**Punchline** : *« Un système fiable, c'est un système dont on connaît les modes d'échec. »*

---

## Slide 14 — Stack technique (tech used)

**Titre** : Le stack — pourquoi ces briques, pas d'autres

**Grid 3×2 avec logos** :

| Brique | Rôle | Pourquoi celle-là |
|---|---|---|
| 🕸️ **LangGraph 1.2** | Orchestration + HITL | Checkpointing natif · `interrupt()` · 42k ⭐ |
| ⚡ **FastAPI** | API REST | Pydantic partagé agents/API · OpenAPI gratuit |
| ⚛️ **React 19 + Vite + TS** | Espace admin | Build statique · déploy Vercel · 0 secret front |
| 🗄️ **SQLAlchemy + SQLite→PG** | Persistance | Laptop offline → cloud sans redesign |
| 🔗 **n8n** | Colle vers canaux | 280+ templates · notifie · n'envoie jamais |
| 🤖 **LLM optionnel** | Anthropic / OpenAI / Ollama | `LLM_PROVIDER=none` → tourne offline |

**Punchline** : *« Coût d'infrastructure : ~0 MAD. Licences : 0 (MIT/Apache). »*

---

## Slide 15 — Généralisation (la vraie valeur)

**Titre** : Pourquoi "AutoFlow" — pas "RentalBot"

**Schéma central** : au centre le squelette `intake → vérifier → brouillon → valider → suivi`
**Autour, 4 branches** :
- 🚗 Agence de location (V1 livrée)
- 🏥 Cabinet médical / clinique dentaire
- 🔧 Artisan (plombier, électricien)
- 🏠 Agence immobilière

**Une phrase clé** :
> Seuls changent **les lexiques, la table de "disponibilité" et les règles**. Le graphe, la machine à états, la matrice d'escalade, le journal — restent identiques.

**Punchline** : *« Un métier livré. Quatre métiers accessibles. C'est ça, AutoFlow. »*

---

## Slide 16 — Conclusion + Perspectives + Q/R

**Titre** : Ce que j'emporte

**3 puces "livré"** :
- ✅ Prototype V1 end-to-end (backend, frontend, tests, dataset, kit commercial)
- ✅ Architecture reproductible sur 3+ métiers
- ✅ Discipline : *le système prépare, l'équipe décide*

**3 puces "prochaines étapes"** :
- 🎯 Audit sur site → base KPI "avant"
- 🎯 Pilote 2–4 semaines → mesure avant/après honnête
- 🎯 Connecteur WhatsApp Business via n8n (notification, jamais envoi)

**Dernière phrase (à prononcer lentement)** :
> *« La contribution principale n'est pas un modèle. C'est une discipline d'architecture : les agents proposent, l'orchestrateur route, l'humain décide, tout est tracé, rien n'est promis avant d'être mesuré. »*

**Bloc final** : **Merci — questions ?**

---

## Slides bonus (optionnels si temps)

### Bonus A — Difficultés vécues (montre le vrai travail)

**Titre** : 3 bugs qu'on ne trouve qu'en simulant

1. **Dates FR** — « du 27 août au 17 septembre » prenait le second mois pour les deux → capture optionnelle du premier mois
2. **Horloge de silence** — repartait à zéro à chaque relance → `stalled` inatteignable → référence = première réponse envoyée
3. **Intention piégée** — « je passerai réserver plus tard » écrasait une simple question info → règle ajoutée

**Punchline** : *« Les simulations ne sont pas de la démo. Ce sont des tests. Et elles ont trouvé de vrais bugs. »*

### Bonus B — Modèle économique

**Titre** : Pour l'agence — combien ça coûte

| Poste | Pilote | Après |
|---|---|---|
| Hébergement | 0 MAD (laptop) | 5–7 $/mois cloud |
| LLM | 0 (offline) | 0.005–0.02 MAD/demande |
| Licences | 0 (open source) | 0 |
| Temps équipe | 30 min de prise en main | — |

**Positionnement** : *outil quasi gratuit à faire tourner, facturé sur l'audit et l'adaptation, jamais sur une licence*

---

## Section démo live (5 min, après slides)

**Script express** :
1. Tableau de bord — « 45 demandes, agence vivante » (0:30)
2. Scénario A standard — extraction avec preuves + brouillon (1:00)
3. Onglet Raisonnement — chemin allumé + règles évaluées (0:45)
4. Scénario C ambigu + remise — 2 interruptions humaines (1:30)
5. +24h et +72h — relances puis stalled (0:45)
6. Suivi en direct — flux d'événements pendant qu'on parle (0:30)

**Phrase pour "et si le système se trompe ?"** :
> *« Il le dit. Et il transmet à une personne. »*

---

# 🎨 PROMPT À DONNER À L'ASSISTANT VISUEL

Copie-colle ce bloc entier + le contenu ci-dessus (slides 1 à 16 + bonus) à l'assistant qui générera la présentation visuelle.

---

```
Tu es un designer de présentations qui construit des decks impactants pour la
soutenance d'un projet d'ingénieur IA de niveau top student. Ton livrable est
UN SEUL fichier HTML autonome (une slide = une section plein écran, navigation
clavier ← → ou scroll) qui rende à l'écran sans dépendance externe autre que
Google Fonts et une CDN de police d'icônes.

## CONTEXTE
Le contenu des slides (16 principales + 2 bonus + section démo) est fourni
dans le .md ci-après. C'EST DE LA DATA — ne le résume pas, ne le paraphrase
pas. Utilise chaque punchline VERBATIM. Les tableaux, listes et diagrammes
ASCII doivent être TRANSFORMÉS en composants visuels (grids, cards, badges,
schémas SVG inline) — jamais rendus comme du texte brut.

## OBJECTIF ÉMOTIONNEL
Le jury doit ressentir : « ce n'est pas un projet d'étudiant, c'est une
solution mûre présentée par un ingénieur qui a diagnostiqué un vrai problème
et livré une vraie réponse ». Chaque slide doit avoir UNE idée principale et
la faire respirer. Pas de mur de texte.

## LANGAGE VISUEL
- **Palette** : navy #0B1F3A (fond primaire) · teal #0E9C99 (accent principal) ·
  crème #F7F4EC (texte sur navy) · doré #E9B44C (accent rare, réservé au
  « point humain » et aux insights) · rouge #E74C3C (erreur/friction) ·
  vert #10B981 (validation/succès).
- **Typographie** : Manrope (titres, tracking -0.02em, poids 800) + Inter
  (corps, poids 400/600). Titres énormes (60–96px), corps confortable (18–22px).
- **Layout** : full-bleed dark navy par défaut. Alterner 2–3 slides "light
  cream" pour rompre le rythme (typiquement les slides métriques et
  généralisation).
- **Animations** : subtiles uniquement — fade-in séquencé des éléments d'une
  slide, jamais de transition tape-à-l'œil entre slides. Respect
  `prefers-reduced-motion`.
- **Icônes** : Lucide (via unpkg CDN) OU emoji système — cohérent partout.
- **Composants récurrents attendus** :
  * `pill-badge` (petit tag arrondi pour catégories)
  * `stat-hero` (grand nombre + label — pour la slide 12)
  * `friction-card` (icône + titre + coût — pour slide 3)
  * `invariant-badge` (grand badge coloré avec ✅/🚫 — pour slide 5)
  * `flow-diagram` (SVG inline pour slides 6, 8, 15)
  * `code-inline` (mono, background subtil)

## RÈGLES DE STRUCTURE PAR SLIDE
- **1 slide = 1 idée**. Si une slide te semble chargée, coupe.
- Titre de slide en haut à gauche, petit numéro discret en haut à droite
  (« 06 / 16 »).
- Une slide de **transition/pivot** entre chaque grande section (Problème →
  Solution → Architecture → Exploitation → Évaluation → Conclusion) : juste
  un mot-clé énorme centré + un numéro de section.
- Les **punchlines** marquées "à prononcer" dans le .md deviennent des
  citations grande taille en italique + guillemets typographiques
  (« … »), fond navy foncé, filet teal à gauche.
- Les **diagrammes ASCII** du .md (slides 6, 8, 15) → SVG inline avec les
  nœuds colorés, arêtes propres, style flat moderne. Le nœud "humain" doit
  avoir un traitement visuel spécial (doré, halo, ou icône proéminente).
- Les **tables** deviennent des grids de cards ou des vraies tables stylisées
  avec zébrage subtil — jamais de bordures épaisses.

## SLIDES CLÉS À SOIGNER PARTICULIÈREMENT
- **Slide 1 (cover)** : minimalisme extrême — un seul mot « AutoFlow » énorme,
  baseline « Le système prépare. L'équipe décide. » en teal juste dessous.
- **Slide 4 (problématique)** : la question dans une grande boîte au centre,
  les 3 anti-patterns barrés en dessous — rythme cinématographique.
- **Slide 5 (solution)** : « 1 · 3 · 1 » en typo géante (nombres énormes),
  les 3 invariants comme 3 badges verticaux.
- **Slide 12 (chiffres)** : 4 stat-heroes plein écran, chaque nombre occupe
  1/4 de l'écran, animation de count-up au chargement.
- **Slide 15 (généralisation)** : schéma radial — squelette AutoFlow au
  centre, 4 métiers en satellites.
- **Slide 16 (conclusion)** : la dernière phrase seule, plein écran, taille
  énorme, fond dégradé navy → teal.

## CE QU'IL FAUT ÉVITER ABSOLUMENT
- ❌ Puces à rallonge (> 3 lignes)
- ❌ Screenshots pixellisés (utilise des placeholders `<div class="screenshot-placeholder">Screenshot : file à valider</div>` si les images ne sont pas fournies)
- ❌ Emojis décoratifs partout — un emoji doit avoir un sens
- ❌ Slides qui « expliquent » un concept déjà dit — sois brutal, coupe
- ❌ Templates génériques Corporate / SlidesGo — invente ta grille

## LIVRABLE ATTENDU
Un fichier `presentation.html` unique, ≤ 500 Ko, qui :
- S'ouvre plein écran (touche F ou bouton discret en bas à droite)
- Se navigue au clavier (← →, PageUp/Down, espace)
- Affiche un indicateur de progression fin en bas
- Contient une slide de sommaire cliquable (touche `m`)
- Imprime proprement en PDF (une slide = une page A4 paysage)

## LE CONTENU
[Colle ici tout le contenu du .md à partir de « Slide 1 — Cover »
jusqu'à la fin de la section « démo live ».]
```

---

## Notes pour toi (pas pour l'assistant visuel)

- Ce `.md` est **aussi utilisable tel quel** dans Marp, reveal.js ou Slidev — n'importe quel outil qui lit du Markdown en slides. Le prompt ci-dessus vise un rendu HTML custom haut de gamme, mais si tu veux quelque chose de rapide : `marp presentation.md --html` sort déjà un beau deck.
- **Chronométrage** : compte ~45–60 s par slide × 16 = 12–16 min. Coupe les bonus si tu dépasses.
- **Screenshots à préparer** avant la présentation : file à valider, suivi en direct (chemin allumé), simulations, fiche demande onglet Raisonnement. Les mêmes que ceux listés dans `IMAGES.md`.
- **Pour la démo live** : lance le backend + frontend avant la soutenance, garde une deuxième fenêtre avec des captures de secours au cas où le wifi lâche.
