#!/usr/bin/env python3
"""
Example of integrating the chromecap API server with a custom FastAPI application

This example demonstrates how to:
1. Start the chromecap server programmatically
2. Create a custom FastAPI application that interacts with chromecap
3. Create endpoints that capture and return screenshots
"""

import os
import sys
import asyncio
import subprocess
import time
import uuid
import requests
from pathlib import Path
import threading
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Dict, Any


# Create custom FastAPI app
app = FastAPI(title="ChromeCap Integration Example")


# Define models
class CaptureRequest(BaseModel):
    url: HttpUrl
    output_filename: Optional[str] = None
    timeout: int = 30


class CaptureResponse(BaseModel):
    success: bool
    message: str
    screenshot_id: Optional[str] = None
    screenshot_path: Optional[str] = None


# Global settings
CHROMECAP_SERVER_URL = "http://localhost:8000"
SCREENSHOT_DIR = Path("./screenshot_storage")
SCREENSHOT_DIR.mkdir(exist_ok=True)


def ensure_server_running():
    """Make sure the chromecap server is running"""
    try:
        response = requests.get(f"{CHROMECAP_SERVER_URL}/status", timeout=2)
        if response.status_code == 200:
            print("ChromeCap server is already running")
            return True
    except:
        pass
    
    # Start the server
    print("Starting ChromeCap server...")
    
    # We'll start it in a separate process
    server_process = subprocess.Popen(
        ["chromecap", "start"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start
    for _ in range(5):  # Try 5 times
        time.sleep(1)
        try:
            response = requests.get(f"{CHROMECAP_SERVER_URL}/status", timeout=2)
            if response.status_code == 200:
                print("ChromeCap server started successfully")
                return True
        except:
            pass
    
    print("Failed to start ChromeCap server")
    return False


async def capture_screenshot(url: str, output_path: Optional[str] = None, timeout: int = 30):
    """Capture a screenshot asynchronously"""
    # Create a unique request ID
    request_id = str(uuid.uuid4())
    
    # Initiate the capture
    params = {
        'url': str(url),
        'request_id': request_id,
        'extension_type': 'BGPT'
    }
    
    # Make the capture request (in a non-blocking way)
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(
        None,
        lambda: requests.get(
            f"{CHROMECAP_SERVER_URL}/api/capture",
            params=params
        )
    )
    
    if response.status_code != 200:
        return {
            "success": False,
            "message": f"Failed to initiate capture: {response.text}"
        }
    
    # Record start time for timeout
    start_time = time.time()
    
    # Poll for the screenshot
    while True:
        # Check if we've exceeded the timeout
        if time.time() - start_time > timeout:
            return {
                "success": False,
                "message": "Timed out waiting for screenshot"
            }
        
        # Poll for the result (non-blocking)
        try:
            response = await loop.run_in_executor(
                None,
                lambda: requests.get(
                    f"{CHROMECAP_SERVER_URL}/api/screenshots",
                    timeout=5,
                )
            )
            
            screenshots = response.json().get("screenshots", [])
            matching_screenshots = [
                s for s in screenshots 
                if s.get("request_id") == request_id
            ]
            
            if matching_screenshots:
                screenshot = matching_screenshots[0]
                screenshot_id = screenshot.get("id")
                
                # Get the raw image data
                image_response = await loop.run_in_executor(
                    None,
                    lambda: requests.get(
                        f"{CHROMECAP_SERVER_URL}/api/raw-screenshot/{screenshot_id}",
                        timeout=5
                    )
                )
                
                if image_response.status_code == 200:
                    final_path = output_path
                    
                    # If no output path provided, create one based on UUID
                    if not final_path:
                        filename = f"screenshot_{screenshot_id}.png"
                        final_path = str(SCREENSHOT_DIR / filename)
                    
                    # Write the image to disk
                    with open(final_path, "wb") as f:
                        f.write(image_response.content)
                    
                    return {
                        "success": True,
                        "message": "Screenshot captured successfully",
                        "screenshot_id": screenshot_id,
                        "screenshot_path": final_path
                    }
        
        except Exception as e:
            # Just log and continue polling
            print(f"Error polling for screenshot: {e}")
        
        # Wait a bit before polling again
        await asyncio.sleep(0.5)


@app.on_event("startup")
async def startup_event():
    """Run when the server starts"""
    # Ensure ChromeCap server is running
    if not ensure_server_running():
        print("ERROR: Could not start ChromeCap server")
        sys.exit(1)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "app": "ChromeCap Integration Example",
        "endpoints": [
            "/capture - Capture a screenshot",
            "/screenshots - List all screenshots",
            "/screenshot/{screenshot_id} - Get a specific screenshot"
        ]
    }


@app.post("/capture", response_model=CaptureResponse)
async def capture_endpoint(capture_req: CaptureRequest):
    """Capture a screenshot via API"""
    output_path = None
    if capture_req.output_filename:
        output_path = str(SCREENSHOT_DIR / capture_req.output_filename)
    
    result = await capture_screenshot(
        url=str(capture_req.url),
        output_path=output_path,
        timeout=capture_req.timeout
    )
    
    if not result["success"]:
        return CaptureResponse(
            success=False,
            message=result["message"]
        )
    
    return CaptureResponse(
        success=True,
        message=result["message"],
        screenshot_id=result["screenshot_id"],
        screenshot_path=result["screenshot_path"]
    )


@app.get("/screenshots")
async def list_screenshots():
    """List all screenshots in storage"""
    screenshots = []
    
    for file_path in SCREENSHOT_DIR.glob("*.png"):
        screenshots.append({
            "id": file_path.stem,
            "filename": file_path.name,
            "path": str(file_path),
            "size_bytes": file_path.stat().st_size
        })
    
    return {"screenshots": screenshots, "count": len(screenshots)}


@app.get("/screenshot/{screenshot_id}")
async def get_screenshot(screenshot_id: str):
    """Get a specific screenshot by ID"""
    # Look for matching file
    for file_path in SCREENSHOT_DIR.glob(f"*{screenshot_id}*.png"):
        return FileResponse(
            path=str(file_path),
            media_type="image/png",
            filename=file_path.name
        )
    
    raise HTTPException(status_code=404, detail=f"Screenshot with ID {screenshot_id} not found")


def main():
    # Run the FastAPI app
    print("Starting integration server on http://localhost:8080")
    uvicorn.run(app, host="0.0.0.0", port=8080)


if __name__ == "__main__":
    main() 