/**
 * Chrome Cap - BGPT Client Debug Tools
 * 
 * This file contains debugging utilities for Chrome Cap's BGPT integration.
 * Load this file in your browser console to access debugging functions.
 * 
 * Usage:
 *   1. Open Chrome DevTools console (F12)
 *   2. Load this script by entering:
 *      fetch('/static/debug-tools.js').then(r => r.text()).then(t => eval(t))
 *   3. Use the ChromeCapDebug object to access debugging functions
 */

// Create global debug namespace
window.ChromeCapDebug = {
    /**
     * Test BGPT extension communication
     * @returns {Promise<boolean>} True if communication is working
     */
    testBGPTCommunication: function() {
        return new Promise((resolve) => {
            console.group("🧪 Testing BGPT Extension Communication");
            
            // Check if we have a state ID
            if (!window.bgptStateId) {
                console.error("❌ No BGPT state ID found");
                console.log("Try refreshing the page or check if BGPT extension is installed");
                console.groupEnd();
                resolve(false);
                return;
            }
            
            console.log("✓ BGPT state ID found:", window.bgptStateId);
            
            // Set up a response listener
            const messageListener = function(event) {
                const data = event.data;
                
                if (event.source === window && 
                    data && 
                    data.type === 'BGPT_FROM_EXTENSION' && 
                    data.content && 
                    data.content.action === 'PONG') {
                    
                    console.log("✓ Received PONG response from BGPT extension");
                    console.groupEnd();
                    window.removeEventListener('message', messageListener);
                    resolve(true);
                }
            };
            
            // Add the listener
            window.addEventListener('message', messageListener);
            
            // Set a timeout
            setTimeout(() => {
                console.error("❌ No response from BGPT extension (timeout)");
                console.groupEnd();
                window.removeEventListener('message', messageListener);
                resolve(false);
            }, 3000);
            
            // Send ping
            const pingMessage = {
                type: "BGPT_INVOKE_EXTENSION",
                action: "PING",
                currentStateId: window.bgptStateId
            };
            
            console.log("Sending PING to BGPT extension:", pingMessage);
            window.postMessage(pingMessage, "*");
        });
    },
    
    /**
     * Test URL pattern conversion
     * @param {string} url - URL to convert to a pattern
     * @returns {string} - Chrome compatible URL pattern
     */
    convertURL: function(url) {
        console.group(`🔄 Converting URL: ${url}`);
        
        if (!url) {
            console.warn("Empty URL provided");
            console.groupEnd();
            return "";
        }
        
        try {
            if (url.includes("*")) {
                console.log("URL already contains wildcards, using as is");
                console.groupEnd();
                return url;
            }
            
            const urlObj = new URL(url);
            const pattern = `*://${urlObj.hostname}/*`;
            
            console.log(`Converted to pattern: ${pattern}`);
            console.groupEnd();
            return pattern;
        } catch (e) {
            console.error("Failed to convert URL:", e);
            console.groupEnd();
            return url;
        }
    },
    
    /**
     * Request a screenshot of a specific URL
     * @param {string} url - The URL to capture (will be converted to pattern)
     * @returns {Promise<boolean>} - Resolves to true if capture was successful
     */
    captureURL: function(url) {
        return new Promise((resolve) => {
            console.group(`📸 Requesting screenshot of: ${url}`);
            
            // Check if we have a state ID
            if (!window.bgptStateId) {
                console.error("❌ No BGPT state ID found");
                console.groupEnd();
                resolve(false);
                return;
            }
            
            // Convert URL to pattern
            const urlPattern = this.convertURL(url);
            
            // Set up a response listener
            const messageListener = function(event) {
                const data = event.data;
                
                if (event.source === window && 
                    data && 
                    data.type === 'BGPT_FROM_EXTENSION' && 
                    data.content && 
                    data.content.action === 'captureScreenResponse') {
                    
                    if (data.content.status === 'success') {
                        console.log("✓ Screenshot captured successfully");
                        console.groupEnd();
                        window.removeEventListener('message', messageListener);
                        resolve(true);
                    } else {
                        console.error("❌ Screenshot capture failed:", data.content.message);
                        console.groupEnd();
                        window.removeEventListener('message', messageListener);
                        resolve(false);
                    }
                }
            };
            
            // Add the listener
            window.addEventListener('message', messageListener);
            
            // Set a timeout
            setTimeout(() => {
                console.error("❌ No response from BGPT extension (timeout)");
                console.groupEnd();
                window.removeEventListener('message', messageListener);
                resolve(false);
            }, 10000);
            
            // Send capture request
            const captureMessage = {
                type: "BGPT_INVOKE_EXTENSION",
                action: "captureScreen",
                url: urlPattern,
                currentStateId: window.bgptStateId,
                bgptIndex: false
            };
            
            console.log("Sending capture request to BGPT extension:", captureMessage);
            window.postMessage(captureMessage, "*");
        });
    },
    
    /**
     * Monitor all messages for debugging
     * @param {boolean} enable - Whether to enable or disable monitoring
     */
    monitorMessages: function(enable = true) {
        if (this._messageMonitor) {
            window.removeEventListener('message', this._messageMonitor);
            this._messageMonitor = null;
            console.log("🔍 Message monitoring disabled");
            return;
        }
        
        if (enable) {
            this._messageMonitor = function(event) {
                const data = event.data;
                console.group("🔍 Message Intercepted");
                console.log("Source:", event.source === window ? "window" : event.source);
                console.log("Data:", data);
                console.groupEnd();
            };
            
            window.addEventListener('message', this._messageMonitor);
            console.log("🔍 Message monitoring enabled - all postMessage communications will be logged");
        }
    },
    
    /**
     * Diagnostic summary of the client state
     */
    diagnostics: function() {
        console.group("📊 Chrome Cap Client Diagnostics");
        
        console.log("Client URL:", window.location.href);
        console.log("Target URL:", new URLSearchParams(window.location.search).get('target'));
        console.log("Extension type:", new URLSearchParams(window.location.search).get('extension_type') || 'BGPT');
        console.log("BGPT state ID:", window.bgptStateId || "Not set");
        console.log("Document ready state:", document.readyState);
        console.log("Status element:", document.getElementById('status')?.className || "Not found");
        
        const eventListeners = getEventListeners(window);
        console.log("Window event listeners:", eventListeners);
        
        console.groupEnd();
    },
    
    // Internal properties
    _messageMonitor: null
};

console.log("🛠️ Chrome Cap Debug Tools loaded - Access debugging functions via ChromeCapDebug object");
console.log("📚 Available commands:");
console.log("  • ChromeCapDebug.testBGPTCommunication() - Test BGPT extension communication");
console.log("  • ChromeCapDebug.convertURL('https://example.com') - Test URL pattern conversion");
console.log("  • ChromeCapDebug.captureURL('https://example.com') - Test screenshot capture");
console.log("  • ChromeCapDebug.monitorMessages(true) - Monitor all postMessage communications");
console.log("  • ChromeCapDebug.diagnostics() - Show client diagnostic information"); 