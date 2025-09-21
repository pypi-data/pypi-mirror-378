// Global function references
let updateStatus;
let setError;
let handleScreenshotError;
let getUrlParams;

// Socket.IO connection and handlers
let socket = null;
let isSocketConnected = false;

// Define core functions early
// Set error function - define this early so it's available when needed
function setErrorInternal(message) {
    console.error(`[ERROR] ${message}`);
    const errorPanel = document.getElementById('error');
    const errorMessage = document.getElementById('error-message');
    
    if (errorPanel && errorMessage) {
        errorMessage.textContent = message;
        errorPanel.classList.remove('hidden');
        
        // Use console.error as fallback if updateStatus isn't ready
        if (typeof updateStatus === 'function') {
            updateStatus('Error', 'error');
        } else {
            console.error('[STATUS] Error');
        }
    }
}

// Assign to global reference immediately
setError = setErrorInternal;

// Update status function - define early
function updateStatusInternal(message, state) {
    console.log(`[STATUS] ${message} (${state || ''})`);
    
    const statusElement = document.getElementById('status');
    if (!statusElement) return;
    
    const statusText = statusElement.querySelector('.status-text');
    if (!statusText) return;
    
    // Remove all state classes
    statusElement.classList.remove('checking', 'ready', 'capturing', 'success', 'error');
    
    // Add new state class
    if (state) {
        statusElement.classList.add(state);
    }
    
    // Update status text
    statusText.textContent = message;
    
    // Auto-capture is handled in the DOM Content Loaded event handler
}

// Assign to global reference immediately
updateStatus = updateStatusInternal;

/**
 * Handles errors during screenshot capture.
 * @param {string} errorMessage - Error message to display.
 */
async function handleScreenshotErrorInternal(errorMessage) {
    console.error('Screenshot error:', errorMessage);
    updateStatusInternal(`Error: ${errorMessage}`, 'error');
    
    // If we have a callback URL, send the error there
    if (callbackUrl) {
        try {
            const payload = {
                error: errorMessage,
                target_url: targetUrl,
                request_id: requestId,
                chrome_cap_execute: false,
                status: 'error'
            };
            
            console.log('[CALLBACK] Error payload:', payload);
            
            console.log('[CALLBACK] Sending screenshot error to:', callbackUrl);
            
            const fetchResponse = await fetch(callbackUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });
            
            if (!fetchResponse.ok) {
                throw new Error(`HTTP error! status: ${fetchResponse.status}`);
            }
            
            console.log('[CALLBACK] Screenshot error sent successfully');
            
        } catch (error) {
            console.error('[CALLBACK] Failed to send screenshot error:', error);
        }
    }
    
    // Show error info
    const resultInfo = document.getElementById('result-info');
    if (resultInfo) {
        resultInfo.textContent = `Failed to capture screenshot: ${errorMessage}`;
        resultInfo.style.display = 'block';
        resultInfo.className = 'error';
    }
}

// Assign to global reference immediately
handleScreenshotError = handleScreenshotErrorInternal;

