# 00 — Système visuel partagé (Design System)

> Source de vérité pour tous les visuels A → F. Chaque spec visuelle référence ces tokens ; ne pas redéfinir les couleurs localement.

## 1. Intention

Un visuel de proposition de conseil moderne : calme, structuré, crédible face à un directeur d'agence. Pas une présentation étudiante, pas un README développeur, pas une esthétique « IA futuriste ».

Le lecteur cible ne lit pas — il **balaie**. Chaque visuel doit livrer son message en 30 secondes, en commençant par **sa** douleur opérationnelle, jamais par notre technologie.

## 2. Palette — chaque couleur a un sens

| Token | Hex | Rôle sémantique | Utilisation autorisée |
|---|---|---|---|
| `navy` | `#0B1F3A` | **Structure, autorité, humain** | Titres, blocs de cadre, silhouettes/postes des employés, texte principal sur fond clair |
| `navy-700` | `#16304F` | Structure secondaire | Fonds de section sombre, sous-titres sur navy |
| `teal` | `#0E9C99` | **Workflow intelligent, action positive, système** | Flèches de workflow, agents, états « traité », boutons d'action |
| `teal-100` | `#DDF3F2` | Surface système | Fond léger des cartes « après », des cartes agents |
| `orange` | `#D9772B` | **Friction, goulot, risque** — usage restreint | Uniquement : points de blocage, relance oubliée, délai, cas « avant ». Jamais décoratif. |
| `orange-100` | `#FBEBDD` | Surface friction | Fond léger des cartes « avant » |
| `ink` | `#111827` | Texte corps | Paragraphes |
| `slate` | `#5B6472` | Texte secondaire | Légendes, méta, notes de mesure |
| `line` | `#D8DCE3` | Séparateurs, grilles | Traits fins, bordures 1 px |
| `paper` | `#FAF8F4` | **Fond chaud neutre** | Fond de toutes les pages |
| `white` | `#FFFFFF` | Cartes | Surfaces sur `paper` |
| `human` | `#0B1F3A` + icône contour | **Validation humaine** | Toujours navy + pictogramme personne à contour, jamais teal (le teal = système) |

Règle de lecture : **navy = humain/structure**, **teal = système**, **orange = friction**. Ne jamais mélanger. Un employé n'est jamais teal ; un agent n'est jamais navy plein.

Interdits : dégradés violets, néons, glassmorphism, ombres portées lourdes, cartes ultra-arrondies, cerveau lumineux, robots.

## 3. Typographie

- Famille principale : **Manrope** (Google Fonts) — fallback **Inter**, puis `system-ui`.
- Titres : Manrope 700, tracking -1 %, tailles A4 : H1 34–40 pt, H2 20–24 pt.
- Corps : Manrope 400/500, 11–13 pt sur A4 ; **jamais < 10 pt** sur un support imprimable.
- Chiffres KPI : Manrope 800, tabular-nums.
- Libellés de schémas : 12–14 pt, phrase courte, jamais plus de 6 mots par bloc.
- Français : accents obligatoires y compris sur majuscules (É, À). Espaces insécables avant `:` `;` `!` `?`.

## 4. Grille & espace

- A4 portrait : marges 18 mm, grille 12 colonnes, gouttière 6 mm.
- Carré 1080 × 1080 (WhatsApp/LinkedIn) : marges 72 px, grille 6 colonnes.
- Carrousel LinkedIn : 1080 × 1350, marges 80 px.
- Espace blanc minimum entre sections : 2 × la hauteur d'une ligne de titre.
- Alignement gauche par défaut ; centrage uniquement pour le triptyque Problème → Système → Résultat.

## 5. Vocabulaire graphique

| Élément | Forme | Couleur | Signification |
|---|---|---|---|
| Flèche pleine | → trait 2 px, pointe fermée | teal | Flux normal du workflow |
| Flèche pointillée | ⇢ trait 2 px pointillé | navy | Escalade vers un humain / retour humain |
| Bloc rectangle, coin 4 px | bordure 1 px `line` | white | Étape, agent, action |
| Bloc navy plein, texte blanc | — | navy | Orchestrateur (colonne vertébrale) ou étape humaine |
| Pastille orange | ● 8 px | orange | Point de friction dans l'état « avant » |
| Pastille teal | ● 8 px | teal | Point résolu dans l'état « après » |
| Pictogramme personne (contour) | — | navy | Validation humaine, employé, manager |
| Losange | ◇ | navy contour | Point de décision |

