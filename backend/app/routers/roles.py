from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.models.database import get_db, Role as DBRole, User
from app.schemas.schemas import RoleCreate, Role as RoleSchema, RoleUpdate
from app.dependencies.permissions import require_abac_permission, check_permission
from app.services.auth import get_current_active_user
from app.services.query_filter_service import QueryFilterService, get_query_filter_service

router = APIRouter(
    prefix="/roles",
    tags=["roles"],
)

@router.post("", response_model=RoleSchema, dependencies=[Depends(require_abac_permission("role", "create"))], include_in_schema=False)
@router.post("/", response_model=RoleSchema, dependencies=[Depends(require_abac_permission("role", "create"))])
def create_role(role: RoleCreate, db: Session = Depends(get_db)):
    """
    Create a new role.
    """
    db_role = DBRole(name=role.name, description=role.description)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

@router.get("", response_model=List[RoleSchema], include_in_schema=False)
@router.get("/", response_model=List[RoleSchema])
def read_roles(
    db: Session = Depends(get_db),
    qfs: QueryFilterService = Depends(get_query_filter_service),
    skip: int = 0,
    limit: int = 100,
):
    """
    Retrieve a list of roles, filtered by the current user's permissions.
    """
    filters = qfs.get_query_filters(resource_type="role", action="read_list")
    query = db.query(DBRole)
    if filters:
        query = query.filter(*filters)
    roles = query.offset(skip).limit(limit).all()
    return roles

@router.get("/{role_id}", response_model=RoleSchema)
def read_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve a single role by its ID.
    """
    role = db.query(DBRole).filter(DBRole.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    check_permission(db, current_user, "read", resource_obj=role)
    
    return role

@router.put("/{role_id}", response_model=RoleSchema)
def update_role(
    role_id: int,
    role_update: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a role's name and description.
    """
    role = db.query(DBRole).filter(DBRole.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
        
    check_permission(db, current_user, "update", resource_obj=role)

    update_data = role_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(role, key, value)
        
    db.commit()
    db.refresh(role)
    return role

@router.delete("/{role_id}", status_code=204)
def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a role.
    """
    role = db.query(DBRole).filter(DBRole.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
        
    check_permission(db, current_user, "delete", resource_obj=role)
    
    db.delete(role)
    db.commit()
    return {"detail": "Role deleted successfully"}