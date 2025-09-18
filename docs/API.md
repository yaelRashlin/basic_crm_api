# API Documentation

## Base URL
```
http://localhost:5000
```

## Authentication
No authentication required for this demo API.

## Content Type
All requests and responses use `application/json`.

## Endpoints

### 1. Home / Server Info
Get basic server information and available endpoints.

**Endpoint:** `GET /`

**Response:**
```json
{
  "message": "Welcome to User Management Flask Server",
  "total_users": 0,
  "endpoints": {
    "GET /": "This endpoint",
    "POST /users": "Create new user",
    "GET /users/<id>": "Get user by Israeli ID",
    "GET /users": "List all user IDs",
    "GET /health": "Health check"
  },
  "timestamp": "2024-01-01T12:00:00.000000"
}
```

### 2. Create User
Create a new user with Israeli ID validation.

**Endpoint:** `POST /users`

**Request Body:**
```json
{
  "id": "123456782",
  "name": "John Doe",
  "phone": "+972501234567",
  "address": "123 Main St, Tel Aviv, Israel"
}
```

**Success Response (201):**
```json
{
  "message": "User created successfully",
  "user": {
    "id": "123456782",
    "name": "John Doe",
    "phone": "+972501234567",
    "address": "123 Main St, Tel Aviv, Israel",
    "created_at": "2024-01-01T12:00:00.000000",
    "updated_at": "2024-01-01T12:00:00.000000"
  },
  "timestamp": "2024-01-01T12:00:00.000000"
}
```

**Validation Error Response (400):**
```json
{
  "error": "Validation failed",
  "details": {
    "id": "Invalid Israeli ID checksum",
    "phone": "Phone number must start with +"
  }
}
```

**User Already Exists (409):**
```json
{
  "error": "User already exists",
  "user_id": "123456782"
}
```

### 3. Get User by ID
Retrieve a specific user by their Israeli ID.

**Endpoint:** `GET /users/{id}`

**Path Parameters:**
- `id` (string): 9-digit Israeli ID

**Success Response (200):**
```json
{
  "message": "User retrieved successfully",
  "user": {
    "id": "123456782",
    "name": "John Doe",
    "phone": "+972501234567",
    "address": "123 Main St, Tel Aviv, Israel",
    "created_at": "2024-01-01T12:00:00.000000",
    "updated_at": "2024-01-01T12:00:00.000000"
  },
  "timestamp": "2024-01-01T12:00:00.000000"
}
```

**User Not Found (404):**
```json
{
  "error": "User not found",
  "user_id": "123456782"
}
```

**Invalid ID Format (400):**
```json
{
  "error": "Invalid Israeli ID format",
  "message": "Israeli ID must be exactly 9 digits",
  "user_id": "12345"
}
```

### 4. List All Users
Get a list of all user IDs in the system.

**Endpoint:** `GET /users`

**Success Response (200):**
```json
{
  "message": "Users listed successfully",
  "users": ["123456782", "987654321"],
  "count": 2,
  "timestamp": "2024-01-01T12:00:00.000000"
}
```

### 5. Health Check
Check the health status of the server and database.

**Endpoint:** `GET /health`

**Success Response (200):**
```json
{
  "message": "Service is healthy",
  "status": "healthy",
  "users_count": 2,
  "version": "1.0.0",
  "server_type": "Class-based Flask Server with Database",
  "database": {
    "status": "healthy",
    "user_count": 2,
    "database_url": "sqlite:///users.db"
  },
  "timestamp": "2024-01-01T12:00:00.000000"
}
```

## Data Validation Rules

### Israeli ID
- Must be exactly 9 digits
- Must pass official Israeli ID checksum validation
- Required field

### Name
- Must be a non-empty string
- Maximum 100 characters
- Required field

### Phone Number
- Must follow E.164 international format
- Must start with `+`
- Must be 8-16 characters total (including `+`)
- Must contain only digits after `+`
- Required field

### Address
- Must be a non-empty string
- Maximum 200 characters
- Required field

## Error Responses

All error responses follow this format:

```json
{
  "error": "Error Type",
  "message": "Detailed error message",
  "details": {
    "field": "Field-specific error"
  }
}
```

### Common HTTP Status Codes

- `200 OK` - Successful GET request
- `201 Created` - Successful POST request
- `400 Bad Request` - Validation error or malformed request
- `404 Not Found` - Resource not found
- `405 Method Not Allowed` - HTTP method not supported
- `409 Conflict` - Resource already exists
- `500 Internal Server Error` - Server error

## Example Usage

### Create a User
```bash
curl -X POST http://localhost:5000/users \
  -H "Content-Type: application/json" \
  -d '{
    "id": "123456782",
    "name": "John Doe",
    "phone": "+972501234567",
    "address": "123 Main St, Tel Aviv, Israel"
  }'
```

### Get a User
```bash
curl http://localhost:5000/users/123456782
```

### List All Users
```bash
curl http://localhost:5000/users
```

### Health Check
```bash
curl http://localhost:5000/health
```

## Rate Limiting
No rate limiting is currently implemented.

## Versioning
API version 1.0.0 - No versioning scheme implemented yet.