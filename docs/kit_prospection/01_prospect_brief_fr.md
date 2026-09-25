# Note de cadrage — Agence de location de voitures, Rabat

**Objet :** hypothèse d'audit opérationnel et proposition de pilote supervisé
**Statut :** document préparatoire, avant tout échange avec l'agence
**Auteur :** Ingénieur IA & Architecte d'automatisation

---

## 1. Avant-propos — ce que ce document est, et ce qu'il n'est pas

Ce document est une **hypothèse de travail**, préparée avant de vous rencontrer.

Il ne décrit pas votre agence. Il décrit ce que nous observons fréquemment dans des agences de location de taille comparable, et il propose une méthode courte pour vérifier, avec vous, si ces situations existent chez vous — et à quel coût.

Nous partons du principe que votre équipe est compétente et fait déjà beaucoup avec des outils dispersés. Notre rôle n'est pas de juger l'organisation actuelle ; il est de repérer les frictions répétitives qui coûtent du temps et des opportunités, puis de les traiter avec une solution simple, supervisée, et mesurable.

---

## 2. Ce qu'une journée ressemble souvent dans une agence de location

Une demande arrive par WhatsApp. Une autre par téléphone pendant qu'un client est au comptoir. Une troisième via un formulaire ou une page Facebook. Un collègue note les dates sur un carnet, un autre ouvre le tableau Excel des véhicules, un troisième cherche si le SUV demandé est encore en maintenance.

Le client demande : « C'est disponible du 12 au 15 ? » Il faut vérifier. Puis il demande le prix. Puis si la livraison à l'aéroport est possible. Chaque réponse prend deux minutes, mais il y en a trente par jour.

Un devis est envoyé. Le client ne répond pas. Personne n'a le temps de le relancer. Trois jours plus tard, il a loué ailleurs.

Le gérant, en fin de journée, demande : « On en est où avec la demande de la famille pour le week-end ? » La réponse dépend de qui s'en souvient.

Ce ne sont pas des erreurs. Ce sont des **frictions structurelles** d'un travail manuel et éclaté sur plusieurs canaux.

---

## 3. Frictions probables à valider ensemble

| # | Friction (hypothèse) | Comment elle se manifeste | Ce qu'elle coûte probablement |
|---|---|---|---|
| F1 | **Demandes dispersées** sur WhatsApp, téléphone, Facebook, formulaire, comptoir | Copier-coller des infos client d'un endroit à l'autre ; demandes perdues entre deux canaux | Temps de saisie répété, informations incomplètes, oubli |
| F2 | **Vérification de disponibilité manuelle** | Consulter un tableau, appeler un collègue, vérifier les retours prévus | Réponses lentes ou incertaines, double réservation possible |
| F3 | **Questions répétitives** | Prix, conditions, caution, kilométrage, livraison — reposées à chaque demande | Attention de l'équipe consommée par des réponses identiques |
| F4 | **Relances oubliées après devis** | Un devis part, aucune trace du « à relancer jeudi » | Opportunités perdues sans que personne ne le voie |
| F5 | **Statut des demandes flou** | « Qui gère ? Où en est-on ? » se règle par messages et mémoire | Coordination fragile, stress, erreurs de communication |
| F6 | **Visibilité du gérant limitée** | Pas de vue simple : demandes en attente, devis sans réponse, cas bloqués | Décisions prises sans données, pilotage à l'instinct |

> Nous ne savons pas encore lesquelles de ces frictions existent chez vous, ni leur ampleur. C'est précisément l'objet de l'audit court proposé en section 6.

---

## 4. Le coût caché — en langage simple

- **Une réponse lente** est une réponse que le client compare déjà avec celle d'un concurrent.
- **Une relance oubliée** est un devis payé en temps d'équipe, puis abandonné gratuitement.
- **Une demande incomplète** (dates manquantes, catégorie floue) coûte deux allers-retours au lieu d'un.
- **Une disponibilité incertaine** coûte soit une vente refusée à tort, soit une promesse impossible à tenir.
- **Un statut flou** coûte du temps de coordination interne et fatigue l'équipe.

