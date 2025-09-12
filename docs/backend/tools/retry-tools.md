# `tools/retry_tools.py` - 重试工具

本文档描述了 `backend/app/tools/retry_tools.py` 文件，该文件包含了用于实现函数重试逻辑的工具函数，以提高系统在面对暂时性错误时的健壮性。

## 功能描述
*   **函数重试**: 提供一个装饰器或函数，用于在被装饰的函数执行失败时自动重试。
*   **可配置策略**: 支持配置重试次数、重试间隔、指数退避等策略。
*   **错误捕获**: 捕获特定类型的异常并触发重试。

## 逻辑实现
该模块通常会使用自定义装饰器或 `tenacity` 等库来实现重试逻辑。

例如，一个简单的重试装饰器：
```python
import time
import logging
from functools import wraps

logger = logging.getLogger(__name__)

def retry(max_attempts: int = 3, delay_seconds: int = 1, backoff_factor: int = 2, exceptions=(Exception,)):
    """
    A decorator to retry a function call if it fails.

    Args:
        max_attempts (int): Maximum number of attempts.
        delay_seconds (int): Initial delay between retries in seconds.
        backoff_factor (int): Factor by which the delay increases each time.
        exceptions (tuple): A tuple of exceptions to catch and retry on.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_delay = delay_seconds
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    logger.warning(f"Attempt {attempt}/{max_attempts} failed for {func.__name__}: {e}")
                    if attempt < max_attempts:
                        logger.info(f"Retrying {func.__name__} in {current_delay} seconds...")
                        await asyncio.sleep(current_delay) # For async functions
                        current_delay *= backoff_factor
                    else:
                        logger.error(f"All {max_attempts} attempts failed for {func.__name__}.")
                        raise
        return wrapper
    return decorator

# 示例用法：
# @retry(max_attempts=5, delay_seconds=2, exceptions=(SomeAPIError, AnotherError))
# async def call_external_api():
#     # ... API 调用逻辑
#     pass
```

## 路径
`/backend/app/tools/retry_tools.py`