document.addEventListener('DOMContentLoaded', async () => {
    console.log('[INIT] Chrome Cap client initializing...');
    
    /**
     * Extracts URL parameters from the window location.
     * @returns {Object} URL parameters as key-value pairs.
     */
    function getUrlParamsInternal() {
        const params = {};
        const queryString = window.location.search.substring(1);
        const pairs = queryString.split('&');
        
        for (const pair of pairs) {
            if (pair === '') continue;
            const parts = pair.split('=');
            params[decodeURIComponent(parts[0])] = decodeURIComponent(parts[1] || '');
        }
        
        return params;
    }
    
    // Set global reference
    getUrlParams = getUrlParamsInternal;
    
    // UI Elements
    const statusElement = document.getElementById('status');
    const statusText = statusElement?.querySelector('.status-text');
    const targetUrlElement = document.getElementById('target-url');
    const captureBtn = document.getElementById('capture-btn');
    const closeBtn = document.getElementById('close-btn');
    const resultPanel = document.getElementById('result');
    const errorPanel = document.getElementById('error');
    const errorMessage = document.getElementById('error-message');
    const retryBtn = document.getElementById('retry-btn');
    const screenshotPreview = document.getElementById('screenshot-preview');
    const filenameElement = document.getElementById('filename');
    const filesizeElement = document.getElementById('filesize');
    const downloadBtn = document.getElementById('download-btn');
    const copyBtn = document.getElementById('copy-btn');
    const modeIndicator = document.getElementById('mode');
    
    // Parse URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const initialTargetUrl = urlParams.get('target');
    const initialCallbackUrl = urlParams.get('callback');
    const initialRequestId = urlParams.get('request_id');
    const initialActions = urlParams.get('actions');
    const initialTimeout = parseInt(urlParams.get('timeout')) || 180; // Default to 180 seconds
    const initialLogFile = urlParams.get('log_file');
    const initialAction = urlParams.get('action');
    const lastCaptureSuccess = urlParams.get('success') === 'true';
    
    // Debug logging for URL parameters
    console.log('🚨 CHROMECAP DEBUG - URL Parameters:', {
        target: initialTargetUrl,
        callback: initialCallbackUrl,
        request_id: initialRequestId,
        actions: initialActions,
        success: lastCaptureSuccess
    });
    console.log('🚨 CHROMECAP DEBUG - Full URL:', window.location.href);
    console.log('🚨 CHROMECAP DEBUG - Search params:', window.location.search);
    
    // Store values in rewritable variables for use in Socket.IO events
    window.targetUrl = initialTargetUrl;
    window.chromeCapActions = initialActions;
    let targetUrl = initialTargetUrl;
    let callbackUrl = initialCallbackUrl;
    let requestId = initialRequestId;
    
    // Debug logging for stored values
    console.log('[DEBUG] Stored values:', {
        targetUrl: window.targetUrl,
        chromeCapActions: window.chromeCapActions,
        callbackUrl: callbackUrl,
        requestId: requestId
    });
    
    // Determine mode
    const isListenerMode = !targetUrl && !callbackUrl;
    if (modeIndicator) {
        modeIndicator.textContent = isListenerMode ? 'LISTENER MODE' : 'CAPTURE MODE';
    }
    
    // Extension Configuration
    let extensionType = urlParams.get('extension_type') || 'BGPT'; // STANDARD or BGPT
    const extensionListenerId = `chrome-cap-${Date.now()}`;
    
    console.log(`[CONFIG] Mode: ${isListenerMode ? 'LISTENER' : 'CAPTURE'}`);
    console.log(`[CONFIG] Extension type: ${extensionType}`);
    console.log(`[CONFIG] Target URL: ${targetUrl}`);
    console.log(`[CONFIG] Callback URL: ${callbackUrl}`);
    console.log(`[CONFIG] Request ID: ${requestId}`);
    console.log(`[CONFIG] Extension listener ID: ${extensionListenerId}`);
    
    // Show success message if redirected after successful capture
    if (lastCaptureSuccess) {
        updateStatus('Last screenshot captured and delivered, switch back to the origin window', 'success');
    }
    
    // Initialize UI
    if (targetUrl && targetUrlElement) {
        targetUrlElement.textContent = targetUrl;
    } else if (!isListenerMode) {
        console.error('[ERROR] Missing target URL parameter');
        setError('Missing target URL parameter');
        return;
    }
    
    // Custom auto-capture initialization
    function checkExtensionReadyForCapture() {
        const startAutoCapture = (state) => {
            console.log('🚨 AUTO DEBUG - startAutoCapture called with state:', state);
            console.log('🚨 AUTO DEBUG - window.captureInitiated:', window.captureInitiated);
            console.log('🚨 AUTO DEBUG - targetUrl:', targetUrl);
            if (state === 'ready' && !window.captureInitiated && targetUrl) {
                console.log('[AUTO] Extension ready, auto-capturing screenshot');
                // Set flag to prevent multiple auto-captures
                window.captureInitiated = true;
                
                // Small delay to ensure everything is initialized
                setTimeout(() => {
                    // Check if we have log capture mode
                    if (initialAction === 'log_capture' && initialLogFile) {
                        console.log('[AUTO] Log capture mode detected - starting automatically');
                        window.chromeCapLogFile = initialLogFile;
                        window.chromeCapLogTimeout = initialTimeout;
                        if (typeof startLogCapture === 'function') {
                            startLogCapture();
                        } else {
                            console.error('[AUTO] startLogCapture function not available');
                            setError('Log capture function not available');
                        }
                    } else if (window.chromeCapActions) {
                        // Check if we have actions to perform (chromeCapExecute mode)
                        console.log('[AUTO] Actions detected, using ChromeCap Execute mode');
                        if (typeof executeChromeCapExecute === 'function') {
                            executeChromeCapExecute();
                        } else {
                            console.error('[AUTO] executeChromeCapExecute function not available');
                            setError('ChromeCap Execute function not available');
                        }
                    } else {
                        console.log('[AUTO] No actions, using regular capture mode');
                        if (typeof captureScreenshot === 'function') {
                            captureScreenshot();
                        } else {
                            console.error('[AUTO] captureScreenshot function not available');
                            setError('Screenshot capture function not available');
                        }
                    }
                }, 1000);
            }
        };
        
        // If statusElement already has ready class, trigger auto-capture
        if (statusElement && statusElement.classList.contains('ready')) {
            startAutoCapture('ready');
        }
        
        // Also hook into updateStatus for future ready state
        const originalUpdateStatus = updateStatus;
        updateStatus = (message, state) => {
            originalUpdateStatus(message, state);
            startAutoCapture(state);
        };
    }
    
    // Setup auto-capture if we're in capture mode
    if (targetUrl) {
        checkExtensionReadyForCapture();
    }
    
    // BGPT Extension State
    let bgptStateId = null;
    
    // Timeout references
    let extensionCheckTimeout = null;
    let captureTimeout = null;
    
    // Add a test button to verify extension connectivity
    const testExtensionBtn = document.createElement('button');
    testExtensionBtn.innerText = 'Test BGPT Extension';
    testExtensionBtn.className = 'btn secondary';
    testExtensionBtn.style.marginTop = '10px';
    testExtensionBtn.onclick = function() {
        testBGPTExtension();
    };
    
    // Add it to the DOM after the status panel
    const statusPanel = document.querySelector('.status-panel');
    if (statusPanel && statusPanel.parentNode) {
        statusPanel.parentNode.insertBefore(testExtensionBtn, statusPanel.nextSibling);
    }
    
    // Check if Chrome extension is available
    function checkExtension() {
        console.log('[CHECK] Starting extension check...');
        updateStatusInternal('Checking for Chrome extension...', 'checking');
        
        // Add a listener for the extension response
        window.addEventListener('message', handleExtensionResponse);
        console.log('[CHECK] Added message event listener');
        
        if (extensionType === 'BGPT') {
            checkBGPTExtension();
        } else {
            checkStandardExtension();
        }
    }
    
    // Check for standard Chrome Cap extension
    function checkStandardExtension() {
        console.log('[STANDARD] Checking for standard Chrome Cap extension...');
        
        // Send a ping message to check if the extension is available
        const pingMessage = {
            action: 'ping',
            source: extensionListenerId
        };
        
        console.log('[SEND] Ping message:', pingMessage);
        window.postMessage(pingMessage, '*');
        
        // Clear any existing timeout
        if (extensionCheckTimeout) {
            console.log('[TIMEOUT] Clearing existing extension check timeout');
            clearTimeout(extensionCheckTimeout);
        }
        
        // Set a timeout for extension response
        console.log('[TIMEOUT] Setting ping response timeout (2s)');
        extensionCheckTimeout = setTimeout(() => {
            // If status is still checking, the extension didn't respond
            if (statusElement.classList.contains('checking')) {
                console.error('[TIMEOUT] No response from standard extension');
                updateStatusInternal('Chrome Cap extension not found', 'error');
                setError('Please make sure the Chrome Cap extension is installed and enabled');
            }
        }, 2000);
    }
    
    // Check for BGPT extension
    function checkBGPTExtension() {
        console.log('[BGPT] Checking for BGPT extension...');
        
        // First, try to get the current stateId
        const stateIdRequest = {
            type: "BGPT_INVOKE_EXTENSION",
            action: "getFreshStateId",
            bgptIndex: false,
        };
        
        console.log('[SEND] BGPT stateId request:', stateIdRequest);
        window.postMessage(stateIdRequest, '*');
        
        // Clear any existing timeout
        if (extensionCheckTimeout) {
            console.log('[TIMEOUT] Clearing existing extension check timeout');
            clearTimeout(extensionCheckTimeout);
        }
        
        // Set a timeout for extension response
        console.log('[TIMEOUT] Setting BGPT extension response timeout (3s)');
        extensionCheckTimeout = setTimeout(() => {
            // If status is still checking and no stateId is set, the extension didn't respond
            if (statusElement.classList.contains('checking') && !bgptStateId) {
                console.error('[TIMEOUT] No response from BGPT extension');
                updateStatusInternal('BGPT extension not found', 'error');
                setError('Please make sure the BGPT extension is installed and enabled');
            }
        }, 3000);
    }
    
    /**
     * Handles response from the extension.
     * @param {MessageEvent} event - Event containing message from extension.
     */
    async function handleExtensionResponse(event) {
        const data = event.data;
        
        // Log all incoming messages for debugging
        console.log('[RECEIVE] Message received:', JSON.stringify(data));
        
        // Get request ID from URL parameters
        const urlParams = getUrlParams();
        const requestId = urlParams.request_id || '';
        
        // Handle BGPT extension messages
        if (extensionType === 'BGPT' && event.source === window && data.type === 'BGPT_FROM_EXTENSION') {
            console.log('[BGPT] Message received from BGPT extension:', JSON.stringify(data.content));
            
            // Handle stateId setting
            if (data.content && data.content.action === 'setStateId') {
                bgptStateId = data.content.stateId;
                window.bgptStateId = bgptStateId;
                console.log('[BGPT] Set BGPT state ID:', bgptStateId);
                
                // Once we have the stateId, send a ping
                const pingMessage = {
                    type: "BGPT_INVOKE_EXTENSION",
                    action: "PING",
                    currentStateId: bgptStateId
                };
                
                console.log('[SEND] BGPT ping message:', JSON.stringify(pingMessage));
                window.postMessage(pingMessage, '*');
                
                // Clear extension check timeout since we received a response
                if (extensionCheckTimeout) {
                    console.log('[TIMEOUT] Clearing extension check timeout after stateId set');
                    clearTimeout(extensionCheckTimeout);
                    extensionCheckTimeout = null;
                }
            } 
            // Handle ping response
            else if (data.content && data.content.action === 'PONG') {
                console.log('[BGPT] Received PONG response');
                updateStatusInternal('BGPT extension detected', 'ready');
                
                // Clear extension check timeout since we received a response
                if (extensionCheckTimeout) {
                    console.log('[TIMEOUT] Clearing extension check timeout after PONG');
                    clearTimeout(extensionCheckTimeout);
                    extensionCheckTimeout = null;
                }
                
                // Directly trigger screenshot capture
                if (targetUrl && !window.captureInitiated) {
                    console.log('[AUTO] Extension ready, directly triggering screenshot capture');
                    window.captureInitiated = true;
                    setTimeout(() => {
                        // Check if we have actions to perform (chromeCapExecute mode)
                        if (window.chromeCapActions) {
                            console.log('[AUTO] Actions detected, using ChromeCap Execute mode');
                            executeChromeCapExecute();
                        } else {
                            console.log('[AUTO] No actions, using regular capture mode');
                            captureScreenshot();
                        }
                    }, 1000);
                }
            }
            // Handle screenshot capture response
            else if (data.content && data.content.action === 'captureScreenResponse') {
                console.log('[BGPT] Received screenshot capture response');
                
                // Check stateId match
                if (data.content.stateId !== bgptStateId) {
                    console.warn(`[BGPT] State ID mismatch. Expected: ${bgptStateId}, Got: ${data.content.stateId}`);
                }
                
                // Clear capture timeout since we received a response
                if (captureTimeout) {
                    console.log('[TIMEOUT] Clearing capture timeout after response');
                    clearTimeout(captureTimeout);
                    captureTimeout = null;
                }
                
                const imageData = data.content.message;
                console.log('[BGPT] Image data received. Keys:', Object.keys(imageData));
                
                if (!imageData || !imageData.image) {
                    console.error('[BGPT] Missing image data in response');
                    await handleScreenshotError('Missing image data in BGPT extension response');
                    return;
                }
                
                // BGPT extension returns raw base64 without prefix, add it
                let imageBase64 = imageData.image;
                
                // Add prefix if it's not already present
                if (imageBase64 && !imageBase64.startsWith('data:')) {
                    console.log('[BGPT] Adding data URL prefix to raw base64 image');
                    imageBase64 = 'data:image/png;base64,' + imageBase64;
                }
                
                console.log('[BGPT] Screenshot captured, size:', estimateBase64Size(imageBase64), 'bytes');
                
                // Process the screenshot with the request ID
                handleScreenshotSuccess(imageBase64);
            }
            // Handle ChromeCap Execute response
            else if (data.content && data.content.action === 'chromeCapExecuteResponse') {
                console.log('[BGPT] Received ChromeCap Execute response:', data.content);
                
                // Clear capture timeout since we received a response
                if (captureTimeout) {
                    console.log('[TIMEOUT] Clearing capture timeout after ChromeCap Execute response');
                    clearTimeout(captureTimeout);
                    captureTimeout = null;
                }
                
                // Handle ChromeCap Execute response (success or error)
                if (data.content.status === 'success') {
                    handleChromeCapExecuteSuccess(data.content);
                } else {
                    handleChromeCapExecuteError(data.content);
                }
            }
            // Handle Log Capture response
            else if (data.content && data.content.action === 'captureLogResponse') {
                console.log('[BGPT] Received Log Capture response:', data.content);
                
                // Clear capture timeout since we received a response
                if (captureTimeout) {
                    console.log('[TIMEOUT] Clearing capture timeout after Log Capture response');
                    clearTimeout(captureTimeout);
                    captureTimeout = null;
                }
                
                // Handle Log Capture response (success or error)
                if (data.content.status === 'success') {
                    handleLogCaptureSuccess(data.content);
                } else {
                    handleLogCaptureError(data.content);
                }
            } else {
                console.log('[BGPT] Unhandled BGPT message action:', data.content?.action);
            }
            
            return;
        }
        
        // Handle standard extension messages
        if (!data || data.source !== 'chrome-cap-extension') {
            return;
        }
        
        console.log('[STANDARD] Message received from Chrome Cap extension:', data.action);
        
        // Handle different response types
        switch (data.action) {
            case 'pong':
                console.log('[STANDARD] Received PONG response');
                updateStatusInternal('Extension detected', 'ready');
                
                // Clear extension check timeout since we received a response
                if (extensionCheckTimeout) {
                    console.log('[TIMEOUT] Clearing extension check timeout after PONG');
                    clearTimeout(extensionCheckTimeout);
                    extensionCheckTimeout = null;
                }
                
                // Directly trigger screenshot capture
                if (targetUrl && !window.captureInitiated) {
                    console.log('[AUTO] Extension ready, directly triggering screenshot capture');
                    window.captureInitiated = true;
                    setTimeout(() => {
                        // Check if we have actions to perform (chromeCapExecute mode)
                        if (window.chromeCapActions) {
                            console.log('[AUTO] Actions detected, using ChromeCap Execute mode');
                            executeChromeCapExecute();
                        } else {
                            console.log('[AUTO] No actions, using regular capture mode');
                            captureScreenshot();
                        }
                    }, 1000);
                }
                break;
                
            case 'screenshot-success':
                console.log('[STANDARD] Received screenshot success response');
                
                // Clear capture timeout since we received a response
                if (captureTimeout) {
                    console.log('[TIMEOUT] Clearing capture timeout after success');
                    clearTimeout(captureTimeout);
                    captureTimeout = null;
                }
                
                // Process the image data with the request ID
                let imageData = data.image;
                if (imageData && !imageData.startsWith('data:image')) {
                    console.log('[STANDARD] Adding data URL prefix to image data');
                    imageData = 'data:image/png;base64,' + imageData;
                }
                
                handleScreenshotSuccess(imageData);
                break;
                
            case 'screenshot-error':
                console.error('[STANDARD] Received screenshot error:', data.error);
                
                // Clear capture timeout since we received a response
                if (captureTimeout) {
                    console.log('[TIMEOUT] Clearing capture timeout after error');
                    clearTimeout(captureTimeout);
                    captureTimeout = null;
                }
                
                await handleScreenshotError(data.error || 'Failed to capture screenshot');
                break;
                
            default:
                console.log('[STANDARD] Unknown action:', data.action);
        }
    }
    
    /**
     * Handles successful screenshot capture.
     * @param {string} data - Screenshot data URL.
     */
    async function handleScreenshotSuccess(data) {
        console.log('[SUCCESS] Screenshot captured');
        
        // If we have a callback URL, send the screenshot there
        if (callbackUrl) {
            try {
                // Format the data for the server
                const imageData = typeof data === 'string' ? data : data.dataUrl;
                const payload = {
                    image: imageData,
                    target_url: targetUrl,
                    request_id: requestId
                };
                
                console.log('[CALLBACK] Sending screenshot to:', callbackUrl);
                
                const response = await fetch(callbackUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(payload)
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                console.log('[CALLBACK] Screenshot sent successfully');
                
                // Only redirect if not already in listener mode with success=true
                const currentUrl = window.location.href;
                if (!currentUrl.includes('/client?success=true')) {
                    console.log('[REDIRECT] Redirecting to listener mode');
                    window.location.href = '/client?success=true';
                } else {
                    console.log('[REDIRECT] Already in listener mode, not redirecting');
                    updateStatus('Screenshot captured and delivered, switch back to the origin window', 'success');
                }
                
            } catch (error) {
                console.error('[CALLBACK] Failed to send screenshot:', error);
                setError(`Failed to send screenshot: ${error.message}`);
            }
        } else {
            // Display the result in the UI
            updateStatus('Screenshot captured successfully!', 'success');
            
            // Handle both string and object data formats
            if (typeof data === 'string') {
                screenshotPreview.src = data;
                filenameElement.textContent = `screenshot_${Date.now()}.png`;
                filesizeElement.textContent = formatFileSize(estimateBase64Size(data));
            } else {
                filenameElement.textContent = data.filename;
                filesizeElement.textContent = formatFileSize(data.size);
                screenshotPreview.src = data.dataUrl;
            }
            
            resultPanel.style.display = 'block';
            errorPanel.style.display = 'none';
        }
    }
    
    /**
     * Handles successful ChromeCap Execute completion.
     * @param {Object} response - ChromeCap Execute response containing action results and screenshot.
     */
    async function handleChromeCapExecuteSuccess(response) {
        console.log('[CHROMECAP_EXECUTE_SUCCESS] ChromeCap Execute completed');
        console.log('[CHROMECAP_EXECUTE_SUCCESS] Action result:', response.actionResult);
        console.log('[CHROMECAP_EXECUTE_SUCCESS] Message data:', response.message);
        console.log('[CHROMECAP_EXECUTE_SUCCESS] Screenshot available:', !!(response.message && response.message.image));
        
        // If we have a callback URL, send the combined result there
        if (callbackUrl) {
            try {
                // Format the data for the server
                const payload = {
                    image: response.message ? response.message.image : null,
                    target_url: response.targetUrl || targetUrl,
                    request_id: requestId,
                    action_result: response.actionResult,
                    action_summary: response.actionResult?.summary || null,
                    action_collected_logs: response.actionResult?.collected_logs || null,
                    action_status: response.actionResult?.status || null,
                    chrome_cap_execute: true
                };
                
                console.log('[CALLBACK] Sending ChromeCap Execute result to:', callbackUrl);
                
                const fetchResponse = await fetch(callbackUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(payload)
                });
                
                if (!fetchResponse.ok) {
                    throw new Error(`HTTP error! status: ${fetchResponse.status}`);
                }
                
                console.log('[CALLBACK] ChromeCap Execute result sent successfully');
                
                // Redirect to listener mode
                const currentUrl = window.location.href;
                if (!currentUrl.includes('/client?success=true')) {
                    console.log('[REDIRECT] Redirecting to listener mode');
                    window.location.href = '/client?success=true';
                } else {
                    console.log('[REDIRECT] Already in listener mode, not redirecting');
                    updateStatus('ChromeCap Execute completed and delivered, switch back to the origin window', 'success');
                }
                
            } catch (error) {
                console.error('[CALLBACK] Failed to send ChromeCap Execute result:', error);
                setError(`Failed to send ChromeCap Execute result: ${error.message}`);
            }
        } else {
            // Display the result in the UI
            updateStatus('ChromeCap Execute completed successfully!', 'success');
            
            // Display action results
            if (response.actionResult) {
                console.log('[CHROMECAP_EXECUTE_SUCCESS] Action results:', response.actionResult);
                
                // Display action result summary if available
                if (response.actionResult.summary) {
                    console.log('[CHROMECAP_EXECUTE_SUCCESS] Action summary:', response.actionResult.summary);
                    updateStatus(`Action completed: ${response.actionResult.summary}`, 'success');
                }
                
                // Display collected logs if available
                if (response.actionResult.collected_logs && response.actionResult.collected_logs.length > 0) {
                    console.log('[CHROMECAP_EXECUTE_SUCCESS] Collected logs:', response.actionResult.collected_logs);
                    // You could add UI elements here to display collected logs
                }
                
                // Display action status
                if (response.actionResult.status) {
                    console.log('[CHROMECAP_EXECUTE_SUCCESS] Action status:', response.actionResult.status);
                }
            }
            
            // Display the screenshot
            if (response.message && response.message.image) {
                let imageBase64 = response.message.image;

                // Add prefix if it's not already present
                if (imageBase64 && !imageBase64.startsWith('data:')) {
                    console.log('[CHROMECAP_EXECUTE_SUCCESS] Adding data URL prefix to screenshot');
                    imageBase64 = 'data:image/png;base64,' + imageBase64;
                }

                screenshotPreview.src = imageBase64;
                filenameElement.textContent = `chromecap_execute_${Date.now()}.png`;
                filesizeElement.textContent = formatFileSize(estimateBase64Size(imageBase64));

                resultPanel.style.display = 'block';
                errorPanel.style.display = 'none';
            }
        }
    }
    
    /**
     * Handles ChromeCap Execute error.
     * @param {Object} response - ChromeCap Execute error response.
     */
    async function handleChromeCapExecuteError(response) {
        console.error('[CHROMECAP_EXECUTE_ERROR] ChromeCap Execute failed:', response.message);
        
        // If we have a callback URL, send the error there
        if (callbackUrl) {
            try {
                const payload = {
                    error: response.message,
                    target_url: response.targetUrl || targetUrl,
                    request_id: requestId,
                    chrome_cap_execute: true,
                    status: 'error'
                };
                
                console.log('[CALLBACK] Error payload:', payload);
                
                console.log('[CALLBACK] Sending ChromeCap Execute error to:', callbackUrl);
                
                const fetchResponse = await fetch(callbackUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(payload)
                });
                
                if (!fetchResponse.ok) {
                    throw new Error(`HTTP error! status: ${fetchResponse.status}`);
                }
                
                console.log('[CALLBACK] ChromeCap Execute error sent successfully');
                
            } catch (error) {
                console.error('[CALLBACK] Failed to send ChromeCap Execute error:', error);
            }
        }
        
        // Display error in UI
        setError(`ChromeCap Execute failed: ${response.message}`);
    }
    
    /**
     * Handles successful log capture completion.
     * @param {Object} response - Log capture response containing log data.
     */
    async function handleLogCaptureSuccess(response) {
        console.log('[LOG_CAPTURE_SUCCESS] Log capture completed');
        console.log('[LOG_CAPTURE_SUCCESS] Response:', response);
        console.log('[LOG_CAPTURE_SUCCESS] Message data:', response.message);
        
        // Extract data from response (following chromeCapExecuteResponse pattern)
        const messageData = response.message || {};
        const logs = messageData.logs || [];
        const metadata = messageData.metadata || {};
        const responseTargetUrl = response.targetUrl || targetUrl;
        const logFile = messageData.logFile || window.chromeCapLogFile;
        
        console.log('[LOG_CAPTURE_SUCCESS] Log data:', logs);
        console.log('[LOG_CAPTURE_SUCCESS] Metadata:', metadata);
        
        // Reset the log capture in progress flag
        window.logCaptureInProgress = false;
        
        // Update UI
        updateStatusInternal('Log capture completed successfully', 'success');
        
        // If we have a callback URL, send the log data there
        if (callbackUrl) {
            try {
                const payload = {
                    request_id: requestId,
                    target_url: responseTargetUrl,
                    log_file: logFile,
                    logs: logs,
                    metadata: metadata,
                    extension_type: extensionType,
                    status: 'success'
                };
                
                console.log('[CALLBACK] Log capture payload:', payload);
                console.log('[CALLBACK] Sending log data to:', callbackUrl);
                
                // Create AbortController for timeout
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 60000); // 60 second timeout
                
                const fetchResponse = await fetch(callbackUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(payload),
                    signal: controller.signal
                });
                
                clearTimeout(timeoutId);
                
                if (!fetchResponse.ok) {
                    throw new Error(`HTTP error! status: ${fetchResponse.status}`);
                }
                
                console.log('[CALLBACK] Log data sent successfully');
                
            } catch (error) {
                console.error('[CALLBACK] Failed to send log data:', error);
            }
        }
        
        // Display success message
        const logCount = logs ? logs.length : 0;
        updateStatusInternal(`Log capture completed! ${logCount} logs captured.`, 'success');
    }
    
    /**
     * Handles log capture error.
     * @param {Object} response - Log capture error response.
     */
    async function handleLogCaptureError(response) {
        console.error('[LOG_CAPTURE_ERROR] Log capture failed:', response.message);
        
        // Reset the log capture in progress flag
        window.logCaptureInProgress = false;
        
        // If we have a callback URL, send the error there
        if (callbackUrl) {
            try {
                const payload = {
                    error: response.message,
                    target_url: response.targetUrl || targetUrl,
                    request_id: requestId,
                    log_file: response.logFile || window.chromeCapLogFile,
                    status: 'error'
                };
                
                console.log('[CALLBACK] Log capture error payload:', payload);
                console.log('[CALLBACK] Sending log capture error to:', callbackUrl);
                
                const fetchResponse = await fetch(callbackUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(payload)
                });
                
                if (!fetchResponse.ok) {
                    throw new Error(`HTTP error! status: ${fetchResponse.status}`);
                }
                
                console.log('[CALLBACK] Log capture error sent successfully');
                
            } catch (error) {
                console.error('[CALLBACK] Failed to send log capture error:', error);
            }
        }
        
        // Display error in UI
        setError(`Log capture failed: ${response.message}`);
    }
    
    /**
     * Initializes Socket.IO connection for listener mode.
     */
    function initializeSocketIO() {
        console.log('[SOCKET.IO] Initializing connection...');
        
        try {
            // Connect to Socket.IO server
            socket = io();
            
            socket.on('connect', () => {
                console.log('🚨 SOCKET.IO DEBUG - Connected to server');
                isSocketConnected = true;
                updateStatus('Connected to server', 'success');
                modeIndicator.textContent = 'LISTENER MODE (CONNECTED)';
            });
            
            socket.on('disconnect', () => {
                console.log('[SOCKET.IO] Disconnected');
                isSocketConnected = false;
                updateStatus('Disconnected from server', 'error');
                modeIndicator.textContent = 'LISTENER MODE (DISCONNECTED)';
            });
            
            socket.on('capture_task', async (task) => {
                console.log('🚨 SOCKET.IO DEBUG - Received capture task:', task);
                console.log('🚨 SOCKET.IO DEBUG - Task type:', task.type);
                console.log('🚨 SOCKET.IO DEBUG - Task actions:', task.actions);
                
                // Initialize capture with the received task parameters
                targetUrl = task.target_url;
                callbackUrl = task.callback_url;
                requestId = task.request_id;
                
                // Update the window.targetUrl as well for global access
                window.targetUrl = task.target_url;
                
                // Update UI
                if (targetUrlElement) {
                    targetUrlElement.textContent = targetUrl;
                }
                
                // Set extension type if provided
                if (task.extension_type) {
                    extensionType = task.extension_type;
                }
                
                // Check if this is a capture-with-actions task
                if (task.type === 'capture_with_actions' && task.actions) {
                    console.log(`[SOCKET.IO] ChromeCap Execute task - Actions: ${task.actions}`);
                    window.chromeCapActions = task.actions;
                    await initializeChromeCapExecuteMode();
                } else if (task.type === 'capture_logs' && task.log_file) {
                    console.log(`[SOCKET.IO] Log capture task - Log file: ${task.log_file}`);
                    window.chromeCapLogFile = task.log_file;
                    window.chromeCapLogTimeout = task.timeout || 300;
                    await initializeLogCaptureMode();
                } else {
                    console.log(`[SOCKET.IO] Regular capture task`);
                    await initializeCaptureMode();
                }
                
                console.log(`[SOCKET.IO] Set target URL: ${targetUrl}`);
                console.log(`[SOCKET.IO] Set callback URL: ${callbackUrl}`);
                console.log(`[SOCKET.IO] Set request ID: ${requestId}`);
            });
            
            // Send heartbeat every 30 seconds
            setInterval(() => {
                if (isSocketConnected) {
                    socket.emit('heartbeat');
                }
            }, 30000);
        } catch (error) {
            console.error('[SOCKET.IO] Error initializing:', error);
            updateStatus('Error connecting to server', 'error');
        }
    }
    
    /**
     * Initializes capture mode from a Socket.IO task.
     */
    async function initializeCaptureMode() {
        console.log('[CAPTURE] Initializing capture mode...');
        updateStatusInternal('Initializing capture...', 'checking');
        
        try {
            // We can't directly use chrome.tabs.query in the webpage context
            // Instead, use the existing captureScreenshot function which uses messaging
            window.captureInitiated = true;
            captureScreenshot();
        } catch (error) {
            console.error('[CAPTURE] Failed to capture screenshot:', error);
            setError(`Failed to capture screenshot: ${error.message}`);
        }
    }
    
    /**
     * Initializes ChromeCap Execute mode from a Socket.IO task.
     */
    async function initializeChromeCapExecuteMode() {
        console.log('[CHROMECAP_EXECUTE] Initializing ChromeCap Execute mode...');
        updateStatusInternal('Initializing ChromeCap Execute...', 'checking');
        
        try {
            // Set flag to prevent multiple executions
            window.captureInitiated = true;
            
            // Execute ChromeCap Execute flow
            await executeChromeCapExecute();
        } catch (error) {
            console.error('[CHROMECAP_EXECUTE] Failed to execute ChromeCap Execute:', error);
            setError(`Failed to execute ChromeCap Execute: ${error.message}`);
        }
    }
    
    /**
     * Executes the ChromeCap Execute flow: switch to tab, perform actions, capture screenshot
     */
    async function executeChromeCapExecute() {
        console.log('[CHROMECAP_EXECUTE] Starting ChromeCap Execute flow');
        console.log('[CHROMECAP_EXECUTE] Target URL:', targetUrl);
        console.log('[CHROMECAP_EXECUTE] Actions:', window.chromeCapActions);
        
        if (!window.chromeCapActions) {
            throw new Error('No actions specified for ChromeCap Execute');
        }
        
        updateStatusInternal('Executing ChromeCap Execute...', 'capturing');
        
        // Send chromeCapExecute message to BGPT extension
        const chromeCapExecuteMessage = {
            type: "BGPT_INVOKE_EXTENSION",
            action: "chromeCapExecute",
            url: targetUrl,
            actions: window.chromeCapActions,
            requestId: requestId,
            bgptIndex: false,
            currentStateId: bgptStateId,
            timeout: initialTimeout
        };
        
        console.log('[SEND] ChromeCap Execute request:', chromeCapExecuteMessage);
        window.postMessage(chromeCapExecuteMessage, '*');
        
        // Set timeout for ChromeCap Execute response
        if (captureTimeout) {
            clearTimeout(captureTimeout);
        }
        
        captureTimeout = setTimeout(() => {
            if (statusElement.classList.contains('capturing')) {
                console.error('[TIMEOUT] ChromeCap Execute timed out');
                updateStatusInternal('ChromeCap Execute timed out', 'error');
                setError('ChromeCap Execute timed out. Please try again.');
            }
        }, initialTimeout * 1000); // Use timeout from URL parameter (convert to milliseconds)
    }
    
    /**
     * Initializes Log Capture mode from a Socket.IO task.
     */
    async function initializeLogCaptureMode() {
        console.log('[LOG_CAPTURE] Initializing Log Capture mode...');
        updateStatusInternal('Initializing Log Capture...', 'checking');
        
        try {
            // Set flag to prevent multiple executions
            if (window.logCaptureInProgress) {
                console.log('[LOG_CAPTURE] Log capture already in progress, skipping...');
                return;
            }
            window.logCaptureInProgress = true;
            
            // Update UI for log capture mode
            updateStatusInternal('Starting log capture...', 'capturing');
            
            // Automatically start log capture
            startLogCapture();
            
            console.log('[LOG_CAPTURE] Log capture mode initialized and started automatically');
            
        } catch (error) {
            console.error('[LOG_CAPTURE] Error initializing log capture mode:', error);
            updateStatusInternal('Error initializing log capture', 'error');
            setError('Failed to initialize log capture mode');
        }
    }
    
    /**
     * Starts the log capture process
     */
    async function startLogCapture() {
        console.log('[LOG_CAPTURE] Starting log capture...');
        updateStatusInternal('Starting log capture...', 'capturing');
        
        try {
            // Get log capture parameters
            const logFile = window.chromeCapLogFile;
            const timeout = window.chromeCapLogTimeout || 300;
            
            if (!logFile) {
                throw new Error('Log file not specified');
            }
            
            console.log(`[LOG_CAPTURE] Log file: ${logFile}, Timeout: ${timeout}s`);
            
            // Send log capture request to extension
            const logCaptureMessage = {
                type: "BGPT_INVOKE_EXTENSION",
                action: "captureLog",
                url: targetUrl,
                logFile: logFile,
                requestId: requestId,
                timeout: timeout,
                bgptIndex: false,
                currentStateId: bgptStateId
            };
            
            console.log('[SEND] Log capture request:', logCaptureMessage);
            window.postMessage(logCaptureMessage, '*');
            
            // Set timeout for log capture response
            if (captureTimeout) {
                clearTimeout(captureTimeout);
            }
            
            captureTimeout = setTimeout(() => {
                if (statusElement.classList.contains('capturing')) {
                    console.error('[TIMEOUT] Log capture timed out');
                    // Reset the log capture in progress flag
                    window.logCaptureInProgress = false;
                    updateStatusInternal('Log capture timed out', 'error');
                    setError('Log capture timed out. Please try again.');
                }
            }, timeout * 1000); // Use timeout from request (convert to milliseconds)
            
        } catch (error) {
            console.error('[LOG_CAPTURE] Error starting log capture:', error);
            // Reset the log capture in progress flag
            window.logCaptureInProgress = false;
            const errorMessage = `Failed to start log capture: ${error.message}`;
            updateStatusInternal('Error starting log capture', 'error');
            setError(errorMessage);
            
            // Send error to server via callback URL
            if (callbackUrl) {
                const errorPayload = {
                    error: errorMessage,
                    target_url: targetUrl,
                    request_id: requestId,
                    log_file: window.chromeCapLogFile,
                    status: 'error'
                };
                
                fetch(callbackUrl, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(errorPayload)
                }).catch(err => console.error('[CALLBACK] Failed to send error:', err));
            }
        }
    }
    
    // Format file size
    function formatFileSize(bytes) {
        if (bytes < 1024) {
            return bytes + ' B';
        } else if (bytes < 1024 * 1024) {
            return (bytes / 1024).toFixed(1) + ' KB';
        } else {
            return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
        }
    }
    
    // Estimate base64 size in bytes
    function estimateBase64Size(dataUrl) {
        // Extract base64 part, handling both formats
        const base64 = dataUrl.includes(',') ? dataUrl.split(',')[1] : dataUrl;
        // Base64 size to binary size: base64Length * 0.75
        return base64 ? Math.floor(base64.length * 0.75) : 0;
    }
    
    // Copy image to clipboard
    function copyImageToClipboard(dataUrl) {
        console.log('[CLIPBOARD] Copying image to clipboard');
        
        // Create a canvas element
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        
        // Create an image element
        const img = new Image();
        img.src = dataUrl;
        
        img.onload = function() {
            console.log('[CLIPBOARD] Image loaded, dimensions:', img.width, 'x', img.height);
            
            // Set canvas dimensions
            canvas.width = img.width;
            canvas.height = img.height;
            
            // Draw image on canvas
            ctx.drawImage(img, 0, 0);
            
            // Copy canvas content to clipboard
            canvas.toBlob(function(blob) {
                try {
                    navigator.clipboard.write([
                        new ClipboardItem({ 'image/png': blob })
                    ]).then(() => {
                        console.log('[CLIPBOARD] Image copied successfully');
                        alert('Screenshot copied to clipboard');
                    }).catch(err => {
                        console.error('[CLIPBOARD] Could not copy image:', err);
                        alert('Failed to copy to clipboard: ' + err);
                    });
                } catch (err) {
                    console.error('[CLIPBOARD] Clipboard API not supported:', err);
                    alert('Your browser does not support copying images to clipboard');
                }
            });
        };
    }
    
    // Button event listeners
    captureBtn.addEventListener('click', () => {
        console.log('[UI] Capture button clicked');
        captureScreenshot();
    });
    
    closeBtn.addEventListener('click', function() {
        console.log('[UI] Close button clicked');
        window.close();
    });
    
    retryBtn.addEventListener('click', () => {
        console.log('[UI] Retry button clicked');
        captureScreenshot();
    });
    
    // Start the application
    console.log('[INIT] Starting extension check...');

    setTimeout(() => {
        checkExtension();
    }, 1000);

    // Format timestamp for display
    function formatNow() {
        const now = new Date();
        return now.toLocaleTimeString();
    }
    
    // Format timestamp for filenames
    function formatFileTimestamp() {
        const now = new Date();
        return now.getFullYear() + 
               ('0' + (now.getMonth() + 1)).slice(-2) + 
               ('0' + now.getDate()).slice(-2) + '_' + 
               ('0' + now.getHours()).slice(-2) + 
               ('0' + now.getMinutes()).slice(-2) + 
               ('0' + now.getSeconds()).slice(-2);
    }
    
    // Make these functions globally accessible
    window.formatNow = formatNow;
    window.formatFileTimestamp = formatFileTimestamp;

    // Test function for BGPT extension
    function testBGPTExtension() {
        console.log('[TEST] Testing BGPT extension connectivity...');
        
        // First, try to get a fresh stateId
        const stateIdRequest = {
            type: "BGPT_INVOKE_EXTENSION",
            action: "getFreshStateId",
            bgptIndex: false,
        };
        
        console.log('[TEST] Sending getFreshStateId request:', JSON.stringify(stateIdRequest));
        window.postMessage(stateIdRequest, '*');
        
        const testStatusElement = document.createElement('div');
        testStatusElement.style.margin = '10px 0';
        testStatusElement.style.padding = '10px';
        testStatusElement.style.backgroundColor = '#f0f8ff';
        testStatusElement.style.borderRadius = '5px';
        testStatusElement.innerText = 'Testing extension connectivity... Check console (F12) for details.';
        
        if (statusPanel && statusPanel.parentNode) {
            statusPanel.parentNode.insertBefore(testStatusElement, testExtensionBtn.nextSibling);
        }
        
        // Set a timeout to check if we got a response
        setTimeout(() => {
            if (bgptStateId) {
                testStatusElement.style.backgroundColor = '#d4edda';
                testStatusElement.innerText = `Extension connected! State ID: ${bgptStateId}`;
            } else {
                testStatusElement.style.backgroundColor = '#f8d7da';
                testStatusElement.innerText = 'Extension not responding. Please check that the BGPT extension is installed and enabled.';
            }
        }, 3000);
    }

    /**
     * Captures a screenshot using the appropriate extension method.
     */
    function captureScreenshot() {
        console.log('[CAPTURE] Starting screenshot capture process');
        updateStatusInternal('Capturing screenshot...', 'capturing');
        
        // Hide result/error panels
        resultPanel.style.display = 'none';
        errorPanel.style.display = 'none';
        
        if (extensionType === 'BGPT') {
            captureBGPTScreenshot();
        } else {
            captureStandardScreenshot();
        }
    }

    /**
     * Captures a screenshot using the BGPT extension.
     */
    function captureBGPTScreenshot() {
        console.log('[BGPT] Initiating BGPT screenshot capture');
        
        if (!bgptStateId) {
            console.error('[BGPT] Cannot capture: missing state ID');
            setError('BGPT extension not ready: Missing state ID');
            return;
        }
        
        // Log the current stateId 
        console.log('[BGPT] Using state ID:', bgptStateId);
        
        // Format target URL as a pattern with wildcards for the query
        let urlPattern = targetUrl;
        
        // Chrome's tabs.query() API requires URL patterns with wildcards
        if (urlPattern && !urlPattern.includes('*')) {
            try {
                const urlObj = new URL(urlPattern);
                
                // Special handling for localhost URLs
                if (urlObj.hostname === 'localhost') {
                    // For localhost, we need to use explicit protocols since wildcards aren't supported
                    urlPattern = `http://localhost:${urlObj.port}/*`;
                    console.log('[BGPT] Converted localhost URL to pattern:', urlPattern);
                } else {
                    urlPattern = `*://${urlObj.hostname}/*`;
                    console.log('[BGPT] Converted URL to pattern:', urlPattern);
                }
            } catch (e) {
                console.error('[BGPT] Invalid URL, using as-is:', urlPattern);
            }
        }
        
        // Use the BGPT extension's captureScreen function
        const captureMessage = {
            type: "BGPT_INVOKE_EXTENSION",
            action: "captureScreen",
            url: urlPattern,
            currentStateId: bgptStateId,
            bgptIndex: false
        };
        
        console.log('[SEND] BGPT capture request:', captureMessage);
        window.postMessage(captureMessage, '*');
        
        // Clear any existing timeout
        if (captureTimeout) {
            clearTimeout(captureTimeout);
        }
        
        // Set a timeout for capture response
        captureTimeout = setTimeout(() => {
            if (statusElement.classList.contains('capturing')) {
                console.error('[TIMEOUT] Screenshot capture timed out');
                updateStatusInternal('Capture timed out', 'error');
                setError('Screenshot capture timed out. Please try again.');
            }
        }, 30000); // 30 seconds timeout
    }

    /**
     * Captures a screenshot using the standard extension.
     */
    function captureStandardScreenshot() {
        console.log('[STANDARD] Initiating standard screenshot capture');
        
        const captureMessage = {
            action: 'takeScreenshot',
            source: extensionListenerId,
            targetUrl: targetUrl,
            callbackUrl: callbackUrl
        };
        
        console.log('[SEND] Standard capture request:', captureMessage);
        window.postMessage(captureMessage, '*');
        
        // Clear any existing timeout
        if (captureTimeout) {
            clearTimeout(captureTimeout);
        }
        
        // Set a timeout for capture response
        captureTimeout = setTimeout(() => {
            if (statusElement.classList.contains('capturing')) {
                console.error('[TIMEOUT] Screenshot capture timed out');
                updateStatusInternal('Capture timed out', 'error');
                setError('Screenshot capture timed out. Please try again.');
            }
        }, 30000); // 30 seconds timeout
    }

    // Update the main initialization code
    const params = getUrlParams();
    
    if (params.target) {
        // We're in capture mode
        console.log('[INIT] Running in capture mode');
        
        // Start the extension check to initiate capture process
        setTimeout(() => {
            checkExtension();
        }, 1000);
        
        // No need to redirect - the handleScreenshotSuccess function handles that
    } else {
        // We're in listener mode
        console.log('[INIT] Running in listener mode');
        
        try {
            // Only initialize Socket.IO in listener mode
            if (typeof io !== 'undefined') {
                initializeSocketIO();
            } else {
                console.error('[SOCKET.IO] Socket.IO client library not loaded');
                updateStatus('Socket.IO not available', 'error');
            }
        } catch (e) {
            console.error('[SOCKET.IO] Error initializing Socket.IO:', e);
            updateStatus('Error initializing Socket.IO', 'error');
        }
        
        // Update UI for listener mode
        document.getElementById('status').style.display = 'block';
        updateStatus('Initializing connection to server...');
    }
}); 