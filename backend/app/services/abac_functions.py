from datetime import datetime
from typing import Any

def is_resource_owner(user_id: str, resource_owner_id: str) -> bool:
    """
    检查用户是否是资源的拥有者。
    """
    return str(user_id) == str(resource_owner_id)

def is_within_working_hours(current_time: datetime) -> bool:
    """
    检查当前时间是否在工作时间 (例如 9 AM - 5 PM)。
    """
    return 9 <= current_time.hour < 17

# 可以在这里添加更多自定义函数