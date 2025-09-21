"""Client package for Chrome Cap."""

import os
from pathlib import Path

# Get the directory where this file is located
CLIENT_DIR = Path(__file__).parent
STATIC_DIR = CLIENT_DIR / "static"

def get_client_dir():
    """Get the client directory path."""
    return CLIENT_DIR

def get_static_dir():
    """Get the static directory path."""
    return STATIC_DIR 