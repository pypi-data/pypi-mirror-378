"""
ChromeCap - Chrome screenshot capture utility.

A Python package for capturing and analyzing screenshots from Chrome.
"""

import os
import sys
import importlib
from pathlib import Path

__version__ = "0.1.3"


# Post-installation message
def _display_post_install_message():
    """Display important post-installation information."""
    # Only show message once per session
    if hasattr(sys, '_chromecap_message_shown'):
        return
    # Type ignore for dynamically added attribute
    sys._chromecap_message_shown = True  # type: ignore

    # Check if this is a fresh installation by looking for a marker file
    marker_file = os.path.join(os.path.dirname(__file__), '.chromecap_installed')

    if not os.path.exists(marker_file):
        print("\n" + "="*70)
        print("🎉 ChromeCap installed successfully!")
        print("="*70)
        print()
        print("📋 NEXT STEPS:")
        print("1. Install the BrowserGPT Chrome Extension:")
        print("   🔗 https://chromewebstore.google.com/detail/browsergpt-operator/"
              "hipciehccffmaaoghpleiffkcgbefjhf")
        print()
        print("2. Start the ChromeCap server:")
        print("   💻 chromecap start")
        print()
        print("3. Capture your first screenshot:")
        print("   📸 chromecap capture https://example.com --output screenshot.png")
        print()
        print("4. Or capture console logs:")
        print("   📝 chromecap capture https://example.com --log logs.txt")
        print()
        print("📚 For more examples and documentation:")
        print("   🔗 https://github.com/civai-technologies/chrome-cap")
        print()
        print("⚠️  IMPORTANT: Make sure to install the BrowserGPT extension")
        print("   for the best experience with ChromeCap!")
        print("="*70)
        print()

        # Create marker file to prevent showing message again
        try:
            with open(marker_file, 'w') as f:
                f.write(f"ChromeCap installed on "
                        f"{__import__('datetime').datetime.now()}\n")
        except Exception:
            pass  # Ignore errors creating marker file


# Display message on import
_display_post_install_message()

# Explicitly import importlib.util to avoid AttributeError
# For compatibility with all Python versions
try:
    import importlib.util
except (ImportError, AttributeError):
    # For very old Python versions, provide a fallback
    print("ERROR: Your Python installation appears to be missing "
          "importlib.util.")
    print("This is a standard library module that should be available.")
    print("Please ensure you're using Python 3.6 or newer.")
    sys.exit(1)

# Add the parent directory to sys.path
BASE_DIR = Path(__file__).parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Ensure required packages are available
packages_to_check = ['client', 'server', 'extension']
for package_name in packages_to_check:
    try:
        # Try to import, or create empty packages if needed
        if importlib.util.find_spec(package_name) is None:
            package_dir = BASE_DIR / package_name
            if package_dir.exists():
                sys.path.insert(0, str(package_dir.parent))
    except ImportError:
        pass


def get_cli():
    """Get the CLI object for use in entry points."""
    try:
        from .server.cli import cli
        return cli
    except ImportError:
        # Fallback to a direct import through server module
        try:
            server_cli_path = os.path.join(BASE_DIR, "server", "cli.py")
            if os.path.exists(server_cli_path):
                spec = importlib.util.spec_from_file_location(
                    "server.cli", server_cli_path)
                if spec is not None and spec.loader is not None:
                    server_cli = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(server_cli)
                    return server_cli.cli
        except Exception as ex:
            print(f"Warning: Failed to import server CLI: {ex}")

        # Last resort fallback
        import click

        @click.group()
        @click.version_option(version=__version__, prog_name="chromecap")
        def fallback_cli():
            """ChromeCap CLI (limited functionality due to import failure)."""
            pass

        @fallback_cli.command()
        def version():
            """Show the chromecap version."""
            click.echo(f"ChromeCap version: {__version__}")

        @fallback_cli.command()
        def status():
            """Show the status of the ChromeCap installation."""
            click.echo("WARNING: Limited functionality due to import errors.")
            click.echo(f"Version: {__version__}")
            sys.exit(1)

        return fallback_cli


# Get CLI for entry point - referenced in setup.py
cli = get_cli()
