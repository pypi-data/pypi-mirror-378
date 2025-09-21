# BrowserGPT Extension Integration Guide

This document provides instructions for integrating Chrome Cap with the BrowserGPT extension's tab capture functionality.

## Issue: Tab Capture by URL Fails

When attempting to capture a tab by URL, the following errors may occur:

```
Error handling response: TypeError: Cannot read properties of undefined (reading '0')
Unchecked runtime.lastError: Invalid url pattern 'https://web.whatsapp.com'
```

These errors happen because:
1. Chrome's `tabs.query()` API requires URL patterns with wildcards
2. The asynchronous query isn't properly handled
3. The code doesn't account for cases where no tabs match the pattern

Additionally, even when the tab ID is found correctly, the extension might capture the currently active tab instead of the target tab. This is because Chrome's `captureVisibleTab()` function only captures what's visible on screen.

## Required Changes to BrowserGPT Extension

Find the section in `background.js` that handles the "captureScreen" action. It should look similar to this:

```javascript
else if (request.action === "captureScreen") {
    console.warn("Capture screen request received");
    // Need to return true to keep the message channel open

    // if request.url is not null, then get the tab id from the url
    let tabId = null;
    if (request.url) {
        chrome.tabs.query({ url: request.url }, (tabs) => {
            tabId = tabs[0].id;
        });
    }

    if (tabId) {
        captureCurrentTab(tabId).then((image) => {
            // Send response...
        });
    } else {
        // Handle current tab...
    }
}
```

### Fix: Improved Tab Capture Implementation

Replace both the problematic code and the `captureCurrentTab` function with this implementation:

