# API Documentation

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, authentication is not implemented but will be added in future versions.

## Endpoints

### Jobs

#### Get All Jobs
```http
GET /api/jobs
```

Query Parameters:
- `status`: Filter by status (new, approved, rejected, applied)
- `source`: Filter by source (greenhouse, lever, ashby)
- `limit`: Maximum number of results (default: 50)
- `offset`: Pagination offset (default: 0)

#### Get Job by ID
```http
GET /api/jobs/{job_id}
```

#### Approve Job
```http
POST /api/jobs/{job_id}/approve
```

#### Reject Job
```http
POST /api/jobs/{job_id}/reject
```

#### Fetch Jobs
```http
POST /api/jobs/fetch
```

Body:
```json
{
  "sources": ["greenhouse", "lever", "ashby"],
  "force_refresh": false
}
```

### Applications

#### Get All Applications
```http
GET /api/applications
```

#### Get Application by ID
```http
GET /api/applications/{application_id}
```

#### Create Application
```http
POST /api/applications
```

Body:
```json
{
  "job_id": "string",
  "resume_version": "string",
  "notes": "string"
}
```

#### Update Application Status
```http
PUT /api/applications/{application_id}/status
```

Body:
```json
{
  "stage": "applied",
  "next_action": "Follow up in 5 days",
  "follow_up_due": "2024-01-15"
}
```

### Outreach

#### Get Contacts for Company
```http
GET /api/outreach/contacts/{company}
```

#### Generate Outreach Draft
```http
POST /api/outreach/generate
```

Body:
```json
{
  "application_id": "string",
  "contact_id": "string",
  "contact_type": "recruiter"
}
```

#### Mark Outreach Sent
```http
POST /api/outreach/{outreach_id}/send
```

### Tracker

#### Sync Tracker
```http
POST /api/tracker/sync
```

#### Get Tracker Data
```http
GET /api/tracker
```

### Profile

#### Get Profile
```http
GET /api/profile
```

#### Update Profile
```http
PUT /api/profile
```

Body:
```json
{
  "full_name": "string",
  "email": "string",
  "phone": "string",
  "linkedin": "string",
  "github": "string"
}
```

## Error Responses

All endpoints may return error responses in the following format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {}
  }
}
```

Common error codes:
- `VALIDATION_ERROR`: Invalid request data
- `NOT_FOUND`: Resource not found
- `INTERNAL_ERROR`: Server error
- `EXTERNAL_API_ERROR`: Error calling external API