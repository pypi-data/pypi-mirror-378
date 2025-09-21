# Vizly Enterprise API Documentation

## Overview

The Vizly Enterprise API provides comprehensive access to commercial visualization capabilities including GPU-accelerated chart creation, VR/AR visualization, real-time streaming, user management, and enterprise security features.

## Authentication

The API uses JWT-based authentication. Obtain a token by posting credentials to `/api/auth/login`:

```bash
curl -X POST http://localhost:8888/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "your-username", "password": "your-password"}'
```

Include the token in subsequent requests:

```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  http://localhost:8888/api/charts
```

## Quick Start

### Python SDK

```python
from vizly.enterprise.api import VizlyEnterpriseClient

# Initialize client
client = VizlyEnterpriseClient(
    base_url="http://localhost:8888",
    username="admin@company.com",
    password="your-password"
)

# Create executive dashboard
response = client.create_chart(
    chart_type="executive_dashboard",
    title="Q4 Performance Dashboard",
    data={
        "kpis": {
            "Revenue": {"value": 1200000, "target": 1000000, "status": "good"},
            "Profit": {"value": 180000, "target": 150000, "status": "good"}
        }
    },
    security_level="confidential",
    compliance_tags=["SOX", "Executive Reporting"]
)

print(f"Chart created: {response.data['id']}")
```

### JavaScript/Node.js

```javascript
const axios = require('axios');

class VizlyClient {
    constructor(baseUrl, token) {
        this.baseUrl = baseUrl;
        this.headers = { 'Authorization': `Bearer ${token}` };
    }

    async createChart(chartData) {
        const response = await axios.post(
            `${this.baseUrl}/api/charts`,
            chartData,
            { headers: this.headers }
        );
        return response.data;
    }
}

// Usage
const client = new VizlyClient('http://localhost:8888', 'your-jwt-token');
const chart = await client.createChart({
    type: 'executive_dashboard',
    title: 'Sales Dashboard',
    security_level: 'internal'
});
```

## API Endpoints


### System

#### `GET /health`

Check server health and service status

**Response:**
```json
{
  "type": "object",
  "properties": {
    "status": {
      "type": "string"
    },
    "timestamp": {
      "type": "number"
    },
    "version": {
      "type": "string"
    },
    "services": {
      "type": "object"
    }
  }
}
```

**Example:**
```bash
curl \
  /health
```

#### `GET /metrics`

Get system performance metrics

**Response:**
```json
{
  "type": "object",
  "properties": {
    "cpu_usage": {
      "type": "number"
    },
    "memory_usage": {
      "type": "number"
    },
    "active_sessions": {
      "type": "integer"
    },
    "total_users": {
      "type": "integer"
    }
  }
}
```

**Example:**
```bash
curl \
  /metrics
```


### Authentication

#### `POST /api/auth/login`

Authenticate user and obtain JWT token

**Request Body:**
```json
{
  "type": "object",
  "required": [
    "username",
    "password"
  ],
  "properties": {
    "username": {
      "type": "string"
    },
    "password": {
      "type": "string"
    }
  }
}
```

**Response:**
```json
{
  "type": "object",
  "properties": {
    "token": {
      "type": "string"
    },
    "user_id": {
      "type": "string"
    },
    "roles": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "expires_at": {
      "type": "string"
    }
  }
}
```

**Example:**
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"username": "example_username", "password": "example_password"}' \
  /api/auth/login
```


### Charts

#### `GET /api/charts`

List all accessible charts

**Required Permissions:** read

**Response:**
```json
{
  "type": "object",
  "properties": {
    "charts": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": {
            "type": "string"
          },
          "title": {
            "type": "string"
          },
          "type": {
            "type": "string"
          },
          "created_at": {
            "type": "string"
          }
        }
      }
    }
  }
}
```

**Example:**
```bash
curl \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  /api/charts
```

#### `POST /api/charts`

Create new enterprise chart

**Required Permissions:** write

**Required License:** advanced_charts

**Request Body:**
```json
{
  "type": "object",
  "required": [
    "type",
    "title"
  ],
  "properties": {
    "type": {
      "type": "string",
      "enum": [
        "executive_dashboard",
        "financial_analytics",
        "compliance",
        "risk_analysis"
      ]
    },
    "title": {
      "type": "string"
    },
    "security_level": {
      "type": "string",
      "enum": [
        "public",
        "internal",
        "confidential",
        "restricted"
      ],
      "default": "internal"
    },
    "compliance_tags": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "kpis": {
      "type": "object"
    },
    "metrics": {
      "type": "object"
    }
  }
}
```

**Response:**
```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "string"
    },
    "title": {
      "type": "string"
    },
    "type": {
      "type": "string"
    },
    "security_level": {
      "type": "string"
    },
    "compliance_tags": {
      "type": "array"
    },
    "audit_trail_count": {
      "type": "integer"
    }
  }
}
```

**Example:**
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"type": "executive_dashboard", "title": "example_title", "security_level": "public", "compliance_tags": ["example_item"], "kpis": {"example_key": "example_value"}, "metrics": {"example_key": "example_value"}}' \
  /api/charts
```

