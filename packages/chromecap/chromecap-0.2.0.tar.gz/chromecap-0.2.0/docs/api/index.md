# Chrome Cap API Reference

This section contains detailed documentation for the Chrome Cap API.

## Server API

The Chrome Cap server exposes both REST and Socket.IO APIs.

### REST API Endpoints

#### Screenshot Management

- `POST /api/capture` - Capture a screenshot of a URL
- `GET /api/screenshots/{screenshot_id}` - Get screenshot metadata
- `GET /api/raw-screenshot/{screenshot_id}` - Get raw screenshot image
- `GET /api/screenshots` - List all screenshots

#### Server Management

- `GET /api/status` - Get server status
- `POST /api/shutdown` - Shut down the server

### Socket.IO Events

- `connect` - Client connection event
- `disconnect` - Client disconnection event
- `heartbeat` - Client heartbeat event
- `capture_task` - Screenshot capture task event
- `screenshot_captured` - Screenshot captured event

## Python API

### CLI Module

The `chromecap.cli` module provides the command-line interface for Chrome Cap.

```python
from chromecap import cli

# Start the server
cli.start()

# Capture a screenshot
cli.capture("https://example.com", output="screenshot.png")
```

### Server Module

The `chromecap.server` module provides the server functionality for Chrome Cap.

```python
from chromecap.server import config, main

# Get server URL
server_url = config.SERVER_URL

# Access FastAPI app
app = main.app
``` 