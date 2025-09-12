from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
import redis
import json

from app.models.database import get_db, User, Role as DBRole
from app.schemas.schemas import UserRoleAssign, Role as RoleSchema
from app.dependencies.permissions import require_abac_permission, check_permission
from app.services.auth import get_current_active_user

router = APIRouter(
    prefix="/user-roles",
    tags=["user-roles"],
)

@router.post("", dependencies=[Depends(require_abac_permission("user", "assign_role"))], include_in_schema=False)
@router.post("/", dependencies=[Depends(require_abac_permission("user", "assign_role"))])
def assign_role_to_user(user_role: UserRoleAssign, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_role.user_id).first()
    role = db.query(DBRole).filter(DBRole.id == user_role.role_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    if role in user.roles:
        return {"message": "User already has this role"}

    user.roles.append(role)
    db.commit()
    return {"message": "Role assigned successfully"}

@router.delete("", dependencies=[Depends(require_abac_permission("user", "remove_role"))], include_in_schema=False)
@router.delete("/", dependencies=[Depends(require_abac_permission("user", "remove_role"))])
def remove_role_from_user(user_role: UserRoleAssign, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_role.user_id).first()
    role = db.query(DBRole).filter(DBRole.id == user_role.role_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    if role not in user.roles:
        raise HTTPException(status_code=400, detail="User does not have this role")

    user.roles.remove(role)
    db.commit()
    return {"message": "Role removed successfully"}

@router.get("/user/{user_id}/roles", response_model=List[RoleSchema])
def get_user_roles(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get the roles for a specific user.
    Permission to view is determined by ABAC policies.
    """
    target_user = db.query(User).options(joinedload(User.roles)).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check permission to read the roles of the target user.
    # The 'resource_obj' is the user whose roles are being requested.
    check_permission(db, current_user, "read_roles", resource_obj=target_user)

    return target_user.roles