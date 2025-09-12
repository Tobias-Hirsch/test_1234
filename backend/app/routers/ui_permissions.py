from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict
import redis

from app.models.database import User, get_db
from app.services.auth import get_current_active_user
from app.dependencies.permissions import has_permission
from app.core.redis_client import get_redis_client

router = APIRouter(
    tags=["UI Permissions"],
)

@router.get("/ui_permissions", response_model=Dict[str, Dict[str, bool]])
async def get_ui_permissions(
    components: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    redis_client: redis.Redis = Depends(get_redis_client)
):
    """
    Evaluates and returns the UI permissions for the current user for a given list of components.
    Permissions are determined by the centralized ABAC `has_permission` function.

    - **components**: A comma-separated string of UI component IDs (e.g., "ui.page.rag_list,ui.button.rag_list.create").
    """
    if not components:
        return {}

    component_ids = [comp.strip() for comp in components.split(',') if comp.strip()]
    permissions = {}

    for comp_id in component_ids:
        # Determine the action based on the component ID convention
        action_name = "execute" if "button" in comp_id or "action" in comp_id else "view"
        
        # Use the centralized has_permission function
        is_allowed = has_permission(
            db=db,
            redis_client=redis_client,
            current_user=current_user,
            action=action_name,
            resource_type="ui_element",
            resource_id=comp_id
        )
        
        permissions[comp_id] = {action_name: is_allowed}

    return permissions