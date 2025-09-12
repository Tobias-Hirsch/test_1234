# Stage 1: Build the Vue.js application
# Use a specific Node.js version for reproducibility
FROM node:22-alpine AS build-stage

# Update packages to the latest version to patch vulnerabilities
RUN apk --no-cache upgrade

# Set the working directory
WORKDIR /app

# Copy package.json and package-lock.json for dependency caching
COPY package*.json ./

# Install dependencies
RUN npm ci && npm cache clean --force

# Copy the rest of the application source code
COPY . .

# Build the application for production
# The output will be in the /app/dist directory
RUN npm run build

# Stage 2: Serve the application using a lightweight Nginx server
FROM nginx:1-alpine AS production-stage

# Update packages to the latest version to patch vulnerabilities
RUN apk --no-cache upgrade

# Copy the built static assets from the build stage to the Nginx public directory
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Copy the custom Nginx configuration for the frontend SPA
# This file will be created in the next step
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80 to be accessible by the gateway Nginx
EXPOSE 80

# Start Nginx in the foreground
CMD ["nginx", "-g", "daemon off;"]
