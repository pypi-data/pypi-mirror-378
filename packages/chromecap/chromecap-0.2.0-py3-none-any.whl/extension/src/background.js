/**
 * Chrome Cap - Background Service Worker
 * Listens for messages and captures screenshots of tabs
 */

// Listen for messages from the client page
window.addEventListener('message', handleMessage);

// Add a listener for content script messages
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log('Received message from content script:', message);
  if (message.action === 'relayMessage') {
    handleMessage({ data: message.data });
  }
  sendResponse({ success: true });
  return true;
});

/**
 * Handle incoming messages
 * @param {MessageEvent} event - The message event
 */
async function handleMessage(event) {
  console.log('Message received in background:', event.data);
  
  // Validate message
  if (!event.data || typeof event.data !== 'object') {
    console.log('Invalid message format');
    return;
  }
  
  const { action, source, targetUrl, callbackUrl } = event.data;
  
  // Ignore messages not meant for us
  if (!action) {
    return;
  }
  
  // Source ID for outgoing messages
  const responseSource = 'chrome-cap-extension';
  
  // Handle different message types
  switch (action) {
    case 'ping':
      // Respond to ping to let the client know we're here
      window.postMessage({
        action: 'pong',
        source: responseSource
      }, '*');
      break;
      
    case 'takeScreenshot':
      if (!targetUrl) {
        window.postMessage({
          action: 'screenshot-error',
          source: responseSource,
          error: 'Missing target URL'
        }, '*');
        return;
      }
      
      try {
        await captureScreenshot(targetUrl, callbackUrl);
      } catch (error) {
        console.error('Error capturing screenshot:', error);
        window.postMessage({
          action: 'screenshot-error',
          source: responseSource,
          error: error.message || 'Failed to capture screenshot'
        }, '*');
      }
      break;
      
    default:
      console.log('Unknown action:', action);
  }
}

/**
 * Capture a screenshot of the specified URL
 * @param {string} targetUrl - The URL to capture
 * @param {string} callbackUrl - The URL to send the screenshot to
 */
async function captureScreenshot(targetUrl, callbackUrl) {
  console.log('Capturing screenshot of:', targetUrl);
  
  try {
    // Get current active tab (to return to later)
    const [currentTab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    // Find existing tab with target URL or create new one
    let targetTab;
    const [existingTab] = await chrome.tabs.query({ url: targetUrl });
    
    if (existingTab) {
      console.log('Found existing tab:', existingTab.id);
      targetTab = existingTab;
      
      // Activate the target tab
      await chrome.tabs.update(targetTab.id, { active: true });
    } else {
      console.log('Creating new tab for target URL');
      targetTab = await chrome.tabs.create({ url: targetUrl, active: true });
      
      // Wait for the tab to load
      await new Promise(resolve => {
        chrome.tabs.onUpdated.addListener(function listener(tabId, changeInfo) {
          if (tabId === targetTab.id && changeInfo.status === 'complete') {
            chrome.tabs.onUpdated.removeListener(listener);
            resolve();
          }
        });
      });
    }
    
    // Give the page a moment to render fully
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Capture the visible area of the tab
    const dataUrl = await chrome.tabs.captureVisibleTab(null, { format: 'png' });
    console.log('Screenshot captured successfully');
    
    // Calculate screenshot size
    const base64Data = dataUrl.split(',')[1];
    const byteCharacters = atob(base64Data);
    const byteSize = byteCharacters.length;
    
    // If a callback URL was provided, send the screenshot to it
    if (callbackUrl) {
      console.log('Sending screenshot to callback URL:', callbackUrl);
      await sendScreenshot(dataUrl, callbackUrl);
    }
    
    // Generate a filename for the screenshot
    const date = new Date();
    const timestamp = date.toISOString().replace(/:/g, '-').replace(/\..+/, '');
    const filename = `screenshot_${timestamp}.png`;
    
    // Notify the client of success
    window.postMessage({
      action: 'screenshot-success',
      source: responseSource,
      image: dataUrl,
      filename: filename,
      size: byteSize
    }, '*');
    
    // Switch back to the original tab
    if (currentTab && currentTab.id !== targetTab.id) {
      await chrome.tabs.update(currentTab.id, { active: true });
    }
    
  } catch (error) {
    console.error('Error in captureScreenshot:', error);
    throw error;
  }
}

/**
 * Send screenshot to the callback URL
 * @param {string} dataUrl - The screenshot data URL
 * @param {string} callbackUrl - The URL to send the screenshot to
 */
async function sendScreenshot(dataUrl, callbackUrl) {
  try {
    const response = await fetch(callbackUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        image: dataUrl
      })
    });
    
    if (!response.ok) {
      throw new Error(`Server responded with status: ${response.status}`);
    }
    
    const data = await response.json();
    console.log('Server response:', data);
    
    return data;
  } catch (error) {
    console.error('Error sending screenshot to server:', error);
    throw error;
  }
}

// Log that the background script is running
console.log('Chrome Cap background script loaded'); 