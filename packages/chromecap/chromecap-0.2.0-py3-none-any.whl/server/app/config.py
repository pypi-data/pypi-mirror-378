"""
Configuration module for Chrome Cap server.
Loads environment variables from .env file.
"""
import os
import sys
import importlib.util
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
BASE_DIR = Path(__file__).resolve().parent.parent.parent
env_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=env_path)

# Server configuration
SERVER_HOST = os.getenv("SERVER_HOST", "localhost")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))
SERVER_URL = f"http://{SERVER_HOST}:{SERVER_PORT}"

# Extension configuration
EXTENSION_TYPE = os.getenv("EXTENSION_TYPE", "BGPT")  # STANDARD or BGPT

# Application paths
CLIENT_DIR = BASE_DIR / "client"

# Try to import client module to get a more accurate path
try:
    import client
    if hasattr(client, 'CLIENT_DIR'):
        CLIENT_DIR = client.CLIENT_DIR
    else:
        CLIENT_DIR = Path(client.__file__).parent
except ImportError:
    # Try different relative paths if direct import fails
    for client_path in [
        BASE_DIR / "client",
        Path(__file__).parent.parent.parent / "client",
        Path(sys.prefix) / "client",
    ]:
        if client_path.exists():
            CLIENT_DIR = client_path
            break

SCREENSHOTS_DIR = BASE_DIR / "screenshots"

# Create screenshots directory if it doesn't exist
SCREENSHOTS_DIR.mkdir(exist_ok=True)

# Server metadata
SERVER_VERSION = "1.1.0"

# Print debug info for directory structure
print(f"Config: BASE_DIR = {BASE_DIR}")
print(f"Config: CLIENT_DIR = {CLIENT_DIR}")
print(f"Config: SCREENSHOTS_DIR = {SCREENSHOTS_DIR}")
print(f"Config: Client dir exists: {CLIENT_DIR.exists()}")
print(f"Config: Client static dir exists: {(CLIENT_DIR / 'static').exists()}")
