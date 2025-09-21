# Chrome Cap Developer Notes

This section contains notes for developers working on Chrome Cap.

## Project Structure

```
chromecap/
├── __init__.py         # Package initialization, version info
├── cli.py              # Command-line interface
├── server/             # Server module
│   ├── __init__.py     # Server package initialization
│   ├── config.py       # Server configuration
│   └── main.py         # FastAPI and Socket.IO server
└── static/             # Static assets
    ├── client/         # Web client
    └── extension/      # Chrome extension
```

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/civai-technologies/chrome-cap.git
   cd chrome-cap
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install in development mode:
   ```bash
   pip install -e ".[dev]"
   ```

4. Set up pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Testing

Run the tests:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=chromecap
```

## Building and Publishing

Build the package:

```bash
python -m build
```

Publish to TestPyPI:

```bash
python -m twine upload --repository testpypi dist/*
```

Publish to PyPI:

```bash
python -m twine upload dist/*
```

## Release Process

1. Update version in `chromecap/__init__.py`
2. Update `CHANGELOG.md`
3. Commit changes
4. Create a tag: `git tag -a v0.1.0 -m "Release v0.1.0"`
5. Push changes and tag: `git push && git push --tags`
6. Build and publish the package

## Design Decisions

### Package Structure

The package follows a standard Python package structure with a main package directory (`chromecap`) containing the package modules and sub-packages.

### Version Management

Version information is stored in `chromecap/__init__.py` and follows semantic versioning.

### Dependency Management

Dependencies are managed in `setup.py` with version constraints to ensure compatibility.

### Testing

Tests are written using pytest and are located in the `tests` directory.

### Documentation

Documentation is written in Markdown and is located in the `docs` directory. 