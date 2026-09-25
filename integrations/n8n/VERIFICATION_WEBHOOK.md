# Preuve d'intégration n8n ↔ AutoFlow

Statut : vérifié localement le **2026-09-25 19:47:17 UTC**.

## Workflow publié

- Nom : `AutoFlow - Demo local intake webhook`
- Identifiant n8n : `c7274c98-9b68-4f2f-a975-bdf3189f8e29`
- Déclencheur : `POST /webhook/autoflow-demo-intake`
- Cible métier : `POST http://127.0.0.1:8000/api/public/intake`
- Sécurité fonctionnelle : le workflow crée une demande ; il ne contacte aucun client ni service externe.

## Rejouer la preuve

Les services n8n et AutoFlow doivent être actifs sur le même ordinateur.

```powershell
$body = @{
  message = 'Bonjour, je souhaite louer une Clio du 15 au 18 octobre.'
  customer_name = 'Demo Webhook'
  channel = 'n8n-proof'
} | ConvertTo-Json -Compress

Invoke-RestMethod `
  -Uri 'http://127.0.0.1:5678/webhook/autoflow-demo-intake' `
  -Method Post -ContentType 'application/json' -Body $body
```

Résultat observé durant la vérification :

```json
{
  "request_id": "A-0055",
  "message": "Merci ! Votre demande a été reçue, l'agence revient vers vous rapidement."
}
```

La demande `A-0055` est donc créée par le vrai graphe AutoFlow à partir d'un appel HTTP entrant n8n. Pour la soutenance, ouvrez ensuite **À traiter** dans AutoFlow et l'onglet **Executions** du workflow n8n : les deux interfaces montrent le même passage de relais.
