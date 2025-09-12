# `routers/authentication.py` - 认证路由

本文档描述了 `backend/app/routers/authentication.py` 文件，该文件定义了与用户认证相关的 API 路由。

## 功能描述
*   **用户注册**: 提供用户注册新账户的接口。
*   **用户登录**: 提供用户通过用户名/邮箱和密码登录的接口，并返回 JWT 访问令牌。
*   **令牌刷新**: 可能包含刷新访问令牌的接口。
*   **密码重置**: 提供请求密码重置和实际重置密码的接口。
*   **账户激活**: 提供通过邮件链接激活用户账户的接口。
*   **OAuth 认证**: 可能集成第三方 OAuth 认证流程（如 Google、GitHub）。

## 逻辑实现
1.  **依赖注入**: 路由函数通常会使用 FastAPI 的 `Depends` 来注入数据库会话 (`get_db`) 和当前用户 (`get_current_user`) 等依赖。
2.  **用户注册**: 接收用户注册信息，对密码进行哈希处理，将用户数据存储到数据库，并发送账户激活邮件。
    *   `@router.post("/register")`
3.  **用户登录**: 验证用户凭据，如果有效则生成并返回 JWT 访问令牌。
    *   `@router.post("/login")`
4.  **密码重置**:
    *   请求重置：接收用户邮箱，生成重置令牌，并发送包含重置链接的邮件。
        *   `@router.post("/forgot-password")`
    *   执行重置：接收重置令牌和新密码，验证令牌，更新用户密码。
        *   `@router.post("/reset-password")`
5.  **账户激活**: 接收激活令牌，验证令牌，激活用户账户。
    *   `@router.get("/activate/{token}")`
6.  **当前用户**: 提供一个受保护的路由，用于获取当前已认证的用户信息。
    *   `@router.get("/users/me")`

## 路径
`/backend/app/routers/authentication.py`