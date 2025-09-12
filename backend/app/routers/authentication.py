from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from datetime import timedelta, datetime, timezone
import secrets
import redis # Add this import
from app.models.database import get_db, User, Role
from app.schemas import schemas
from app.services import auth
from app.services.email import send_activation_email, send_password_reset_email
from app.services.auth_thirdparty import oauth, handle_oauth_callback
from app.core.config import settings

from starlette.responses import RedirectResponse

router = APIRouter()

# Authentication Endpoints
@router.post("/register", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if username, email, or phone already exists
    db_user_username = auth.get_user_by_username(db, username=user.username)
    if db_user_username:
        raise HTTPException(status_code=400, detail="Username already registered")
    if user.email:
        db_user_email = auth.get_user_by_email(db, email=user.email)
        if db_user_email:
            raise HTTPException(status_code=400, detail="Email already registered")
    if user.phone:
        db_user_phone = auth.get_user_by_phone(db, phone=user.phone)
        if db_user_phone:
            raise HTTPException(status_code=400, detail="Phone number already registered")

    # Create user using the new service function, initially inactive
    db_user = auth.create_user(db=db, user_create=user, is_active=False)

    # Generate activation token and set expiration
    activation_token = secrets.token_urlsafe(32)
    activation_expires_at = datetime.now(timezone.utc) + timedelta(hours=24) # 24 hours expiration

    db_user.activation_token = activation_token
    db_user.activation_expires_at = activation_expires_at

    db.commit()
    db.refresh(db_user)

    # Check if this is the first user
    if db.query(User).count() == 1:
        # Assign the 'admin' role to the first user
        admin_role = db.query(Role).filter(Role.name == "admin").first()
        if admin_role:
            db_user.roles.append(admin_role)
            db.commit()
            db.refresh(db_user)
            print(f"Assigned 'admin' role to the first user: {db_user.username}")
        else:
            print("Warning: 'admin' role not found in the database.")

    # Send activation email (assuming user provided email)
    if db_user.email:
        frontend_base_url = settings.FRONTEND_BASE_URL
        activation_link = f"{frontend_base_url}/activate?token={db_user.activation_token}"
        send_activation_email(db_user.email, activation_link)
        print(f"Activation email sent to {db_user.email} with token {activation_token}")
    else:
        print(f"User {db_user.username} registered without email. Cannot send activation email.")
        # TODO: Handle users without email - maybe require email for activation flow?

    # Return a response indicating that activation is required
    # Re-fetch the user with roles and permissions eagerly loaded to avoid serialization errors
    from sqlalchemy.orm import joinedload
    final_user = db.query(User).options(
        joinedload(User.roles)
    ).filter(User.id == db_user.id).first()
    return final_user

# OAuth2.0 Third-Party Authentication Endpoints
@router.get("/auth/enabled-providers")
def get_enabled_auth_providers():
    """Returns a dictionary indicating which OAuth providers are enabled."""
    try:
        google_enabled = settings.GOOGLE_AUTH_ENABLE
        microsoft_enabled = settings.MICROSOFT_AUTH_ENABLE
        oauth_generic_enabled = settings.OAUTH_GENERIC_AUTH_ENABLE

        enabled_providers = {
            "google": google_enabled,
            "microsoft": microsoft_enabled,
            "oauth_generic": oauth_generic_enabled,
        }
        print(f"Enabled auth providers returned to frontend: {enabled_providers}")
        return enabled_providers
    except Exception as e:
        print(f"Error fetching enabled auth providers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error when fetching enabled auth providers: {e}"
        )

@router.get("/auth/{provider}/login")
async def oauth_login(provider: str, request: Request):
    """Initiates the OAuth login flow for a given provider."""
    client = oauth.create_client(provider)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth provider '{provider}' is not configured or enabled."
        )
    
    # Check if the provider is enabled via settings
    if provider.upper() == "GOOGLE" and not settings.GOOGLE_AUTH_ENABLE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"OAuth provider '{provider}' is currently disabled.")
    elif provider.upper() == "MICROSOFT" and not settings.MICROSOFT_AUTH_ENABLE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"OAuth provider '{provider}' is currently disabled.")
    elif provider.upper() == "OAUTH_GENERIC" and not settings.OAUTH_GENERIC_AUTH_ENABLE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"OAuth provider '{provider}' is currently disabled.")

    redirect_uri = getattr(settings, f"{provider.upper()}_REDIRECT_URI", None)
    if not redirect_uri:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Redirect URI for {provider} is not configured."
        )
    
    return await client.authorize_redirect(request, redirect_uri)

@router.get("/auth/{provider}/callback")
async def oauth_callback(provider: str, request: Request, db: Session = Depends(get_db)):
    """Handles the OAuth callback from the provider."""
    # Check if the provider is enabled via settings
    if provider.upper() == "GOOGLE" and not settings.GOOGLE_AUTH_ENABLE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"OAuth provider '{provider}' is currently disabled.")
    elif provider.upper() == "MICROSOFT" and not settings.MICROSOFT_AUTH_ENABLE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"OAuth provider '{provider}' is currently disabled.")
    elif provider.upper() == "OAUTH_GENERIC" and not settings.OAUTH_GENERIC_AUTH_ENABLE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"OAuth provider '{provider}' is currently disabled.")
            
    auth_response = await handle_oauth_callback(provider, request, db)
    
    # Redirect to frontend with token
    frontend_base_url = settings.FRONTEND_BASE_URL
    # Assuming frontend has a route to handle the token, e.g., /auth/callback?token=...
    # Or you can set a cookie here if preferred
    return RedirectResponse(url=f"{frontend_base_url}/auth/callback?token={auth_response['access_token']}", status_code=status.HTTP_302_FOUND)


