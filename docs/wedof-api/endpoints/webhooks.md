# Webhooks API Documentation

## Overview
Wedof webhooks allow you to receive real-time notifications when events occur in your account. Instead of polling the API, you can register webhook endpoints to be notified of changes.

## Webhook Management

### List Webhooks
```http
GET /api/v2/webhooks
```

#### Response
```json
{
  "data": [
    {
      "id": "webhook_123",
      "url": "https://your-app.com/webhooks/wedof",
      "events": ["stagiaire.created", "stagiaire.updated"],
      "active": true,
      "secret": "whsec_***",
      "created_at": "2024-01-15T10:00:00Z",
      "last_triggered": "2024-03-20T15:30:00Z"
    }
  ]
}
```

### Create Webhook
```http
POST /api/v2/webhooks
```

#### Request Body
```json
{
  "url": "https://your-app.com/webhooks/wedof",
  "events": [
    "stagiaire.created",
    "stagiaire.updated",
    "formation.inscription",
    "bilan.completed"
  ],
  "description": "Main webhook for BDC system"
}
```

#### Response
```json
{
  "id": "webhook_456",
  "url": "https://your-app.com/webhooks/wedof",
  "events": ["stagiaire.created", "stagiaire.updated"],
  "secret": "whsec_1234567890abcdef",
  "active": true
}
```

### Update Webhook
```http
PUT /api/v2/webhooks/{id}
```

### Delete Webhook
```http
DELETE /api/v2/webhooks/{id}
```

### Test Webhook
```http
POST /api/v2/webhooks/{id}/test
```

## Webhook Events

### Stagiaire Events

#### stagiaire.created
Triggered when a new stagiaire is created

```json
{
  "id": "evt_123456",
  "type": "stagiaire.created",
  "created": "2024-03-25T10:00:00Z",
  "data": {
    "id": "stag_789",
    "nom": "Nouveau",
    "prenom": "Stagiaire",
    "email": "nouveau@example.com",
    "formation_id": "form_123"
  }
}
```

#### stagiaire.updated
Triggered when stagiaire information is updated

#### stagiaire.deleted
Triggered when a stagiaire is deleted

#### stagiaire.progression.updated
Triggered when stagiaire progression is updated

```json
{
  "id": "evt_123457",
  "type": "stagiaire.progression.updated",
  "created": "2024-03-25T11:00:00Z",
  "data": {
    "stagiaire_id": "stag_789",
    "formation_id": "form_123",
    "module_id": "mod_456",
    "old_progression": 45,
    "new_progression": 60,
    "module_completed": false
  }
}
```

### Formation Events

#### formation.created
New formation created

#### formation.updated
Formation details updated

#### formation.inscription
New inscription to formation

```json
{
  "id": "evt_123458",
  "type": "formation.inscription",
  "created": "2024-03-25T12:00:00Z",
  "data": {
    "formation_id": "form_123",
    "stagiaire_id": "stag_789",
    "date_inscription": "2024-03-25",
    "date_debut_prevue": "2024-04-01",
    "financement": {
      "type": "CPF",
      "montant": 5000
    }
  }
}
```

#### formation.started
Formation has started

#### formation.completed
Formation has ended

#### formation.cancelled
Formation was cancelled

### Bilan Events

#### bilan.scheduled
New bilan scheduled

#### bilan.started
Bilan session started

#### bilan.completed
Bilan completed and ready

```json
{
  "id": "evt_123459",
  "type": "bilan.completed",
  "created": "2024-03-25T16:00:00Z",
  "data": {
    "bilan_id": "bilan_001",
    "stagiaire_id": "stag_789",
    "type": "intermediaire",
    "evaluateur_id": "eval_123",
    "synthese": {
      "progression_generale": 75,
      "competences_validees": 8,
      "competences_totales": 12
    },
    "rapport_url": "/api/v2/bilans/bilan_001/rapport"
  }
}
```

#### bilan.signed
Bilan signed by parties

### Financial Events

#### paiement.received
Payment received

```json
{
  "id": "evt_123460",
  "type": "paiement.received",
  "created": "2024-03-25T14:00:00Z",
  "data": {
    "paiement_id": "pay_789",
    "stagiaire_id": "stag_123",
    "formation_id": "form_456",
    "montant": 2000,
    "devise": "EUR",
    "source": "CPF",
    "reference": "CPF-2024-123456"
  }
}
```

