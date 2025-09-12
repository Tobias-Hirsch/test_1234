# `main.py` - 后端应用入口

本文档描述了 `backend/main.py` 文件，它是 Rosti 后端服务的核心入口点。

## 功能描述
*   **FastAPI 应用初始化**: 创建并配置 FastAPI 应用程序实例。
*   **环境变量加载**: 使用 `python-dotenv` 加载 `.env` 文件中的环境变量。
*   **生命周期管理**: 定义 `lifespan` 上下文管理器，处理应用启动（如数据库表创建、Milvus 连接、定时任务调度）和关闭（如关闭调度器）事件。
*   **中间件配置**: 添加 CORS 中间件以处理跨域请求，并配置 Session 中间件用于 OAuth。
*   **路由注册**: 包含所有主要功能模块的 API 路由，如认证、RAG、聊天、用户管理、设置等。
*   **健康检查**: 提供根路径 `/` 的简单健康检查接口。

## 逻辑实现
1.  **环境变量**: `load_dotenv(override=True)` 确保 `.env` 文件中的配置优先加载。
2.  **日志**: 配置 `logging` 模块以记录应用启动和关闭信息。
3.  **数据库与 Milvus**: 在应用启动时调用 `create_database_tables()` 初始化数据库，并调用 `await connect_to_milvus()` 建立 Milvus 连接。
4.  **定时任务**: 使用 `AsyncIOScheduler` 调度后台任务，例如 `remove_expired_unactivated_users` 和 `remove_old_conversations`，以定期清理数据。
5.  **CORS**: `CORSMiddleware` 配置允许来自指定源的跨域请求，确保前端可以与后端通信。
6.  **Session**: `SessionMiddleware` 使用 `SECRET_KEY` 来管理会话，这对于 OAuth 等认证流程至关重要。
7.  **路由包含**: 通过 `app.include_router()` 导入并注册 `backend/app/routers` 目录下定义的各个模块的 API 路由，例如 `authentication.router`, `rag.router`, `chat.router` 等。

## 路径
`/backend/main.py`