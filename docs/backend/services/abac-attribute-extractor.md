# `services/abac_attribute_extractor.py` - ABAC 属性提取器

本文档描述了 `backend/app/services/abac_attribute_extractor.py` 文件，该文件负责从请求上下文、用户会话和资源数据中提取用于 ABAC（Attribute-Based Access Control）策略评估的属性。

## 功能描述
*   **属性收集**: 从各种来源（如 HTTP 请求头、URL 参数、请求体、当前认证用户、数据库中的资源信息）收集相关属性。
*   **统一属性格式**: 将收集到的属性转换为统一的格式，以便策略评估器使用。

## 逻辑实现
该模块会定义函数来解析请求和数据，并提取出主体（Subject）、客体（Object）、动作（Action）和环境（Environment）属性。

例如：
```python
from typing import Dict, Any
from fastapi import Request
from sqlalchemy.orm import Session
from backend.app.models.database import User # 假设有User模型
# from backend.app.models.database import Resource # 假设有Resource模型

def extract_abac_attributes(
    request: Request,
    current_user: User,
    db: Session,
    resource_id: Optional[int] = None,
    action: str = ""
) -> Dict[str, Any]:
    """
    Extracts attributes for ABAC policy evaluation.
    """
    attributes = {
        "subject": {
            "user_id": current_user.id,
            "username": current_user.username,
            "is_superuser": current_user.is_superuser,
            # ... 其他用户属性，如角色、部门等
        },
        "action": action,
        "resource": {},
        "environment": {
            "ip_address": request.client.host,
            "timestamp": datetime.utcnow().isoformat(),
            # ... 其他环境属性，如时间、地点等
        }
    }

    if resource_id:
        # 假设从数据库中获取资源信息
        # resource = db.query(Resource).filter(Resource.id == resource_id).first()
        # if resource:
        #     attributes["resource"] = resource.to_dict() # 将资源对象转换为字典
        pass # 实际项目中需要从数据库加载资源属性

    # 可以从请求体中提取更多属性
    # if request.method == "POST" or request.method == "PUT":
    #     request_body = await request.json()
    #     attributes["request_body"] = request_body

    return attributes
```

## 路径
`/backend/app/services/abac_attribute_extractor.py`