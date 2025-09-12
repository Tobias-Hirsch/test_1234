# `main.py` - Backend Application Entry Point

This document describes the `backend/main.py` file, which is the core entry point for the Rosti backend service.

## Function Description
*   **FastAPI Application Initialization**: Creates and configures the FastAPI application instance.
*   **Environment Variable Loading**: Uses `python-dotenv` to load environment variables from the `.env` file.
*   **Lifecycle Management**: Defines a `lifespan` context manager to handle application startup (e.g., database table creation, Milvus connection, scheduled task scheduling) and shutdown (e.g., scheduler shutdown) events.
*   **Middleware Configuration**: Adds CORS middleware to handle cross-origin requests and configures Session middleware for OAuth.
*   **Route Registration**: Includes API routes for all major functional modules, such as authentication, RAG, chat, user management, settings, etc.
*   **Health Check**: Provides a simple health check endpoint at the root path `/`.

## Logic Implementation
1.  **Environment Variables**: `load_dotenv(override=True)` ensures that configurations in the `.env` file are loaded with priority.
2.  **Logging**: Configures the `logging` module to record application startup and shutdown information.
3.  **Database and Milvus**: Calls `create_database_tables()` to initialize the database and `await connect_to_milvus()` to establish a Milvus connection upon application startup.
4.  **Scheduled Tasks**: Uses `AsyncIOScheduler` to schedule background tasks, such as `remove_expired_unactivated_users` and `remove_old_conversations`, to periodically clean up data.
5.  **CORS**: `CORSMiddleware` is configured to allow cross-origin requests from specified sources, ensuring the frontend can communicate with the backend.
6.  **Session**: `SessionMiddleware` uses `SECRET_KEY` to manage sessions, which is crucial for authentication flows like OAuth.
7.  **Route Inclusion**: Imports and registers API routes for various modules defined under `backend/app/routers` via `app.include_router()`, such as `authentication.router`, `rag.router`, `chat.router`, etc.

## Path
`/backend/main.py`