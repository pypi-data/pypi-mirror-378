# stdresponse

A lightweight Python package to standardize API responses across Flask, FastAPI, and other Python web frameworks. Create consistent, well-structured API responses with minimal boilerplate code.

## Features

- 🚀 **Framework Agnostic** - Works with Flask, FastAPI, Django, and any Python web framework
- 📦 **Lightweight** - Zero dependencies beyond Python standard library
- 🎯 **Consistent Structure** - Standardized response format for success and error cases
- 🔍 **Request Tracking** - Automatic request ID generation for better debugging
- ⏰ **Timestamps** - ISO 8601 timestamps for all responses
- 🛠️ **Flexible Metadata** - Custom metadata support for additional context

## Installation

```bash
pip install stdresponse
```

## Quick Start

```python
from stdresponse import StandardResponse

# Success response
response = StandardResponse.success(
    data={"user_id": 123, "username": "johndoe"},
    message="User retrieved successfully"
)

# Error response
response = StandardResponse.error(
    message="User not found",
    status_code=404,
    error_type="NOT_FOUND"
)
```

## Response Format

### Success Response Structure
```json
{
  "success": true,
  "status_code": 200,
  "message": "Request successful.",
  "data": { ... },
  "error": null,
  "meta": {
    "timestamp": "2024-01-15T10:30:45.123456Z",
    "requestId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
  }
}
```

### Error Response Structure
```json
{
  "success": false,
  "status_code": 400,
  "message": "An error occurred.",
  "data": null,
  "error": {
    "type": "GENERAL_ERROR",
    "details": []
  },
  "meta": {
    "timestamp": "2024-01-15T10:30:45.123456Z",
    "requestId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
  }
}
```

## Basic Usage

### Success Responses

```python
from stdresponse import StandardResponse

# Simple success response
response = StandardResponse.success()

# Success with data
response = StandardResponse.success(
    data={"items": [1, 2, 3], "total": 3},
    message="Items retrieved successfully"
)

# Success with custom status code
response = StandardResponse.success(
    data={"user_id": 456},
    message="User created successfully",
    status_code=201
)

# Success with custom request ID and metadata
response = StandardResponse.success(
    data={"result": "processed"},
    request_id="custom-request-123",
    meta={"version": "v1.0", "source": "api"}
)
```

### Error Responses

```python
from stdresponse import StandardResponse

# Simple error response
response = StandardResponse.error()

# Error with details
response = StandardResponse.error(
    message="Validation failed",
    status_code=422,
    error_type="VALIDATION_ERROR",
    error_details=[
        {"field": "email", "message": "Invalid email format"},
        {"field": "password", "message": "Password too short"}
    ]
)

# Error with custom metadata
response = StandardResponse.error(
    message="Database connection failed",
    status_code=503,
    error_type="DATABASE_ERROR",
    meta={"retry_after": "30", "service": "postgres"}
)
```

## Framework Integration

### Flask Example

```python
from flask import Flask, jsonify, request
from stdresponse import StandardResponse

app = Flask(__name__)

@app.route('/users/<int:user_id>')
def get_user(user_id):
    try:
        # Your business logic here
        user_data = {"id": user_id, "name": "John Doe"}
        
        response = StandardResponse.success(
            data=user_data,
            message="User retrieved successfully",
            request_id=request.headers.get('X-Request-ID')
        )
        return jsonify(response), response['status_code']
        
    except Exception as e:
        response = StandardResponse.error(
            message="Failed to retrieve user",
            status_code=500,
            error_type="INTERNAL_ERROR"
        )
        return jsonify(response), response['status_code']
```

### FastAPI Example

```python
from fastapi import FastAPI, HTTPException, Request
from stdresponse import StandardResponse

app = FastAPI()

@app.get("/users/{user_id}")
async def get_user(user_id: int, request: Request):
    try:
        # Your business logic here
        user_data = {"id": user_id, "name": "John Doe"}
        
        return StandardResponse.success(
            data=user_data,
            message="User retrieved successfully",
            request_id=request.headers.get('x-request-id')
        )
        
    except Exception as e:
        return StandardResponse.error(
            message="Failed to retrieve user",
            status_code=500,
            error_type="INTERNAL_ERROR"
        )
```

