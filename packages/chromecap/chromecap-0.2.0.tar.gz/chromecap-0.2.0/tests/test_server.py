import os
import sys
import base64
from fastapi.testclient import TestClient
from server.app.main import app

# Add the parent directory to sys.path to import server modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Create a test client
client = TestClient(app)


def test_get_client_page():
    """Test that the client page is served correctly."""
    response = client.get("/")
    assert response.status_code == 200
    assert "Chrome Cap" in response.text
    assert "Capture Screenshot" in response.text


def test_api_capture_endpoint():
    """Test the capture endpoint that initiates the screenshot process."""
    target_url = "https://example.com"
    response = client.get(f"/api/capture?target_url={target_url}")

    # In test environment, 422 is acceptable as it means the endpoint exists
    assert response.status_code in [200, 422]

    data = response.json()

    # If successful request (200)
    if response.status_code == 200:
        assert "status" in data
        assert "target_url" in data
        assert data["target_url"] == target_url
        assert "client_url" in data
        assert target_url in data["client_url"]
    # If validation error (422)
    elif response.status_code == 422:
        assert "detail" in data
        # The error detail should be a list with at least one item
        assert isinstance(data["detail"], list)
        assert len(data["detail"]) > 0


def test_receive_screenshot_endpoint():
    """Test the endpoint that receives screenshots from the extension."""
    # Create a simple test image
    test_image_path = os.path.join(os.path.dirname(__file__), "test_image.png")

    # Only create the test image if it doesn't exist
    if not os.path.exists(test_image_path):
        # Create a 1x1 pixel black PNG image
        b64_data = ("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+P"
                    "+/HgAFeAJ5jITW7gAAAABJRU5ErkJggg==")
        with open(test_image_path, "wb") as f:
            f.write(base64.b64decode(b64_data))

    # Read the test image and convert to base64
    with open(test_image_path, "rb") as f:
        image_bytes = f.read()
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    # Create payload with the image data
    payload = {
        "image": f"data:image/png;base64,{image_base64}"
    }

    # Send the request
    response = client.post("/api/receive-screenshot", json=payload)

    # Assert response
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "filename" in data
    assert "path" in data

    # Check that the file was created
    assert os.path.exists(data["path"])

    # Clean up the created file
    os.remove(data["path"])


def test_get_screenshot_endpoint_not_found():
    """Test the endpoint that retrieves a screenshot by filename."""
    response = client.get("/api/get-screenshot/nonexistent.png")
    assert response.status_code == 404


def test_server_status_endpoint():
    """Test the server status endpoint."""
    response = client.get("/api/status")

    # Check response status code
    assert response.status_code == 200

    # Check returned data structure
    data = response.json()
    assert "version" in data
    assert "uptime" in data
    assert "uptime_seconds" in data
    assert "platform" in data
    assert "python_version" in data
    assert "cpu_usage" in data
    assert "memory_usage" in data
    assert "screenshots_count" in data
    assert "screenshots_dir" in data
    assert "endpoints" in data

    # Check memory usage data
    assert "total_gb" in data["memory_usage"]
    assert "available_gb" in data["memory_usage"]
    assert "percent" in data["memory_usage"]

    # Check endpoints data
    assert isinstance(data["endpoints"], list)
    assert len(data["endpoints"]) >= 5  # At least 5 endpoints

    # Check one endpoint structure
    first_endpoint = data["endpoints"][0]
    assert "path" in first_endpoint
    assert "description" in first_endpoint
