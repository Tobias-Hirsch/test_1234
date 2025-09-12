# `services/auth.py` - 认证服务

本文档描述了 `backend/app/services/auth.py` 文件，该文件包含了与用户认证和授权相关的核心业务逻辑。

## 功能描述
*   **用户认证**: 验证用户提供的凭据（用户名/邮箱和密码）。
*   **JWT 令牌管理**: 生成、验证和刷新 JWT 访问令牌。
*   **当前用户获取**: 提供获取当前已认证用户的功能。
*   **权限验证**: 辅助进行用户权限检查。

## 逻辑实现
1.  **`authenticate_user(db: Session, username: str, password: str)`**:
    *   根据用户名或邮箱从数据库中查找用户。
    *   使用 `security.verify_password` 验证用户密码。
    *   如果凭据有效，返回用户对象。
2.  **`create_access_token(data: dict, expires_delta: Optional[timedelta] = None)`**:
    *   调用 `security.create_access_token` 生成 JWT 访问令牌。
3.  **`get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db))`**:
    *   使用 OAuth2 方案从请求头中获取 JWT 令牌。
    *   调用 `security.decode_access_token` 解码令牌并获取用户 ID。
    *   从数据库中获取用户对象。
    *   如果令牌无效或用户不存在，则抛出 `HTTPException`。
4.  **`get_current_active_user(current_user: User = Depends(get_current_user))`**:
    *   在 `get_current_user` 的基础上，进一步检查用户是否处于激活状态。
5.  **`get_current_active_superuser(current_user: User = Depends(get_current_active_user))`**:
    *   在 `get_current_active_user` 的基础上，进一步检查用户是否是超级用户。

## 路径
`/backend/app/services/auth.py`