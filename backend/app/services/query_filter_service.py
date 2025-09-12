import redis
from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, text
from typing import List, Any, Dict

from app.dependencies.permissions import get_db
from app.models.database import User, FileGist, Policy, RagData
from app.services.abac_attribute_extractor import ABACAttributeExtractor
from app.services.auth import get_current_active_user
from app.core.redis_client import get_redis_client

# A mapping from resource type strings to SQLAlchemy model classes
MODEL_MAP = {
    "file": FileGist,
    "user": User,
    "rag": RagData,
    # Add other models here as they become part of the ABAC system
}


class QueryFilterService:
    def __init__(self, db: Session, user: User, redis_client: redis.Redis):
        self.db = db
        self.user = user
        self.redis_client = redis_client
        self.attribute_extractor = ABACAttributeExtractor(db, self.redis_client)

    def get_query_filters(self, resource_type: str, action: str) -> List[Any]:
        """
        Generates a list of SQLAlchemy filter conditions based on active ABAC policies.

        Args:
            resource_type: The type of resource being queried (e.g., "file", "user").
            action: The action being performed (e.g., "read_list").

        Returns:
            A list of SQLAlchemy filter expressions. If no policies grant access,
            returns a list containing a single `False` expression to deny all results.
        """
        # 1. Get all active policies from the database.
        active_policies = self.db.query(Policy).filter(Policy.is_active == 1).all()

        # 2. Get all attributes for the current user.
        user_attributes = self.attribute_extractor.get_user_attributes(self.user)
        
        applicable_filters = []
        grant_access_without_conditions = False

        # 3. Iterate through policies to find applicable ones.
        for policy in active_policies:
            if self._is_policy_applicable(policy, user_attributes, resource_type, action):
                # If the policy has query conditions, build a filter from them.
                if policy.query_conditions:
                    policy_filter = self._build_filter_from_policy(policy.query_conditions, user_attributes, resource_type)
                    if policy_filter is not None:
                        applicable_filters.append(policy_filter)
                else:
                    # If the policy grants access but has NO query conditions,
                    # it means this policy allows access to all items of this resource type.
                    grant_access_without_conditions = True
                    break

        # 4. Determine the final filter.
        if grant_access_without_conditions:
            # If any policy grants full access, no filtering is needed.
            return []

        if not applicable_filters:
            # If no policies granted access at all, deny access.
            return [text("1=0")]  # Return a condition that is always false

        # 5. If there are filters, combine them with an OR condition.
        return [or_(*applicable_filters)]

    def _is_policy_applicable(self, policy: Policy, user_attributes: Dict[str, Any], resource_type: str, action: str) -> bool:
        """
        Checks if a policy applies based on the new standardized policy format.
        """
        # 1. Action Matching: True if actions list is empty, contains '*' or the specific action.
        if not (not policy.actions or "*" in policy.actions or action in policy.actions):
            return False

        # 2. Resource Matching: True if resources list is empty, or matches the type.
        if not policy.resources:
            resource_match = True
        else:
            resource_match = False
            for res in policy.resources:
                # Standard: {'key': 'resource.type', 'operator': 'in', 'value': ['rag', '*']}
                if (res.get("key") == "resource.type" and
                    res.get("operator") == "in" and
                    ("*" in res["value"] or resource_type in res["value"])):
                    resource_match = True
                    break
        if not resource_match:
            return False

        # 3. Subject Matching: True if subjects list is empty, or matches the user's roles.
        if not policy.subjects:
            return True  # No subject constraints, matches all users

        subject_match = False
        for sub in policy.subjects:
            # Standard: {'key': 'user.roles', 'operator': 'in', 'value': ['admin']}
            user_roles = set(user_attributes.get("roles", []))
            policy_roles = set(sub.get("value", []))
            if (sub.get("key") == "user.roles" and
                sub.get("operator") == "in" and
                user_roles.intersection(policy_roles)):
                subject_match = True
                break
        
        return subject_match

    def _build_filter_from_policy(self, query_conditions: List[Dict], user_attributes: Dict[str, Any], resource_type: str) -> Any:
        """
        Builds a single SQLAlchemy filter expression from a policy's query_conditions list.
        """
        model = MODEL_MAP.get(resource_type)
        if not model:
            return None

        condition_expressions = []
        for cond in query_conditions:
            resource_attr_name = cond.get("resource_attribute")
            subject_attr_name = cond.get("subject_attribute")
            operator = cond.get("operator")

            if not all([resource_attr_name, subject_attr_name, operator]):
                continue

            if hasattr(model, resource_attr_name) and subject_attr_name in user_attributes:
                model_attribute = getattr(model, resource_attr_name)
                user_value = user_attributes[subject_attr_name]

                if operator == "eq":
                    condition_expressions.append(model_attribute == user_value)
                # Add other operators like 'neq', 'gt', 'lt', etc. as needed
                # elif operator == "neq":
                #     condition_expressions.append(model_attribute != user_value)

        if not condition_expressions:
            return None
        
        return and_(*condition_expressions)

# Dependency for FastAPI routes
def get_query_filter_service(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    redis_client: redis.Redis = Depends(get_redis_client)
) -> QueryFilterService:
    return QueryFilterService(db, current_user, redis_client)