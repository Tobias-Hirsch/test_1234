# `requirements.txt` - Backend Dependency Management

This document describes the `backend/requirements.txt` file, which lists all Python dependencies required for the Rosti backend service.

## Function Description
*   **Dependency Declaration**: Explicitly declares all third-party Python libraries and their versions required for the project to run.
*   **Environment Reproduction**: Ensures that the same versions of dependencies can be installed across different environments (e.g., development, testing, production), guaranteeing environment consistency.
*   **Automated Installation**: Dockerfiles and other automation scripts (e.g., CI/CD) can use this file to automatically install project dependencies.

## Logic Implementation
The `requirements.txt` file is a plain text file, with each line containing the name of a Python package, usually followed by a version specifier (e.g., `==` for exact version, `>=` for minimum version).

Key dependencies listed in the file and their roles:
*   **`fastapi`**: A modern, fast (based on Starlette and Pydantic) web framework for building high-performance APIs.
*   **`uvicorn`**: An ASGI server implementation used to run FastAPI applications.
*   **`python-dotenv`**: Used to load environment variables from `.env` files, facilitating configuration management.
*   **`langchain-openai`**: Integration of the LangChain framework with OpenAI models for LLM interaction.
*   **`pymysql`**: Python's MySQL client library for interacting with MySQL databases.
*   **`python-multipart`**: Handles `multipart/form-data` requests, supporting file uploads.
*   **`sqlalchemy`**: Python SQL toolkit and Object Relational Mapper (ORM) for database operations.
*   **`python-jose[cryptography]`**: Used for processing JSON Web Tokens (JWT), supporting authentication and authorization.
*   **`apscheduler`**: A lightweight task scheduling library for running scheduled tasks in the background.
*   **`pillow`**: Image processing library.
*   **`minio`**: MinIO client library for interacting with the MinIO object storage service for file uploads and downloads.
*   **`azure-cognitiveservices-search-websearch`**: Client library for Azure Cognitive Services Web Search API.
*   **`httpx`**: Modern, fast Python HTTP client.
*   **`requests`**: Simple and easy-to-use HTTP library.
*   **`Authlib`**: A Python library for building OAuth, OpenID Connect, and JWT.
*   **`PyPDF2`**: A Python library for working with PDF files.
*   **`ldap3`**: A Python library for interacting with LDAP servers.

## Path
`/backend/requirements.txt`