from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional, Any
import redis
import json
 
from app.models.database import SessionLocal, User, Role, Policy
from app.services.auth import get_current_active_user
from app.services.abac_attribute_extractor import ABACAttributeExtractor
from app.services.abac_policy_evaluator import ABACPolicyEvaluator
from app.core.redis_client import get_redis_client
from app.core.config import settings
 
# Initialize the ABAC policy evaluator
abac_evaluator = ABACPolicyEvaluator()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Function to check if the current user has any of the required roles
def require_role(roles: List[str]):
    def role_checker(
        current_user: User = Depends(get_current_active_user),
        redis_client: redis.Redis = Depends(get_redis_client)
    ):
        user_cache_key = f"user:{current_user.username}"
        cached_user_data = redis_client.get(user_cache_key)

        if cached_user_data:
            user_dict = json.loads(cached_user_data)
            cached_roles = user_dict.get("roles", [])
            if any(role_name in roles for role_name in cached_roles):
                return current_user
        else:
            # Fallback to DB if cache is empty or expired (should be rare if auth.py caches)
            # This part might be redundant if get_current_user always populates cache
            # but kept for robustness.
            if any(role.name in roles for role in current_user.roles):
                return current_user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return role_checker



from fastapi import Request # Add Request import

def has_permission(
    db: Session,
    redis_client: redis.Redis,
    current_user: User,
    action: str,
    resource_type: str,
    resource_obj: Optional[Any] = None,
    resource_id: Optional[int] = None
) -> bool:
    """
    Core ABAC permission checking logic. Returns True if permitted, False otherwise.
    Does not raise exceptions.
    """
    if not current_user.is_active:
        return False

    attribute_extractor = ABACAttributeExtractor(db, redis_client)
    attributes = attribute_extractor.get_all_attributes(
        user=current_user,
        action_type=action,
        resource_obj=resource_obj,
        resource_type=resource_type,
        resource_id=resource_id
    )

    policies_cache_key = "abac_policies"
    cached_policies_data = redis_client.get(policies_cache_key)
    policies = []
    if cached_policies_data:
        policies_dicts = json.loads(cached_policies_data)
        for p_dict in policies_dicts:
            p_dict.setdefault('effect', 'allow')
            policies.append(Policy(**p_dict))
    else:
        db_policies = db.query(Policy).filter(Policy.is_active == 1).all()
        if db_policies:
            policies_to_cache = [
                {
                    "id": p.id, "name": p.name, "description": p.description,
                    "effect": p.effect, "actions": p.actions, "subjects": p.subjects,
                    "resources": p.resources, "query_conditions": p.query_conditions, "is_active": p.is_active
                } for p in db_policies
            ]
            redis_client.setex(policies_cache_key, settings.ABAC_POLICY_CACHE_EXPIRE_MINUTES * 60, json.dumps(policies_to_cache))
            policies = [Policy(**p) for p in policies_to_cache]

    return abac_evaluator.evaluate(
        policies=policies,
        attributes=attributes,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id or getattr(resource_obj, 'id', None)
    )

def require_abac_permission(resource_type: str, action_type: str):
    def abac_permission_checker(
        request: Request,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db),
        redis_client: redis.Redis = Depends(get_redis_client)
    ):
        resource_id = request.path_params.get(f"{resource_type}_id") if request else None
        
        is_permitted = has_permission(
            db=db,
            redis_client=redis_client,
            current_user=current_user,
            action=action_type,
            resource_type=resource_type,
            resource_id=resource_id
        )

        if not is_permitted:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action.",
            )
        return current_user
    return abac_permission_checker



def check_permission(
    db: Session,
    current_user: User,
    action: str,
    resource_obj: Optional[Any] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[int] = None
):
    """
    A direct, non-dependency function to check ABAC permissions.
    Can check based on a resource object or an explicit type/id pair.
    Raises an HTTPException if permission is denied.
    """
    if resource_obj is None and resource_type is None:
        raise ValueError("check_permission requires either a resource_obj or a resource_type.")

    redis_client = next(get_redis_client())
    
    # Prioritize explicit resource_type, otherwise infer it from the object.
    final_resource_type = resource_type or resource_obj.__class__.__name__.lower()
    
    # Ensure we have an ID if the object is not provided
    final_resource_id = resource_id
    if resource_obj:
        final_resource_id = getattr(resource_obj, 'id', resource_id)


    is_permitted = has_permission(
        db=db,
        redis_client=redis_client,
        current_user=current_user,
        action=action,
        resource_type=final_resource_type,
        resource_obj=resource_obj,
        resource_id=final_resource_id
    )

    if not is_permitted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You do not have permission to perform '{action}' on '{final_resource_type}'.",
        )