# Wedof API Authentication

## Overview
Wedof API uses token-based authentication. You need to include your API key in all requests.

## Getting Your API Key

1. Log in to your Wedof account
2. Navigate to **Settings** → **API Access**
3. Generate or copy your API key
4. Store it securely in your environment variables

## Authentication Methods

### Bearer Token (Recommended)
Include your API key in the Authorization header:

```http
Authorization: Bearer YOUR_API_KEY
```

### Example Request
```bash
curl -X GET https://api.wedof.fr/v2/stagiaires \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json"
```

## Security Best Practices

1. **Never commit API keys** to version control
2. **Use environment variables** for key storage
3. **Rotate keys regularly** for security
4. **Implement request signing** for additional security
5. **Use HTTPS only** for all API calls

## Environment Configuration

### Development (.env.development)
```env
WEDOF_API_KEY=your_development_key
WEDOF_API_URL=https://api.wedof.fr/v2/
WEDOF_ORG_ID=your_organization_id
```

### Production (.env.production)
```env
WEDOF_API_KEY=your_production_key
WEDOF_API_URL=https://api.wedof.fr/v2/
WEDOF_ORG_ID=your_organization_id
```

## Error Responses

### 401 Unauthorized
```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid or missing API key"
  }
}
```

### 403 Forbidden
```json
{
  "error": {
    "code": "FORBIDDEN",
    "message": "You don't have permission to access this resource"
  }
}
```

## Rate Limiting

Wedof API implements rate limiting based on your subscription:

- **API Plan**: 10,000 requests/month
- **Essential Plan**: 50,000 requests/month
- **Standard Plan**: 100,000 requests/month

Headers returned with each response:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Requests remaining
- `X-RateLimit-Reset`: When the limit resets (Unix timestamp)

## OAuth 2.0 (Future)
Wedof may implement OAuth 2.0 for more granular permissions in the future.
