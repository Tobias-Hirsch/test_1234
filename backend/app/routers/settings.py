from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

from app.core.config import settings
from app.services import auth
from app.models.database import User, get_db
from sqlalchemy.orm import Session

router = APIRouter()

# Define a Pydantic model for the settings to be exposed
class AppSettingsResponse(BaseModel):
    app_name: str
    app_version: str
    description: str
    google_auth_enable: bool
    microsoft_auth_enable: bool
    oauth_generic_auth_enable: bool
    msad_sso_enable: bool
    # Add other non-sensitive settings you want to expose to the frontend

@router.get("/settings", response_model=AppSettingsResponse)
def get_app_settings(current_user: User = Depends(auth.get_current_active_user), db: Session = Depends(get_db)):
    from sqlalchemy.orm import joinedload
    # Eagerly load roles to prevent lazy loading issues that might be triggered by FastAPI's dependency management
    _ = db.query(User).options(joinedload(User.roles)).filter(User.id == current_user.id).one_or_none()
    """
    Retrieve non-sensitive application settings.
    Requires authentication.
    """
    # You can add permission checks here if needed, e.g.:
    # if not auth.has_permission(db, current_user, "settings:view"):
    #     raise HTTPException(status_code=403, detail="Not authorized to view settings")

    return AppSettingsResponse(
        app_name=settings.APP_NAME,
        app_version=settings.APP_VERSION,
        description=settings.DESCRIPTION,
        google_auth_enable=settings.GOOGLE_AUTH_ENABLE,
        microsoft_auth_enable=settings.MICROSOFT_AUTH_ENABLE,
        oauth_generic_auth_enable=settings.OAUTH_GENERIC_AUTH_ENABLE,
        msad_sso_enable=settings.MSAD_SSO_ENABLED,
    )

@router.put("/settings")
def update_app_settings(current_user: User = Depends(auth.get_current_active_user)):
    """
    Update application settings.
    This is a placeholder and needs a proper implementation.
    """
    # You can add permission checks here, e.g.:
    # if not auth.has_permission(db, current_user, "settings:edit"):
    #     raise HTTPException(status_code=403, detail="Not authorized to edit settings")
        
    # The actual logic for updating settings can be complex.
    # It might involve writing to a config file, updating environment variables,
    # or storing settings in a database. This often requires a service restart.
    
    raise HTTPException(status_code=501, detail="Updating settings is not yet implemented.")
