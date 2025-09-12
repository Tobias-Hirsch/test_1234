# `services/abac_policy_evaluator.py` - ABAC 策略评估器

本文档描述了 `backend/app/services/abac_policy_evaluator.py` 文件，该文件是 ABAC（Attribute-Based Access Control）系统的核心组件，负责根据定义的策略规则评估访问请求。

## 功能描述
*   **策略加载**: 从数据库或配置文件中加载 ABAC 策略。
*   **属性匹配**: 将请求中的属性与策略规则中定义的属性进行匹配。
*   **规则评估**: 根据匹配结果和策略的组合逻辑（如“允许优先”或“拒绝优先”）评估访问请求。
*   **决策输出**: 返回访问决策（允许或拒绝）以及可能的原因。

## 逻辑实现
该模块会定义一个或多个函数来执行策略评估。策略通常以 JSON 或其他结构化格式定义，包含规则、条件和效果（允许/拒绝）。

例如：
```python
from typing import Dict, Any
from backend.app.services.abac_functions import equals, greater_than, contains # 导入辅助函数
import logging

logger = logging.getLogger(__name__)

# 示例策略结构
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
#                     {"attribute": "action", "operator": "equals", "value": "read"}
#                 ]
#             },
#             {
#                 "effect": "Deny",
#                 "conditions": [
#                     {"attribute": "environment.ip_address", "operator": "not_in_range", "value": ["192.168.1.0/24"]}
#                 ]
#             }
#         ],
#         "combiner": "PermitOverrides" # 允许优先
#     }
# }

def evaluate_policy(policy_name: str, attributes: Dict[str, Any]) -> bool:
    """
    Evaluates an ABAC policy based on the given attributes.
    """
    # 实际应用中，策略会从数据库加载
    # policy = get_policy_from_db(policy_name)
    # if not policy:
    #     logger.warning(f"Policy '{policy_name}' not found.")
    #     return False # 默认拒绝

    # 简化示例：假设策略已硬编码或通过某种方式获取
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
    combiner = policy.get("combiner", "DenyOverrides") # 默认拒绝优先

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
                value = resource_attr_value # 使用资源中的属性值进行比较

            # 执行条件判断
            if operator == "equals":
                if not equals(current_attr_value, value):
                    all_conditions_met = False
            elif operator == "greater_than":
                if not greater_than(current_attr_value, value):
                    all_conditions_met = False
            elif operator == "contains":
                if not contains(current_attr_value, value):
                    all_conditions_met = False
            # ... 其他操作符

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
    
    return False # 默认拒绝

```

## 路径
`/backend/app/services/abac_policy_evaluator.py`