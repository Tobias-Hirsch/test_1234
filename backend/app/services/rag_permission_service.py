from typing import List, Dict, Any
from sqlalchemy.orm import Session, joinedload

from app.models.database import User, RagData, Policy
from app.services.abac_attribute_extractor import ABACAttributeExtractor
from app.services.abac_policy_evaluator import ABACPolicyEvaluator
from app.core.redis_client import get_redis_client
from app.core.config import settings
import json

class RagPermissionService:
    """
    A service to handle all permission checks related to RAG items.
    """
    def __init__(self, db: Session, redis_client: any):
        self.db = db
        self.redis_client = redis_client
        self.attribute_extractor = ABACAttributeExtractor(db, self.redis_client)
        self.evaluator = ABACPolicyEvaluator()

    def _load_policies(self) -> List[Policy]:
        """
        Loads active ABAC policies from Redis cache or database.
        """
        policies_cache_key = "abac_policies"
        # Always delete the cache first to ensure fresh data is loaded.
        self.redis_client.delete(policies_cache_key)
        
        # Load fresh policies from the database
        policies = self.db.query(Policy).filter(Policy.is_active == 1).all()
        
        # After loading, repopulate the cache
        if policies:
            policies_to_cache = [
                {
                    "id": p.id, "name": p.name, "description": p.description,
                    "effect": p.effect,
                    "actions": p.actions,
                    "subjects": p.subjects,
                    "resources": p.resources,
                    "conditions": p.conditions,
                    "is_active": p.is_active
                } for p in policies
            ]
            self.redis_client.setex(
                policies_cache_key,
                settings.ABAC_POLICY_CACHE_EXPIRE_MINUTES * 60,
                json.dumps(policies_to_cache)
            )
        return policies

    def get_accessible_rags(self, current_user: User) -> List[Dict[str, Any]]:
        """
        Gets all RAG items accessible by the user, based on the User -> Role -> Permission model.
        """
        # 1. Admin check: Admins can see everything.
        if any(role.name == 'admin' for role in current_user.roles):
            all_rags = self.db.query(RagData).all()
            return [
                {
                    **rag.__dict__,
                    "access_level": "all"
                } for rag in all_rags
            ]

        # 2. Get all permissions for the current user.
        user_permissions = []
        for role in current_user.roles:
            # This line is a remnant of the old RBAC system and is no longer needed.
            # Permissions are now handled by the ABAC policy engine.
            pass

        # 3. Filter for permissions related to 'ragitem'.
        rag_permissions = [p for p in user_permissions if p.type == 'ragitem']

        # 4. Get all RAG items.
        all_rags = self.db.query(RagData).all()
        accessible_rags = []

        # 5. Determine access for each RAG item.
        for rag in all_rags:
            determined_access_level = "none"
            
            # Check for ownership first
            if rag.owner_id == current_user.id:
                determined_access_level = "all" # Owner gets full access
            else:
                # Check permissions from roles
                for perm in rag_permissions:
                    # Check for wildcard resource '*'
                    if perm.resource == '*':
                        determined_access_level = max(determined_access_level, perm.access_level, key=lambda x: ["none", "read-only", "edit", "all"].index(x))
                    # Check for specific resource match
                    elif perm.resource == str(rag.id):
                         determined_access_level = max(determined_access_level, perm.access_level, key=lambda x: ["none", "read-only", "edit", "all"].index(x))

            if determined_access_level != "none":
                rag_dict = {c.name: getattr(rag, c.name) for c in rag.__table__.columns}
                rag_dict["access_level"] = determined_access_level
                accessible_rags.append(rag_dict)

        return accessible_rags

    def get_retrievable_rag_ids(self, current_user: User) -> List[int]:
        """
        Gets the IDs of all RAG items the user has at least read-only access to.
        """
        accessible_rags = self.get_accessible_rags(current_user)
        return [rag['id'] for rag in accessible_rags]

    def check_rag_creation_permission(self, current_user: User) -> bool:
        """
        Checks if the user has permission to create a new RAG.
        """
        if any(role.name == 'admin' for role in current_user.roles):
            return True

        policies = self._load_policies()
        attributes = self.attribute_extractor.get_all_attributes(
            user=current_user,
            resource_type="rag", # Generic resource type for creation
            action_type="create"
        )
        return self.evaluator.evaluate(policies, attributes, "create", "rag")
