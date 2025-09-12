# `core/config.py` - 核心配置

本文档描述了 `backend/app/core/config.py` 文件，该文件用于定义应用程序的各种配置设置。

## 功能描述
*   **环境变量管理**: 集中管理从环境变量中读取的配置，如数据库连接字符串、API 密钥、MinIO 配置等。
*   **类型安全**: 通常使用 Pydantic `BaseSettings` 或类似机制，确保配置值的类型安全和验证。
*   **默认值**: 为配置项提供默认值，以便在环境变量未设置时使用。

## 逻辑实现
该文件通常会定义一个配置类，继承自 `BaseSettings`（如果使用 Pydantic）。类中的属性对应于应用程序的配置项，并通过 `Field` 或直接赋值来设置默认值和类型。例如：

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./sql_app.db"
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    MINIO_ENDPOINT: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_BUCKET_NAME: str = "rosti-rag-files"
    MILVUS_HOST: str = "localhost"
    MILVUS_PORT: str = "19530"
    MILVUS_COLLECTION_NAME: str = "rosti_rag_collection"
    MILVUS_VECTOR_DIM: int = 1536 # For OpenAI embeddings
    AGENTIC_RAG_ENABLE: bool = False
    SMTP_TLS: bool = True
    SMTP_PORT: int = 587
    SMTP_HOST: str
    SMTP_USER: str
    SMTP_PASSWORD: str
    EMAILS_FROM_EMAIL: str
    EMAILS_FROM_NAME: str = "Rosti Support"
    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48
    EMAIL_ACTIVATE_TOKEN_EXPIRE_HOURS: int = 48
    FIRST_SUPERUSER_EMAIL: str
    FIRST_SUPERUSER_PASSWORD: str
    FIRST_SUPERUSER_USERNAME: str = "admin"
    FIRST_SUPERUSER_FULL_NAME: str = "Admin User"
    CONVERSATION_CLEANUP_DAYS: int = 30 # Days after which old conversations are removed

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

通过实例化 `Settings` 类，应用程序可以在运行时访问所有配置值。

## 路径
`/backend/app/core/config.py`