# Chrome Cap Troubleshooting Guide

## Common Issues

### 1. Screenshot Capture Fails with the BGPT Extension

#### Errors

**Error 1: Cannot read properties of undefined (reading '0')**
```
Error handling response: TypeError: Cannot read properties of undefined (reading '0')
```

**Error 2: Invalid URL pattern**
```
Unchecked runtime.lastError: Invalid url pattern 'https://example.com'
```

#### Causes

1. **URL Pattern Format**: Chrome's `tabs.query()` API requires URL patterns with wildcards, not exact URLs. Direct URLs cause the "Invalid url pattern" error.

2. **Asynchronous Code Issues**: The BrowserGPT extension uses asynchronous `chrome.tabs.query()` but may not wait for the result before accessing it.

3. **No Matching Tab**: When no tab matches the URL pattern, `tabs` will be an empty array, causing the TypeError when trying to access `tabs[0]`.

#### Solutions

1. **Use Correct URL Patterns**:
   - Convert URLs to patterns with wildcards: `*://hostname/*`
   - Example: `https://web.whatsapp.com` → `*://web.whatsapp.com/*`

2. **Fix Asynchronous Code**:
   - Always handle the tabs query callback properly
   - Check if tabs exist and have length before accessing elements
   - Use promises or async/await for cleaner code

3. **Check Permissions**:
   - Ensure your extension has the `tabs` permission in the manifest

### 2. Extension Not Detected

#### Symptoms
- Extension check times out
- "Extension not found" error message appears
- Cannot capture screenshots

#### Causes
1. Extension not installed or disabled
2. Extension failed to initialize
3. Communication channel problems

#### Solutions
1. Verify the extension is installed and enabled
2. Check browser console for errors
3. Try reloading the extension
4. Ensure the extension has the required permissions

### 3. Screenshot Capture Times Out

#### Symptoms
- "Capture timed out" error message
- The status remains "capturing" indefinitely

#### Causes
1. Extension crashed
2. Tab is in a suspended state
3. Tab contains content that blocks screenshots
4. Network issues

#### Solutions
1. Check the extension's background console for errors
2. Ensure the target tab is active and not in a suspended state
3. Try capturing a different tab as a test
4. Reload both the client page and the extension

## Debugging Tools

### Console Logging

Chrome Cap includes extensive logging with categorized prefixes to help diagnose issues:

- `[INIT]` - Initialization events
- `[CONFIG]` - Configuration details
- `[CHECK]` - Extension check operations
- `[SEND]` - Messages sent to extensions
- `[RECEIVE]` - All incoming messages
- `[BGPT]` - BGPT extension interactions
- `[STANDARD]` - Standard extension interactions
- `[TIMEOUT]` - Timeout handling
- `[ERROR]` - Error details

### URL Pattern Test Tool

Use the included URL pattern test tool to verify your URL patterns:
1. Open `/tests/test_url_pattern.html` in a browser
2. Enter a URL to convert
3. The tool will show the corresponding pattern for Chrome's `tabs.query()`

### Extension Debug Helper

For BGPT extension development, use the debug-helper.js:

```javascript
// In the extension background script
// @ts-ignore
importScripts('debug-helper.js');

// Then you can use
ChromeCapDebug.listAllTabs();
ChromeCapDebug.findTabsByPattern("*://example.com/*");
ChromeCapDebug.testUrlPattern("*://example.com/*");
```

## Advanced Troubleshooting

### Testing BGPT Communication

1. Open the DevTools console (F12) in the Chrome Cap client page
2. Run this command to test communication with the BGPT extension:
   ```javascript
   window.postMessage({
     type: "BGPT_INVOKE_EXTENSION",
     action: "PING",
     currentStateId: window.bgptStateId
   }, "*");
   ```
3. You should see a PONG response in the console

### Checking Tab Query Results

In the extension background script console, run:

```javascript
chrome.tabs.query({}, tabs => console.table(tabs.map(t => ({id: t.id, url: t.url}))));
```

This will show all open tabs and their IDs to verify your target tab is accessible.

## Contacting Support

If you're still experiencing issues after trying the solutions above:

1. Collect the console logs from both the client page and the extension
2. Take note of the exact errors displayed
3. Report the issue with details of your browser version and the steps to reproduce

## FAQ

**Q: Why can't I capture tabs from certain websites?**  
A: Some websites block screenshots for security reasons or are run in isolated contexts.

**Q: Does Chrome Cap work in Incognito mode?**  
A: Yes, but the extension must have permission to run in Incognito mode.

**Q: Can I capture screenshots of multiple tabs simultaneously?**  
A: Currently, Chrome Cap only supports capturing one tab at a time.

**Q: Why does capturing take a long time sometimes?**  
A: Large or complex pages may take longer to capture. Network conditions and system resources also affect performance. 