Aucun de ces coûts n'apparaît dans un bilan. Ils apparaissent dans les minutes perdues, les clients silencieux, et la charge mentale de l'équipe.

---

## 5. La proposition : un workflow supervisé, pas un robot

Nous proposons un **système d'assistance au traitement des demandes**, construit autour de votre équipe — pas à sa place.

Concrètement, une demande client suit un chemin clair :

1. **Comprendre la demande** — dates, véhicule souhaité, lieu, contraintes sont extraits et structurés. Si une information manque, une question courte est proposée.
2. **Vérifier la disponibilité** — selon vos règles (durée, catégorie, maintenance, lieu), avec une **alternative proposée** si le véhicule demandé n'est pas libre.
3. **Préparer la réponse et le suivi** — un brouillon de réponse est rédigé pour l'équipe, une relance est planifiée si le client ne répond pas, les devis en attente sont signalés.
4. **Coordonner et sécuriser** — un composant central suit l'état de chaque demande, applique vos règles, garde une trace de chaque action, et **transmet à un membre de l'équipe** tout cas ambigu, sensible ou exceptionnel.
5. **Votre équipe décide** — prix spéciaux, réclamations, clients sensibles, dates floues, confirmation finale : toujours validés par une personne.

Le gérant dispose d'une **vue simple** : demandes en cours, devis sans réponse, cas à valider, indicateurs suivis.

### Ce que le système ne fait pas

- Il ne confirme pas de réservation sans validation humaine si votre politique l'exige.
- Il n'invente jamais une disponibilité : s'il ne sait pas, il le dit et transmet.
- Il ne remplace pas la relation client : il libère du temps pour elle.
- Il ne nécessite pas de changer vos outils du jour au lendemain.

---

## 6. La valeur attendue — en termes d'agence, pas de technologie

| Ce que vous gagnez | Comment on le mesure |
|---|---|
| Des réponses plus rapides | Temps entre la demande et la première réponse |
| Des devis qui ne meurent pas en silence | Taux de relances effectuées, devis sans réponse détectés |
| Moins de saisie et de vérification répétitives | Minutes de travail manuel par demande |
| Des demandes complètes dès le départ | Part des demandes avec toutes les informations nécessaires |
| Une vue claire pour piloter | Nombre de cas en attente, escaladés, clos — visibles en un écran |
| Une équipe qui garde la main | Nombre de cas validés par un humain (c'est une fonctionnalité, pas un défaut) |

**Nous ne promettons pas de chiffres avant de les avoir mesurés chez vous.** Le pilote sert exactement à cela : établir une base de départ, puis observer ce qui change.

---

## 7. Le pilote proposé — court, cadré, réversible

| Étape | Durée indicative | Ce que vous y gagnez |
|---|---|---|
| 1. Audit court | 30 min d'échange + 1 demi-journée d'observation | Une cartographie honnête de vos frictions réelles, chiffrées |
| 2. Cartographie du workflow | 1 semaine | Un schéma clair de « comment une demande circule » aujourd'hui et demain |
| 3. Prototype supervisé | 2–3 semaines | Un système fonctionnel sur vos cas types (données simulées ou réelles) |
| 4. Démonstration | 1 session | Vous voyez le système traiter des demandes réelles ou simulées |
| 5. Mesure des indicateurs | 2–4 semaines d'usage | Des chiffres avant/après, honnêtes |
| 6. Décision | 1 réunion | Vous décidez de continuer, ajuster ou arrêter — sans engagement au-delà |

Le pilote est conçu pour **ne rien casser** : il s'ajoute à côté de vos outils actuels, et votre équipe reste responsable des décisions.

---

## 8. Prochaine étape — simple et sans engagement

Un **échange de 30 minutes**, à l'agence ou en visio, pour :

- écouter comment une demande client est traitée aujourd'hui, de bout en bout ;
- identifier ensemble une ou deux frictions qui valent la peine d'être mesurées ;
- décider si un audit court a du sens pour vous.

Si à l'issue de cet échange la réponse est « non », vous repartez avec une cartographie de votre workflow que vous pourrez utiliser librement.

---

*Ce document présente des hypothèses à valider. Aucun chiffre de performance n'y figure volontairement : ils seront mesurés, pas annoncés.*
