from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import redis

from app.schemas import schemas
from app.models.database import User
from app.dependencies.permissions import get_db, has_permission
from app.services.auth import get_current_active_user
from app.core.redis_client import get_redis_client

router = APIRouter(
    prefix="/abac",
    tags=["abac"],
)

@router.get("/attributes", response_model=list[schemas.AttributeSchema])
def get_abac_attributes():
    """
    Get a list of all available ABAC attributes for building policies.
    This provides the "vocabulary" for the frontend policy builder.
    """
    attributes = [
        # User Attributes
        {"key": "user.id", "name": "用户ID", "category": "subject", "type": "integer"},
        {"key": "user.username", "name": "用户名", "category": "subject", "type": "string"},
        {"key": "user.email", "name": "邮箱", "category": "subject", "type": "string"},
        {"key": "user.phone", "name": "电话", "category": "subject", "type": "string"},
        {"key": "user.department", "name": "部门", "category": "subject", "type": "string"},
        {"key": "user.is_active", "name": "是否激活", "category": "subject", "type": "boolean"},
        {"key": "user.security_level", "name": "安全级别", "category": "subject", "type": "integer"},
        {"key": "user.roles", "name": "用户角色", "category": "subject", "type": "array_string"},

        # Resource Attributes
        {"key": "resource.type", "name": "资源类型", "category": "resource", "type": "string"},
        {"key": "resource.id", "name": "资源ID", "category": "resource", "type": "string"}, # ID can be string or integer
        {"key": "resource.owner_id", "name": "所有者ID", "category": "resource", "type": "integer"},

        # Environment Attributes
        {"key": "environment.current_time", "name": "当前时间", "category": "environment", "type": "datetime"},
    ]
    return attributes


@router.get("/actions", response_model=list[str])
def get_abac_actions():
    """
    Get a list of all available ABAC actions.
    """
    return [action.value for action in schemas.Action]


@router.get("/resource-types", response_model=list[str])
def get_abac_resource_types():
    """
    Get a list of all available ABAC resource types.
    """
    # In a real-world scenario, these might be dynamically discovered
    # or managed in a central configuration.
    # For now, we'll hardcode the known types.
    return [
        "ui.page",
        "api.endpoint",
        "rag_data",
        "rag_file",
        "user",
        "role",
        "policy"
    ]


@router.post("/check-permission", response_model=schemas.CheckPermissionResponse)
def check_user_permission(
    request: schemas.CheckPermissionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    redis_client: redis.Redis = Depends(get_redis_client)
):
    """
    Check if the current user has a specific permission.
    This endpoint is designed to be called by the frontend to dynamically control UI elements.
    """
    is_permitted = has_permission(
        db=db,
        redis_client=redis_client,
        current_user=current_user,
        action=request.action,
        resource_type=request.resource_type,
        resource_id=request.resource_id
    )
    return schemas.CheckPermissionResponse(allowed=is_permitted)