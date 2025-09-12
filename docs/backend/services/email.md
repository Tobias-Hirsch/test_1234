# `services/email.py` - 邮件服务

本文档描述了 `backend/app/services/email.py` 文件，该文件包含了用于发送电子邮件的业务逻辑，例如账户激活邮件、密码重置邮件和测试邮件。

## 功能描述
*   **SMTP 配置**: 从应用程序配置中读取 SMTP 服务器设置。
*   **邮件发送**: 封装了使用 `smtplib` 或其他邮件库发送电子邮件的功能。
*   **邮件模板**: 可能支持使用模板来构建邮件内容。
*   **激活邮件**: 发送包含账户激活链接的邮件。
*   **重置密码邮件**: 发送包含密码重置链接的邮件。
*   **测试邮件**: 用于验证邮件服务配置是否正确。

## 逻辑实现
1.  **SMTP 客户端**: 使用 `smtplib` 库连接到 SMTP 服务器，并进行认证。
    ```python
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    from backend.app.core.config import settings
    import logging

    logger = logging.getLogger(__name__)

    async def send_email(
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ):
        msg = MIMEMultipart("alternative")
        msg["From"] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
        msg["To"] = to_email
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))
        if html_body:
            msg.attach(MIMEText(html_body, "html"))

        try:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                if settings.SMTP_TLS:
                    server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
            logger.info(f"Email sent to {to_email} with subject: {subject}")
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            raise
    ```
2.  **`send_activation_email(email: str, username: str, token: str)`**:
    *   构建账户激活邮件的主题和内容，包含一个激活链接。
    *   调用 `send_email` 发送邮件。
3.  **`send_reset_password_email(email: str, username: str, token: str)`**:
    *   构建密码重置邮件的主题和内容，包含一个重置链接。
    *   调用 `send_email` 发送邮件。
4.  **`send_test_email(email: str)`**:
    *   发送一个简单的测试邮件。

## 路径
`/backend/app/services/email.py`