"""ChromeCap Server - FastAPI server for Chrome screenshot capture."""

import os
import sys
from pathlib import Path
from typing import Any, Optional

# Server version
SERVER_VERSION = "v0.1.0"

# Configure paths to ensure resources can be found
BASE_DIR = Path(__file__).parent.parent.parent
SERVER_DIR = BASE_DIR / "server"
CLIENT_DIR = BASE_DIR / "client"
EXTENSION_DIR = BASE_DIR / "extension"

if SERVER_DIR.exists():
    sys.path.insert(0, str(BASE_DIR))

# Initialize default configuration
SERVER_HOST = "localhost"
SERVER_PORT = 8000
SERVER_URL = f"http://{SERVER_HOST}:{SERVER_PORT}"
EXTENSION_TYPE = "BGPT"
SCREENSHOTS_DIR = Path("")

# Type declarations for dynamic imports
app: Optional[Any] = None
socket_app: Optional[Any] = None

# Update EXTENSION_DIR if needed
if os.path.exists(CLIENT_DIR / "extension"):
    EXTENSION_DIR = CLIENT_DIR / "extension"

# Import key components from server if available
try:
    # Import server components
    import server

    # Set app variables
    app = server.app
    socket_app = server.socket_app

    # Update configuration from server module
    from server.app.config import SERVER_HOST, SERVER_PORT

    # Override directories in server config if needed
    if CLIENT_DIR.exists():
        try:
            from server.app import config
            if config is not None and hasattr(config, 'CLIENT_DIR'):
                config.CLIENT_DIR = CLIENT_DIR
        except (ImportError, AttributeError) as e:
            print(f"Warning: Cannot update CLIENT_DIR: {e}")

    if EXTENSION_DIR.exists():
        try:
            from server.app import config
            if config is not None and not hasattr(config, 'EXTENSION_DIR'):
                setattr(config, 'EXTENSION_DIR', EXTENSION_DIR)
        except (ImportError, AttributeError) as e:
            print(f"Warning: Cannot update EXTENSION_DIR: {e}")

except ImportError as e:
    # Fallback if imports fail
    print(f"Error importing server components: {e}")
    print("Please ensure the server directory is installed correctly.")
