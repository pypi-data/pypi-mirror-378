#!/usr/bin/env python3
"""
Basic screenshot capture example using chromecap

This example demonstrates how to:
1. Start the chromecap server
2. Capture a screenshot of a website
3. Save it to a file
"""

import os
import subprocess
import time
import requests
import tempfile
import webbrowser
from pathlib import Path

def ensure_server_running():
    """Make sure the chromecap server is running"""
    try:
        response = requests.get("http://localhost:8000/status", timeout=2)
        if response.status_code == 200:
            print("Server is already running")
            return True
    except:
        pass
    
    # Start the server
    print("Starting chromecap server...")
    subprocess.Popen(
        ["chromecap", "start"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start
    for _ in range(5):  # Try 5 times
        time.sleep(1)
        try:
            response = requests.get("http://localhost:8000/status", timeout=2)
            if response.status_code == 200:
                print("Server started successfully")
                return True
        except:
            pass
    
    print("Failed to start server")
    return False

def capture_screenshot(url, output_path=None):
    """Capture a screenshot of a URL and save it"""
    # Create a unique request ID
    import uuid
    request_id = str(uuid.uuid4())
    
    # Initiate the capture
    params = {
        'url': url,
        'request_id': request_id,
        'extension_type': 'BGPT'
    }
    
    # Make the capture request
    response = requests.get(
        "http://localhost:8000/api/capture",
        params=params
    )
    
    if response.status_code != 200:
        print(f"Failed to initiate capture: {response.text}")
        return None
    
    # Record start time for timeout
    start_time = time.time()
    timeout = 30  # 30 seconds timeout
    
    print(f"Capturing screenshot of {url}...")
    print("Please switch to Chrome with the BrowserGPT extension to complete the capture.")
    
    # If response indicates HTTP fallback mode, open the client URL
    capture_data = response.json()
    if capture_data.get('status') == 'fallback_http':
        client_url = capture_data.get('client_url')
        print(f"Opening browser capture client: {client_url}")
        webbrowser.open(client_url)
    
    # Poll for the screenshot
    while True:
        try:
            # Check if we've exceeded the timeout
            if time.time() - start_time > timeout:
                print("Timed out waiting for screenshot")
                return None
            
            # Poll for the result
            response = requests.get(
                "http://localhost:8000/api/screenshots",
                timeout=5,
            )
            
            screenshots = response.json().get("screenshots", [])
            matching_screenshots = [
                s for s in screenshots 
                if s.get("request_id") == request_id
            ]
            
            if matching_screenshots:
                screenshot = matching_screenshots[0]
                screenshot_id = screenshot.get("id")
                print(f"Screenshot captured with ID: {screenshot_id}")
                
                # Get the raw image data
                image_response = requests.get(
                    f"http://localhost:8000/api/raw-screenshot/{screenshot_id}",
                    timeout=5
                )
                
                if image_response.status_code == 200:
                    if output_path:
                        with open(output_path, "wb") as f:
                            f.write(image_response.content)
                        print(f"Screenshot saved to {output_path}")
                        return output_path
                    else:
                        # Save to temp file
                        temp_file = tempfile.NamedTemporaryFile(
                            suffix=".png", delete=False
                        )
                        temp_file.write(image_response.content)
                        temp_file.close()
                        print(f"Screenshot saved to temporary file: {temp_file.name}")
                        return temp_file.name
            
            # Wait a bit before polling again
            time.sleep(0.5)
            print(".", end="", flush=True)
            
        except Exception as e:
            print(f"\nError polling for results: {e}")
            time.sleep(1)

def main():
    # Ensure server is running
    if not ensure_server_running():
        return
    
    # Capture a screenshot
    url = "https://example.com"
    output_dir = Path("./screenshots")
    output_dir.mkdir(exist_ok=True)
    
    output_path = output_dir / "example_screenshot.png"
    result = capture_screenshot(url, str(output_path))
    
    if result:
        print(f"Success! Screenshot saved to: {result}")
        
        # On macOS, open the image
        if os.name == 'posix' and os.uname().sysname == 'Darwin':
            subprocess.run(['open', result])
    else:
        print("Failed to capture screenshot")

if __name__ == "__main__":
    main() 