#### `GET /api/charts/{chart_id}`

Get chart details by ID

**Required Permissions:** read

**Example:**
```bash
curl \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  /api/charts/123
```


### Users

#### `GET /api/users`

List all users (admin only)

**Required Permissions:** admin

**Response:**
```json
{
  "type": "object",
  "properties": {
    "users": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "username": {
            "type": "string"
          },
          "email": {
            "type": "string"
          },
          "role": {
            "type": "string"
          },
          "department": {
            "type": "string"
          },
          "last_login": {
            "type": "string"
          },
          "is_active": {
            "type": "string"
          }
        }
      }
    }
  }
}
```

**Example:**
```bash
curl \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  /api/users
```

#### `POST /api/users`

Create new user (admin only)

**Required Permissions:** admin

**Request Body:**
```json
{
  "type": "object",
  "required": [
    "username",
    "role"
  ],
  "properties": {
    "username": {
      "type": "string"
    },
    "role": {
      "type": "string",
      "enum": [
        "viewer",
        "analyst",
        "admin",
        "super_admin"
      ]
    }
  }
}
```

**Example:**
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"username": "example_username", "role": "viewer"}' \
  /api/users
```


## Chart Types

### Executive Dashboard
Create KPI dashboards with status indicators and progress tracking.

```python
client.create_chart(
    chart_type="executive_dashboard",
    title="Executive KPI Dashboard",
    data={
        "kpis": {
            "Revenue": {"value": 1500000, "target": 1400000, "status": "good"},
            "Customer Satisfaction": {"value": 87, "target": 90, "status": "warning"},
            "Market Share": {"value": 12.5, "status": "neutral"}
        }
    }
)
```

### Financial Analytics
Waterfall charts and variance analysis for financial reporting.

```python
client.create_chart(
    chart_type="financial_analytics",
    title="Revenue Analysis",
    data={
        "categories": ["Q1", "Q2 Growth", "Q3 Decline", "Q4", "Total"],
        "values": [1000000, 250000, -180000, 320000, 1390000]
    }
)
```

### Compliance Scorecard
Traffic light scorecards for compliance monitoring.

```python
client.create_chart(
    chart_type="compliance",
    title="Compliance Dashboard",
    data={
        "metrics": {
            "Data Protection": {"score": 95, "threshold_good": 90},
            "Security": {"score": 88, "threshold_good": 90},
            "Audit Readiness": {"score": 76, "threshold_good": 90}
        }
    }
)
```

### Risk Analysis
Risk matrices and probability analysis.

```python
client.create_chart(
    chart_type="risk_analysis",
    title="Enterprise Risk Matrix",
    data={
        "risks": [
            {"name": "Cyber Security", "probability": 70, "impact": 85, "category": "Technology"},
            {"name": "Market Volatility", "probability": 60, "impact": 70, "category": "Financial"}
        ]
    }
)
```

## Error Handling

All API responses follow a consistent format:

```json
{
    "success": true,
    "data": {...},
    "error": null,
    "status_code": 200,
    "metadata": {...}
}
```

Common error codes:
- `400` - Bad Request (invalid parameters)
- `401` - Unauthorized (missing or invalid token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found (resource doesn't exist)
- `500` - Internal Server Error

## Rate Limiting

The API implements rate limiting:
- 1000 requests per minute per IP address
- Rate limit headers included in responses
- Exceeded limits return HTTP 429

## Security

- All data transmission encrypted via HTTPS in production
- JWT tokens expire after 8 hours
- Role-based access control (RBAC)
- Data classification and security watermarks
- Comprehensive audit logging

## Support

- **Email**: durai@infinidatum.net
- **Company**: Infinidatum Corporation
- **Documentation**: https://pypi.org/project/vizly/
- **Enterprise Support**: 24/7 professional support with SLA guarantees
- **Commercial Licensing**: Professional and Enterprise editions available
