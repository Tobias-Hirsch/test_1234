# `services/abac_functions.py` - ABAC 辅助函数

本文档描述了 `backend/app/services/abac_functions.py` 文件，该文件可能包含用于支持 ABAC（Attribute-Based Access Control）策略评估的辅助函数或工具。

## 功能描述
*   **属性比较**: 提供用于比较不同类型属性的函数（例如，字符串匹配、数值范围检查、集合包含）。
*   **逻辑操作**: 实现策略规则中可能用到的逻辑操作（如 AND, OR, NOT）。
*   **条件判断**: 封装复杂的条件判断逻辑，供策略评估器调用。

## 逻辑实现
该模块会定义一系列可重用的函数，这些函数在 ABAC 策略评估器中被引用，以执行具体的属性比较和逻辑判断。

例如：
```python
from typing import Any, List, Union

def equals(attr1: Any, attr2: Any) -> bool:
    """Checks if two attributes are equal."""
    return attr1 == attr2

def greater_than(attr1: Union[int, float], attr2: Union[int, float]) -> bool:
    """Checks if attr1 is greater than attr2."""
    return attr1 > attr2

def contains(collection: List[Any], item: Any) -> bool:
    """Checks if a collection contains an item."""
    return item in collection

def starts_with(text: str, prefix: str) -> bool:
    """Checks if a string starts with a prefix."""
    return text.startswith(prefix)

def is_member_of_group(user_groups: List[str], required_group: str) -> bool:
    """Checks if a user is a member of a specific group."""
    return required_group in user_groups

# 更多辅助函数...
```

## 路径
`/backend/app/services/abac_functions.py`