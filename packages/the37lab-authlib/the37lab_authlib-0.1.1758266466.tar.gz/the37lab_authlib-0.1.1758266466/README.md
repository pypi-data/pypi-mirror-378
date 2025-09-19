# AuthLib

A Python authentication library that provides JWT, OAuth2, and API token authentication with PostgreSQL backend. This library is designed for seamless integration with Flask applications and provides a robust set of endpoints and utilities for user management, authentication, and API token handling.

## Table of Contents
- [AuthLib](#authlib)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [Quick Start](#quick-start)
  - [Configuration](#configuration)
    - [Required Parameters](#required-parameters)
    - [Optional Parameters](#optional-parameters)
      - [Example `oauth_config`:](#example-oauth_config)
  - [API Endpoints](#api-endpoints)
    - [Authentication](#authentication)
    - [User Management](#user-management)
    - [API Tokens](#api-tokens)
  - [Authentication Flow](#authentication-flow)
  - [User Object](#user-object)
  - [Token Management](#token-management)
  - [Development](#development)
    - [Setup](#setup)
    - [Database Setup](#database-setup)
    - [Running Tests](#running-tests)
  - [API Token Override for Testing](#api-token-override-for-testing)
    - [Usage](#usage)
    - [Warning](#warning)
  - [User Override for Testing](#user-override-for-testing)
    - [Usage](#usage-1)
    - [Warning](#warning-1)

## Installation

```bash
pip install -e .
```

## Quick Start

```python
from flask import Flask
from authlib import AuthManager

app = Flask(__name__)

# Option 1: Explicit configuration
auth = AuthManager(
    app=app,
    db_dsn="postgresql://user:pass@localhost/dbname",
    jwt_secret="your-secret-key",
    oauth_config={
        "google": {
            "client_id": "your-client-id",
            "client_secret": "your-client-secret"
        }
    }
)

# Option 2: Use environment variables with a prefix (e.g., AMPA_)
# This will load:
#   AMPA_DATABASE_URL, AMPA_JWT_SECRET, AMPA_GOOGLE_CLIENT_ID, AMPA_GOOGLE_CLIENT_SECRET
# auth = AuthManager(app=app, environment_prefix="AMPA")

@app.route("/protected")
@auth.require_auth(roles=["admin"])
def protected_route():
    return "Protected content"

@app.route("/public")
@auth.public_endpoint
def custom_public_route():
    return "Public content"
```

`AuthManager`'s blueprint now registers a global error handler for
`AuthError` and authenticates requests for all of its routes by default.
Authenticated users are made available as `flask.g.requesting_user`.
Only the login, OAuth, token refresh, registration and role listing
endpoints are exempt from this check. Additional routes can be marked as
public using the `@auth.public_endpoint` decorator or
`auth.add_public_endpoint("auth.some_endpoint")`.

## Configuration

### Required Parameters
- `app`: Flask application instance
- `db_dsn`: PostgreSQL connection string
- `jwt_secret`: Secret key for JWT signing

### Optional Parameters
- `oauth_config`: Dictionary of OAuth provider configurations (see below)
- `token_expiry`: JWT token expiry time in seconds (default: 3600)
- `refresh_token_expiry`: Refresh token expiry time in seconds (default: 2592000)
- `environment_prefix`: If set, loads all configuration from environment variables with this prefix (e.g., `AMPA_DATABASE_URL`, `AMPA_JWT_SECRET`, `AMPA_GOOGLE_CLIENT_ID`, `AMPA_GOOGLE_CLIENT_SECRET`). Overrides other config if set.

#### Example `oauth_config`:
```python
{
    "google": {
        "client_id": "...",
        "client_secret": "..."
    },
    "github": {
        "client_id": "...",
        "client_secret": "..."
    }
}
```

## API Endpoints

### Authentication
- `POST /api/v1/users/login` - Login with username/password
  - **Request:** `{ "username": "string", "password": "string" }`
  - **Response:** `{ "token": "jwt", "refresh_token": "jwt", "user": { ... } }`
- `POST /api/v1/users/login/oauth` - Get OAuth redirect URL
  - **Request:** `{ "provider": "google|github|..." }`
  - **Response:** `{ "redirect_url": "string" }`
- `GET /api/v1/users/login/oauth2callback` - OAuth callback
  - **Query Params:** `code`, `state`, `provider`
  - **Response:** `{ "token": "jwt", "refresh_token": "jwt", "user": { ... } }`
- `POST /api/v1/users/token-refresh` - Refresh JWT token
  - **Request:** `{ "refresh_token": "jwt" }`
  - **Response:** `{ "token": "jwt", "refresh_token": "jwt" }`

### User Management
- `POST /api/v1/users/register` - Register new user
  - **Request:** `{ "username": "string", "password": "string", "email": "string", ... }`
  - **Response:** `{ "user": { ... }, "token": "jwt", "refresh_token": "jwt" }`
- `GET /api/v1/users/login/profile` - Get user profile
  - **Auth:** Bearer JWT
  - **Response:** `{ "user": { ... } }`
- `GET /api/v1/users/roles` - Get available roles
  - **Response:** `[ "admin", "user", ... ]`

### API Tokens
- `POST /api/v1/users/{user}/api-tokens` - Create API token
  - **Request:** `{ "name": "string", "scopes": [ ... ] }`
  - **Response:** `{ "token": "string", "id": "uuid", ... }`
- `GET /api/v1/users/{user}/api-tokens` - List API tokens
  - **Response:** `[ { "id": "uuid", "name": "string", ... } ]`
- `DELETE /api/v1/users/{user}/api-tokens/{token_id}` - Delete API token
  - **Response:** `{ "success": true }`

## Authentication Flow

1. **Login:**
   - User submits credentials to `/api/v1/users/login`.
   - Receives JWT and refresh token.
2. **Token Refresh:**
   - Use `/api/v1/users/token-refresh` with refresh token to get new JWT.
3. **OAuth:**
   - Get redirect URL from `/api/v1/users/login/oauth`.
   - Complete OAuth flow via `/api/v1/users/login/oauth2callback`.
4. **Protected Routes:**
   - All routes inside the provided blueprint are authenticated by default.
     The authenticated user can be accessed via `g.requesting_user`.
     Use `@auth.require_auth()` to protect custom routes in your application.

## User Object

The user object returned by the API typically includes:
```json
{
  "id": "uuid",
  "username": "string",
  "email": "string",
  "roles": ["user", "admin"],
  "created_at": "timestamp",
  "last_login": "timestamp"
}
```

## Token Management
- **JWT:** Used for authenticating API requests. Include in `Authorization: Bearer <token>` header.
- **Refresh Token:** Used to obtain new JWTs without re-authenticating.
- **API Tokens:** Long-lived tokens for programmatic access, managed per user.

## Development

### Setup
1. Clone the repository
2. Create virtual environment:
```bash
python -m venv venv
venv\Scripts\activate
```
3. Install dependencies:
```bash
pip install -e ".[dev]"
```

### Database Setup
```bash
createdb authlib
python -m authlib.cli db init
```

### Running Tests
```bash
pytest
```

## API Token Override for Testing

For testing purposes, you can bypass the database and provide a static mapping of API tokens to usernames using the `api_tokens` argument to `AuthManager` or the `{PREFIX}API_TOKENS` environment variable.

### Usage

- **Constructor argument:**
  ```python
  AuthManager(api_tokens={"token1": "user1", "token2": "user2"})
  ```
- **Environment variable:**
  Set `{PREFIX}API_TOKENS` to a comma-separated list of `token:username` pairs, e.g.:
  ```
  export MYAPP_API_TOKENS="token1:user1,token2:user2"
  ```
  Replace `MYAPP` with your environment prefix.

**Warning:** This method is intended only for testing and development. Do not use this approach in production environments.

## User Override for Testing

For testing purposes, you can force all authentication to return a specific user by setting the `{PREFIX}USER_OVERRIDE` environment variable:

```bash
export MYAPP_USER_OVERRIDE="testuser"
```

If set, all requests will be authenticated as the specified user, regardless of any tokens or credentials provided. This cannot be combined with `api_tokens` or `db_dsn`.

**Warning:** This method is intended only for testing and development. Do not use this approach in production environments.
