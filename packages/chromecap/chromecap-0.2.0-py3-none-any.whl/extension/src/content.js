/**
 * Chrome Cap - Content Script
 * This script runs in the context of web pages and helps relay messages to the background script
 */

// Listen for messages from the page
window.addEventListener('message', function(event) {
  // We only accept messages from this window
  if (event.source !== window) {
    return;
  }

  // Check if the message has the required format
  if (!event.data || typeof event.data !== 'object' || !event.data.action) {
    return;
  }

  // Relay the message to the background script
  chrome.runtime.sendMessage({
    action: 'relayMessage',
    data: event.data
  });
});

// Listen for messages from the background script
chrome.runtime.onMessage.addListener(function(message, sender, sendResponse) {
  // Relay messages from background script to the page
  if (message.action === 'relayToPage') {
    window.postMessage(message.data, '*');
    sendResponse({ success: true });
  }
  
  return true;
});

// Announce that the content script is loaded
console.log('Chrome Cap content script loaded'); 