@router.post("/login", response_model=schemas.Token)
def login_for_access_token(user_login: schemas.UserLogin, db: Session = Depends(get_db), redis_client: redis.Redis = Depends(auth.get_redis_client)):
    try:
        # Authenticate using username (which can be email or phone) and password
        user = auth.authenticate_user(db, username=user_login.username, password=user_login.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = auth.create_access_token(
            data={"sub": user.username, "user_id": user.id, "provider": user.provider, "provider_id": user.provider_id}, # Include provider info
            expires_delta=access_token_expires
        )
        # Update Redis cache expiration for the user upon successful login
        # This extends the user's session if they are actively logging in
        user_cache_key = f"user:{user.username}"
        # Set expiration for the user's cache key to match the token's expiration
        redis_client.expire(user_cache_key, settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)

        # Re-fetch the user with roles and permissions eagerly loaded to avoid serialization errors
        from sqlalchemy.orm import joinedload

        user_for_response = db.query(User).options(
            joinedload(User.roles)
        ).filter(User.id == user.id).first()

        # Return the access token, token type, and the authenticated user object
        return {"access_token": access_token, "token_type": "bearer", "user": user_for_response}
    except HTTPException as e:
        # Re-raise HTTPException to be handled by FastAPI's default handler
        raise e
    except Exception as e:
        # Catch any other unexpected errors and return a 500 response
        print(f"Internal server error during login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}",
        )

@router.post("/forgot-password")
def forgot_password_request(request: schemas.ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = auth.get_user_by_email(db, email=request.email_or_phone)
    if not user:
        user = auth.get_user_by_phone(db, phone=request.email_or_phone)

    if not user:
        # Return a success message even if user not found to prevent enumeration
        return {"message": "If a user with that email or phone exists, a password reset link has been sent."}

    # Generate a unique token
    token = secrets.token_urlsafe(32)
    # Set token expiration time (e.g., 1 hour)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

    # Store the token and expiration in the database
    user.password_reset_token = token
    user.password_reset_expires_at = expires_at
    db.commit()
    db.refresh(user) # Refresh user to get the updated token and expiration

    # Send email with the reset link
    if user.email:
        frontend_base_url = settings.FRONTEND_BASE_URL
        reset_link = f"{frontend_base_url}/reset-password?token={user.password_reset_token}"
        send_password_reset_email(user.email, reset_link)
        print(f"Password reset email sent to {user.email} with token {token}")
    else:
        print(f"User {user.username} has no email. Cannot send password reset email.")

    return {"message": "If a user with that email or phone exists, a password reset link has been sent."}

@router.post("/reset-password")
def reset_password(request: schemas.PasswordResetRequest, db: Session = Depends(get_db)):
    # Find user by the reset token
    user = db.query(User).filter(User.password_reset_token == request.token).first()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    # Check if the token has expired
    if user.password_reset_expires_at:
        # Ensure user.password_reset_expires_at is timezone-aware (UTC)
        if user.password_reset_expires_at.tzinfo is None:
            expires_at_aware = user.password_reset_expires_at.replace(tzinfo=timezone.utc)
        else:
            expires_at_aware = user.password_reset_expires_at

        if expires_at_aware < datetime.now(timezone.utc):
            # Clear the expired token
            user.password_reset_token = None
            user.password_reset_expires_at = None
            db.commit()
            raise HTTPException(status_code=400, detail="Invalid or expired token")

    # Hash the new password and update the user
    hashed_password = auth.get_password_hash(request.new_password)
    user.hashed_password = hashed_password
    user.password_reset_token = None # Clear the token after use
    user.password_reset_expires_at = None
    db.commit()

    return {"message": "Password reset successfully"}

@router.get("/activate")
def activate_user(token: str = Query(..., description="The activation token"), db: Session = Depends(get_db)):
    # Find user by activation token
    user = db.query(User).filter(User.activation_token == token).first()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid activation token")

    # Check if the token has expired
    if user.activation_expires_at:
        # Ensure user.activation_expires_at is timezone-aware (UTC)
        if user.activation_expires_at.tzinfo is None:
            expires_at_aware = user.activation_expires_at.replace(tzinfo=timezone.utc)
        else:
            expires_at_aware = user.activation_expires_at

        if expires_at_aware < datetime.now(timezone.utc):
            # For now, we'll just indicate that the token is expired.
            # We have an APS scheduled job to remove inactivated new registered user after 24 hours.
            raise HTTPException(status_code=400, detail="Activation token expired")

    # Activate the user
    user.is_active = 1
    user.activation_token = None # Clear the token after use
    user.activation_expires_at = None
    db.commit()
    db.refresh(user)

    return {"message": "Account activated successfully"}

# Protected endpoint example
@router.get("/users/me", response_model=schemas.User)
def read_users_me(current_user: User = Depends(auth.get_current_active_user), db: Session = Depends(get_db)):
    # Re-fetch the user with roles and permissions eagerly loaded to avoid serialization errors
    from sqlalchemy.orm import joinedload
    user = db.query(User).options(
        joinedload(User.roles)
    ).filter(User.id == current_user.id).first()
    return user

@router.put("/users/me", response_model=schemas.User)
def update_users_me(user_update: schemas.UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(auth.get_current_active_user)):
    # Get the user from the database to ensure it's attached to the current session
    from sqlalchemy.orm import joinedload
    db_user = db.query(User).options(
        joinedload(User.roles)
    ).filter(User.id == current_user.id).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Update user fields based on user_update schema
    for field, value in user_update.model_dump(exclude_unset=True).items():
        setattr(db_user, field, value)

    db.commit()
    db.refresh(db_user)
    return db_user
