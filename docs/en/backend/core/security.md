# `core/security.py` - Core Security Module

This document describes the `backend/app/core/security.py` file, which contains security-related functionalities for the application, such as password hashing, JWT (JSON Web Token) generation, and validation.

## Function Description
*   **Password Hashing**: Provides hashing functions for securely storing user passwords.
*   **JWT Generation**: Used to create access tokens and refresh tokens.
*   **JWT Validation**: Used to validate the authenticity of incoming JWT tokens.
*   **Token Expiration Management**: Handles the expiration time of tokens.

## Logic Implementation
1.  **Password Hashing**: Typically uses the `passlib` library (e.g., `bcrypt` or `PBKDF2`) to salt and hash user passwords, ensuring that even if the database is compromised, passwords are difficult to crack.
    ```python
    from passlib.context import CryptContext

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)
    ```
2.  **JWT Generation**: Uses the `python-jose` library to generate JWTs. It will include information such as user ID, expiration time, and will be signed using the `SECRET_KEY` and `ALGORITHM` defined in the configuration.
    ```python
    from datetime import datetime, timedelta
    from typing import Optional
    from jose import jwt
    from backend.app.core.config import settings

    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    ```
3.  **JWT Validation**: Validates the JWT's signature and expiration time, and decodes its content to retrieve user information.
    ```python
    from jose import JWTError, jwt
    from fastapi import HTTPException, status

    def decode_access_token(token: str) -> dict:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    ```

## Path
`/backend/app/core/security.py`