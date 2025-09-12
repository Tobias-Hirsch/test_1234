# `routers/smtp.py` - SMTP 邮件服务路由

本文档描述了 `backend/app/routers/smtp.py` 文件，该文件定义了与 SMTP 邮件发送功能相关的 API 路由。

## 功能描述
*   **发送测试邮件**: 提供一个接口用于发送测试邮件，以验证 SMTP 配置是否正确。

## 逻辑实现
1.  **依赖注入**: 路由函数通常会使用 `Depends` 来注入当前用户（通常是管理员或具有相应权限的用户）。
2.  **邮件发送**: 调用 `backend.app.services.email` 模块中的函数来实际发送邮件。
    *   `@router.post("/test-email")`

## 路径
`/backend/app/routers/smtp.py`