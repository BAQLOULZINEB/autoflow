# 07 — Portfolio, CV et entretien

## Section README (GitHub)

**AutoFlow — supervised workflow automation for a car-rental agency (LangGraph · FastAPI · React)**

Turns scattered WhatsApp/Facebook/form requests into a traced, human-supervised pipeline: an intake agent structures the message (with verbatim evidence for every field), a deterministic availability agent checks the fleet and proposes alternatives, a follow-up agent drafts French replies and schedules reminders, and a LangGraph orchestrator routes every ambiguous or sensitive case to staff or manager through a real `interrupt()`. Admin dashboard with a live reasoning panel that lights up the graph path and lists every rule evaluated. 8 e2e tests; 100 % of extraction errors caught by the human gate on a 45-message labeled set. Runs offline (no LLM) at zero cost; deploys to Vercel/Netlify + Docker.

## Bullet CV

- Conçu et livré **AutoFlow**, un système multi-agents supervisé (LangGraph 1.x, FastAPI, React) automatisant le traitement des demandes d'une agence de location : extraction structurée avec preuves, disponibilité déterministe, brouillons et relances, escalade humaine par matrice de règles, journal d'événements et KPI auditables ; 100 % des erreurs d'extraction rattrapées par la validation humaine sur un jeu étiqueté.

## Pitch d'entretien (60 s)

> J'ai pris un problème banal — une agence qui reçoit ses demandes sur WhatsApp et les traite à la main — et j'ai construit un workflow supervisé plutôt qu'un chatbot. Un orchestrateur LangGraph route chaque demande entre trois agents étroits : comprendre, vérifier, préparer. Le point clé, c'est que le système ne prend aucune décision commerciale : il prépare, et une personne clique. La disponibilité est du code déterministe, donc il ne peut pas inventer une voiture libre ; l'extraction ne garde un champ que s'il cite le message ; et chaque transition est un événement, donc les KPI sont calculés, jamais déclarés. J'ai un panneau « suivi en direct » qui montre, pour n'importe quelle demande, le chemin pris dans le graphe et chaque règle évaluée avec sa valeur et son seuil. Sur 45 messages étiquetés, l'extraction est à ~90 % par champ, et surtout 100 % des erreurs passent par un humain. Ça tourne hors ligne à coût zéro, et ça se déploie sur Vercel en une commande.

## Questions probables du jury et réponses courtes

| Question | Réponse |
|---|---|
| Pourquoi pas un seul LLM avec des outils ? | Parce que le gérant doit pouvoir dire « je sais exactement ce que ça peut faire ». Un graphe explicite + des règles versionnées se testent ; un agent libre s'observe. |
| Où est l'IA alors ? | Dans l'intake (compréhension du langage, optionnellement LLM), dans la structure de décision (signaux calibrés → routage), et dans la conception : l'IA *sert* le workflow, elle ne le remplace pas. |
| Et si l'extraction se trompe ? | Elle le dit (confiance par champ) et la demande va dans la file humaine. Mesuré : 8/8. |
| Ça vaut quoi économiquement ? | Zéro infrastructure, LLM optionnel à quelques centimes par demande ; la valeur se mesure en pilote avec une base avant/après, pas dans un slide. |
| Généralisable ? | Oui : intake → vérification déterministe → brouillon → validation → suivi est le squelette de la plupart des workflows de PME de service. |
