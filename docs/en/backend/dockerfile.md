# `Dockerfile` - Backend Application Containerization

This document describes the `backend/Dockerfile` file, which defines how to build the Docker image for the Rosti backend service.

## Function Description
*   **Base Image**: Uses the official Python 3.10 slim image as a base, providing a lightweight Python runtime environment.
*   **Working Directory**: Sets the working directory inside the container to `/app`.
*   **Dependency Installation**: Copies the `requirements.txt` file and installs all Python dependencies.
*   **Code Copying**: Copies the entire backend application code to the container's working directory.
*   **Port Exposure**: Exposes port 8000 of the container, allowing external access to the FastAPI service.
*   **Startup Command**: Defines the command to be executed when the container starts, running the FastAPI application with Uvicorn.

## Logic Implementation
1.  **`FROM python:3.10-slim`**: Selects a lightweight Python 3.10 image to reduce the final image size.
2.  **`WORKDIR /app`**: Sets `/app` as the default directory for subsequent commands; all file operations will be relative to this directory.
3.  **`COPY requirements.txt .`**: Copies the `requirements.txt` file from the host to the `/app` directory in the container.
4.  **`RUN pip install --no-cache-dir -r requirements.txt`**: Installs all Python packages listed in `requirements.txt` inside the container. The `--no-cache-dir` option prevents pip from retaining cache in the image, further reducing image size.
5.  **`COPY . .`**: Copies all files and subdirectories from the host's current directory (i.e., the `backend/` directory) to the `/app` directory in the container.
6.  **`EXPOSE 8000`**: Declares that the container will listen for connections on port 8000. This is merely a documentation declaration; actual port mapping needs to be specified using the `-p` parameter when running the Docker container.
7.  **`CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]`**: Defines the default command to be executed when the container starts. `uvicorn` is an ASGI server used to run FastAPI applications. `main:app` instructs Uvicorn to run the `app` object in the `main.py` file. `--host 0.0.0.0` makes the application listen on all available network interfaces, and `--port 8000` specifies the listening port.

## Path
`/backend/Dockerfile`