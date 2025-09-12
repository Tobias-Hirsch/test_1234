import os
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas import schemas
from app.models import database
from app.services.email import send_test_email, test_smtp_connection # Import send_test_email and test_smtp_connection
from app.services import auth
from ..core.config import settings # Global import
router = APIRouter()


@router.get("/smtp/config", response_model=schemas.SmtpConfig)
def get_smtp_config(current_user: database.User = Depends(auth.get_current_active_user)):
    # TODO: Implement proper configuration loading (e.g., from DB)
    # For now, read from environment variables
    smtp_server = settings.SMTP_SERVER
    smtp_port = settings.SMTP_PORT
    smtp_user = settings.SMTP_USER
    smtp_password = settings.SMTP_PASSWORD
    smtp_sender_email = settings.SMTP_SENDER_EMAIL

    if not all([smtp_server, smtp_port, smtp_user, smtp_password, smtp_sender_email]):
        # Return default or empty values if not configured
        # Or raise HTTPException if configuration is mandatory
        # For now, return what's available, Pydantic will handle validation
        pass # Pydantic will handle validation and potential errors

    try:
        smtp_port = int(smtp_port) if smtp_port else 587 # Default port if not set
    except ValueError:
        raise HTTPException(status_code=500, detail="Invalid SMTP_PORT environment variable.")


    return schemas.SmtpConfig(
        smtp_server=smtp_server or "", # Provide default empty string if None
        smtp_port=smtp_port,
        smtp_user=smtp_user or "",
        smtp_password=smtp_password or "",
        smtp_sender_email=smtp_sender_email or ""
    )

@router.put("/smtp/config")
def update_smtp_config(config: schemas.SmtpConfig, current_user: database.User = Depends(auth.get_current_active_user)):
    # TODO: Implement proper configuration saving (e.g., to DB)
    # WARNING: Modifying .env file programmatically is generally not recommended for production.
    # This is a simplified approach for demonstration.

    env_path = ".env"
    env_content = []
    try:
        with open(env_path, "r") as f:
            env_content = f.readlines()
    except FileNotFoundError:
        print(f"{env_path} not found. Creating a new one.")
        # If .env doesn't exist, create with new config
        env_content = [
            f"SMTP_SERVER={config.smtp_server}\n",
            f"SMTP_PORT={config.smtp_port}\n",
            f"SMTP_USER={config.smtp_user}\n",
            f"SMTP_PASSWORD={config.smtp_password}\n",
            f"SMTP_SENDER_EMAIL={config.smtp_sender_email}\n",
        ]
        with open(env_path, "w") as f:
             f.writelines(env_content)
        return {"message": "SMTP configuration saved to new .env file."}


    updated_content = []
    smtp_keys = {
        "SMTP_SERVER": config.smtp_server,
        "SMTP_PORT": str(config.smtp_port), # Convert port to string for .env
        "SMTP_USER": config.smtp_user,
        "SMTP_PASSWORD": config.smtp_password,
        "SMTP_SENDER_EMAIL": config.smtp_sender_email,
    }
    updated_keys = set()

    for line in env_content:
        stripped_line = line.strip()
        if "=" in stripped_line:
            key, value = stripped_line.split("=", 1)
            if key in smtp_keys:
                updated_content.append(f"{key}={smtp_keys[key]}\n")
                updated_keys.add(key)
            else:
                updated_content.append(line)
        else:
            updated_content.append(line)

    # Add any missing SMTP keys to the end
    for key, value in smtp_keys.items():
        if key not in updated_keys:
            updated_content.append(f"{key}={value}\n")

    try:
        with open(env_path, "w") as f:
            f.writelines(updated_content)
        # Reload environment variables after updating .env
        from dotenv import load_dotenv # Import here to ensure it's reloaded
        load_dotenv(override=True)
        return {"message": "SMTP configuration updated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to write to .env file: {e}")

@router.post("/smtp/test")
def test_smtp_config(request: schemas.TestEmailRequest, current_user: database.User = Depends(auth.get_current_active_user)):
    # First, test the SMTP connection
    connection_success, connection_message = test_smtp_connection()
    if not connection_success:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"SMTP connection test failed: {connection_message}")

    # If connection is successful, proceed to send the test email
    success = send_test_email(request.recipient_email)

    if success:
        return {"message": f"Test email sent successfully to {request.recipient_email}"}
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to send test email to {request.recipient_email}. Check backend logs for details.")