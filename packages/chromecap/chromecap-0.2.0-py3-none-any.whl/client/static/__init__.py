"""Static assets for the ChromeCap client."""

import os
from pathlib import Path

STATIC_DIR = Path(__file__).parent
"""Path to the static directory."""

def get_static_dir():
    """Return the path to the static directory."""
    return STATIC_DIR

def list_static_files():
    """List all static files in the directory."""
    return [f for f in STATIC_DIR.iterdir() if f.is_file()] 