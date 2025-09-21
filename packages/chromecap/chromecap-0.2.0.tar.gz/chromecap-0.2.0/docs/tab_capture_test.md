# Tab Capture Testing Guide

This document provides a step-by-step guide to test the tab capture functionality with the BrowserGPT extension.

## Prerequisites

1. Chrome browser with Developer Tools access
2. BrowserGPT extension installed and enabled
3. Chrome Cap client running
4. At least two tabs open (one for testing, one for the Chrome Cap client)

## Test Case 1: Capture Active Tab

1. **Setup**:
   - Open Chrome Cap client in one tab
   - Navigate to another tab (like Google.com)
   - Make sure the Google tab is active (visible)

2. **Execute**:
   - Go back to the Chrome Cap client tab
   - Set target URL to the Google tab URL
   - Click "Capture Screenshot"

3. **Expected Result**:
   - Screenshot of Google.com should be captured and displayed
   - No tab switching should occur (since you're capturing the active tab)

4. **Diagnose (if failing)**:
   - Open Chrome Dev Tools (F12) in the client tab
   - Check console logs for any errors
   - Verify the URL format in the logs (should be converted to pattern)

## Test Case 2: Capture Non-Active Tab

1. **Setup**:
   - Open Chrome Cap client in one tab
   - Open another tab with WhatsApp Web (https://web.whatsapp.com)
   - Make sure Chrome Cap client tab is active (visible)

2. **Execute**:
   - In the Chrome Cap client, set target URL to "https://web.whatsapp.com"
   - Click "Capture Screenshot"
   - Observe if tab switching occurs

3. **Expected Result**:
   - Brief switch to WhatsApp tab (visible for a moment)
   - Screenshot capture
   - Return to Chrome Cap client tab
   - Screenshot of WhatsApp displayed in the client

4. **Diagnose (if failing)**:
   - Open extension background page:
     - Go to chrome://extensions/
     - Find BrowserGPT extension
     - Click "background page" link under "Inspect views"
   - Check console logs for:
     - URL pattern conversion
     - Tab ID detection
     - Tab switching logs
     - Any errors during capture

## Test Case 3: Capture Non-Existent URL

1. **Setup**:
   - Open Chrome Cap client in one tab

2. **Execute**:
   - Set target URL to a URL that you don't have open (e.g., "https://nonexistent-testing-url.com")
   - Click "Capture Screenshot"

3. **Expected Result**:
   - Error message: "No tab found matching the URL pattern"
   - No tab switching should occur

4. **Diagnose (if failing)**:
   - Check extension background console for error messages
   - Verify URL pattern conversion is working

## Manual Testing with Debug Tools

### Test URL Pattern Conversion

1. Open the extension background page console
2. Run the following commands:
   ```javascript
   // Load debug helper if not already loaded
   try { importScripts('debug-helper.js'); } catch(e) { console.error(e); }
   
   // List all open tabs
   ChromeCapDebug.listAllTabs();
   
   // Test converting a URL to pattern
   ChromeCapDebug.urlToPattern('https://web.whatsapp.com');
   
   // Try finding tabs with the pattern
   ChromeCapDebug.findTabsByPattern('*://web.whatsapp.com/*');
   ```

### Test Tab Capturing Directly

1. Open the extension background page console
2. Run the following commands:
   ```javascript
   // Find tab ID for WhatsApp
   const tabs = await chrome.tabs.query({url: '*://web.whatsapp.com/*'});
   const tabId = tabs[0]?.id;
   console.log('Found tab ID:', tabId);
   
   // Capture that tab using debug helper
   if (tabId) {
     const image = await ChromeCapDebug.captureTabById(tabId);
     console.log('Image captured, length:', image.length);
   }
   ```

## Debugging from Client Page

1. Open Chrome Cap client
2. Open browser console (F12)
3. Load the debug utilities with:
   ```javascript
   fetch('/static/debug-tools.js').then(r => r.text()).then(t => eval(t))
   ```
4. Run tests directly from console:
   ```javascript
   // Test communication with BGPT extension
   await ChromeCapDebug.testBGPTCommunication();
   
   // Test URL conversion
   ChromeCapDebug.convertURL('https://web.whatsapp.com');
   
   // Test screenshot capture directly
   await ChromeCapDebug.captureURL('https://web.whatsapp.com');
   
   // Monitor all postMessage communications
   ChromeCapDebug.monitorMessages(true);
   ```

## Common Issues and Solutions

### "Cannot read properties of undefined (reading '0')"
- **Cause**: No tabs found matching the URL pattern
- **Solution**: Check the URL pattern is correct and the tab is open

### "Invalid url pattern"
- **Cause**: URL format is invalid for chrome.tabs.query()
- **Solution**: Convert URL to pattern format with wildcards

### Captures wrong tab
- **Cause**: tab switching not implemented or not working
- **Solution**: Verify tab switching code is working properly

### No response from extension
- **Cause**: Communication channel issues or extension crashed
- **Solution**: Reload extension and check for errors in background console 