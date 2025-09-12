# `services/auth.py` - Authentication Service

This document describes the `backend/app/services/auth.py` file, which contains the core business logic related to user authentication and authorization.

## Function Description
*   **User Authentication**: Validates user-provided credentials (username/email and password).
*   **JWT Token Management**: Generates, validates, and refreshes JWT access tokens.
*   **Current User Retrieval**: Provides functionality to retrieve the currently authenticated user.
*   **Permission Validation**: Assists in performing user permission checks.

## Logic Implementation
1.  **`authenticate_user(db: Session, username: str, password: str)`**:
    *   Finds the user in the database by username or email.
    *   Validates the user's password using `security.verify_password`.
    *   If credentials are valid, returns the user object.
2.  **`create_access_token(data: dict, expires_delta: Optional[timedelta] = None)`**:
    *   Calls `security.create_access_token` to generate a JWT access token.
3.  **`get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db))`**:
    *   Retrieves the JWT token from the request header using the OAuth2 scheme.
    *   Calls `security.decode_access_token` to decode the token and get the user ID.
    *   Retrieves the user object from the database.
    *   Raises `HTTPException` if the token is invalid or the user does not exist.
4.  **`get_current_active_user(current_user: User = Depends(get_current_user))`**:
    *   Further checks if the user is active, building upon `get_current_user`.
5.  **`get_current_active_superuser(current_user: User = Depends(get_current_active_user))`**:
    *   Further checks if the user is a superuser, building upon `get_current_active_user`.

## Path
`/backend/app/services/auth.py`