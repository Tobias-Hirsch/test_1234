# System Architecture

This section describes the overall system architecture of the Rosti product, including frontend, backend, database, and external service components.

## 1. Overall Architecture Overview

The Rosti product adopts a microservice architecture with separate frontend and backend, communicating via RESTful APIs.

## 2. Frontend Architecture

*   **Tech Stack**: Vue.js, TypeScript, Element Plus (UI component library).
*   **Build Tool**: Vite.
*   **Modules**: Chat interface, knowledge base management, user authentication, settings.

## 3. Backend Architecture

*   **Tech Stack**: Python, FastAPI.
*   **Core Services**:
    *   **Authentication Service**: User registration, login, permission management.
    *   **Chat Service**: Session management, message storage, attachment handling.
    *   **RAG Service**: Document parsing, vector embedding, knowledge retrieval.
    *   **Tool Service**: Integrates online search, PDF/Word/Excel content extraction, etc.
*   **Asynchronous Processing**: Uses `async/await` and FastAPI's asynchronous features to handle high-concurrency requests.

## 4. Databases and Storage

*   **Relational Database**: PostgreSQL/MySQL (accessed via SQLAlchemy ORM), used for storing structured data such as users and RAG entries.
*   **Document Database**: MongoDB (accessed via PyMongo), used for storing chat messages, attachment metadata, and RAG document summaries.
*   **Vector Database**: Milvus, used for storing vector embeddings of document chunks, supporting efficient similarity search.
*   **Object Storage**: MinIO, used for storing raw document files and chat attachments.

## 5. External Services and Integrations

*   **Large Language Models (LLM)**: DeepSeek (or other Ollama-compatible models), integrated via API for generating chat responses and RAG answers.
*   **MinIO**: Used for file storage.
*   **DuckDuckGo Search API**: Used for online search functionality.

## 6. Deployment and Operations

*   **Containerization**: Uses Docker for application containerization.
*   **Orchestration**: Can be deployed via Docker Compose or Kubernetes.
*   **Monitoring and Logging**: Integrates logging systems and monitoring tools.