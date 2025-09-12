# `services/email.py` - Email Service

This document describes the `backend/app/services/email.py` file, which contains the business logic for sending emails, such as account activation emails, password reset emails, and test emails.

## Function Description
*   **SMTP Configuration**: Reads SMTP server settings from the application configuration.
*   **Email Sending**: Encapsulates the functionality for sending emails using `smtplib` or other email libraries.
*   **Email Templates**: May support using templates to construct email content.
*   **Activation Email**: Sends an email containing an account activation link.
*   **Reset Password Email**: Sends an email containing a password reset link.
*   **Test Email**: Used to verify that the email service configuration is correct.

## Logic Implementation
1.  **SMTP Client**: Uses the `smtplib` library to connect to the SMTP server and perform authentication.
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
    *   Constructs the subject and content of the account activation email, including an activation link.
    *   Calls `send_email` to send the email.
3.  **`send_reset_password_email(email: str, username: str, token: str)`**:
    *   Constructs the subject and content of the password reset email, including a reset link.
    *   Calls `send_email` to send the email.
4.  **`send_test_email(email: str)`**:
    *   Sends a simple test email.

## Path
`/backend/app/services/email.py`