# `services/inactive_user_cleaner.py` - 非活跃用户清理服务

本文档描述了 `backend/app/services/inactive_user_cleaner.py` 文件，该文件包含了定期清理未激活用户账户的业务逻辑。

## 功能描述
*   **定期清理**: 自动删除超过指定期限仍未激活的用户账户。
*   **数据维护**: 帮助管理数据库大小，提高系统安全性，并清理无效的用户数据。

## 逻辑实现
1.  **`remove_expired_unactivated_users()`**:
    *   从 `backend.app.core.config` 中获取 `EMAIL_ACTIVATE_TOKEN_EXPIRE_HOURS` 配置，确定未激活账户的保留期限。
    *   计算出需要删除的账户的截止日期。
    *   连接到数据库。
    *   在 `users` 表中查找并删除所有 `is_active` 为 `False` 且 `created_at` 早于截止日期的用户。
    *   记录清理操作的日志。

## 路径
`/backend/app/services/inactive_user_cleaner.py`