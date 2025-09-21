# ChromeCap Client Static Assets

This directory contains the static assets for the ChromeCap client interface. These files are served by the ChromeCap server to provide the user interface for screenshot capture and interaction with the Chrome extension.

## Files

- `client.js`: Main JavaScript file for the client interface
- `debug-tools.js`: JavaScript tools for debugging the capture process
- `styles.css`: CSS styles for the client interface

## Socket.IO Communication

ChromeCap uses Socket.IO for real-time communication between the server and Chrome extension. This enables:

1. Instant screenshot capture requests without page reloads
2. Real-time status updates during the capture process
3. Delivery of screenshot data back to the server

The client establishes a Socket.IO connection to the server and listens for capture task events. When a capture is requested, the client:

1. Receives the capture task via Socket.IO
2. Captures the screenshot using the Chrome extension
3. Sends the screenshot data back to the server via a `capture_result` event

## Important Note

These static files are required for ChromeCap to function properly. They provide the interface for communicating with the Chrome extension and handling the capture process.

If you're having issues with ChromeCap, make sure these files are correctly included in your installation. Run `chromecap --version` to check if the package is properly installed.

## Troubleshooting

If screenshots are being captured but not detected:

1. Check server logs for any errors during the capture process
2. Verify the Socket.IO connection is established (look for "Client connected" messages)
3. Run ChromeCap with `--debug` flag for more detailed logging
4. Make sure the BrowserGPT extension is properly installed and connected 