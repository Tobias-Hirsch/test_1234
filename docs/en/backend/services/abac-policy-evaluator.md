# `services/abac_policy_evaluator.py` - ABAC Policy Evaluator

This document describes the `backend/app/services/abac_policy_evaluator.py` file, which is the core component of the ABAC (Attribute-Based Access Control) system, responsible for evaluating access requests based on defined policy rules.

## Function Description
*   **Policy Loading**: Loads ABAC policies from a database or configuration files.
*   **Attribute Matching**: Matches attributes from the request with attributes defined in policy rules.
*   **Rule Evaluation**: Evaluates access requests based on matching results and the policy's combining logic (e.g., "Permit Overrides" or "Deny Overrides").
*   **Decision Output**: Returns the access decision (permit or deny) and possible reasons.

## Logic Implementation
This module defines one or more functions to perform policy evaluation. Policies are typically defined in JSON or other structured formats, containing rules, conditions, and effects (permit/deny).

For example:
```python
from typing import Dict, Any
from backend.app.services.abac_functions import equals, greater_than, contains # Import helper functions
import logging

logger = logging.getLogger(__name__)

# Example policy structure
# policies = {
#     "document_access_policy": {
#         "rules": [
#             {
#                 "effect": "Permit",
#                 "conditions": [
#                     {"attribute": "subject.is_superuser", "operator": "equals", "value": True}
#                 ]
#             },
#             {
#                 "effect": "Permit",
#                 "conditions": [
#                     {"attribute": "subject.user_id", "operator": "equals", "value_from_resource": "resource.owner_id"},
#                     {"action": "read", "operator": "equals", "value": "read"}
#                 ]
#             },
#             {
#                 "effect": "Deny",
#                 "conditions": [
#                     {"attribute": "environment.ip_address", "operator": "not_in_range", "value": ["192.168.1.0/24"]}
#                 ]
#             }
#         ],
#         "combiner": "PermitOverrides" # Permit overrides
#     }
# }

def evaluate_policy(policy_name: str, attributes: Dict[str, Any]) -> bool:
    """
    Evaluates an ABAC policy based on the given attributes.
    """
    # In a real application, policies would be loaded from a database
    # policy = get_policy_from_db(policy_name)
    # if not policy:
    #     logger.warning(f"Policy '{policy_name}' not found.")
    #     return False # Default deny

    # Simplified example: assume policy is hardcoded or obtained somehow
    policies = {
        "rag_document_access_policy": {
            "rules": [
                {
                    "effect": "Permit",
                    "conditions": [
                        {"attribute": "subject.is_superuser", "operator": "equals", "value": True}
                    ]
                },
                {
                    "effect": "Permit",
                    "conditions": [
                        {"attribute": "subject.user_id", "operator": "equals", "value_from_resource": "resource.user_id"},
                        {"attribute": "action", "operator": "equals", "value": "read_rag_document"}
                    ]
                }
            ],
            "combiner": "PermitOverrides"
        }
    }
    policy = policies.get(policy_name)
    if not policy:
        logger.warning(f"Policy '{policy_name}' not found.")
        return False

    rules = policy.get("rules", [])
    combiner = policy.get("combiner", "DenyOverrides") # Default deny overrides

    permit_found = False
    deny_found = False

    for rule in rules:
        rule_effect = rule.get("effect")
        conditions = rule.get("conditions", [])
        
        all_conditions_met = True
        for condition in conditions:
            attr_path = condition.get("attribute").split('.')
            operator = condition.get("operator")
            value = condition.get("value")
            value_from_resource_path = condition.get("value_from_resource")

            current_attr_value = attributes
            for part in attr_path:
                current_attr_value = current_attr_value.get(part)
                if current_attr_value is None:
                    all_conditions_met = False
                    break
            
            if not all_conditions_met:
                break

            if value_from_resource_path:
                resource_attr_value = attributes
                for part in value_from_resource_path.split('.'):
                    resource_attr_value = resource_attr_value.get(part)
                    if resource_attr_value is None:
                        all_conditions_met = False
                        break
                if not all_conditions_met:
                    break
                value = resource_attr_value # Use attribute value from resource for comparison

            # Perform conditional judgment
            if operator == "equals":
                if not equals(current_attr_value, value):
                    all_conditions_met = False
            elif operator == "greater_than":
                if not greater_than(current_attr_value, value):
                    all_conditions_met = False
            elif operator == "contains":
                if not contains(current_attr_value, value):
                    all_conditions_met = False
            # ... Other operators

            if not all_conditions_met:
                break
        
        if all_conditions_met:
            if rule_effect == "Permit":
                permit_found = True
            elif rule_effect == "Deny":
                deny_found = True
    
    if combiner == "PermitOverrides":
        return permit_found
    elif combiner == "DenyOverrides":
        return not deny_found
    
    return False # Default deny

```

## Path
`/backend/app/services/abac_policy_evaluator.py`