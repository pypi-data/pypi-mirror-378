# Chrome Cap Documentation

Welcome to the Chrome Cap documentation. Chrome Cap is a powerful tool that enables capturing screenshots of Chrome tabs via CLI commands, utilizing a FastAPI server, a web client, and a Chrome extension.

## Documentation Sections

- [API Reference](./api/index.md) - Detailed API documentation for developers
- [User Guides](./user_guides/index.md) - How-to guides for using Chrome Cap
- [Developer Notes](./dev_notes/index.md) - Notes for developers working on Chrome Cap

## Quick Start

```bash
# Install from PyPI
pip install chromecap

# Start the server
chromecap start

# Capture a screenshot
chromecap capture https://example.com --output screenshot.png
```

See the [User Guides](./user_guides/index.md) for more detailed usage instructions. 