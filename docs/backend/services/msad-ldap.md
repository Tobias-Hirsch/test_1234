# `services/msad_ldap.py` - MS AD/LDAP 集成服务

本文档描述了 `backend/app/services/msad_ldap.py` 文件，该文件包含了与 Microsoft Active Directory (MS AD) 或通用 LDAP 服务器进行用户认证和信息同步的业务逻辑。

## 功能描述
*   **LDAP 连接**: 建立与 LDAP 服务器的安全连接。
*   **用户认证**: 通过 LDAP 绑定（bind）操作验证用户凭据。
*   **用户信息查询**: 从 LDAP 目录中查询用户属性（如邮箱、组信息）。
*   **用户同步**: 可能包含将 LDAP 用户信息同步到本地数据库的功能。

## 逻辑实现
该模块通常会使用 `ldap3` 库与 LDAP 服务器进行交互。

例如，一个基本的 LDAP 认证和用户查询示例：
```python
from ldap3 import Server, Connection, ALL, SUBTREE
from backend.app.core.config import settings
import logging

logger = logging.getLogger(__name__)

def authenticate_ldap_user(username: str, password: str) -> bool:
    server = Server(settings.LDAP_SERVER, port=settings.LDAP_PORT, use_ssl=settings.LDAP_USE_SSL, get_info=ALL)
    conn = Connection(server, user=f"uid={username},{settings.LDAP_BASE_DN}", password=password, auto_bind=True)
    if conn.bind():
        logger.info(f"LDAP authentication successful for user: {username}")
        conn.unbind()
        return True
    else:
        logger.warning(f"LDAP authentication failed for user: {username}, error: {conn.result}")
        conn.unbind()
        return False

def get_ldap_user_info(username: str) -> Optional[dict]:
    server = Server(settings.LDAP_SERVER, port=settings.LDAP_PORT, use_ssl=settings.LDAP_USE_SSL, get_info=ALL)
    conn = Connection(server, user=settings.LDAP_BIND_DN, password=settings.LDAP_BIND_PASSWORD, auto_bind=True)
    if conn.bind():
        conn.search(
            search_base=settings.LDAP_BASE_DN,
            search_filter=f'(uid={username})',
            search_scope=SUBTREE,
            attributes=['mail', 'cn', 'memberOf'] # 根据需要获取的属性
        )
        if conn.entries:
            user_entry = conn.entries[0]
            user_info = {
                "username": str(user_entry.cn),
                "email": str(user_entry.mail) if hasattr(user_entry, 'mail') else None,
                "groups": [str(g) for g in user_entry.memberOf] if hasattr(user_entry, 'memberOf') else []
            }
            conn.unbind()
            return user_info
        conn.unbind()
    return None
```

## 路径
`/backend/app/services/msad_ldap.py`