#### paiement.failed
Payment failed

#### financement.approved
Financing approved

#### financement.rejected
Financing rejected

### Document Events

#### document.uploaded
New document uploaded

#### document.signed
Document signed

```json
{
  "id": "evt_123461",
  "type": "document.signed",
  "created": "2024-03-25T15:00:00Z",
  "data": {
    "document_id": "doc_789",
    "type": "contrat_formation",
    "signer": {
      "type": "stagiaire",
      "id": "stag_123",
      "nom": "Dupont",
      "prenom": "Marie"
    },
    "signature_method": "electronic",
    "ip_address": "192.168.1.1",
    "timestamp": "2024-03-25T15:00:00Z"
  }
}
```

## Webhook Security

### Signature Verification

All webhook requests include a signature in the `X-Wedof-Signature` header. Verify this signature to ensure the webhook is from Wedof.

#### PHP Example
```php
function verifyWebhookSignature($payload, $signature, $secret) {
    $expected = hash_hmac('sha256', $payload, $secret);
    return hash_equals($expected, $signature);
}

$payload = file_get_contents('php://input');
$signature = $_SERVER['HTTP_X_WEDOF_SIGNATURE'];
$secret = 'whsec_your_webhook_secret';

if (!verifyWebhookSignature($payload, $signature, $secret)) {
    http_response_code(401);
    exit('Unauthorized');
}
```

#### Node.js Example
```javascript
const crypto = require('crypto');

function verifyWebhookSignature(payload, signature, secret) {
    const expected = crypto
        .createHmac('sha256', secret)
        .update(payload)
        .digest('hex');
    
    return crypto.timingSafeEqual(
        Buffer.from(signature),
        Buffer.from(expected)
    );
}

app.post('/webhooks/wedof', (req, res) => {
    const signature = req.headers['x-wedof-signature'];
    const secret = process.env.WEDOF_WEBHOOK_SECRET;
    
    if (!verifyWebhookSignature(req.rawBody, signature, secret)) {
        return res.status(401).send('Unauthorized');
    }
    
    // Process webhook
    const event = req.body;
    console.log('Received event:', event.type);
    
    res.status(200).send('OK');
});
```

#### Python Example
```python
import hmac
import hashlib

def verify_webhook_signature(payload, signature, secret):
    expected = hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected)

@app.route('/webhooks/wedof', methods=['POST'])
def handle_webhook():
    signature = request.headers.get('X-Wedof-Signature')
    secret = os.environ.get('WEDOF_WEBHOOK_SECRET')
    
    if not verify_webhook_signature(request.data, signature, secret):
        return 'Unauthorized', 401
    
    event = request.json
    print(f"Received event: {event['type']}")
    
    return 'OK', 200
```

## Webhook Payload Structure

All webhook payloads follow this structure:

```json
{
  "id": "evt_unique_id",
  "type": "event.type",
  "created": "2024-03-25T10:00:00Z",
  "api_version": "v2",
  "data": {
    // Event-specific data
  },
  "previous_attributes": {
    // For update events, contains previous values
  }
}
```

## Best Practices

1. **Respond Quickly**: Return a 2xx status code as soon as possible
2. **Process Asynchronously**: Queue events for processing don't block the response
3. **Verify Signatures**: Always verify webhook signatures
4. **Handle Retries**: Be prepared to receive the same event multiple times
5. **Use HTTPS**: Only use HTTPS endpoints for webhooks
6. **Monitor Failures**: Set up alerting for webhook failures

## Retry Policy

Wedof will retry failed webhook deliveries with exponential backoff:

- 1st retry: 10 seconds
- 2nd retry: 1 minute  
- 3rd retry: 10 minutes
- 4th retry: 1 hour
- 5th retry: 6 hours

After 5 failed attempts, the webhook will be marked as failed and you'll be notified by email.

## Testing Webhooks

### Using Webhook Test Tool
```bash
curl -X POST https://api.wedof.fr/v2/webhooks/webhook_123/test \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "stagiaire.created"
  }'
```

### Local Development with ngrok
For local development, use ngrok to expose your local server:

```bash
ngrok http 3000
```

Then register the ngrok URL as your webhook endpoint.

## Webhook Logs

View webhook delivery attempts and responses:

```http
GET /api/v2/webhooks/{id}/logs
```

Response includes delivery attempts, response codes, and response times for debugging.
