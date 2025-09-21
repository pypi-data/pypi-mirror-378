#!/usr/bin/env python3
"""
Screenshot capture and analysis example using chromecap with cursor-agent-tools

This example demonstrates how to:
1. Capture a screenshot using chromecap
2. Analyze the captured image using cursor-agent-tools
3. Save both the image and analysis results
"""

import os
import subprocess
import time
import requests
import tempfile
import webbrowser
from pathlib import Path
import sys

# Try to import cursor-agent-tools
try:
    from cursor_agent.agent import create_agent
    CURSOR_AGENT_AVAILABLE = True
except ImportError:
    CURSOR_AGENT_AVAILABLE = False


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


def analyze_image(image_path, query):
    """Analyze an image using cursor-agent-tools"""
    if not CURSOR_AGENT_AVAILABLE:
        print("\nError: cursor-agent-tools is not installed.")
        print("To use image analysis, install it with:")
        print("pip install cursor-agent-tools")
        return None
    
    try:
        print(f"\nAnalyzing image with query: '{query}'")
        print("Please wait, this may take a moment...\n")
        
        # Create agent and analyze image
        agent = create_agent()
        result = agent.analyze_image(image_path, query)
        
        # Save analysis to text file
        analysis_path = f"{os.path.splitext(image_path)[0]}_analysis.txt"
        with open(analysis_path, 'w') as f:
            f.write(result)
        
        print(f"Analysis saved to: {analysis_path}")
        
        # Print analysis result
        print("\n" + "="*50)
        print("IMAGE ANALYSIS RESULT:")
        print("="*50)
        print(result)
        print("="*50 + "\n")
        
        return analysis_path
        
    except Exception as e:
        print(f"Error analyzing image: {e}")
        return None


def main():
    # Check for cursor-agent-tools
    if not CURSOR_AGENT_AVAILABLE:
        print("Warning: cursor-agent-tools is not installed.")
        print("The screenshot will be captured, but analysis will be skipped.")
        print("To enable analysis, install cursor-agent-tools:")
        print("pip install cursor-agent-tools")
        print()
    
    # Ensure server is running
    if not ensure_server_running():
        return
    
    # URL to capture
    url = "https://news.ycombinator.com/"  # Hacker News has a complex UI for analysis
    
    # Create output directory
    output_dir = Path("./analysis_results")
    output_dir.mkdir(exist_ok=True)
    
    # Capture screenshot
    output_path = output_dir / "hn_screenshot.png"
    screenshot_path = capture_screenshot(url, str(output_path))
    
    if not screenshot_path:
        print("Failed to capture screenshot")
        return
    
    print(f"Success! Screenshot saved to: {screenshot_path}")
    
    # Analyze the image if cursor-agent-tools is available
    if CURSOR_AGENT_AVAILABLE:
        # Example query about UI elements
        query = "Analyze this screenshot of Hacker News. What are the main UI components? Identify any potential usability issues."
        
        analysis_path = analyze_image(screenshot_path, query)
        
        if analysis_path:
            print(f"Analysis complete and saved to: {analysis_path}")
            
            # On macOS, open the image
            if os.name == 'posix' and os.uname().sysname == 'Darwin':
                subprocess.run(['open', screenshot_path])
                subprocess.run(['open', analysis_path])
    else:
        # Just open the image
        if os.name == 'posix' and os.uname().sysname == 'Darwin':
            subprocess.run(['open', screenshot_path])


if __name__ == "__main__":
    main() 