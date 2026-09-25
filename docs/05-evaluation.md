# 05 — Évaluation

Trois niveaux : (1) le code fait ce que la spec dit, (2) l'agent Intake extrait juste — et surtout, ses erreurs sont rattrapées, (3) la valeur métier, mesurée seulement en pilote.

## 5.1 Tests end-to-end (`backend/tests/test_workflow.py`)

| Test | Exigence couverte | Résultat |
|---|---|---|
| `test_auth_required` | RF10 — token obligatoire | ✅ |
| `test_scenario_a_standard_quote` | RF1, RF6, RF7 — devis standard, envoi humain, relance planifiée | ✅ |
| `test_scenario_b_alternative` | RF2 — indisponible → alternatives + raisons | ✅ |
| `test_scenario_c_ambiguous_sensitive` | RF5 — ambigu + remise → manager ; complétion → revérification → escalade | ✅ |
| `test_scenario_d_complaint` | RF4 — réclamation escaladée sans brouillon | ✅ |
| `test_follow_up_engine_time_travel` | RF7 — relance due à +24 h, lead sans réponse à +72 h | ✅ |
| `test_customer_accepts_creates_booking` | confirmation humaine → réservation en base | ✅ |
| `test_kpis_and_graph` | RF9 — KPI depuis le journal ; graphe exposé | ✅ |

`8 passed` — chaque exécution rejoue aussi les 45 messages d'historique (≈ 8 s).

### Simulations métier (`backend/tests/test_simulations.py`, 7 cas paramétrés + catalogue)

Les sept cas de la page **Simulations** sont exécutés tels quels : chaque étape (soumission, décision humaine, réponse client, avance d'horloge, relance) est suivie d'assertions sur l'état, le niveau de revue, les brouillons, les relances et les réservations. Deux défauts réels ont été trouvés par cette suite avant la démo : (1) l'horloge de « lead sans réponse » repartait à zéro à chaque relance envoyée — un lead ne pouvait jamais passer `stalled` après la 2e relance ; (2) « je passerai réserver plus tard » faisait primer l'intention *réservation* sur une question d'information. Les deux sont corrigés et couverts.

**Total : 16 tests, tous verts.**

## 5.2 Exactitude de l'agent Intake (`backend/eval/report.md`)

Jeu : 45 messages historiques étiquetés + 5 scénarios. Moteur `rules` (hors ligne).

| Champ | Exactitude |
|---|---|
| pickup_date | 89 % (39/44) |
| return_date | 82 % (36/44) |
| vehicle_category | 91 % (40/44) |
| intention | 100 % (45/45) |

**Filet de sécurité** : 8 extractions contiennent au moins une erreur → **8/8 routées vers un humain** par les seuils (`confidence_threshold 0.75`, `critical_field_threshold 0.7`, champs manquants).

**Calibration** : confiance ≥ 0,8 → 94 % d'extractions entièrement correctes ; < 0,8 → 0 %. Le seuil est donc bien placé : ce qui passe en automatique est fiable, ce qui doute est relu.

Limites déclarées : étiquettes issues du même générateur que les messages (résultat optimiste) ; un jeu de 30 messages réels annotés à la main est prévu en phase pilote ; les formulations libres (« vers la fin du mois ») tombent en `needs_human`, ce qui est le comportement voulu.

Reproduire : `cd backend && python -m eval.eval_intake` (`--llm` pour le moteur LLM+règles).

## 5.3 Robustesse

| Cas | Comportement vérifié |
|---|---|
| LLM indisponible | flag `llm_failed`, résultat des règles conservé, confiance × 0,9 |
| Champ LLM sans preuve dans le message | rejeté (`null`) |
| Transition d'état illégale | `IllegalTransition` → HTTP 409, rien n'est écrit |
| Redémarrage pendant une validation en attente | checkpoint SQLite → `pending_interrupt` toujours présent |
| Boucle | `hops > 8` → humain |
| Relances | plafond `max_reminders = 2`, puis `stalled` → appel recommandé |

## 5.4 Indicateurs métier — cadre de mesure du pilote

| Indicateur | Source (journal) | Avant (audit) | Objectif | Après |
|---|---|---|---|---|
| Temps de 1re réponse | `received_at` → 1er `Draft.sent_at` | à mesurer | ↓ | à mesurer |
| Délai de devis | `received_at` → `quote_ready` | à mesurer | ↓ | à mesurer |
| % demandes complètes | `missing_fields == []` au 1er message | à mesurer | ↑ | à mesurer |
| Taux de relances effectuées | `FollowUp.status == done` / dues | à mesurer | ↑ | à mesurer |
| Minutes manuelles / demande | chrono sur site | à mesurer | ↓ | à mesurer |
| Cas escaladés | `Event.to_state ∈ {needs_human, escalated}` | à mesurer | contrôle garanti | à mesurer |

Règles : même méthode avant/après ; résultats en fourchettes si n < 30 ; effet Hawthorne noté ; distinguer *temps gagné*, *tâches déplacées vers l'humain*, *cas exigeant toujours une intervention*.

Les compteurs affichés dans la démo (45 demandes, 22 confirmées, 7 relances…) sont des **compteurs d'activité simulée**, jamais des gains.
