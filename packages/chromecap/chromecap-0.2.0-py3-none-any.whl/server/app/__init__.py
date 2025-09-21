"""Chrome Cap Server FastAPI Application."""

from typing import Any, Optional

# Define module-level variables with proper type annotations
config: Optional[Any] = None
app: Optional[Any] = None
socket_app: Optional[Any] = None

# Attempt to import modules
try:
    # Import config first
    from . import config as config_module
    config = config_module

    # Then try to import main with specific error handling
    try:
        from . import main
        # Export key components if import successful
        if hasattr(main, 'app'):
            app = main.app
        if hasattr(main, 'socket_app'):
            socket_app = main.socket_app
    except ImportError as e:
        print(f"Warning: Unable to import main module: {e}")
        # Create fallback objects
        try:
            from fastapi import FastAPI
            app = FastAPI(title="ChromeCap [Fallback]")
            socket_app = app
        except ImportError:
            print("Warning: FastAPI not available for fallback")
            # app and socket_app remain None
except ImportError as e:
    print(f"Warning: Unable to initialize server application: {e}")
    # config, app, and socket_app remain None
