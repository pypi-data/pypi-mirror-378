"""Chrome Cap Server."""

import importlib.util
from typing import Any, Optional

# Define module level variables with proper type annotations
app: Optional[Any] = None
socket_app: Optional[Any] = None

# Add import safeguards
try:
    # Import app components
    if importlib.util.find_spec('server.app') is not None:
        try:
            from . import app as app_module
            # Export app components with proper type checking
            if hasattr(app_module, 'app'):
                app = app_module.app
            if hasattr(app_module, 'socket_app'):
                socket_app = app_module.socket_app
        except (ImportError, AttributeError) as e:
            print(f"Warning: Failed to import app components: {e}")
            # app and socket_app remain None
    else:
        print("Warning: server.app module not found")
        # app and socket_app remain None
except Exception as e:
    print(f"Warning: Error initializing server package: {e}")
    # app and socket_app remain None