```javascript
// Improved captureCurrentTab function to properly handle tab switching
async function captureCurrentTab(tabId) {
    console.warn("captureCurrentTab triggered");
    
    // If no tabId provided, capture the current tab
    if (!tabId) {
        return new Promise((resolve, reject) => {
            chrome.tabs.captureVisibleTab(null, { format: "png" }, (dataUrl) => {
                if (chrome.runtime.lastError) {
                    reject(chrome.runtime.lastError);
                } else {
                    resolve(dataUrl);
                }
            });
        });
    }
    
    try {
        // Get the target tab to verify it exists and check if it's active
        const tab = await chrome.tabs.get(tabId);
        console.log("Target tab:", { id: tab.id, url: tab.url, active: tab.active });
        
        let originalTabId = null;
        
        // Only switch tabs if the target tab is not already active
        if (!tab.active) {
            // Remember current active tab
            const activeTabs = await chrome.tabs.query({ active: true, currentWindow: true });
            originalTabId = activeTabs.length > 0 ? activeTabs[0].id : null;
            console.log("Original active tab:", originalTabId);
            
            // Switch to the target tab
            console.log(`Switching to tab ID ${tabId}...`);
            await chrome.tabs.update(tabId, { active: true });
            
            // Wait for the tab to become fully visible
            await new Promise(resolve => setTimeout(resolve, 500));
        } else {
            console.log("Tab is already active, capturing directly");
        }
        
        // Capture the now-visible tab
        const dataUrl = await new Promise((resolve, reject) => {
            chrome.tabs.captureVisibleTab(null, { format: "png" }, (dataUrl) => {
                if (chrome.runtime.lastError) {
                    reject(chrome.runtime.lastError);
                } else {
                    resolve(dataUrl);
                }
            });
        });
        
        console.log("CAPTURED THE IMAGE FOR SPECIFIC URL WITH TAB ID: ", tabId);
        
        // Switch back to the original tab if needed
        if (originalTabId && originalTabId !== tabId) {
            console.log(`Switching back to original tab ID ${originalTabId}...`);
            await chrome.tabs.update(originalTabId, { active: true });
        }
        
        return dataUrl;
    } catch (error) {
        console.error("Error capturing tab:", error);
        throw error;
    }
}

// Main handler for "captureScreen" action
else if (request.action === "captureScreen") {
    console.warn("Capture screen request received");
    
    // If URL is provided, find the corresponding tab
    if (request.url) {
        console.log("CAPTURE SCREEN FOR SPECIFIC URL: ", request.url);
        
        // Use chrome.tabs.query asynchronously with await
        try {
            const tabs = await chrome.tabs.query({ url: request.url });
            
            if (tabs && tabs.length > 0) {
                const tabId = tabs[0].id;
                console.log("TAB ID FOUND FOR SPECIFIC URL: ", tabId);
                
                // Capture the found tab
                try {
                    const image = await captureCurrentTab(tabId);
                    console.warn("CAPTURED THE IMAGE FOR SPECIFIC URL");
                    
                    chrome.tabs.sendMessage(sender.tab.id, {
                        action: "captureScreenResponse",
                        status: "success",
                        message: { 
                            image: image, 
                            description: "", 
                            currentUrl: tabs[0].url 
                        },
                        stateId: request.currentStateId,
                        bgptIndex: request.bgptIndex,
                    });
                    
                    // Send response if needed
                    if (sendResponse) {
                        sendResponse({ status: "success", image: image });
                    }
                } catch (error) {
                    console.error("Failed to capture tab:", error);
                    
                    // Send error response
                    chrome.tabs.sendMessage(sender.tab.id, {
                        action: "captureScreenResponse",
                        status: "error",
                        message: { error: "Failed to capture screenshot: " + error.message },
                        stateId: request.currentStateId,
                        bgptIndex: request.bgptIndex,
                    });
                }
            } else {
                console.error("No tabs found matching pattern:", request.url);
                
                // Handle the case where no matching tab is found
                chrome.tabs.sendMessage(sender.tab.id, {
                    action: "captureScreenResponse",
                    status: "error",
                    message: { error: "No tab found matching the URL pattern" },
                    stateId: request.currentStateId,
                    bgptIndex: request.bgptIndex,
                });
            }
        } catch (error) {
            console.error("Error querying tabs:", error);
            
            // Send error response
            chrome.tabs.sendMessage(sender.tab.id, {
                action: "captureScreenResponse",
                status: "error",
                message: { error: "Error querying tabs: " + error.message },
                stateId: request.currentStateId,
                bgptIndex: request.bgptIndex,
            });
        }
    } else {
        // Capture current active tab (existing code)
        captureCurrentTab().then((image) => {
            console.warn("CAPTURED THE IMAGE FOR CURRENT TAB");
            
            chrome.tabs.sendMessage(sender.tab.id, {
                action: "captureScreenResponse",
                status: "success",
                message: { 
                    image: image, 
                    description: "" 
                },
                stateId: request.currentStateId,
                bgptIndex: request.bgptIndex,
            });
            
            if (sendResponse) {
                sendResponse({ status: "success", image: image });
            }
        });
    }
    
    // Keep the message channel open
    return true;
}
```

### Key Improvements:

1. **URL Pattern Handling**: The client now converts regular URLs to patterns with wildcards (e.g., `*://domain.com/*`)
2. **Proper Async Handling**: Using async/await for cleaner asynchronous code
3. **Smart Tab Switching**: Only switches tabs when needed (if target tab isn't already active)
4. **Tab Restoration**: Returns to the original tab after capturing
5. **Proper Error Handling**: All errors are caught and reported properly
6. **Response Management**: Ensures responses are sent correctly in all cases
7. **Message Channel**: Properly returns true to keep the message channel open

## Testing the Integration

1. Apply the changes to the BrowserGPT extension
2. Reload the extension
3. Try capturing a tab by URL using Chrome Cap
4. Check the console logs for detailed debugging information

## Important Note

This implementation briefly makes the target tab visible before capturing it. This is required because Chrome's extension API only allows capturing the currently visible tab. The implementation minimizes disruption by:

1. Only switching tabs when necessary
2. Immediately switching back after capture
3. Preserving the original tab for the user

There is no way to capture a non-active tab without briefly making it visible, as this is a limitation of Chrome's extension API. 