

docs/api.md
# API Documentation

## Overview

EBUSINESS AI provides a comprehensive API for managing prospect automation, email campaigns, and system monitoring. This document describes the available endpoints, their parameters, and response formats.

## Base URL

```
https://your-app-name.onrender.com
```

## Authentication

The API uses API key authentication. Include your API key in the `Authorization` header:

```
Authorization: Bearer your-api-key
```

## Endpoints

### Health Check

#### GET /health

Check the system health status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-06-17T10:30:00.000Z",
  "version": "1.0.0",
  "services": {
    "database": "connected",
    "scheduler": "running",
    "email_service": "ready"
  }
}
```

### System Statistics

#### GET /api/stats

Get comprehensive system statistics.

**Response:**
```json
{
  "prospects": {
    "total": 150,
    "qualified": 75,
    "contacted": 50,
    "responded": 25,
    "audit_booked": 5
  },
  "emails": {
    "total": 100,
    "opened": 60,
    "clicked": 15,
    "open_rate": 60.0,
    "click_rate": 25.0
  },
  "by_country": {
    "France": 80,
    "Belgique": 30,
    "Suisse": 25,
    "Luxembourg": 10,
    "Canada (Québec)": 5
  },
  "by_sector": {
    "Mode": 45,
    "Électronique": 35,
    "Services": 30,
    "Digital": 25,
    "Retail": 15
  }
}
```

### Prospects Management

#### GET /api/prospects

Get a list of prospects with optional filtering.

**Parameters:**
- `status` (optional): Filter by status (nouveau, qualifié, contacté, répondu, audit_réservé)
- `limit` (optional): Maximum number of prospects to return (default: 50)
- `offset` (optional): Offset for pagination (default: 0)

**Response:**
```json
{
  "prospects": [
    {
      "id": 1,
      "name": "Jean Dupont",
      "company": "Boutique Mode Paris",
      "email": "contact@boutiquemodeparis.com",
      "sector": "Mode",
      "country": "France",
      "website": "https://boutiquemodeparis.com",
      "status": "qualifié",
      "qualification_score": 8.5,
      "date_added": "2025-06-17T10:30:00.000Z",
      "email_sent": false,
      "email_opened": false,
      "email_clicked": false
    }
  ],
  "total": 150,
  "limit": 50,
  "offset": 0
}
```

#### GET /api/prospects/{id}

Get details of a specific prospect.

**Response:**
```json
{
  "id": 1,
  "name": "Jean Dupont",
  "company": "Boutique Mode Paris",
  "email": "contact@boutiquemodeparis.com",
  "sector": "Mode",
  "country": "France",
  "website": "https://boutiquemodeparis.com",
  "phone": "+33 1 23 45 67 89",
  "status": "qualifié",
  "qualification_score": 8.5,
  "problem_detected": ["Conversion faible", "Données inexploitées"],
  "specificity": ["Secteur Mode", "Email professionnel disponible"],
  "date_added": "2025-06-17T10:30:00.000Z",
  "date_contacted": null,
  "date_responded": null,
  "date_audit_booked": null,
  "email_sent": false,
  "email_opened": false,
  "email_clicked": false,
  "source": "google_dorks",
  "raw_data": {
    "dork": "e-commerce mode France",
    "title": "Boutique Mode Paris",
    "snippet": "Boutique de mode française avec les dernières tendances"
  }
}
```

#### POST /api/prospects

Create a new prospect.

**Request Body:**
```json
{
  "name": "Jean Dupont",
  "company": "Boutique Mode Paris",
  "email": "contact@boutiquemodeparis.com",
  "sector": "Mode",
  "country": "France",
  "website": "https://boutiquemodeparis.com",
  "phone": "+33 1 23 45 67 89"
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Jean Dupont",
  "company": "Boutique Mode Paris",
  "email": "contact@boutiquemodeparis.com",
  "sector": "Mode",
  "country": "France",
  "website": "https://boutiquemodeparis.com",
  "phone": "+33 1 23 45 67 89",
  "status": "nouveau",
  "qualification_score": 0.0,
  "date_added": "2025-06-17T10:30:00.000Z",
  "email_sent": false,
  "email_opened": false,
  "email_clicked": false
}
```

#### PUT /api/prospects/{id}

Update a prospect.

**Request Body:**
```json
{
  "status": "qualifié",
  "qualification_score": 8.5,
  "problem_detected": ["Conversion faible"],
  "specificity": ["Secteur Mode"]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Prospect updated successfully"
}
```

#### DELETE /api/prospects/{id}

Delete a prospect.

**Response:**
```json
{
  "success": true,
  "message": "Prospect deleted successfully"
}
```

### Email Campaigns

#### GET /api/campaigns

Get email campaign statistics.

**Parameters:**
- `days` (optional): Number of days to analyze (default: 30)

**Response:**
```json
{
  "total_sent": 100,
  "total_opened": 60,
  "total_clicked": 15,
  "open_rate": 60.0,
  "click_rate": 25.0,
  "period_days": 30,
  "daily_stats": {
    "2025-06-17": {
      "sent": 5,
      "opened": 3,
      "clicked": 1
    },
    "2025-06-16": {
      "sent": 4,
      "opened": 2,
      "clicked": 0
    }
  }
}
```

#### GET /api/campaigns/{prospect_id}

Get email campaign history for a specific prospect.

**Response:**
```json
{
  "campaigns": [
    {
      "id": 1,
      "prospect_id": 1,
      "subject": "Opportunités pour votre boutique",
      "content": "Email content...",
      "sent_at": "2025-06-17T10:30:00.000Z",
      "opened_at": "2025-06-17T11:15:00.000Z",
      "clicked_at": "2025-06-17T11:20:00.000Z",
      "tracking_id": "abc123-def456-ghi789"
    }
  ]
}
```

### Search and Qualification

#### POST /api/search

Trigger a manual search for prospects.

**Request Body:**
```json
{
  "dorks": ["e-commerce mode France", "boutique en ligne France"],
  "max_results_per_dork": 20
}
```

**Response:**
```json
{
  "success": true,
  "prospects_found": 15,
  "prospects_added": 12,
  "message": "Search completed successfully"
}
```

#### POST /api/qualify/{prospect_id}

Qualify a specific prospect.

**Response:**
```json
{
  "success": true,
  "qualified": true,
  "score": 8.5,
  "reasons": ["Secteur cible", "Email professionnel disponible"],
  "detected_problems": ["Conversion faible"],
  "specificities": ["Secteur Mode"]
}
```

#### POST /api/generate-email/{prospect_id}

Generate a personalized email for a prospect.

**Response:**
```json
{
  "success": true,
  "subject": "Opportunités pour votre boutique",
  "content": "Generated email content...",
  "generated_at": "2025-06-17T10:30:00.000Z"
}
```

#### POST /api/send-email/{prospect_id}

Send an email to a prospect.

**Request Body:**
```json
{
  "content": "Email content to send..."
}
```

**Response:**
```json
{
  "success": true,
  "message_id": "abc123-def456-ghi789",
  "sent_at": "2025-06-17T10:30:00.000Z"
}
```

### System Management

#### GET /api/system/logs

Get system logs.

**Parameters:**
- `level` (optional): Filter by log level (DEBUG, INFO, WARNING, ERROR)
- `limit` (optional): Maximum number of logs (default: 100)

**Response:**
```json
{
  "logs": [
    {
      "id": 1,
      "level": "INFO",
      "message": "Search prospects completed: 12 prospects added",
      "module": "search_prospects_task",
      "created_at": "2025-06-17T10:30:00.000Z",
      "extra_data": {
        "dorks_used": 2,
        "prospects_found": 15,
        "prospects_added": 12
      }
    }
  ]
}
```

#### POST /api/system/backup

Trigger a system backup.

**Response:**
```json
{
  "success": true,
  "backup_file": "backup_2025-06-17_103000.sql",
  "created_at": "2025-06-17T10:30:00.000Z"
}
```

#### GET /api/system/config

Get current system configuration.

**Response:**
```json
{
  "config": {
    "target_sectors": ["Mode", "Électronique", "Services", "Digital", "Retail"],
    "target_countries": ["France", "Belgique", "Suisse", "Luxembourg", "Monaco"],
    "email_sending_days": ["tuesday", "wednesday", "thursday", "friday"],
    "email_sending_start": 9,
    "email_sending_end": 17,
    "max_emails_per_day": 50,
    "search_frequency_hours": 2
  }
}
```

### Tracking Endpoints

#### GET /track/open/{tracking_id}

Track email open (used for tracking pixel).

**Response:**
```json
{
  "success": true,
  "message": "Open tracked successfully"
}
```

#### GET /track/click/{tracking_id}

Track email click and redirect to landing page.

**Response:**
Redirects to the landing page URL.

#### GET /unsubscribe/{tracking_id}

Handle unsubscribe requests.

**Response:**
```json
{
  "success": true,
  "message": "Unsubscribed successfully"
}
```

## Error Responses

All endpoints return appropriate HTTP status codes and error messages:

```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Prospect not found",
    "details": "Prospect with ID 999 does not exist"
  }
}
```

### Common Error Codes

- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Missing or invalid API key
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

## Rate Limiting

API requests are rate limited to:
- 100 requests per minute per API key
- 1000 requests per hour per API key

Rate limit headers are included in responses:
- `X-RateLimit-Limit`: Request limit per window
- `X-RateLimit-Remaining`: Remaining requests in current window
- `X-RateLimit-Reset`: Time when the window resets

## Webhooks

The system supports webhooks for real-time notifications:

### Webhook Events

- `prospect.created`: New prospect added
- `prospect.qualified`: Prospect qualified
- `email.sent`: Email sent
- `email.opened`: Email opened
- `email.clicked`: Email clicked
- `audit.booked`: Audit booked

### Webhook Configuration

Webhooks can be configured via the dashboard or API:

```json
{
  "url": "https://your-webhook-url.com/endpoint",
  "events": ["prospect.created", "email.opened"],
  "secret": "your-webhook-secret"
}
```

## Data Export

#### GET /api/export/prospects

Export prospects data.

**Parameters:**
- `format` (optional): Export format (csv, xlsx, json) - default: csv
- `status` (optional): Filter by status
- `date_from` (optional): Export prospects from date
- `date_to` (optional): Export prospects to date

**Response:**
File download in the specified format.

## SDK Integration

### Python SDK Example

```python
import requests
import json

