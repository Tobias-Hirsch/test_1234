import os
import smtplib
from email.mime.text import MIMEText
from ..core.config import settings  # Global import for configuration settings

# TODO: Load SMTP configuration from environment variables or a config file
SMTP_SERVER = settings.SMTP_SERVER
SMTP_PORT = int(settings.SMTP_PORT)
SMTP_USER = settings.SMTP_USER
SMTP_PASSWORD = settings.SMTP_PASSWORD
SMTP_SENDER_EMAIL = settings.SMTP_SENDER_EMAIL

def send_activation_email(recipient_email: str, activation_link: str):
    """Sends an activation email to the user."""
    if not all([SMTP_SERVER, SMTP_USER, SMTP_PASSWORD, SMTP_SENDER_EMAIL]):
        print("SMTP configuration missing. Cannot send activation email.")
        # TODO: Implement proper error handling or logging
        return

    subject = "Activate your account"
    body = f"""
    Please click the link below to activate your account:

    {activation_link}

    This link will expire in 24 hours.
    """

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = SMTP_SENDER_EMAIL
    msg['To'] = recipient_email

    try:
        if SMTP_PORT == 465:
            server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        else:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls() # Secure the connection
        with server:
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_SENDER_EMAIL, recipient_email, msg.as_string())
        print(f"Activation email sent to {recipient_email}")
    except Exception as e:
        print(f"Failed to send activation email to {recipient_email}: {e}")
        # TODO: Implement proper error handling or logging

def send_password_reset_email(recipient_email: str, reset_link: str):
    """Sends a password reset email to the user."""
    if not all([SMTP_SERVER, SMTP_USER, SMTP_PASSWORD, SMTP_SENDER_EMAIL]):
        print("SMTP configuration missing. Cannot send password reset email.")
        return

    subject = "Password Reset Request"
    body = f"""
    You have requested a password reset. Please click the link below to reset your password:

    {reset_link}

    This link will expire in 1 hour. If you did not request a password reset, please ignore this email.
    """

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = SMTP_SENDER_EMAIL
    msg['To'] = recipient_email

    try:
        if SMTP_PORT == 465:
            server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        else:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
        with server:
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_SENDER_EMAIL, recipient_email, msg.as_string())
        print(f"Password reset email sent to {recipient_email}")
    except Exception as e:
        print(f"Failed to send password reset email to {recipient_email}: {e}")

def test_smtp_connection() -> tuple[bool, str]:
    """Tests the SMTP connection and authentication."""
    if not all([SMTP_SERVER, SMTP_USER, SMTP_PASSWORD, SMTP_SENDER_EMAIL]):
        return False, "SMTP configuration missing. Please ensure all SMTP environment variables are set."

    try:
        if SMTP_PORT == 465:
            server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        else:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
        with server:
            server.login(SMTP_USER, SMTP_PASSWORD)
        return True, "SMTP connection and authentication successful."
    except smtplib.SMTPAuthenticationError as e:
        return False, f"SMTP authentication failed: {e}"
    except smtplib.SMTPConnectError as e:
        return False, f"SMTP connection failed: {e}"
    except Exception as e:
        return False, f"An unexpected error occurred during SMTP connection test: {e}"
    
# Functions for testing SMTP configuration
def send_test_email(recipient_email: str) -> bool:
    """Sends a test email to the specified recipient."""
    if not all([SMTP_SERVER, SMTP_USER, SMTP_PASSWORD, SMTP_SENDER_EMAIL]):
        print("SMTP configuration missing. Cannot send test email.")
        # TODO: Implement proper error handling or logging
        return False

    subject = "Test Email from RAG Application"
    body = "This is a test email sent from the RAG application's SMTP configuration."

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = SMTP_SENDER_EMAIL
    msg['To'] = recipient_email

    try:
        if SMTP_PORT == 465:
            server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        else:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls() # Secure the connection
        with server:
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_SENDER_EMAIL, recipient_email, msg.as_string())
        print(f"Test email sent to {recipient_email}")
        return True
    except Exception as e:
        print(f"Failed to send test email to {recipient_email}: {e}")
        # TODO: Implement proper error handling or logging
        return False
    
# if __name__ == "__main__":
#     # Example usage
#     # recipient = "
#     test_smtp_connection()