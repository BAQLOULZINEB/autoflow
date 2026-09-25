# 04 — Démo, données et déploiement

## 4.1 Lancer en local (2 terminaux)

```bash
# 1) API — Python 3.12+
cd backend
python -m venv ../.venv && ../.venv/Scripts/activate      # Windows ; Linux/mac : source ../.venv/bin/activate
pip install -r requirements.txt
cp .env.example .env                                       # ADMIN_TOKEN, LLM_PROVIDER=none par défaut
python -m uvicorn app.main:app --reload --port 8000        # seed automatique au 1er démarrage (~5 s : 6 semaines d'historique)

# 2) Espace admin
cd frontend
npm install && npm run dev                                 # http://localhost:5173  (proxy /api → :8000)
```

Connexion : token `change-me-admin` (à changer dans `backend/.env`). Formulaire client public : `http://localhost:5173/demande`.

Ou tout en un : `docker compose up` → admin sur :4173, API sur :8000.

## 4.2 Le jeu de données « remis par l'agence »

Généré par `backend/data/generate_dataset.py` (seed fixe, reproductible) — **fictif mais réaliste** pour le marché marocain :

| Fichier | Contenu |
|---|---|
| `fleet.csv` | 24 véhicules : Dacia Sandero/Logan/Duster, Clio, i10, Picanto, 208, Yaris, Polo, Accent, Corolla, Octavia, Classe A, Tucson, Sportage, Creta, 3008, Hilux, Kangoo, Doblo — 230 à 800 MAD/j, 3 sites (Agdal, Hay Riad, aéroport), 2 en maintenance |
| `bookings.csv` | 80 réservations confirmées sept. → déc. 2026, sans chevauchement |
| `customers.csv` | 40 clients, téléphones masqués, 6 « réguliers » |
| `history.json` | 45 messages entrants sur 6 semaines (WhatsApp 60 %, Facebook, téléphone, formulaire, comptoir), FR + darija légère, avec le comportement humain scénarisé (accepté / décliné / sans réponse / refusé / réclamation) |
| `scenarios.json` | Les 5 scénarios de démo live A–E |

Au premier démarrage, `reset_and_seed()` **rejoue l'historique à travers le vrai graphe** (horloge démo reculée message par message) : rien n'est écrit « à la main » en base, chaque ligne vient du code normal. Résultat : 45 demandes, ~370 événements, 22 confirmées, 7 leads sans réponse à rappeler, 7 relances envoyées.

`POST /api/demo/reset?history=false` donne une agence vide pour une démo « à partir de zéro ».

## 4.3 Simulations intégrées (démo automatisée = tests d'acceptation)

Menu **Simulations** : sept cas métier prêts à jouer, chacun avec le logo du canal (WhatsApp, Facebook, Instagram, site, téléphone, comptoir). « Jouer » exécute la séquence complète *client → agents → décision humaine → réponse client → relances* à travers la vraie API, puis révèle les étapes une à une avec, pour chacune : l'acteur, l'état atteint et les vérifications attendues (✓ / ✗). « Tout jouer » enchaîne les sept.

| Cas | Canal | Ce qu'il prouve |
|---|---|---|
| Devis standard | WhatsApp | extraction avec preuves, dispo déterministe, envoi humain, réservation créée |
| SUV indisponible → alternative | Facebook | raisons d'exclusion, repli, brouillon modifié, relance +24 h, client décline |
| Dates floues + remise | Instagram | seuils de confiance → manager, complétion → revérification, note de décision |
| Réclamation | Site web (formulaire public) | escalade immédiate, aucun brouillon, priorité haute |
| Lead silencieux | Téléphone | relances n°1 et n°2, `stalled` à 72 h, recommandation d'appel, reprise |
| Question d'information | Comptoir | intent info → clarification, pas de dispo sans dates |
| Location 25 jours | WhatsApp | règle `max_auto_days` → manager, refus tracé |

