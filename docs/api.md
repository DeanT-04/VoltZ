# VoltForge API Documentation

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication
Currently, the API uses API key authentication. Include your API key in the header:
```
X-API-Key: your-api-key-here
```

## Endpoints

### Health Check
```http
GET /health
```
Returns system health status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-08T12:00:00Z",
  "version": "1.0.0"
}
```

### Projects

#### Create Project
```http
POST /projects/
```

**Request Body:**
```json
{
  "name": "Arduino Weather Station",
  "description": "A weather monitoring system using Arduino",
  "requirements": {
    "voltage": "5V",
    "power_consumption": "low",
    "sensors": ["temperature", "humidity"],
    "connectivity": ["wifi"]
  },
  "budget": 50.00,
  "timeline": "2 weeks"
}
```

**Response:**
```json
{
  "id": "proj_123",
  "name": "Arduino Weather Station",
  "status": "active",
  "created_at": "2025-01-08T12:00:00Z",
  "components": [],
  "estimated_cost": 0.00
}
```

#### Get Project
```http
GET /projects/{project_id}
```

#### Update Project
```http
PUT /projects/{project_id}
```

#### Delete Project
```http
DELETE /projects/{project_id}
```

#### List Projects
```http
GET /projects/
```

**Query Parameters:**
- `limit` (int): Number of results (default: 20)
- `offset` (int): Pagination offset (default: 0)
- `status` (str): Filter by status

### Component Search

#### Search Components
```http
POST /search/components
```

**Request Body:**
```json
{
  "query": "ESP32 microcontroller with WiFi",
  "filters": {
    "category": ["microcontroller"],
    "manufacturer": ["Espressif"],
    "voltage_range": [3.0, 3.6]
  },
  "limit": 10
}
```

**Response:**
```json
{
  "results": [
    {
      "mpn": "ESP32-WROOM-32",
      "manufacturer": "Espressif",
      "description": "WiFi & Bluetooth microcontroller module",
      "category": "microcontroller",
      "specifications": {
        "voltage": "3.3V",
        "frequency": "240MHz",
        "flash": "4MB"
      },
      "similarity_score": 0.95,
      "datasheet_url": "https://example.com/datasheet.pdf"
    }
  ],
  "total": 1,
  "query_time_ms": 45
}
```

### Jobs

#### Create Job
```http
POST /jobs/
```

**Request Body:**
```json
{
  "type": "datasheet_ingestion",
  "parameters": {
    "file_path": "/path/to/datasheet.pdf",
    "mpn": "ESP32-WROOM-32"
  }
}
```

#### Get Job Status
```http
GET /jobs/{job_id}
```

**Response:**
```json
{
  "id": "job_456",
  "type": "datasheet_ingestion",
  "status": "completed",
  "progress": 100,
  "created_at": "2025-01-08T12:00:00Z",
  "completed_at": "2025-01-08T12:05:00Z",
  "result": {
    "chunks_processed": 25,
    "embeddings_generated": 25
  }
}
```

## Error Responses

### 400 Bad Request
```json
{
  "error": "validation_error",
  "message": "Invalid request parameters",
  "details": {
    "field": "requirements.voltage",
    "issue": "must be a valid voltage specification"
  }
}
```

### 401 Unauthorized
```json
{
  "error": "unauthorized",
  "message": "Invalid or missing API key"
}
```

### 404 Not Found
```json
{
  "error": "not_found",
  "message": "Project not found"
}
```

### 429 Too Many Requests
```json
{
  "error": "rate_limit_exceeded",
  "message": "Too many requests. Please try again later.",
  "retry_after": 60
}
```

### 500 Internal Server Error
```json
{
  "error": "internal_error",
  "message": "An unexpected error occurred"
}
```

## Rate Limits

- **General API**: 100 requests per minute per API key
- **Search Endpoints**: 20 requests per minute per API key
- **Job Creation**: 10 requests per minute per API key

## SDKs and Examples

### Python Example
```python
import requests

# Search for components
response = requests.post(
    "http://localhost:8000/api/v1/search/components",
    headers={"X-API-Key": "your-api-key"},
    json={
        "query": "ESP32 microcontroller",
        "limit": 5
    }
)

results = response.json()
print(f"Found {len(results['results'])} components")
```

### JavaScript Example
```javascript
const response = await fetch('http://localhost:8000/api/v1/search/components', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'your-api-key'
  },
  body: JSON.stringify({
    query: 'ESP32 microcontroller',
    limit: 5
  })
});

const results = await response.json();
console.log(`Found ${results.results.length} components`);
```