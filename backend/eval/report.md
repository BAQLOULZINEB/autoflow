# Évaluation de l'agent Intake — moteur `rules`

Jeu de test : 45 messages historiques (fictifs, étiquetés) + 5 scénarios de démo.

## Exactitude par champ (demandes de devis / modification)

| Champ | Exact | Total | Exactitude |
|---|---|---|---|
| pickup_date | 39 | 44 | 89% |
| return_date | 36 | 44 | 82% |
| vehicle_category | 40 | 44 | 91% |

Intention correcte : **45/45 (100%)**

## Filet de sécurité de l'orchestrateur

Extractions avec au moins une erreur : **8** — dont routées vers un humain par les seuils : **8** (100%).

> Ce chiffre est le plus important : une erreur d'extraction qui atteint le client sans qu'une personne la voie est le vrai risque.

## Calibration de la confiance

| Confiance | Extractions 100 % correctes | Total | Taux |
|---|---|---|---|
| <0.6 | 0 | 4 | 0% |
| 0.6–0.8 | 0 | 4 | 0% |
| ≥0.8 | 36 | 36 | 100% |

## Détail

| Message | Intent | Date extraite | Date attendue | Cat. extraite | Cat. attendue | Conf. | Routage |
|---|---|---|---|---|---|---|---|
| Salam alikoum, je voudrais louer une citadine du 18 au 22 août, prise  | quote | 2026-08-18 | 2026-08-18 | citadine | citadine | 0.96 | auto |
| Salam alikoum, on est des clients réguliers, une suv du 19 au 21 août  | quote | 2026-08-19 | 2026-08-19 | suv | suv | 0.96 | auto |
| Slt, besoin d'une berline automatique pour la période du 7 au 11 septe | quote | 2026-09-07 | 2026-09-07 | berline | berline | 0.91 | auto |
| Bonjour, dispo une utilitaire pour le week-end prochain ? | quote | 2026-08-22 | 2026-09-09 | utilitaire | utilitaire | 0.72 | → humain |
| Salam, dispo une berline du 3/09 au 4/09 ? Départ l'aéroport Rabat-Sal | quote | 2026-09-03 | 2026-09-03 | berline | berline | 0.95 | auto |
| Salam, dispo une utilitaire pour le week-end prochain ? | quote | 2026-08-22 | 2026-08-21 | utilitaire | utilitaire | 0.72 | → humain |
| Bonjour l'équipe, une citadine du 27 août au 17 septembre (3 semaines) | quote | 2026-08-27 | 2026-08-27 | citadine | citadine | 0.94 | auto |
| Bonjour l'équipe, je voudrais louer une citadine du 11 au 14 septembre | quote | 2026-09-11 | 2026-09-11 | citadine | citadine | 0.96 | auto |
| Hello, besoin d'une berline pour la période du 11 au 18 septembre, ret | quote | 2026-09-11 | 2026-09-11 | berline | berline | 0.89 | auto |
| Bonjour, je veux modifier ma réservation du 17 septembre : décaler au  | modification | 2026-09-17 | 2026-09-17 | None | berline | 0.35 | → humain |
| Salam, dispo une berline pour le week-end prochain ? Je suis preneur s | quote | 2026-08-29 | 2026-09-03 | berline | berline | 0.72 | → humain |
| Salam alikoum, je cherche une voiture berline du 2 au 9 septembre. Pri | quote | 2026-09-02 | 2026-09-02 | berline | berline | 0.96 | auto |
| Salam, je veux modifier ma réservation du 1 septembre : décaler au 2 s | modification | 2026-09-01 | 2026-09-01 | None | 4x4 | 0.35 | → humain |
| Salam, besoin d'une citadine pour la période du 14 au 21 septembre, re | quote | 2026-09-14 | 2026-09-14 | citadine | citadine | 0.89 | auto |
| Bonjour l'équipe, besoin d'une berline manuelle pour la période du 5 a | quote | 2026-09-05 | 2026-09-05 | berline | berline | 0.89 | auto |
| Bonjour, c'est combien une citadine du 15 au 16 septembre à l'aéroport | quote | 2026-09-15 | 2026-09-15 | citadine | citadine | 0.96 | auto |
| Salam alikoum, location citadine 18-21 septembre svp, Hay Riad. Merci  | quote | 2026-09-18 | 2026-09-18 | citadine | citadine | 0.96 | auto |
| Bonjour l'équipe, une voiture pour ce week-end à l'aéroport Rabat-Salé | quote | 2026-09-05 | 2026-09-15 | None | suv | 0.55 | → humain |
| Bonjour, je cherche une voiture berline du 20 au 22 septembre. Prise l | quote | 2026-09-20 | 2026-09-20 | berline | berline | 0.96 | auto |
| Bonjour, je cherche une voiture citadine automatique du 10 au 15 septe | quote | 2026-09-10 | 2026-09-10 | citadine | citadine | 0.96 | auto |
| Salam, on est des clients réguliers, une 4x4 du 3 au 6 septembre à l'a | quote | 2026-09-03 | 2026-09-03 | 4x4 | 4x4 | 0.96 | auto |
| Hello, dispo une utilitaire automatique du 11/09 au 13/09 ? Départ Hay | quote | 2026-09-11 | 2026-09-11 | utilitaire | utilitaire | 0.95 | auto |
| Salam, dispo une berline pour le week-end prochain ? Vous avez ça ? | quote | 2026-09-05 | 2026-09-25 | berline | berline | 0.72 | → humain |
| Bonjour l'équipe, je voudrais une berline le 19 septembre pour 3 jours | quote | 2026-09-19 | 2026-09-19 | berline | berline | 0.9 | auto |
| Salam alikoum, location utilitaire 24-28 septembre svp, Agdal. Vous av | quote | 2026-09-24 | 2026-09-24 | utilitaire | utilitaire | 0.96 | auto |
| Bonsoir, besoin d'une citadine pour la période du 25 au 28 septembre,  | quote | 2026-09-25 | 2026-09-25 | citadine | citadine | 0.91 | auto |
| Bonjour l'équipe, location citadine 16-18 septembre svp, Agdal. Merci. | quote | 2026-09-16 | 2026-09-16 | citadine | citadine | 0.96 | auto |
| Slt, besoin d'une utilitaire manuelle pour la période du 4 au 8 octobr | quote | 2026-10-04 | 2026-10-04 | utilitaire | utilitaire | 0.89 | auto |
| Bonsoir, je voudrais louer une utilitaire du 13 au 15 septembre, prise | quote | 2026-09-13 | 2026-09-13 | utilitaire | utilitaire | 0.96 | auto |
| Salam alikoum, location suv 23-27 septembre svp, Hay Riad. Merci. | quote | 2026-09-23 | 2026-09-23 | suv | suv | 0.96 | auto |
| Hello, besoin d'une 4x4 manuelle pour la période du 4 au 6 octobre, re | quote | 2026-10-04 | 2026-10-04 | 4x4 | 4x4 | 0.89 | auto |
| Salam, une 4x4 manuelle du 9 au 10 octobre à l'aéroport Rabat-Salé, j' | quote | 2026-10-09 | 2026-10-09 | 4x4 | 4x4 | 0.94 | auto |
| Salam, dispo une berline manuelle du 23/09 au 27/09 ? Départ Rabat. Vo | quote | 2026-09-23 | 2026-09-23 | berline | berline | 0.95 | auto |
| Bonsoir, je voudrais louer une 4x4 du 4 au 5 octobre, prise à Agdal. D | quote | 2026-10-04 | 2026-10-04 | 4x4 | 4x4 | 0.96 | auto |
| Bonsoir, je voudrais une berline le 10 novembre pour 3 jours, Rabat. E | quote | 2026-11-10 | 2026-11-10 | berline | berline | 0.9 | auto |
| Slt, dispo une 4x4 du 4/10 au 9/10 ? Départ Rabat. Merci. | quote | 2026-10-04 | 2026-10-04 | 4x4 | 4x4 | 0.95 | auto |
| Salam alikoum, location berline 23-26 septembre svp, Rabat. Merci. | quote | 2026-09-23 | 2026-09-23 | berline | berline | 0.96 | auto |
| Salam alikoum, c'est combien une citadine du 10 au 13 novembre à Agdal | quote | 2026-11-10 | 2026-11-10 | citadine | citadine | 0.96 | auto |
| Salam, dispo une citadine manuelle du 18/11 au 20/11 ? Départ Agdal. M | quote | 2026-11-18 | 2026-11-18 | citadine | citadine | 0.95 | auto |
| Bonjour l'équipe, location citadine 4-6 octobre svp, Agdal. Merci bcp | quote | 2026-10-04 | 2026-10-04 | citadine | citadine | 0.96 | auto |
| Bonjour l'équipe, je veux modifier ma réservation du 25 septembre : dé | modification | 2026-09-25 | 2026-09-25 | None | suv | 0.35 | → humain |
| Bonjour, dispo une berline manuelle du 16/11 au 23/11 ? Départ Rabat.  | quote | 2026-11-16 | 2026-11-16 | berline | berline | 0.95 | auto |
| Salam, besoin d'une berline pour la période du 17 au 22 novembre, reto | quote | 2026-11-17 | 2026-11-17 | berline | berline | 0.89 | auto |
| Hello, je voudrais louer une suv du 10 au 13 octobre, prise à Rabat. | quote | 2026-10-10 | 2026-10-10 | suv | suv | 0.96 | auto |

## Limites

- Étiquettes générées avec les messages (même générateur) : l'exactitude est **optimiste** ; un jeu de 30 messages réels annotés à la main est prévu en phase pilote.
- Le moteur de règles ne couvre pas les formulations libres (« vers la fin du mois ») : elles tombent en `needs_human`, ce qui est le comportement voulu.
- Aucun gain métier n'est déduit de ce rapport.