### Django REST Framework Example

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from stdresponse import StandardResponse

class UserView(APIView):
    def get(self, request, user_id):
        try:
            # Your business logic here
            user_data = {"id": user_id, "name": "John Doe"}
            
            response_data = StandardResponse.success(
                data=user_data,
                message="User retrieved successfully",
                request_id=request.META.get('HTTP_X_REQUEST_ID')
            )
            return Response(response_data, status=response_data['status_code'])
            
        except Exception as e:
            response_data = StandardResponse.error(
                message="Failed to retrieve user",
                status_code=500,
                error_type="INTERNAL_ERROR"
            )
            return Response(response_data, status=response_data['status_code'])
```

## API Reference

### `StandardResponse.success()`

Creates a successful response object.

**Parameters:**
- `data` (Any, optional): The response data. Default: `None`
- `message` (str, optional): Success message. Default: `"Request successful."`
- `status_code` (int, optional): HTTP status code. Default: `200`
- `request_id` (str, optional): Custom request ID. If not provided, generates UUID4
- `meta` (Dict[str, str], optional): Additional metadata

**Returns:** `Dict[str, Any]` - Formatted success response

### `StandardResponse.error()`

Creates an error response object.

**Parameters:**
- `message` (str, optional): Error message. Default: `"An error occurred."`
- `status_code` (int, optional): HTTP status code. Default: `400`
- `error_type` (str, optional): Type of error. Default: `"GENERAL_ERROR"`
- `error_details` (List[Dict[str, str]], optional): Detailed error information
- `request_id` (str, optional): Custom request ID. If not provided, generates UUID4
- `meta` (Dict[str, str], optional): Additional metadata

**Returns:** `Dict[str, Any]` - Formatted error response

## Best Practices

1. **Use meaningful error types**: Instead of generic errors, use specific types like `VALIDATION_ERROR`, `NOT_FOUND`, `UNAUTHORIZED`

2. **Provide helpful error details**: Include field-level validation errors when applicable

3. **Leverage request IDs**: Pass request IDs from headers for better request tracing

4. **Add relevant metadata**: Include API version, rate limit info, or other contextual data

5. **Consistent status codes**: Use appropriate HTTP status codes that match your error types

## Example: Complete CRUD API

```python
from flask import Flask, jsonify, request
from stdresponse import StandardResponse

app = Flask(__name__)

# Mock database
users = {1: {"id": 1, "name": "John", "email": "john@example.com"}}

@app.route('/users', methods=['GET'])
def list_users():
    response = StandardResponse.success(
        data={"users": list(users.values()), "total": len(users)},
        message="Users retrieved successfully"
    )
    return jsonify(response), response['status_code']

@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    
    if not data or 'name' not in data:
        response = StandardResponse.error(
            message="Invalid input data",
            status_code=422,
            error_type="VALIDATION_ERROR",
            error_details=[{"field": "name", "message": "Name is required"}]
        )
        return jsonify(response), response['status_code']
    
    user_id = max(users.keys()) + 1 if users else 1
    new_user = {"id": user_id, "name": data['name'], "email": data.get('email')}
    users[user_id] = new_user
    
    response = StandardResponse.success(
        data=new_user,
        message="User created successfully",
        status_code=201
    )
    return jsonify(response), response['status_code']

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    if user_id not in users:
        response = StandardResponse.error(
            message="User not found",
            status_code=404,
            error_type="NOT_FOUND"
        )
        return jsonify(response), response['status_code']
    
    response = StandardResponse.success(
        data=users[user_id],
        message="User retrieved successfully"
    )
    return jsonify(response), response['status_code']
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Changelog

### v1.0.1.1
- Initial release
- Basic success and error response methods
- Automatic timestamp and request ID generation
- Framework-agnostic design