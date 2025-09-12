# `services/auth_thirdparty.py` - 第三方认证服务

本文档描述了 `backend/app/services/auth_thirdparty.py` 文件，该文件可能包含了与第三方认证（如 OAuth2、OpenID Connect）相关的业务逻辑。

## 功能描述
*   **OAuth 客户端配置**: 配置用于与第三方身份提供商（如 Google、GitHub、Facebook）交互的 OAuth 客户端。
*   **授权 URL 生成**: 生成用于引导用户到第三方登录页面的授权 URL。
*   **令牌交换**: 处理从第三方获取的授权码，并交换为访问令牌。
*   **用户信息获取**: 使用访问令牌从第三方获取用户资料。
*   **用户注册/登录**: 根据第三方用户信息在本地数据库中创建或查找用户。

## 逻辑实现
该模块通常会使用 `Authlib` 或其他 OAuth 客户端库来实现第三方认证流程。

例如，Google OAuth2 流程：
1.  **配置客户端**:
    ```python
    from authlib.integrations.starlette_client import OAuth
    from backend.app.core.config import settings

    oauth = OAuth()
    oauth.register(
        name='google',
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        authorize_url='https://accounts.google.com/o/oauth2/auth',
        access_token_url='https://accounts.google.com/o/oauth2/token',
        api_base_url='https://www.googleapis.com/oauth2/v1/',
        client_kwargs={'scope': 'openid email profile'},
    )
    ```
2.  **授权重定向**:
    ```python
    from starlette.requests import Request
    from starlette.responses import RedirectResponse

    async def login_google(request: Request):
        redirect_uri = request.url_for('auth_google')
        return await oauth.google.authorize_redirect(request, redirect_uri)
    ```
3.  **回调处理**:
    ```python
    async def auth_google(request: Request, db: Session = Depends(get_db)):
        token = await oauth.google.authorize_access_token(request)
        user_info = await oauth.google.parse_id_token(token)
        # 根据 user_info 在本地数据库中查找或创建用户
        # 生成并返回本地 JWT
    ```

## 路径
`/backend/app/services/auth_thirdparty.py`