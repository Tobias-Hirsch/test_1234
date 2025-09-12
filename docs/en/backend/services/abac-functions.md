# `services/abac_functions.py` - ABAC Helper Functions

This document describes the `backend/app/services/abac_functions.py` file, which may contain helper functions or utilities used to support ABAC (Attribute-Based Access Control) policy evaluation.

## Function Description
*   **Attribute Comparison**: Provides functions for comparing different types of attributes (e.g., string matching, numerical range checking, set inclusion).
*   **Logical Operations**: Implements logical operations (e.g., AND, OR, NOT) that might be used in policy rules.
*   **Conditional Judgment**: Encapsulates complex conditional judgment logic for use by the policy evaluator.

## Logic Implementation
This module defines a series of reusable functions that are referenced by the ABAC policy evaluator to perform specific attribute comparisons and logical judgments.

For example:
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

# More helper functions...
```

## Path
`/backend/app/services/abac_functions.py`