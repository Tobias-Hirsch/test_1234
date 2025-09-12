# `routers/authentication.py` - Authentication Routes

This document describes the `backend/app/routers/authentication.py` file, which defines API routes related to user authentication.

## Function Description
*   **User Registration**: Provides an interface for users to register new accounts.
*   **User Login**: Provides an interface for users to log in with username/email and password, and returns a JWT access token.
*   **Token Refresh**: May include an interface for refreshing access tokens.
*   **Password Reset**: Provides interfaces for requesting password reset and actually resetting the password.
*   **Account Activation**: Provides an interface for activating user accounts via an email link.
*   **OAuth Authentication**: May integrate third-party OAuth authentication flows (e.g., Google, GitHub).

## Logic Implementation
1.  **Dependency Injection**: Route functions typically use FastAPI's `Depends` to inject dependencies such as database sessions (`get_db`) and the current user (`get_current_user`).
2.  **User Registration**: Receives user registration information, hashes the password, stores user data in the database, and sends an account activation email.
    *   `@router.post("/register")`
3.  **User Login**: Validates user credentials, and if valid, generates and returns a JWT access token.
    *   `@router.post("/login")`
4.  **Password Reset**:
    *   Request Reset: Receives user email, generates a reset token, and sends an email containing the reset link.
        *   `@router.post("/forgot-password")`
    *   Execute Reset: Receives the reset token and new password, validates the token, and updates the user's password.
        *   `@router.post("/reset-password")`
5.  **Account Activation**: Receives the activation token, validates the token, and activates the user account.
    *   `@router.get("/activate/{token}")`
6.  **Current User**: Provides a protected route for retrieving information about the currently authenticated user.
    *   `@router.get("/users/me")`

## Path
`/backend/app/routers/authentication.py`