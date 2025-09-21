/**
 * Chrome Cap Extension - Debug Helper
 * 
 * This script provides debugging utilities for the Chrome Cap extension.
 * Include it in your background script with:
 * 
 * // @ts-ignore
 * importScripts('debug-helper.js');
 */

const ChromeCapDebug = {
    /**
     * List all open tabs in a readable format
     * @returns {Promise<void>}
     */
    listAllTabs: async function() {
        try {
            const tabs = await chrome.tabs.query({});
            console.group("📊 Chrome Cap Debug: All Open Tabs");
            
            tabs.forEach((tab, index) => {
                const url = tab.url || "(no URL)";
                const title = tab.title || "(no title)";
                console.log(`Tab ${index + 1}:`, {
                    id: tab.id,
                    active: tab.active,
                    url: url,
                    title: title
                });
            });
            
            console.groupEnd();
        } catch (err) {
            console.error("Error listing tabs:", err);
        }
    },
    
    /**
     * Search for tabs matching a URL pattern and show results
     * @param {string} urlPattern - URL pattern to search for
     * @returns {Promise<chrome.tabs.Tab[]>}
     */
    findTabsByPattern: async function(urlPattern) {
        try {
            console.group(`🔍 Chrome Cap Debug: Searching tabs with pattern "${urlPattern}"`);
            
            const tabs = await chrome.tabs.query({ url: urlPattern });
            
            if (tabs.length === 0) {
                console.warn("No tabs found matching this pattern");
            } else {
                console.log(`Found ${tabs.length} tab(s):`);
                tabs.forEach((tab, index) => {
                    console.log(`Match ${index + 1}:`, {
                        id: tab.id,
                        active: tab.active,
                        url: tab.url,
                        title: tab.title
                    });
                });
            }
            
            console.groupEnd();
            return tabs;
        } catch (err) {
            console.error("Error searching tabs:", err);
            console.groupEnd();
            return [];
        }
    },
    
    /**
     * Test if a URL pattern is valid for chrome.tabs.query
     * @param {string} urlPattern - URL pattern to test
     * @returns {Promise<boolean>}
     */
    testUrlPattern: async function(urlPattern) {
        console.group(`🧪 Chrome Cap Debug: Testing URL pattern validity: "${urlPattern}"`);
        
        try {
            await chrome.tabs.query({ url: urlPattern });
            console.log("✅ Pattern is valid");
            console.groupEnd();
            return true;
        } catch (err) {
            console.error("❌ Invalid URL pattern:", err);
            console.groupEnd();
            return false;
        }
    },
    
    /**
     * Convert a regular URL to a valid pattern for chrome.tabs.query
     * @param {string} url - A regular URL like https://example.com/page
     * @returns {string} URL pattern like *://example.com/*
     */
    urlToPattern: function(url) {
        if (!url) return "";
        
        try {
            if (url.includes("*")) {
                return url; // Already a pattern
            }
            
            const urlObj = new URL(url);
            const pattern = `*://${urlObj.hostname}/*`;
            
            console.log(`🔄 Converted URL "${url}" to pattern "${pattern}"`);
            return pattern;
        } catch (err) {
            console.error(`❌ Failed to convert URL "${url}" to pattern:`, err);
            return url; // Return original as fallback
        }
    },
    
    /**
     * Analyze a tab selection error and suggest fixes
     * @param {Error} error - The error object from chrome.tabs.query
     * @param {string} originalUrl - The URL pattern that was used
     * @returns {string} Suggested fix
     */
    analyzeTabError: function(error, originalUrl) {
        const errorString = error.toString();
        let suggestion = "Unknown error. ";
        
        if (errorString.includes("Invalid url pattern")) {
            suggestion = "URL pattern format is invalid. ";
            
            // Specific fixes for common URL issues
            if (!originalUrl.includes("*")) {
                suggestion += "Add wildcards: change to pattern format like *://hostname/*";
            } else if (originalUrl.includes("?") || originalUrl.includes("&")) {
                suggestion += "URL patterns can't include query parameters. Use hostname pattern only.";
            } else {
                suggestion += "Use the urlToPattern helper to convert your URL to a valid pattern.";
            }
        } else if (errorString.includes("No tab with id")) {
            suggestion = "Tab ID not found. The tab may have been closed or navigated to another page.";
        }
        
        console.warn(`🛠️ Tab error analysis: ${suggestion}`);
        return suggestion;
    },
    
    /**
     * Properly capture a tab by ID, handling tab switching optimally
     * 
     * This function:
     * 1. Checks if the tab is already active
     * 2. Only switches if necessary
     * 3. Captures the screenshot
     * 4. Switches back to original tab if needed
     * 
     * @param {number} tabId - ID of the tab to capture
     * @param {number} [delay=500] - Delay in ms to wait after switching tabs
     * @returns {Promise<string>} dataUrl of the screenshot
     */
    captureTabById: async function(tabId, delay = 500) {
        console.group(`📸 Chrome Cap Debug: Capturing Tab ID ${tabId}`);
        
        try {
            if (!tabId) {
                throw new Error("No tab ID provided");
            }
            
            // Get the target tab to verify it exists
            const tab = await chrome.tabs.get(tabId);
            console.log("Target tab:", { id: tab.id, url: tab.url, active: tab.active });
            
            // Check if the tab is already active
            if (tab.active) {
                console.log("✓ Tab is already active, capturing directly");
                
                // Capture the current tab
                const dataUrl = await new Promise((resolve, reject) => {
                    chrome.tabs.captureVisibleTab(null, { format: "png" }, (dataUrl) => {
                        if (chrome.runtime.lastError) {
                            reject(chrome.runtime.lastError);
                        } else {
                            resolve(dataUrl);
                        }
                    });
                });
                
                console.log("✓ Screenshot captured successfully");
                console.groupEnd();
                return dataUrl;
            }
            
            // Tab is not active, get current active tab
            const activeTabs = await chrome.tabs.query({ active: true, currentWindow: true });
            const originalTabId = activeTabs.length > 0 ? activeTabs[0].id : null;
            
            console.log("Current active tab:", originalTabId);
            
            // Switch to the target tab
            console.log(`Switching to tab ID ${tabId}...`);
            await chrome.tabs.update(tabId, { active: true });
            
            // Wait for the tab to become fully visible
            console.log(`Waiting ${delay}ms for tab to become fully visible...`);
            await new Promise(resolve => setTimeout(resolve, delay));
            
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
            
            console.log("✓ Screenshot captured successfully");
            
            // Switch back to the original tab if needed
            if (originalTabId && originalTabId !== tabId) {
                console.log(`Switching back to original tab ID ${originalTabId}...`);
                await chrome.tabs.update(originalTabId, { active: true });
            }
            
            console.groupEnd();
            return dataUrl;
        } catch (error) {
            console.error("❌ Error capturing tab:", error);
            console.groupEnd();
            throw error;
        }
    }
};

// Log that the helper has been loaded
console.log("🛠️ Chrome Cap Debug Helper loaded"); 