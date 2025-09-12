from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from ..core.config import settings # Global import
from app.models.database import get_db, User, Role, SessionLocal # Import User, Role model and SessionLocal
from app.schemas import schemas # Import schemas
from app.dependencies.permissions import require_abac_permission # Import require_abac_permission dependencies
from app.schemas.schemas import Action # Import the Action enum
from app.services.auth import get_current_active_user # Import get_current_active_user

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from app.services.query_filter_service import get_query_filter_service, QueryFilterService

@router.get("", response_model=List[schemas.User], include_in_schema=False)
@router.get("/", response_model=List[schemas.User])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    qfs: QueryFilterService = Depends(get_query_filter_service)
):
    filters = qfs.get_query_filters(resource_type="user", action="read_list")
    
    query = db.query(User).options(joinedload(User.roles))
    if filters:
        query = query.filter(*filters)
    
    users = query.offset(skip).limit(limit).all()
    
    return users

from app.dependencies.permissions import check_permission

@router.get("/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    user = db.query(User).options(
        joinedload(User.roles)
    ).filter(User.id == user_id).first()
    
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
        
    check_permission(db, current_user, "read", resource_obj=user)
    
    return user

@router.put("/{user_id}", response_model=schemas.User, dependencies=[Depends(require_abac_permission(resource_type="user", action_type=Action.UPDATE))])
def update_user(
    user_id: int,
    user_update: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user) # Inject current user
):
    # The permission check is now handled by the dependency decorator.
    # We can add logic here if a user can update their own profile without the general 'update' permission,
    # but for admin functions, the decorator is sufficient.
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user_update.model_dump(exclude_unset=True)

    # Prevent updating hashed_password for SSO users if it's not explicitly provided
    if user.provider and user.provider != "local" and "hashed_password" in update_data:
        del update_data["hashed_password"]

    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_abac_permission(resource_type="user", action_type=Action.DELETE))])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return {"detail": "User deleted successfully"}

@router.post("", response_model=schemas.User, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_abac_permission(resource_type="user", action_type=Action.CREATE))], include_in_schema=False)
@router.post("/", response_model=schemas.User, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_abac_permission(resource_type="user", action_type=Action.CREATE))])
def create_user(
    user_create: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    # Check if SSO is enabled and prevent local user creation if so
    import os
    MSAD_SSO_ENABLED = eval(settings.MSAD_SSO_ENABLED, "False").lower() == "true"
    if MSAD_SSO_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User creation is managed by MS AD when SSO is enabled. Please use AD to create users."
        )

    db_user = db.query(User).filter(User.username == user_create.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Hash the password before storing
    from app.services.auth import get_password_hash
    hashed_password = get_password_hash(user_create.password)

    new_user = User(
        username=user_create.username,
        email=user_create.email,
        phone=user_create.phone,
        department=user_create.department,
        security_level=user_create.security_level,
        first_name=user_create.first_name,
        surname=user_create.surname,
        hashed_password=hashed_password,
        is_active=user_create.is_active,
        avatar=user_create.avatar,
        provider="local" # Mark as locally created user
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user