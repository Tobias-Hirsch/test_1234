# Stage 1: Builder - More efficient wheel building
FROM python:3.12-slim AS builder

WORKDIR /usr/src/app

# Install build dependencies
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple wheel setuptools

# Copy only necessary files for building the wheel to maximize cache usage.
# First, copy files that define dependencies.
COPY setup.py requirements.txt ./
# Then, copy the application source code.
COPY app ./app

# Build the wheel. This step only re-runs if the source code or setup files change.
RUN python setup.py bdist_wheel


# Stage 2: Final - Create the optimized production image
FROM python:3.12-slim

# Create a non-root user and group
RUN addgroup --system app && adduser --system --ingroup app --home /app app

# Set the working directory
WORKDIR /app

# Create and set permissions for the logs directory
RUN mkdir -p /app/logs/api_log && chown -R app:app /app/logs

# Update system packages and install build-essential for some dependencies
RUN sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list.d/debian.sources && \
    apt-get update && \
    # Install build-essential for compiling some Python packages,
    # and other system libraries required by sub-dependencies of 'mineru',
    # and ca-certificates for SSL trust management.
    # - libgl1-mesa-glx provides libGL.so.1 (for OpenCV) libgl1 replace libgl1-mesa-glx
    # - libglib2.0-0 provides libgthread-2.0.so.0 (for OpenCV/GTK)
    apt-get install -y --no-install-recommends build-essential libgl1 libglib2.0-0 ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# --- Trust Corporate CA Certificate ---
# Copy the custom CA certificate from the build context into the container.
# Ensure you place your CA certificate (e.g., corp-root-ca.crt) in the 'backend/certs/' directory.
# COPY certs/*.crt /usr/local/share/ca-certificates/ wait for them from Rosti
# Update the system's certificate store.
# RUN update-ca-certificates
# --- End Certificate Trust ---

# --- Optimized Dependency Installation ---
# 1. Copy only the requirements file first.
COPY --from=builder /usr/src/app/requirements.txt .

# 2. Install dependencies from requirements.txt. This layer will be cached
# as long as requirements.txt does not change, saving significant time.
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt 

# Install mineru as a direct dependency for the backend to use as a client library
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple 'mineru[core]'

# 3. Copy the built wheel from the builder stage.
COPY --from=builder /usr/src/app/dist/*.whl .

# 4. Install the application wheel WITHOUT its dependencies, as they are
# already installed. This is a very fast operation.
RUN pip install --no-cache-dir --no-deps rosti_backend-0.1.0-py3-none-any.whl && \
    rm rosti_backend-0.1.0-py3-none-any.whl

# --- Alembic Support ---
# Copy Alembic configuration and scripts into the final image so that
# database migrations can be run from within the container.
COPY alembic.ini .
COPY alembic ./alembic
# --- End Alembic Support ---

# Ensure the app user has ownership of the app directory
RUN chown -R app:app /app

# Set the home directory for the app user to a writable location
ENV HOME=/app

# Switch to the non-root user
USER app

# Expose the port the app runs on
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
