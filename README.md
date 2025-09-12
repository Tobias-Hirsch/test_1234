# Rosti_RAG: Enterprise-level Intelligent Q&A Platform

Rosti_RAG is an enterprise-level intelligent question-and-answer platform designed to provide efficient and secure knowledge management and retrieval services for businesses. The platform is built on a modern technology stack, combining large language models (LLM) with Retrieval-Augmented Generation (RAG) technology to deliver accurate and context-aware answers. It also features a sophisticated Attribute-Based Access Control (ABAC) system to ensure data security and compliance.

## ✨ Features

*   **Intelligent Q&A:** Leverages RAG technology to provide accurate answers based on the enterprise's knowledge base.
*   **Fine-grained Access Control:** Implements an ABAC model to control user access to sensitive information dynamically.
*   **User & Role Management:** Supports comprehensive user and role management functionalities.
*   **Third-party Authentication:** Integrates with third-party authentication services for seamless login.
*   **Containerized Deployment:** Uses Docker for easy deployment and scalability.
*   **Separation of Frontend and Backend:** A modern architecture that is easy to maintain and develop.

## 🛠️ Technology Stack

*   **Backend:**
    *   **Framework:** FastAPI
    *   **Language:** Python 3.9+
    *   **Database:** MongoDB, Milvus (for vector storage)
    *   **Object Storage:** MinIO
    *   **Authentication:** JWT
*   **Frontend:**
    *   **Framework:** Vue 3
    *   **Language:** TypeScript
    *   **UI Library:** Element Plus
    *   **State Management:** Pinia
    *   **Routing:** Vue Router
*   **Deployment:**
    *   Docker, Docker Compose
    *   Nginx

## 🚀 Getting Started

### Prerequisites

*   Docker and Docker Compose
*   Git

### Installation & Launch

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd rosti_ai
    ```

2.  **Configure environment variables:**

    Create a `.env` file in the `backend` directory by copying the example file:
    ```bash
    cp backend/.env.example backend/.env
    ```
    Then, modify the `backend/.env` file with your specific configurations (e.g., database credentials, secret keys).

3.  **setup MINIO access key and secret key**
    In browser visit http://localhost:9000 (port number should be the same as setting in docker-compose for minio part)
    Log into minio management plaform with predefined user and password(in docker-compose.yml)，
    create key then copy the value to .env 
    MINIO_ACCESS_KEY=
    MINIO_SECRET_KEY=

4.  **Build and run with Docker Compose:**
    Dev Environment:
    ```bash
    docker-compose -f docker-compose.dev.yml up --build
    ```
    Production Environment:
    ```bash
    docker-compose -f docker-compose.dev.yml up --build
    ```
    This command will build the images and start all the services required for the development environment.

5.  **Access the application:**
    *   **Gateway:88** `http://localhost:80`
    *   **Frontend:** `http://localhost:8080`
    *   **Backend API Docs:** `http://localhost:8000/docs`

## 📂 Project Structure

```
.
├── backend/         # Backend code (FastAPI)
│   ├── app/
│   │   ├── core/      # Core components (config, security)
│   │   ├── models/    # Data models (placeholder, models are dynamically loaded)
│   │   ├── routers/   # API endpoints
│   │   ├── schemas/   # Pydantic schemas
│   │   └── services/  # Business logic
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/        # Frontend code (Vue.js)
│   ├── src/
│   │   ├── components/
│   │   ├── router/
│   │   ├── stores/
│   │   └── views/
│   └── Dockerfile
├── docker-compose.yml # Production deployment
├── docker-compose.dev.yml # Development deployment
└── README.md
```

## ⚙️ Configuration

All backend configurations are managed through environment variables in the `backend/.env` file. Please refer to `backend/.env.example` for a complete list of configurable variables.

---

This `README.md` provides a comprehensive overview of the project. You can further customize it by adding more details about specific features, API documentation, or contribution guidelines.



echo "# rosti_ai" >> README.md
git init
git add README.md
git commit -m "first commit"
git branch -M main
git remote add origin git@github.com:Jeffhaha/rosti_ai.git
git push -u origin main

git remote add origin git@github.com:Jeffhaha/rosti_ai.git
git branch -M main
git push -u origin main
