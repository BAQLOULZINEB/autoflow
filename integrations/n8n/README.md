# n8n — intégration périphérique (optionnelle)

AutoFlow garde l'intelligence et l'état dans LangGraph. n8n sert de **colle** vers les canaux réels :

| Flux n8n | Rôle | Endpoint AutoFlow |
|---|---|---|
| `autoflow_intake_webhook.json` | Webhook (WhatsApp Business / Typeform / site) → crée la demande → notifie l'équipe ou le manager selon `review_level` | `POST /api/public/intake`, `GET /api/requests/{id}` |
| *(à créer)* relances | Cron toutes les heures → `POST /api/demo/sweep` → si `reminders_due > 0`, ping Slack | `POST /api/demo/sweep`, `GET /api/reviews` |

Variables d'environnement n8n : `AUTOFLOW_API_URL`, `AUTOFLOW_ADMIN_TOKEN`, `AUTOFLOW_ADMIN_URL`.

Règle du pilote : n8n **notifie**, il n'envoie jamais un message au client. L'envoi reste un clic humain dans l'espace admin.