Pas d'icônes décoratives. Une icône n'apparaît que si elle remplace un mot.

## 6. Mermaid — thème commun

Coller ce bloc `%%{init}` en tête de chaque diagramme Mermaid pour rester cohérent :

```
%%{init: {
  "theme": "base",
  "themeVariables": {
    "fontFamily": "Manrope, Inter, system-ui",
    "fontSize": "14px",
    "primaryColor": "#FFFFFF",
    "primaryTextColor": "#111827",
    "primaryBorderColor": "#D8DCE3",
    "lineColor": "#0E9C99",
    "secondaryColor": "#DDF3F2",
    "tertiaryColor": "#FAF8F4",
    "background": "#FAF8F4",
    "clusterBkg": "#FAF8F4",
    "clusterBorder": "#D8DCE3"
  },
  "flowchart": { "curve": "linear", "nodeSpacing": 40, "rankSpacing": 48, "padding": 12 }
}}%%
```

Classes réutilisables (à déclarer dans chaque diagramme) :

```
classDef human fill:#0B1F3A,color:#FFFFFF,stroke:#0B1F3A,stroke-width:1px;
classDef system fill:#DDF3F2,color:#0B1F3A,stroke:#0E9C99,stroke-width:1.5px;
classDef orch fill:#0B1F3A,color:#FFFFFF,stroke:#0E9C99,stroke-width:2px;
classDef friction fill:#FBEBDD,color:#0B1F3A,stroke:#D9772B,stroke-width:1.5px;
classDef neutral fill:#FFFFFF,color:#111827,stroke:#D8DCE3,stroke-width:1px;
classDef result fill:#FFFFFF,color:#0B1F3A,stroke:#0B1F3A,stroke-width:1.5px;
```

## 7. Ton des libellés

- Écrit pour un gérant d'agence, pas pour un ingénieur.
- Verbe d'action + objet : « Vérifier la disponibilité », « Proposer une alternative ».
- Jamais : LLM, API, LangGraph, prompt, embedding, pipeline.
- Les noms d'agents apparaissent **en second niveau** (petit texte gris) sous le libellé métier :
  - « Comprendre la demande » — *Intake Agent*
  - « Vérifier la disponibilité » — *Availability Agent*
  - « Relancer et suivre » — *Follow-up Agent*
  - « Coordonner et sécuriser » — *Orchestrateur*
  - « Valider les cas sensibles » — *Équipe de l'agence*

## 8. Intégrité

- Aucun chiffre de résultat inventé. Placeholders explicites : `— à mesurer —`.
- Toute KPI porte trois colonnes : **Avant · Objectif pilote · Après (mesure réelle)**.
- Mention discrète en pied de page des visuels KPI : « Indicateurs à mesurer pendant le pilote — aucun résultat annoncé avant mesure. »

## 9. Prompt de base pour un outil d'image (à préfixer à chaque prompt de visuel)

```
Premium consulting-grade infographic, editorial layout, warm off-white paper background (#FAF8F4),
deep navy (#0B1F3A) structural elements and typography, restrained teal (#0E9C99) accent for the
intelligent workflow, tiny muted orange (#D9772B) markers only on friction points, generous whitespace,
strict grid alignment, clean modern sans-serif (Manrope/Inter), French labels, thin 1px dividers,
flat vector style, no gradients, no neon, no glow, no robots, no sci-fi, no holograms, no 3D,
no purple, minimal icons drawn as thin line outlines, calm confident business tone. Aspect ratio: {RATIO}.
```

## 10. Revue finale (checklist obligatoire par visuel)

- [ ] Compris en 30 s par un gérant non technique ?
- [ ] Commence par sa douleur, pas par notre techno ?
- [ ] L'humain reste visiblement aux commandes ?
- [ ] L'architecture paraît simple et fiable ?
- [ ] Pilote mesurable, aucune promesse chiffrée non mesurée ?
- [ ] Crédible en réunion avec un directeur ?
- [ ] Fonctionne en PDF, WhatsApp, LinkedIn, jury ?
