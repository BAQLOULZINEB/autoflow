# 01 — Cahier des charges

**Projet de stage :** *AutoFlow — système d'automatisation intelligent des workflows d'entreprise*
**Cas d'application :** agence de location de voitures, Rabat
**Rôle :** AI Engineer — automatisation des workflows métier
**Statut :** pilote démontrable, données fictives, aucun gain chiffré revendiqué avant mesure

---

## 1. Contexte et problème

Une agence de location reçoit ses demandes par WhatsApp, Facebook, téléphone, formulaire et comptoir. Aujourd'hui (hypothèses à valider en audit — voir `kit_prospection/02_workflow_audit_template_fr.md`) :

| # | Friction | Coût probable |
|---|---|---|
| F1 | Demandes dispersées sur plusieurs canaux | re-saisie, informations incomplètes, oublis |
| F2 | Disponibilité vérifiée à la main dans un tableau | réponses lentes, risque de double réservation |
| F3 | Questions répétitives (prix, caution, km) | attention de l'équipe consommée |
| F4 | Relances oubliées après devis | devis perdus sans que personne ne le voie |
| F5 | Statut des demandes flou | coordination par messages et mémoire |
| F6 | Visibilité manager limitée | pilotage à l'instinct |

## 2. Objectif

Livrer un **workflow supervisé** : le système structure les demandes, vérifie la disponibilité, prépare les réponses et les relances, trace chaque action, et **transmet à une personne** tout cas ambigu, sensible ou exceptionnel. Il ne remplace pas l'équipe ; il traite la répétition et délègue l'exception.

## 3. Périmètre

### Inclus (pilote)
- Saisie des demandes : collage manuel, formulaire public `/demande`, webhook n8n.
- Agent Intake : intention, dates, catégorie, boîte, lieux, budget, signaux (remise, client régulier), confiance par champ, preuves textuelles, question de clarification.
- Agent Disponibilité : règles déterministes sur la table flotte + réservations + maintenance ; alternatives (catégorie de repli, décalage de dates) ; raisons d'exclusion.
- Agent Suivi : brouillons FR (devis, alternative, clarification, relance), politique de relance (24 h, max 2, sans réponse à 72 h), action recommandée.
- Orchestrateur LangGraph : machine à 10 états, matrice d'escalade, `interrupt()` humain, checkpoints, journal d'événements, cap anti-boucle.
- Espace admin : tableau de bord, file à valider (équipe / manager), fiche demande à 5 onglets, nouvelle demande, flotte & règles, architecture, contrôles démo (scénarios A–E, horloge +24 h / +72 h, reset).
- Déploiement : frontend Vercel/Netlify, backend Docker (Render/Railway) ou Vercel Python.

### Exclu (audit-gated)
Paiement, tarification dynamique, envoi automatique au client, connecteur WhatsApp réel, CRM/ERP, maintenance prédictive, voix.

## 4. Exigences fonctionnelles

| ID | Exigence | Vérification |
|---|---|---|
| RF1 | Toute demande reçue obtient un identifiant, un état et un événement initial | `test_scenario_a_standard_quote` |
| RF2 | Le système ne déclare jamais un véhicule disponible sans vérification déterministe | `availability.py` sans LLM ; `test_scenario_b_alternative` |
| RF3 | Un champ extrait par LLM sans preuve verbatim est rejeté | `extract_llm` (evidence gate) |
| RF4 | Toute réclamation est escaladée au manager sans brouillon automatique | `test_scenario_d_complaint` |
| RF5 | Remise demandée, location > 14 j, valeur > 6000 MAD → manager | `decide_after_availability` |
| RF6 | Aucun message n'est envoyé sans clic humain | `finalize_node` uniquement via `Command(resume)` |
| RF7 | Une relance est planifiée à l'envoi ; au-delà de la politique, la demande passe `stalled` → humain | `test_follow_up_engine_time_travel` |
| RF8 | Chaque transition est journalisée avec acteur, raison, horodatage | `store.transition` |
| RF9 | Les KPI sont calculés depuis le journal, jamais stockés | `orchestrator.kpis` |
| RF10 | L'espace admin exige un token ; le formulaire public n'en exige pas | `test_auth_required` |

## 5. Exigences non fonctionnelles

- **Fonctionne hors ligne** (`LLM_PROVIDER=none`) — la démo ne dépend d'aucune API externe.
- **Explicabilité** : chaque fiche montre *pourquoi* elle est dans la file.
- **Reprise** : l'état du workflow survit à un redémarrage (checkpointer SQLite).
- **Confidentialité** : téléphones masqués, données fictives, seul le texte du message part vers un LLM (si activé). Loi 09-08 à cadrer avec l'agence.
- **Simplicité** : 1 orchestrateur + 3 agents ; < 1 500 lignes de Python métier.

## 6. Indicateurs (à mesurer, pas à promettre)

| Indicateur | Avant (audit) | Objectif pilote | Après |
|---|---|---|---|
| Temps de première réponse | à mesurer | réduire | à mesurer |
| Délai de devis | à mesurer | réduire | à mesurer |
| % demandes complètes au 1er message | à mesurer | augmenter | à mesurer |
| Taux de relances effectuées | à mesurer | ↑ | à mesurer |
| Minutes manuelles / demande | à mesurer | libérer | à mesurer |
| Cas escaladés à un humain | à mesurer | garantir le contrôle | à mesurer |

## 7. Livrables

1. Code : `backend/` (API + LangGraph), `frontend/` (espace admin), `integrations/n8n/`.
2. Tests end-to-end des 5 scénarios (`backend/tests/`).
3. Ce dossier : cahier des charges, architecture (7 vues), choix techniques, plan de démo, guide de déploiement, évaluation, rapport de stage, portfolio.
4. Kit de prospection réutilisé (`docs/kit_prospection/`) et visuels de référence (`docs/assets/`).

## 8. Planning (indicatif, 8 semaines)

| Sem. | Phase | Sortie |
|---|---|---|
| 1 | Cadrage & hypothèses | ce cahier, kit de prospection |
| 2 | Données & machine à états | `db.py`, `store.py`, `rules.json`, données démo |
| 3–4 | Agents + orchestrateur | `agents/*`, `workflow/graph.py`, tests |
| 5 | Espace admin | `frontend/` |
| 6 | Démo & retours agence | scénarios A–E, ajustements |
| 7–8 | Mesure pilote | tableau KPI avant/après, rapport |
