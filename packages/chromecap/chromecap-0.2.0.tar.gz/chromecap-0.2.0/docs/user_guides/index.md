# Chrome Cap User Guides

This section contains user guides for Chrome Cap.

## Installation

### From PyPI

```bash
pip install chromecap
```

### From Source

```bash
git clone https://github.com/civai-technologies/chrome-cap.git
cd chrome-cap
pip install -e .
```

## Basic Usage

### Starting the Server

Before capturing screenshots, you need to start the Chrome Cap server:

```bash
chromecap start
```

The server will run on `http://localhost:8000` by default. You can configure the host and port using environment variables in a `.env` file:

```
SERVER_HOST=localhost
SERVER_PORT=8000
```

### Capturing Screenshots

To capture a screenshot of a URL:

```bash
chromecap capture https://example.com --output screenshot.png
```

### Options

- `--output`: Save the screenshot to a file
- `--timeout`: Maximum time to wait for the screenshot (in seconds)
- `--debug`: Enable debug mode
- `--redirect`: URL to redirect to after capturing the screenshot
- `--query`: Query string to analyze the captured image using AI

## Advanced Usage

### Working with Localhost URLs

When capturing screenshots of localhost URLs, Chrome Cap automatically handles the URL translation:

```bash
chromecap capture http://localhost:3000 --output local.png
```

### Using Redirects

You can redirect to another URL after capturing a screenshot:

```bash
chromecap capture https://example.com --output shot.png --redirect "https://your-app.com"
```

You can also redirect to desktop apps using app protocol URLs:

```bash
chromecap capture https://example.com --output shot.png --redirect "slack://channel?id=123"
```

### Analyzing Screenshots with AI

If you have cursor-agent-tools installed, you can analyze screenshots using AI:

```bash
chromecap capture https://example.com --output screenshot.png --query "What UI elements are misaligned?"
``` 