# Server Startup Guide

## Starting the Server

### Method 1: Using the Main Entry Point (Recommended)
```bash
cd basic-flask-server
python main.py
```

### Method 2: Running the Server Module Directly
```bash
cd basic-flask-server
python app/server.py
```

### Method 3: Using Python Module Syntax
```bash
cd basic-flask-server
python -m app.server
```

## Complete Startup Sequence

### First Time Setup
```bash
# Navigate to project directory
cd basic-flask-server

# Install dependencies
pip install -r requirements.txt

# Initialize database
python scripts/init_database.py --init

# (Optional) Create sample data for testing
python scripts/init_database.py --sample-data
```

### Start the Server
```bash
# Start the server
python main.py
```

### Expected Output
```
Starting User Management Flask Server (Class-based)...
Available endpoints:
  GET  /              - Home page
  POST /users         - Create new user
  GET  /users/<id>    - Get user by Israeli ID
  GET  /users         - List all user IDs
  GET  /health        - Health check

Server running on http://0.0.0.0:5000
```

## Server Configuration

The server starts with default settings from `config/settings.yaml`:

- **Host**: `0.0.0.0` (accessible from any network interface)
- **Port**: `5000`
- **Debug Mode**: `true` (auto-reload on code changes)
- **Threading**: `true` (handle multiple requests)

### Configuration File Structure
```yaml
server:
  host: "0.0.0.0"
  port: 5000
  debug: true
  threaded: true
```

## Environment Variable Overrides

You can override configuration settings using environment variables:

### Windows Command Prompt
```cmd
set SERVER_HOST=127.0.0.1
set SERVER_PORT=8080
set DEBUG=false
python main.py
```

### Windows PowerShell
```powershell
$env:SERVER_HOST="127.0.0.1"
$env:SERVER_PORT="8080"
$env:DEBUG="false"
python main.py
```

### macOS/Linux
```bash
export SERVER_HOST=127.0.0.1
export SERVER_PORT=8080
export DEBUG=false
python main.py
```

## Environment-Specific Configuration

### Development Environment (Default)
```bash
# Uses config/settings.yaml defaults
python main.py
```

### Production Environment
```bash
# Create production config file
cp config/settings.yaml config/production.yaml

# Edit config/production.yaml with production settings
# Then set environment
set FLASK_ENV=production
python main.py
```

Example `config/production.yaml`:
```yaml
server:
  host: "127.0.0.1"
  port: 8080
  debug: false
  threaded: true

database:
  filename: "production.db"
  echo: false

logging:
  level: "WARNING"
```

## Testing the Server

### Method 1: Using the API Test Script
```bash
# In another terminal window
python scripts/test_api.py
```

### Method 2: Using curl Commands
```bash
# Health check
curl http://localhost:5000/health

# Home page
curl http://localhost:5000/

# Create a user
curl -X POST http://localhost:5000/users \
  -H "Content-Type: application/json" \
  -d '{
    "id": "123456782",
    "name": "John Doe",
    "phone": "+972501234567",
    "address": "123 Main St, Tel Aviv"
  }'

# Get user
curl http://localhost:5000/users/123456782

# List all users
curl http://localhost:5000/users
```

### Method 3: Using a Web Browser
Navigate to:
- `http://localhost:5000/` - Home page
- `http://localhost:5000/health` - Health check
- `http://localhost:5000/users` - User list

## Server Management

### Stopping the Server
Press `Ctrl+C` in the terminal where the server is running.

### Restarting the Server
1. Stop the server with `Ctrl+C`
2. Start it again with `python main.py`

Note: In debug mode, the server automatically reloads when you modify code files.

### Checking Server Status
```bash
# Check if server is running
curl -f http://localhost:5000/health && echo "Server is running" || echo "Server is not running"
```

## Troubleshooting

### Port Already in Use
If you get a "port already in use" error:

```bash
# Use a different port
set SERVER_PORT=5001
python main.py
```

### Database Issues
If you encounter database errors:

```bash
# Check database status
python scripts/init_database.py --status

# Reinitialize database if needed
python scripts/init_database.py --init --force
```

### Import Errors
If you get import errors:

1. Make sure you're in the project root directory
2. Ensure all dependencies are installed:
   ```bash
   pip install -r requirements.txt
   ```

### Permission Issues
On some systems, you might need to ensure the directory is writable:
```bash
chmod 755 .
```

## Server Logs

The server logs to the console by default. In debug mode, you'll see:
- Request logs
- Database operations (if `database.echo: true`)
- Error messages and stack traces

### Enabling SQL Query Logging
Edit `config/settings.yaml`:
```yaml
database:
  echo: true  # Shows SQL queries in console
```

## Production Deployment

For production deployment, consider:

1. **Use a production WSGI server** (like Gunicorn):
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:8080 app.server:app
   ```

2. **Set production environment**:
   ```bash
   set FLASK_ENV=production
   ```

3. **Use production configuration**:
   ```bash
   # Create config/production.yaml with production settings
   ```

4. **Run database migrations**:
   ```bash
   python scripts/run_migrations.py --migrate
   ```

## Server Features

- **Auto-reload**: Code changes automatically restart the server in debug mode
- **Multi-threading**: Can handle multiple concurrent requests
- **Health monitoring**: Built-in health check endpoint
- **Database integration**: Automatic database connection and management
- **Error handling**: Comprehensive error responses with proper HTTP status codes
- **Configuration management**: Flexible configuration with environment overrides