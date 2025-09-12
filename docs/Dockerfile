# --- Stage 1: Build the static site ---
# Use a Node.js image to build the VitePress site
FROM docker.io/node:22-alpine AS builder

# Update packages to the latest version to fix security vulnerabilities
RUN apk update && apk upgrade --no-cache

# Set the working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json to leverage Docker cache
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy the rest of the documentation source code
COPY . .

# Build the static files
# The output will be in /app/.vitepress/dist
RUN npm run docs:build

# --- Stage 2: Serve the static files with Nginx ---
# Use a lightweight Nginx image
FROM docker.io/nginx:1-alpine

# Update packages to the latest version to fix security vulnerabilities
RUN apk update && apk upgrade --no-cache

# Copy the built static files from the builder stage
COPY --from=builder /app/.vitepress/dist /usr/share/nginx/html

# Copy a custom Nginx configuration file
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Start Nginx when the container launches
CMD ["nginx", "-g", "daemon off;"]