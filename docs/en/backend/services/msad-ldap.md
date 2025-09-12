# `services/msad_ldap.py` - MS AD/LDAP Integration Service

This document describes the `backend/app/services/msad_ldap.py` file, which contains the business logic for user authentication and information synchronization with Microsoft Active Directory (MS AD) or generic LDAP servers.

## Function Description
*   **LDAP Connection**: Establishes a secure connection to the LDAP server.
*   **User Authentication**: Verifies user credentials through LDAP bind operations.
*   **User Information Query**: Queries user attributes (e.g., email, group information) from the LDAP directory.
*   **User Synchronization**: May include functionality to synchronize LDAP user information to the local database.

## Logic Implementation
This module typically uses the `ldap3` library to interact with the LDAP server.

For example, a basic LDAP authentication and user query example:
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
            attributes=['mail', 'cn', 'memberOf'] # Attributes to retrieve as needed
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

## Path
`/backend/app/services/msad_ldap.py`