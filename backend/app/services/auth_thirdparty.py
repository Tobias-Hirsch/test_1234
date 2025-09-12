import os
from authlib.integrations.starlette_client import OAuth
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.database import User
from app.core.security import create_access_token
from datetime import timedelta
from ..core.config import settings  # Global import

oauth = OAuth()

# Configure Google OAuth
if settings.GOOGLE_AUTH_ENABLE:
    oauth.register(
        name='google',
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        access_token_url='https://oauth2.googleapis.com/token',
        authorize_url='https://accounts.google.com/o/oauth2/auth',
        api_base_url='https://www.googleapis.com/oauth2/v3/',
        client_kwargs={'scope': 'openid email profile'},
        redirect_uri=settings.GOOGLE_REDIRECT_URI,
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration' # Add this line
    )

# Configure Microsoft OAuth
if settings.MICROSOFT_AUTH_ENABLE:
    oauth.register(
        name='microsoft',
        client_id=settings.MICROSOFT_CLIENT_ID,
        client_secret=settings.MICROSOFT_CLIENT_SECRET,
        access_token_url='https://login.microsoftonline.com/common/oauth2/v2.0/token',
        authorize_url='https://login.microsoftonline.com/common/oauth2/v2.0/authorize',
        api_base_url='https://graph.microsoft.com/v1.0/',
        client_kwargs={'scope': 'openid email profile User.Read'},
        redirect_uri=settings.MICROSOFT_REDIRECT_URI,
        server_metadata_url=f"https://login.microsoftonline.com/{settings.MICROSOFT_TENANT_ID}/v2.0/.well-known/openid-configuration"
    )

# Configure Generic OAuth
if settings.OAUTH_GENERIC_AUTH_ENABLE:
    oauth.register(
        name='oauth_generic',
        client_id=settings.OAUTH_GENERIC_CLIENT_ID,
        client_secret=settings.OAUTH_GENERIC_CLIENT_SECRET,
        access_token_url=settings.OAUTH_GENERIC_TOKEN_URL,
        authorize_url=settings.OAUTH_GENERIC_AUTHORIZATION_URL,
        api_base_url=settings.OAUTH_GENERIC_USERINFO_URL, # This should be the userinfo endpoint
        client_kwargs={'scope': settings.OAUTH_GENERIC_SCOPE},
        redirect_uri=settings.OAUTH_GENERIC_REDIRECT_URI
    )

async def handle_oauth_callback(provider_name: str, request, db: Session):
    """Handles the OAuth callback for a given provider."""
    client = oauth.create_client(provider_name)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth provider '{provider_name}' is not configured or enabled."
        )

    try:
        token = await client.authorize_access_token(request)
        print(f"Received token for {provider_name}: {token}") # Add this line for debugging
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get access token from {provider_name}: {e}"
        )

    user_info = {}
    if provider_name == 'google':
        # Authlib's client.get automatically uses the token obtained from authorize_access_token
        user_info = token.get('userinfo')
        if not user_info:
            # Fallback if userinfo is not directly in the token (e.g., for generic OAuth)
            # This part might need further adjustment based on specific provider's userinfo endpoint
            # For Google, it's usually in the token.
            resp = await client.get('userinfo')
            resp.raise_for_status()
            user_info = resp.json()
        # Map Google user info to our User model fields
        email = user_info.get('email')
        name = user_info.get('name')
        avatar = user_info.get('picture')
        provider_id = user_info.get('sub') # Google's unique user ID
    elif provider_name == 'microsoft':
        resp = await client.get('me', token=token) # Microsoft Graph API endpoint for user info
        resp.raise_for_status()
        user_info = resp.json()
        # Map Microsoft user info to our User model fields
        email = user_info.get('mail') or user_info.get('userPrincipalName')
        name = user_info.get('displayName')
        # Microsoft Graph API requires a separate call for profile photo
        # For simplicity, we might skip avatar for now or add a separate call
        avatar = None # TODO: Implement fetching Microsoft user photo
        provider_id = user_info.get('id') # Microsoft's unique user ID
    elif provider_name == 'oauth_generic':
        # For generic OAuth, assume the api_base_url is the userinfo endpoint
        resp = await client.get('') # Empty string means base_url itself
        resp.raise_for_status()
        user_info = resp.json()
        # Map generic OAuth user info to our User model fields
        email = user_info.get('email')
        name = user_info.get('name') or user_info.get('preferred_username')
        avatar = user_info.get('picture')
        provider_id = user_info.get('sub') # Standard OAuth 'sub' claim for unique user ID
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported OAuth provider: {provider_name}"
        )

    # Find or create user
    user = db.query(User).filter(
        User.provider == provider_name,
        User.provider_id == provider_id
    ).first()

    if not user:
        # Create new user
        user = User(
            username=email.split('@')[0] if email else f"{provider_name}_{provider_id}", # Generate username if email not available
            email=email,
            first_name=name.split(' ')[0] if name and ' ' in name else name,
            surname=name.split(' ')[-1] if name and ' ' in name else None,
            avatar=avatar,
            provider=provider_name,
            provider_id=provider_id,
            hashed_password="NO_PASSWORD_FOR_OAUTH", # OAuth users don't have local passwords
            is_active=1,
            department="Default" # Assign a default department for new users
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # Update existing user info if necessary
        user.email = email or user.email
        user.first_name = name.split(' ')[0] if name and ' ' in name else name or user.first_name
        user.surname = name.split(' ')[-1] if name and ' ' in name else None or user.surname
        user.avatar = avatar or user.avatar
        db.commit()
        db.refresh(user)

    # Generate JWT token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id, "provider": user.provider, "provider_id": user.provider_id},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer", "user": user}