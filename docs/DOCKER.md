# Docker Deployment Guide

This guide covers how to build, run, and deploy the User Management Flask Server using Docker.

## Quick Start

### Using Docker Compose (Recommended)

1. **Production environment:**
   ```bash
   docker-compose -f docker/docker-compose.prod.yml up --build
   ```

2. **Development environment:**
   ```bash
   docker-compose -f docker/docker-compose.dev.yml up --build
   ```

3. **Run in background:**
   ```bash
   docker-compose -f docker/docker-compose.prod.yml up -d
   ```

4. **Stop the server:**
   ```bash
   docker-compose -f docker/docker-compose.prod.yml down
   ```

### Using Docker directly

1. **Build the image:**
   ```bash
   docker build -t user-management-server -f docker/Dockerfile .
   ```

2. **Run the container:**
   ```bash
   docker run -p 5000:5000 --name flask-server user-management-server
   ```

## Configuration

### Environment Variables

The following environment variables can be used to configure the server:

| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_ENV` | `production` | Flask environment (development/production) |
| `FLASK_DEBUG` | `0` | Enable Flask debug mode (0/1) |
| `PORT` | `5000` | Port to bind the server to |

### Example with custom configuration:
```bash
docker run -p 8080:8080 -e PORT=8080 -e FLASK_ENV=development user-management-server
```

## Data Persistence

The server uses SQLite for data storage. To persist data between container restarts:

### Using Docker Compose (Automatic)
The `docker-compose.yml` files automatically mount a `./data` directory for persistence.

### Using Docker directly
```bash
# Create a data directory
mkdir -p ./data

# Run with volume mount
docker run -p 5000:5000 -v $(pwd)/data:/app/data user-management-server
```

## Development Mode

For development with live code reloading:

```bash
# Start development service
docker-compose -f docker/docker-compose.dev.yml up

# Or use the management script
python scripts/docker_build.py up --env dev
```

## Health Checks

The container includes built-in health checks:

```bash
# Check container health
docker ps

# View health check logs
docker inspect --format='{{json .State.Health}}' user-management-server
```

## Production Deployment

### Security Features

The Docker image includes several security best practices:

- **Non-root user**: Runs as `appuser` (not root)
- **Minimal base image**: Uses Python slim image
- **No unnecessary packages**: Only installs required dependencies
- **Health checks**: Built-in health monitoring

### Resource Limits

Resource limits are pre-configured in the production compose file (`docker/docker-compose.prod.yml`):

```yaml
deploy:
  resources:
    limits:
      cpus: '0.5'
      memory: 512M
    reservations:
      cpus: '0.25'
      memory: 256M
```

### Scaling

To run multiple instances:

```bash
# Scale to 3 instances
docker-compose -f docker/docker-compose.prod.yml up --scale flask-server=3
```

## Monitoring

### Logs

```bash
# View logs (production)
docker-compose -f docker/docker-compose.prod.yml logs flask-server

# Follow logs (development)
docker-compose -f docker/docker-compose.dev.yml logs -f flask-server-dev

# View logs for specific container
docker logs user-management-server
```

### Health Endpoint

The server exposes a health endpoint at `/health`:

```bash
curl http://localhost:5000/health
```

## Troubleshooting

### Common Issues

1. **Port already in use:**
   ```bash
   # Use different port
   docker run -p 5001:5000 user-management-server
   ```

2. **Permission denied on data directory:**
   ```bash
   # Fix permissions
   sudo chown -R 1000:1000 ./data
   ```

3. **Container won't start:**
   ```bash
   # Check logs
   docker logs user-management-server
   
   # Run interactively for debugging
   docker run -it --entrypoint /bin/bash user-management-server
   ```

### Debug Mode

To run with debug information:

```bash
docker run -p 5000:5000 -e FLASK_DEBUG=1 -e FLASK_ENV=development user-management-server
```

## API Testing

Once the container is running, test the API:

```bash
# Health check
curl http://localhost:5000/health

# Create a user
curl -X POST http://localhost:5000/users \
  -H "Content-Type: application/json" \
  -d '{"id":"123456782","name":"John Doe","phone":"+972501234567","address":"123 Main St"}'

# Get all users
curl http://localhost:5000/users

# Get specific user
curl http://localhost:5000/users/123456782
```

## Multi-stage Builds (Advanced)

For optimized production images, consider using multi-stage builds:

```dockerfile
# Development stage
FROM python:3.13-slim as development
# ... development setup

# Production stage
FROM python:3.13-slim as production
# ... production setup
```

Build specific stage:
```bash
docker build --target production -t user-management-server:prod .
```