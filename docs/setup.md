---
title: DIAL Simple Agent - Setup Guide
description: Complete environment configuration, dependency installation, and troubleshooting for local development
version: 1.0.0
last_updated: 2025-12-30
related: [README.md, architecture.md, api.md]
tags: [setup, installation, docker, environment, configuration]
---

# Setup Guide

> Step-by-step instructions for configuring your development environment

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Detailed Setup](#detailed-setup)
- [Configuration](#configuration)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)
- [Advanced Setup](#advanced-setup)

## Prerequisites

### System Requirements

- **OS**: macOS, Linux, or Windows with WSL2
- **Python**: 3.11 or higher
- **Docker**: 20.10+ with Docker Compose
- **Network**: EPAM VPN connection for DIAL API access
- **RAM**: Minimum 4GB available (for Docker containers)
- **Disk**: 500MB free space

### Required Accounts & Access

1. **DIAL API Key**: Request from [EPAM Service Portal](https://support.epam.com/ess?id=sc_cat_item&table=sc_cat_item&sys_id=910603f1c3789e907509583bb001310c)
2. **EPAM VPN**: Install and configure GlobalProtect or equivalent
3. **Docker Hub**: No login required (uses public images)

### Check Prerequisites

```bash
# Verify Python version
python3 --version
# Expected: Python 3.11.0 or higher

# Verify Docker
docker --version
docker-compose --version

# Verify VPN connection (should resolve internal domain)
ping ai-proxy.lab.epam.com
```

## Quick Start

### 5-Minute Setup

```bash
# 1. Navigate to project directory
cd /path/to/ai-dial-simple-agent

# 2. Activate the included virtual environment
source dial_simple_agent/bin/activate

# 3. Verify dependencies are installed
python -c "import requests; import pydantic; print('✓ Dependencies OK')"

# 4. Start the user service container
docker-compose up -d userservice

# 5. Wait for service to be healthy (30-40 seconds)
docker-compose ps
# Should show "healthy" status

# 6. Export your DIAL API key
export DIAL_API_KEY="your-dial-api-key-here"

# 7. Run the agent
python -m task.app
```

**Expected Output:**
```
DIAL Endpoint: https://ai-proxy.lab.epam.com/openai/deployments/gpt-4o/chat/completions
Tools: ['web_search_tool', 'get_user_by_id', 'search_users', 'add_user', 'update_user', 'delete_user']
User Management Agent started. Type 'exit' or 'quit' to stop.
============================================================
> 
```

## Detailed Setup

### Step 1: Clone or Download Project

```bash
# If using Git
git clone <repository-url> ai-dial-simple-agent
cd ai-dial-simple-agent

# If downloaded as ZIP
unzip ai-dial-simple-agent.zip
cd ai-dial-simple-agent
```

### Step 2: Virtual Environment Setup

The project includes a **pre-configured virtual environment** (`dial_simple_agent/`) with all dependencies installed.

#### Activate Virtual Environment

**macOS/Linux:**
```bash
source dial_simple_agent/bin/activate
```

**Windows (Git Bash/WSL):**
```bash
source dial_simple_agent/Scripts/activate
```

**Verify Activation:**
```bash
which python
# Should show: /path/to/ai-dial-simple-agent/dial_simple_agent/bin/python
```

#### Alternative: Create New Virtual Environment

If the included venv doesn't work for your platform:

```bash
# Create new venv
python3 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Docker Setup

#### Install Docker Desktop

- **macOS**: [Docker Desktop for Mac](https://docs.docker.com/desktop/install/mac-install/)
- **Linux**: [Docker Engine](https://docs.docker.com/engine/install/)
- **Windows**: [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/)

#### Start User Service

```bash
# Start service in detached mode
docker-compose up -d userservice

# View logs
docker-compose logs -f userservice

# Check status
docker-compose ps
```

**Expected Output:**
```
NAME                          IMAGE                                  STATUS         PORTS
ai-dial-simple-agent-userservice-1   khshanovskyi/mockuserservice:latest   Up (healthy)   0.0.0.0:8041->8000/tcp
```

#### Verify User Service

```bash
# Test health endpoint
curl http://localhost:8041/health

# Expected: {"status": "healthy"}

# Test API endpoint
curl http://localhost:8041/v1/users/1

# Expected: User JSON data
```

### Step 4: DIAL API Configuration

#### Request API Key

1. Visit [EPAM Service Portal](https://support.epam.com/ess?id=sc_cat_item&table=sc_cat_item&sys_id=910603f1c3789e907509583bb001310c)
2. Request "DIAL API Access"
3. Follow email instructions to receive API key

#### Configure Environment Variable

**Temporary (session-only):**
```bash
export DIAL_API_KEY="your-dial-api-key-here"
```

**Permanent (add to shell profile):**

```bash
# For Bash
echo 'export DIAL_API_KEY="your-dial-api-key-here"' >> ~/.bashrc
source ~/.bashrc

# For Zsh
echo 'export DIAL_API_KEY="your-dial-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

**Verify:**
```bash
echo $DIAL_API_KEY
# Should output your API key
```

#### Test DIAL API Connection

```bash
# Ensure VPN is connected first
curl -X POST https://ai-proxy.lab.epam.com/openai/deployments/gpt-4o/chat/completions \
  -H "api-key: $DIAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Hello"}],
    "max_tokens": 10
  }'
```

**Expected:** JSON response with AI completion

### Step 5: Run the Agent

```bash
# Ensure venv is activated and DIAL_API_KEY is set
python -m task.app
```

**Test Interaction:**
```
> Search for users named John
```

**Expected:** AI responds with list of users

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DIAL_API_KEY` | Yes | None | DIAL API authentication key |
| `DIAL_ENDPOINT` | No | `https://ai-proxy.lab.epam.com` | DIAL proxy base URL |
| `USER_SERVICE_ENDPOINT` | No | `http://localhost:8041` | User service base URL |

### Configuration File (Optional)

Create `.env` file for persistent configuration:

```bash
# .env
DIAL_API_KEY=your-dial-api-key-here
DIAL_ENDPOINT=https://ai-proxy.lab.epam.com
USER_SERVICE_ENDPOINT=http://localhost:8041
```

Load with `python-dotenv`:
```bash
pip install python-dotenv
```

```python
# In code
from dotenv import load_dotenv
load_dotenv()
```

### Docker Compose Configuration

Edit `docker-compose.yml` to customize user service:

```yaml
services:
  userservice:
    image: khshanovskyi/mockuserservice:latest
    ports:
      - "8041:8000"  # Change host port here
    environment:
      - GENERATE_USERS=true
      - USER_COUNT=1000  # Number of mock users
    volumes:
      - ./data:/app/data  # Persist database
```

### Model Selection

Change model in [app.py](../task/app.py):

```python
dial_client = DialClient(
    endpoint=DIAL_ENDPOINT,
    deployment_name="gemini-2.5-pro",  # Change model here
    api_key=API_KEY,
    tools=tools
)
```

**Available Models:**
- `gpt-4o` - Best for general use
- `gemini-2.5-pro` - Best for web search

## Verification

### Complete Verification Checklist

```bash
#!/bin/bash
# save as verify_setup.sh

echo "=== DIAL Simple Agent Setup Verification ==="

# 1. Check Python
echo -n "1. Python 3.11+: "
python3 --version | grep -q "3.1[1-9]" && echo "✓" || echo "✗"

# 2. Check venv activation
echo -n "2. Virtual environment: "
[[ "$VIRTUAL_ENV" != "" ]] && echo "✓" || echo "✗"

# 3. Check dependencies
echo -n "3. Dependencies: "
python -c "import requests; import pydantic" 2>/dev/null && echo "✓" || echo "✗"

# 4. Check Docker
echo -n "4. Docker running: "
docker ps &>/dev/null && echo "✓" || echo "✗"

# 5. Check user service
echo -n "5. User service: "
curl -s http://localhost:8041/health | grep -q "healthy" && echo "✓" || echo "✗"

# 6. Check DIAL_API_KEY
echo -n "6. DIAL API key: "
[[ -n "$DIAL_API_KEY" ]] && echo "✓" || echo "✗"

# 7. Check VPN
echo -n "7. EPAM VPN: "
ping -c 1 ai-proxy.lab.epam.com &>/dev/null && echo "✓" || echo "✗"

echo "=== Verification Complete ==="
```

**Run:**
```bash
chmod +x verify_setup.sh
./verify_setup.sh
```

## Troubleshooting

### Common Issues

#### Issue: "API key is required"

**Symptoms:**
```
ValueError: API key is required
```

**Solutions:**
1. Check environment variable:
   ```bash
   echo $DIAL_API_KEY
   ```
2. Export in current session:
   ```bash
   export DIAL_API_KEY="your-key"
   ```
3. Verify no spaces in command:
   ```bash
   # Wrong
   export DIAL_API_KEY = "key"
   
   # Correct
   export DIAL_API_KEY="key"
   ```

#### Issue: Connection Timeout to DIAL API

**Symptoms:**
```
requests.exceptions.ConnectionError: Failed to establish connection
```

**Solutions:**
1. **Connect to EPAM VPN**
2. Verify VPN connection:
   ```bash
   ping ai-proxy.lab.epam.com
   ```
3. Check firewall settings
4. Try alternative network

#### Issue: User Service Not Found

**Symptoms:**
```
Error: Connection refused on localhost:8041
```

**Solutions:**
1. Start Docker service:
   ```bash
   docker-compose up -d userservice
   ```
2. Check Docker is running:
   ```bash
   docker ps
   ```
3. View service logs:
   ```bash
   docker-compose logs userservice
   ```
4. Restart container:
   ```bash
   docker-compose restart userservice
   ```

#### Issue: Port 8041 Already in Use

**Symptoms:**
```
Error: bind: address already in use
```

**Solutions:**
1. Find process using port:
   ```bash
   lsof -i :8041
   ```
2. Kill process:
   ```bash
   kill -9 <PID>
   ```
3. Or change port in `docker-compose.yml`:
   ```yaml
   ports:
     - "8042:8000"  # Changed to 8042
   ```

#### Issue: Python Module Not Found

**Symptoms:**
```
ModuleNotFoundError: No module named 'requests'
```

**Solutions:**
1. Ensure venv is activated:
   ```bash
   source dial_simple_agent/bin/activate
   ```
2. Reinstall dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Verify installation:
   ```bash
   pip list
   ```

#### Issue: Docker Permission Denied

**Symptoms:**
```
permission denied while trying to connect to Docker daemon
```

**Solutions:**

**Linux:**
```bash
sudo usermod -aG docker $USER
newgrp docker
```

**macOS:**
- Restart Docker Desktop
- Check Docker Desktop preferences

#### Issue: Virtual Environment Won't Activate

**Symptoms:**
- `source` command not found
- Permission denied on activate script

**Solutions:**

**macOS/Linux:**
```bash
# Make activate executable
chmod +x dial_simple_agent/bin/activate

# Try alternative activation
. dial_simple_agent/bin/activate
```

**Windows:**
```bash
# Use Scripts directory instead of bin
dial_simple_agent\Scripts\activate.bat
```

### Debug Mode

Enable verbose logging:

```python
# In client.py or app.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

Run with debug output:
```bash
python -m task.app 2>&1 | tee debug.log
```

### Health Check Commands

```bash
# 1. Python environment
python -c "import sys; print(sys.version); print(sys.executable)"

# 2. Package versions
pip list | grep -E "requests|pydantic"

# 3. Docker status
docker-compose ps
docker stats --no-stream userservice

# 4. User service API
curl -v http://localhost:8041/health
curl http://localhost:8041/v1/users?limit=1

# 5. DIAL API connectivity
curl -I https://ai-proxy.lab.epam.com
```

## Advanced Setup

### Custom User Service

To use a different user service implementation:

1. Update `USER_SERVICE_ENDPOINT` in `user_client.py`:
   ```python
   USER_SERVICE_ENDPOINT = "http://your-service:8000"
   ```

2. Ensure API compatibility with existing endpoints

### Multiple Environments

Create environment-specific configs:

```bash
# .env.dev
DIAL_API_KEY=dev-key
USER_SERVICE_ENDPOINT=http://localhost:8041

# .env.prod
DIAL_API_KEY=prod-key
USER_SERVICE_ENDPOINT=https://user-service.example.com
```

Load conditionally:
```bash
ENV=dev python -m task.app
```

### Container Networking

To connect from within Docker:

```yaml
services:
  agent:
    build: .
    environment:
      - DIAL_API_KEY=${DIAL_API_KEY}
      - USER_SERVICE_ENDPOINT=http://userservice:8000
    depends_on:
      - userservice
  
  userservice:
    image: khshanovskyi/mockuserservice:latest
```

### Performance Tuning

**Docker Resource Limits:**
```yaml
services:
  userservice:
    image: khshanovskyi/mockuserservice:latest
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
```

**Connection Pooling:**
```python
# In user_client.py
import requests
session = requests.Session()
```

### IDE Configuration

**VS Code:**

1. Select Python interpreter: `Cmd+Shift+P` → "Python: Select Interpreter"
2. Choose: `./dial_simple_agent/bin/python`
3. Install Python extension

**PyCharm:**

1. Settings → Project → Python Interpreter
2. Add interpreter → Existing environment
3. Select: `./dial_simple_agent/bin/python`

### Jupyter Notebook Setup

```bash
# Install Jupyter in venv
pip install jupyter

# Create kernel
python -m ipykernel install --user --name=dial-agent

# Launch notebook
jupyter notebook
```

---

**Last Updated**: 2025-12-30 | **Version**: 1.0.0 | **Next Review**: Q1 2026

## Quick Reference

```bash
# Activate environment
source dial_simple_agent/bin/activate

# Start services
docker-compose up -d

# Set API key
export DIAL_API_KEY="your-key"

# Run agent
python -m task.app

# Stop services
docker-compose down

# View logs
docker-compose logs -f userservice
```
