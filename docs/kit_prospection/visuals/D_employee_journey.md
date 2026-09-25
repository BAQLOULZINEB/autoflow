# D — Parcours de l'employé (une journée, deux versions)

**Message unique :** *L'employé reste au centre. Le système enlève la friction, pas la personne.*
**Formats :** 1080 × 1080 (WhatsApp, LinkedIn) · 16:9 (jury) · A4 paysage
**Tokens :** `00_design_system.md`

---

## 1. Structure du contenu

Un personnage central — **Salma, chargée de clientèle** (prénom fictif, à adapter) — dessiné une seule fois, au milieu. Deux lignes de temps passent par elle : celle du haut (aujourd'hui), celle du bas (avec le pilote). Six étapes chacune, alignées verticalement pour que la comparaison se fasse étape par étape.

**Aujourd'hui (haut, 6 étapes)**
1. Recevoir la demande
2. Chercher les informations
3. Vérifier la disponibilité
4. Répondre à la main
5. Risque d'oublier la relance ● *(friction marquée)*
6. Mettre à jour le statut à la main

**Avec le pilote (bas, 6 étapes)**
1. Recevoir la demande
2. Demande déjà structurée
3. Disponibilité déjà vérifiée
4. Réponse suggérée — elle relit et envoie
5. Relance rappelée au bon moment
6. Elle confirme les exceptions ■ *(décision humaine marquée)*

**Le point de bascule :** l'étape 1 est identique dans les deux lignes (même pastille, même libellé). Tout ce qui change vient *après* la réception — Salma garde le premier contact et le dernier mot.

---

## 2. Copy français

| Zone | Texte |
|---|---|
| Titre | **Une journée de Salma, chargée de clientèle** |
| Sous-titre | Même personne. Même responsabilité. Moins de friction. |
| Ligne haut, étiquette | AUJOURD'HUI |
| Ligne haut, étapes | Recevoir la demande → Chercher les infos → Vérifier la dispo → Répondre à la main → Risque d'oublier la relance → Mettre à jour le statut |
| Ligne bas, étiquette | AVEC LE PILOTE |
| Ligne bas, étapes | Recevoir la demande → Demande structurée → Dispo vérifiée → Réponse suggérée, elle envoie → Relance rappelée → Elle confirme les exceptions |
| Bulle Salma (haut) | « Je fais tout, de mémoire, entre deux appels. » |
| Bulle Salma (bas) | « Je relis, je décide, je parle au client. » |
| Légende | ● orange = friction · ● teal = préparé par le système · ■ navy = décision de Salma |
| Pied | Le système prépare le travail. Salma garde le premier contact et le dernier mot. |

Ton des bulles : factuel, digne. Jamais « je suis débordée », jamais « ouf, sauvée ».

---

## 3. Hiérarchie visuelle

1. **Salma** — silhouette contour navy, centrée, la plus grande forme de la page. Elle est la même dans les deux lignes ; on ne dessine qu'un personnage, les deux lignes de temps passent de part et d'autre.
2. Titre et sous-titre en haut à gauche.
3. Étiquettes AUJOURD'HUI / AVEC LE PILOTE en petites majuscules, à gauche de chaque ligne.
4. Les 6 + 6 pastilles d'étapes, texte 12–13 pt, une ligne et demie max.
5. Les deux bulles de Salma, 12 pt italique.
6. Légende et pied, 9–10 pt slate.

---

## 4. Direction couleur

| Élément | Couleur | Sens |
|---|---|---|
| Salma | `navy` contour 2 px, pas de remplissage | Personne, respectée, constante |
| Ligne du haut | trait `slate` 1,5 px | Le flux actuel, neutre |
| Étapes du haut 1–4, 6 | pastille `line` gris, texte `ink` | Tâches manuelles légitimes |
| Étape 5 du haut | pastille `orange`, texte `ink`, souligné `orange` fin | La friction qui coûte |
| Ligne du bas | trait `teal` 2 px | Flux préparé |
| Étape 1 du bas | pastille `navy` | Identique à aujourd'hui : elle reçoit |
| Étapes 2–5 du bas | pastille `teal` | Préparées par le système |
| Étape 6 du bas | carré `navy` plein, pictogramme personne | Décision humaine |
| Bulles | fond `white`, bord `line` ; pointe vers Salma | — |

Un seul orange sur toute la page (l'étape 5 du haut). Il attire l'œil exactement sur le coût caché : la relance oubliée.

---

## 5. Mise en page

### 16:9 (1920 × 1080)

```
┌────────────────────────────────────────────────────────────────────────────┐
│ Une journée de Salma, chargée de clientèle                                 │
│ Même personne. Même responsabilité. Moins de friction.                     │
│                                                                            │
│ AUJOURD'HUI                                                                │
│  ○ Recevoir  ○ Chercher  ○ Vérifier  ○ Répondre  ● Oublier   ○ Mettre à    │
│    la demande   les infos   la dispo   à la main   la relance   jour       │
│  ──────────────────────────────────────────────────────────────────        │
│                          « Je fais tout, de mémoire, entre deux appels. »  │
│                               ┌───────┐                                    │
│                               │ Salma │  (silhouette contour navy)         │
│                               └───────┘                                    │
│                          « Je relis, je décide, je parle au client. »      │
│  ══════════════════════════════════════════════════════════════════        │
│  ● Recevoir  ● Demande   ● Dispo     ● Réponse   ● Relance    ■ Elle       │
│    la demande  structurée  vérifiée    suggérée    rappelée     confirme   │
│ AVEC LE PILOTE                                                             │
│                                                                            │
│ Légende ○ ● ● ■    Le système prépare le travail. Salma garde le premier   │
│                    contact et le dernier mot.                              │
└────────────────────────────────────────────────────────────────────────────┘
```

### 1080 × 1080
Les deux lignes deviennent verticales, côte à côte (colonne gauche AUJOURD'HUI, colonne droite AVEC LE PILOTE), Salma en haut au centre, les 6 étapes alignées ligne par ligne. Les bulles passent sous le titre.

---

## 6. Mermaid

```mermaid
%%{init: {"theme":"base","themeVariables":{"fontFamily":"Manrope, Inter, system-ui","fontSize":"13px","lineColor":"#0E9C99","primaryColor":"#FFFFFF","primaryBorderColor":"#D8DCE3","primaryTextColor":"#111827","background":"#FAF8F4","clusterBkg":"#FAF8F4","clusterBorder":"#D8DCE3"},"flowchart":{"curve":"linear","nodeSpacing":24,"rankSpacing":40}}}%%
flowchart LR
    classDef manual fill:#FFFFFF,color:#111827,stroke:#D8DCE3;
    classDef friction fill:#FBEBDD,color:#0B1F3A,stroke:#D9772B,stroke-width:1.5px;
    classDef system fill:#DDF3F2,color:#0B1F3A,stroke:#0E9C99,stroke-width:1.5px;
    classDef human fill:#0B1F3A,color:#FFFFFF,stroke:#0B1F3A;
    classDef person fill:#FFFFFF,color:#0B1F3A,stroke:#0B1F3A,stroke-width:2px;

    subgraph AV["AUJOURD'HUI — « Je fais tout, de mémoire, entre deux appels. »"]
        direction LR
        a1["Recevoir<br/>la demande"]:::manual --> a2["Chercher<br/>les infos"]:::manual --> a3["Vérifier<br/>la dispo"]:::manual --> a4["Répondre<br/>à la main"]:::manual --> a5["Risque d'oublier<br/>la relance"]:::friction --> a6["Mettre à jour<br/>le statut"]:::manual
    end

    S(("Salma<br/>chargée de<br/>clientèle")):::person

    subgraph AP["AVEC LE PILOTE — « Je relis, je décide, je parle au client. »"]
        direction LR
        b1["Recevoir<br/>la demande"]:::human --> b2["Demande<br/>structurée"]:::system --> b3["Dispo<br/>vérifiée"]:::system --> b4["Réponse suggérée<br/>elle envoie"]:::system --> b5["Relance<br/>rappelée"]:::system --> b6["Elle confirme<br/>les exceptions"]:::human
    end

    AV ~~~ S ~~~ AP
```

> Note de rendu : Mermaid ne permet pas de « traverser » un personnage avec deux lignes ; la version finale (Figma/Canva) place Salma entre les deux lignes comme spécifié en §5. Le Mermaid sert de structure.

---

## 7. Prompt de génération

```
[préfixe commun] Aspect ratio: 16:9.

An editorial service-design infographic in French titled "Une journée de Salma, chargée de
clientèle", subtitle "Même personne. Même responsabilité. Moins de friction." In the exact centre,
a single thin-outline navy illustration of a professional woman at a desk (no face detail needed,
dignified posture, no cartoon). Above her, a thin grey horizontal timeline labelled "AUJOURD'HUI"
with six evenly spaced steps as small grey outline circles and short labels: "Recevoir la demande",
"Chercher les infos", "Vérifier la dispo", "Répondre à la main", "Risque d'oublier la relance"
(this single step has a muted orange filled dot and a thin orange underline), "Mettre à jour le
statut". A small white speech bubble from her pointing up: « Je fais tout, de mémoire, entre deux
appels. » Below her, a thicker teal timeline labelled "AVEC LE PILOTE" with six steps aligned under
the ones above: first step a navy dot "Recevoir la demande", then four teal dots "Demande
structurée", "Dispo vérifiée", "Réponse suggérée — elle envoie", "Relance rappelée", then a solid
navy square with a tiny white person icon "Elle confirme les exceptions". A second bubble pointing
down: « Je relis, je décide, je parle au client. » Footer: legend with four markers and the line
"Le système prépare le travail. Salma garde le premier contact et le dernier mot." Calm, generous
whitespace, editorial grid, only one orange element on the whole page.
```

---

## 8. Revue finale

| Question | Réponse | Preuve |
|---|---|---|
| 30 secondes ? | Oui | Une personne, deux lignes, six étapes alignées |
| Douleur d'abord ? | Oui | Ligne du haut lue en premier ; l'unique orange sur « oublier la relance » |
| Humain aux commandes ? | Oui | Salma unique et centrale ; étapes 1 et 6 du bas en navy |
| Simple et fiable ? | Oui | Aucune techno visible ; verbes du quotidien |
| Sans promesse ? | Oui | Pas de chiffre, pas de « gain de temps » |
| Crédible directeur ? | Oui | Respect du poste, bulles dignes |
| Multi-format ? | Oui | 16:9 + 1080² spécifiés |