class EBusinessAIClient:
    def __init__(self, api_key, base_url="https://your-app-name.onrender.com"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def get_prospects(self, status=None, limit=50):
        params = {"limit": limit}
        if status:
            params["status"] = status
        
        response = requests.get(
            f"{self.base_url}/api/prospects",
            headers=self.headers,
            params=params
        )
        return response.json()
    
    def create_prospect(self, prospect_data):
        response = requests.post(
            f"{self.base_url}/api/prospects",
            headers=self.headers,
            json=prospect_data
        )
        return response.json()
    
    def send_email(self, prospect_id, content):
        response = requests.post(
            f"{self.base_url}/api/send-email/{prospect_id}",
            headers=self.headers,
            json={"content": content}
        )
        return response.json()

# Usage example
client = EBusinessAIClient("your-api-key")

# Get prospects
prospects = client.get_prospects(status="qualifié")
print(f"Found {len(prospects['prospects'])} qualified prospects")

# Create new prospect
new_prospect = {
    "name": "John Doe",
    "company": "Example Company",
    "email": "john@example.com",
    "sector": "Mode",
    "country": "France"
}
result = client.create_prospect(new_prospect)
print(f"Created prospect with ID: {result['id']}")
```

## Support

For API support and questions:
- Email: ia.ebusinessag@gmail.com
- Documentation: [https://ebusinessag.com/docs](https://ebusinessag.com/docs)
- Issues: [GitHub Issues](https://github.com/your-repo/issues)
