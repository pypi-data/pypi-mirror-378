"""Extension package for Chrome Cap."""

import os
from pathlib import Path

# Get the directory where this file is located
EXTENSION_DIR = Path(__file__).parent

def get_extension_dir():
    """Get the extension directory path."""
    return EXTENSION_DIR 