# `Dockerfile` - 后端应用容器化

本文档描述了 `backend/Dockerfile` 文件，它定义了如何构建 Rosti 后端服务的 Docker 镜像。

## 功能描述
*   **基础镜像**: 使用官方 Python 3.10 slim 镜像作为基础，提供轻量级的 Python 运行环境。
*   **工作目录**: 设置容器内的工作目录为 `/app`。
*   **依赖安装**: 复制 `requirements.txt` 文件并安装所有 Python 依赖。
*   **代码复制**: 将整个后端应用代码复制到容器的工作目录。
*   **端口暴露**: 暴露容器的 8000 端口，以便外部可以访问 FastAPI 服务。
*   **启动命令**: 定义容器启动时执行的命令，使用 Uvicorn 运行 FastAPI 应用。

## 逻辑实现
1.  **`FROM python:3.10-slim`**: 选择一个轻量级的 Python 3.10 镜像，减少最终镜像的大小。
2.  **`WORKDIR /app`**: 将 `/app` 设置为后续命令的默认目录，所有文件操作都将相对于此目录进行。
3.  **`COPY requirements.txt .`**: 将宿主机上的 `requirements.txt` 文件复制到容器的 `/app` 目录。
4.  **`RUN pip install --no-cache-dir -r requirements.txt`**: 在容器内安装 `requirements.txt` 中列出的所有 Python 包。`--no-cache-dir` 选项可以避免在镜像中保留 pip 缓存，进一步减小镜像大小。
5.  **`COPY . .`**: 将宿主机当前目录（即 `backend/` 目录）下的所有文件和子目录复制到容器的 `/app` 目录。
6.  **`EXPOSE 8000`**: 声明容器会在 8000 端口上监听连接。这只是一个文档声明，实际的端口映射需要在运行 Docker 容器时通过 `-p` 参数指定。
7.  **`CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]`**: 定义容器启动时执行的默认命令。`uvicorn` 是一个 ASGI 服务器，用于运行 FastAPI 应用。`main:app` 指示 Uvicorn 运行 `main.py` 文件中的 `app` 对象。`--host 0.0.0.0` 使应用监听所有可用的网络接口，`--port 8000` 指定监听端口。

## 路径
`/backend/Dockerfile`