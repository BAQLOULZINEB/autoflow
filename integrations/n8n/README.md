# n8n — intégration périphérique (optionnelle)

La démonstration locale a été exécutée avec succès : voir
[`VERIFICATION_WEBHOOK.md`](VERIFICATION_WEBHOOK.md) pour le payload, la réponse
réelle `A-0055` et le protocole de reproduction.

## Démo locale prête à tester

Importer `autoflow_demo_local_webhook.json` dans n8n. Il crée une vraie demande dans
AutoFlow et retourne l'identifiant de la demande ; il ne contient aucun token et ne
contacte aucun service externe.

Avec l'API AutoFlow lancée sur le même PC, le webhook de production est :

```text
POST http://127.0.0.1:5678/webhook/autoflow-demo-intake
Content-Type: application/json

{
  "message": "Bonjour, je souhaite une citadine du 10 au 12 octobre à Rabat.",
  "channel": "n8n-demo",
  "customer_name": "Test présentation"
}
```

Dans n8n, activez le workflow avant d'utiliser `/webhook/...`; la version de test
utilise `/webhook-test/...` après **Listen for test event**. Une demande doit alors
apparaître dans **À traiter** dans AutoFlow.

AutoFlow garde l'intelligence et l'état dans LangGraph. n8n sert de **colle** vers les canaux réels :

| Flux n8n | Rôle | Endpoint AutoFlow |
|---|---|---|
| `autoflow_intake_webhook.json` | Webhook (WhatsApp Business / Typeform / site) → crée la demande → notifie l'équipe ou le manager selon `review_level` | `POST /api/public/intake`, `GET /api/requests/{id}` |
| *(à créer)* relances | Cron toutes les heures → `POST /api/demo/sweep` → si `reminders_due > 0`, ping Slack | `POST /api/demo/sweep`, `GET /api/reviews` |

Variables d'environnement n8n : `AUTOFLOW_API_URL`, `AUTOFLOW_ADMIN_TOKEN`, `AUTOFLOW_ADMIN_URL`.

Règle du pilote : n8n **notifie**, il n'envoie jamais un message au client. L'envoi reste un clic humain dans l'espace admin.
