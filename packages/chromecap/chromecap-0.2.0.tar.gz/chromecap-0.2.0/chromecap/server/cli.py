"""ChromeCap CLI module."""

import os
import sys
import importlib.util
from pathlib import Path

# Add the main repository to path to allow for server imports
BASE_DIR = Path(__file__).parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


def fallback_cli():
    """Fallback CLI function if main CLI can't be imported."""
    import click

    @click.group()
    @click.version_option(version="0.1.3", prog_name="chromecap")
    def cli():
        """ChromeCap - Fallback CLI (limited functionality)."""
        pass

    @cli.command()
    def version():
        """Show the chromecap version."""
        click.echo("ChromeCap version: 0.1.3")

    @cli.command()
    def status():
        """Show the status of the ChromeCap installation."""
        click.echo("ERROR: ChromeCap is not properly installed.")
        click.echo("Please run 'pip install -e .' from the repository root.")
        sys.exit(1)

    return cli


# Try to import the main CLI in different ways
try:
    # First try direct import
    from server.cli import cli
except ImportError:
    try:
        # Try relative import through parent
        sys.path.insert(0, str(BASE_DIR))
        spec = importlib.util.spec_from_file_location(
            "server.cli",
            os.path.join(BASE_DIR, "server", "cli.py")
        )
        if spec is not None and spec.loader is not None:
            server_cli = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(server_cli)
            cli = server_cli.cli
    except (ImportError, AttributeError, FileNotFoundError) as e:
        print(f"Warning: Using fallback CLI due to import error: {e}")
        cli = fallback_cli()


if __name__ == "__main__":
    cli()
