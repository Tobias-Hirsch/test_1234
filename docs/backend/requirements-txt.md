# `requirements.txt` - 后端依赖管理

本文档描述了 `backend/requirements.txt` 文件，它列出了 Rosti 后端服务所需的所有 Python 依赖包。

## 功能描述
*   **依赖声明**: 明确声明了项目运行所需的所有第三方 Python 库及其版本。
*   **环境再现**: 确保在不同环境中（如开发、测试、生产）可以安装相同版本的依赖，保证环境一致性。
*   **自动化安装**: Dockerfile 和其他自动化脚本（如 CI/CD）可以使用此文件来自动安装项目依赖。

## 逻辑实现
`requirements.txt` 文件是一个纯文本文件，每行包含一个 Python 包的名称，通常后面跟着版本说明符（例如 `==` 用于精确版本，`>=` 用于最小版本）。

文件中列出的主要依赖及其作用：
*   **`fastapi`**: 用于构建高性能 API 的现代、快速（基于 Starlette 和 Pydantic）Web 框架。
*   **`uvicorn`**: 一个 ASGI 服务器实现，用于运行 FastAPI 应用程序。
*   **`python-dotenv`**: 用于从 `.env` 文件加载环境变量，方便配置管理。
*   **`langchain-openai`**: LangChain 框架与 OpenAI 模型的集成，用于 LLM 交互。
*   **`pymysql`**: Python 的 MySQL 客户端库，用于与 MySQL 数据库交互。
*   **`python-multipart`**: 处理 `multipart/form-data` 请求，支持文件上传。
*   **`sqlalchemy`**: Python SQL 工具包和对象关系映射 (ORM)，用于数据库操作。
*   **`python-jose[cryptography]`**: 用于处理 JSON Web Tokens (JWT)，支持认证和授权。
*   **`apscheduler`**: 一个轻量级的任务调度库，用于在后台运行定时任务。
*   **`pillow`**: 图像处理库。
*   **`minio`**: MinIO 客户端库，用于与 MinIO 对象存储服务交互，进行文件上传和下载。
*   **`azure-cognitiveservices-search-websearch`**: Azure 认知服务 Web 搜索 API 的客户端库。
*   **`httpx`**: 现代、快速的 Python HTTP 客户端。
*   **`requests`**: 简单易用的 HTTP 库。
*   **`Authlib`**: 一个用于构建 OAuth、OpenID Connect 和 JWT 的 Python 库。
*   **`PyPDF2`**: 一个用于处理 PDF 文件的 Python 库。
*   **`ldap3`**: 一个用于与 LDAP 服务器交互的 Python 库。

## 路径
`/backend/requirements.txt`