Les mêmes cas tournent en CI : `backend/tests/test_simulations.py` (7 tests paramétrés). Un écart à l'écran = un test rouge. Le bouton **Mode présentation** agrandit la typographie et masque les contrôles de démo.

## 4.4 Script de démo (7 minutes)

| # | Écran | Ce que ça prouve | Temps |
|---|---|---|---|
| 0 | Tableau de bord : 45 demandes, 7 à valider, bandeau « données de démonstration » | point de départ honnête, agence « vivante » | 0:30 |
| 1 | Barre latérale → **Scénario A** → fiche : structurée (preuves), disponibilité CIT-03, brouillon avec prix de la table | le système comprend et ne dit que ce qu'il sait | 1:00 |
| 2 | Onglet **Raisonnement** : chemin allumé Intake → Routage → Disponibilité → Matrice → Brouillon → Validation | le jury voit chaque règle et seuil | 0:45 |
| 3 | « Approuver & envoyer » → état *Attente client* → relance planifiée +24 h | le système prépare, une personne envoie | 0:30 |
| 4 | **Scénario B** : SUV en maintenance / réservé → alternatives BER-02 ou décalage, raisons d'exclusion | il aide à vendre, pas seulement à dire non | 0:45 |
| 5 | **Scénario C** : « week-end prochain » + « petit geste sur le prix » → *À valider · Manager* ; changer d'utilisateur → Omar ; compléter les dates → revérification → *Escaladée* (remise) → approuver avec note | contrôle humain réel, `Command(goto)` | 1:15 |
| 6 | **Scénario D** : réclamation → *Escaladée*, priorité haute, aucun brouillon | sécurité | 0:20 |
| 7 | **+24 h** → relance n°1 à envoyer → envoyer ; **+72 h** → *Sans réponse* → appeler / clôturer | aucune demande ne meurt en silence | 0:45 |
| 8 | **Suivi en direct** : le flux défile pendant la démo, cliquer un événement montre le raisonnement | transparence totale | 0:30 |
| 9 | Tableau de bord : compteurs (jamais de « % de gain ») | honnêteté KPI | 0:30 |

Phrase pour « et si le système se trompe ? » : *« Il le dit, et il transmet à une personne. »* (100 % des extractions erronées du jeu d'évaluation passent par la file humaine.)

## 4.5 Déployer

### Frontend → Vercel ou Netlify (gratuit)
```bash
cd frontend
echo "VITE_API_URL=https://<votre-backend>" > .env.production
npx vercel --prod          # ou : npx netlify deploy --prod --dir=dist  (après npm run build)
```
`vercel.json` / `netlify.toml` gèrent les routes SPA.

### Backend → Render / Railway / Fly (Docker, gratuit ou ~5 $/mois)
- Image : `backend/Dockerfile`. Volume `/data` pour SQLite.
- Variables : `ADMIN_TOKEN`, `CORS_ORIGINS=https://<votre-frontend>`, `LLM_PROVIDER=none` (ou `anthropic` + `ANTHROPIC_API_KEY`), `DATABASE_URL` si Postgres.

### Backend → Vercel Python (tout sur Vercel)
`backend/vercel.json` + `backend/api/index.py`. Le disque est éphémère : mettre `DATABASE_URL` vers Neon/Supabase, sinon la base repart à zéro à chaque cold start (acceptable pour une démo, `SEED_DEMO=true`).

### Sécurité minimale du pilote
Token admin unique par en-tête (rôles portés par `actor`), formulaire public limité à la création de demandes, téléphones masqués, aucun secret dans le frontend, CORS restreint à l'URL du frontend.

## 4.6 Checklist avant démo

- [ ] `pytest -q` vert (16 tests : scénarios A–E, relances, réservation, 7 simulations)
- [ ] `LLM_PROVIDER=none` : la démo ne dépend d'aucune API
- [ ] Bandeau « Données de démonstration » visible
- [ ] Captures d'écran de secours de chaque étape
- [ ] `docs/diagrams/*.html` ouverts dans un onglet (export PNG/PDF via `⋯`)
