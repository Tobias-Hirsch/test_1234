# `core/security.py` - 核心安全模块

本文档描述了 `backend/app/core/security.py` 文件，该文件包含了应用程序中用于密码哈希、JWT（JSON Web Token）生成和验证等安全相关的功能。

## 功能描述
*   **密码哈希**: 提供用于安全存储用户密码的哈希函数。
*   **JWT 生成**: 用于创建访问令牌和刷新令牌。
*   **JWT 验证**: 用于验证传入的 JWT 令牌的有效性。
*   **令牌过期管理**: 处理令牌的过期时间。

## 逻辑实现
1.  **密码哈希**: 通常使用 `passlib` 库（如 `bcrypt` 或 `PBKDF2`）来对用户密码进行加盐哈希处理，确保即使数据库泄露，密码也难以被破解。
    ```python
    from passlib.context import CryptContext

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)
    ```
2.  **JWT 生成**: 使用 `python-jose` 库生成 JWT。它会包含用户 ID、过期时间等信息，并使用配置中定义的 `SECRET_KEY` 和 `ALGORITHM` 进行签名。
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
3.  **JWT 验证**: 验证 JWT 的签名和过期时间，并解码其内容以获取用户信息。
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

## 路径
`/backend/app/core/security.py`