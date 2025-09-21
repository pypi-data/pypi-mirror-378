import chromecap
"""Tests for the Chrome Cap package installation."""


def test_package_installed():
    """Test that the package can be imported."""
    try:
        import chromecap
        assert hasattr(chromecap, "__version__")
        print(f"Chromecap version: {chromecap.__version__}")
    except ImportError:
        assert False, "Could not import chromecap package"


def test_cli_module():
    """Test that the CLI module can be imported."""
    try:
        from chromecap import cli
        # The CLI is a function decorated by click's group decorator
        # In the dummy implementation, cli is a function returned by dummy_cli_group
        assert callable(cli)
    except ImportError:
        assert False, "Could not import chromecap.cli module"


def test_server_module():
    """Test that the server module can be imported."""
    try:
        import chromecap.server
        assert hasattr(chromecap.server, "SERVER_VERSION")
        assert chromecap.server.SERVER_VERSION in ["0.0.0", "0.1.0", "v0.1.0"]
    except ImportError:
        assert False, "Could not import chromecap.server module"


def test_server_package_contents():
    """Tests for the server package basic contents."""
    # Version string should be defined
    assert hasattr(chromecap.server, "SERVER_VERSION")
    assert isinstance(chromecap.server.SERVER_VERSION, str)

    # Version should follow semantic versioning format
    version = chromecap.server.SERVER_VERSION
    assert version.startswith("v")
    version_parts = version[1:].split(".")
    assert len(version_parts) == 3
    for part in version_parts:
        assert part.isdigit()
