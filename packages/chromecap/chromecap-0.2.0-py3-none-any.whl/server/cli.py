#!/usr/bin/env python
import os
import sys
import webbrowser
import time
from pathlib import Path
import click
import requests
import base64
import uuid
import tempfile
from itertools import cycle
import socket
import random
import json
import asyncio
import subprocess

# Import from config
from server.app.config import SERVER_HOST, SERVER_PORT, SERVER_URL, BASE_DIR

# Try to get version from chromecap if installed
try:
    from chromecap import __version__
except ImportError:
    __version__ = "0.1.0"  # Fallback version

# Import cursor-agent-tools if available
try:
    from cursor_agent_tools import create_agent  # type: ignore
    CURSOR_AGENT_AVAILABLE = True
except ImportError:
    CURSOR_AGENT_AVAILABLE = False
    pass


def get_server_url():
    """Get the server URL using the fixed configuration."""
    return SERVER_URL


def check_server_running():
    """Check if the server is running at the configured URL."""
    try:
        response = requests.get(f"{SERVER_URL}/status", timeout=2)
        return response.status_code == 200
    except Exception:
        return False


def is_port_in_use(port, host='localhost'):
    """Check if a port is already in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) == 0


def find_available_port(start_port=8000, max_attempts=100):
    """Find an available port starting from start_port."""
    # Try to use configured SERVER_PORT first
    if not is_port_in_use(SERVER_PORT):
        return SERVER_PORT
        
    # Then try the start_port
    if start_port != SERVER_PORT and not is_port_in_use(start_port):
        return start_port
        
    # If both are in use, find a random available port
    for _ in range(max_attempts):
        port = random.randint(8000, 9000)
        if not is_port_in_use(port):
            click.echo(f"Port {SERVER_PORT} is in use. Selected alternative port: {port}")
            return port
            
    raise RuntimeError(
        f"Could not find an available port after {max_attempts} attempts"
    )


@click.group()
@click.version_option(version=__version__, prog_name="chromecap")
def cli():
    """Chrome Cap - Capture screenshots of Chrome tabs via CLI"""
    pass


@cli.command()
def version():
    """Show the chromecap version"""
    click.echo(f"ChromeCap version: {__version__}")


@cli.command()
@click.option('--verbose', is_flag=True, help='Show verbose output including server logs')
@click.option('--port', type=int, help='Specify port to use (defaults to SERVER_PORT from config)')
def start(verbose, port):
    """Start the Chrome Cap server"""
    import threading
    from datetime import datetime
    from server.app.config import SERVER_PORT as CONFIG_SERVER_PORT
    
    # Use the port from config by default
    server_port = port or CONFIG_SERVER_PORT
    server_url = f"http://{SERVER_HOST}:{server_port}"

    click.echo(f"🚀 ChromeCap Server v{__version__} initialization")
    click.echo(f"⏱️  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    click.echo("🔧 Configuration:")
    click.echo(f"   - Requested port: {server_port}")
    
    # Check if the requested port is already in use
    if is_port_in_use(server_port):
        click.echo(f"⚠️  Port {server_port} is already in use")
        
        # Check if our server is already running on this port
        if check_server_running():
            click.echo(f"✅ A ChromeCap server is already running at {server_url}")
            return
            
        # Find another available port
        server_port = find_available_port(start_port=server_port)
        server_url = f"http://{SERVER_HOST}:{server_port}"
        click.echo(f"🔄 Switching to available port: {server_port}")
    
    click.echo(f"   - Server URL: {server_url}")

    # Start the server as a subprocess
    server_cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "server.app.main:socket_app",
        "--host", SERVER_HOST,
        "--port", str(server_port),
        "--limit-max-requests", "1000",
        "--timeout-keep-alive", "60"
    ]

    # Create log file for server output
    log_file = os.path.join(BASE_DIR, "chromecap.log")
    
    if verbose:
        click.echo(f"📋 Running command: {' '.join(server_cmd)}")
        click.echo(f"📋 Server logs will be written to: {log_file}")
        with open(log_file, 'w') as f:
            server_process = subprocess.Popen(server_cmd, stdout=f, stderr=f)
    else:
        with open(log_file, 'w') as f:
            server_process = subprocess.Popen(
                server_cmd,
                stdout=f,
                stderr=f
            )

    # Wait for server to start with a spinner
    click.echo("⏳ Waiting for server to start...")
    if not verbose:
        stop_spinner = threading.Event()
        spinner_thread = threading.Thread(
            target=spinner_animation, args=(stop_spinner,)
        )
        spinner_thread.daemon = True
        spinner_thread.start()

    start_time = time.time()
    max_wait_time = 15  # seconds
    server_started = False

    # Keep checking until server starts or timeout
    while time.time() - start_time < max_wait_time:
        if verbose:
            elapsed = time.time() - start_time
            click.echo(f"   Checking server status ({elapsed:.1f}s elapsed)...")

        # Try to connect to the server
        try:
            response = requests.get(f"{server_url}/status", timeout=2)
            if response.status_code == 200:
                server_started = True
                break
        except Exception:
            pass

        # Check if the process is still running
        if server_process.poll() is not None:
            if verbose:
                click.echo(f"   Process exited with code: {server_process.poll()}")
            break

        time.sleep(0.5)

    if not verbose:
        stop_spinner.set()
        spinner_thread.join(0.1)

    if server_started:
        click.echo("\r✅ Server started successfully!")
        click.echo("📊 Server Details:")
        click.echo(f"   - URL: {server_url}")
        click.echo(f"   - Port: {server_port}")
        click.echo(f"   - PID: {server_process.pid}")
        click.echo("   - Status: Running")
        click.echo(f"   - Version: {__version__}")
        
        # Save the port to a temporary file for persistence
        port_file = Path(tempfile.gettempdir()) / "chromecap_port.txt"
        try:
            with open(port_file, 'w') as f:
                f.write(str(server_port))
            if verbose:
                click.echo(f"   - Port saved to: {port_file}")
        except Exception as e:
            if verbose:
                click.echo(f"   - Failed to save port: {e}")

        click.echo("\n🌟 Server is ready! Use the following command to capture screenshots:")
        click.echo("   chromecap capture <URL>")
        return
    else:
        click.echo("\r❌ Server failed to start properly.")
        if server_process.poll() is None:
            click.echo("   Terminating server process...")
            server_process.terminate()
            time.sleep(0.5)  # Give process time to terminate

        # Capture output if available
        if not verbose and server_process.stdout and server_process.stderr:
            stdout, stderr = server_process.communicate()
            if stdout:
                click.echo("   Server stdout:")
                stdout_text = stdout.decode('utf-8', errors='replace')
                click.echo("   " + stdout_text.replace('\n', '\n   '))
            if stderr:
                click.echo("   Server stderr:")
                stderr_text = stderr.decode('utf-8', errors='replace')
                click.echo("   " + stderr_text.replace('\n', '\n   '))

    click.echo(f"❌ Failed to start server.")
    click.echo("   Please check your network configuration and try again.")
    sys.exit(1)


@cli.command()
def status():
    """Check if the Chrome Cap server is running and display details"""
    # Try to read the saved port from the temporary file
    port_file = Path(tempfile.gettempdir()) / "chromecap_port.txt"
    server_ports = [SERVER_PORT]  # Start with default port
    
    # Add saved port if exists
    try:
        if port_file.exists():
            with open(port_file, 'r') as f:
                saved_port_str = f.read().strip()
                if saved_port_str and saved_port_str.isdigit():
                    saved_port = int(saved_port_str)
                    if saved_port != SERVER_PORT:
                        server_ports.insert(0, saved_port)  # Prioritize saved port
    except Exception:
        pass
        
    # Try to connect to server on possible ports
    for port in server_ports:
        server_url = f"http://{SERVER_HOST}:{port}"
        try:
            # First try status endpoint
            status_response = requests.get(f"{server_url}/status", timeout=2)
            if status_response.status_code == 200:
                click.echo("✅ Server status: Running")
                click.echo(f"📊 Server Details:")
                click.echo(f"   - URL: {server_url}")
                click.echo(f"   - Port: {port}")
                
                # Try to get more details from API if available
                try:
                    api_response = requests.get(f"{server_url}/api/status", timeout=2)
                    if api_response.status_code == 200:
                        data = api_response.json()
                        if "version" in data:
                            click.echo(f"   - Version: {data['version']}")
                        if "uptime" in data:
                            click.echo(f"   - Uptime: {data['uptime']}")
                        if "socketio" in data:
                            clients = data["socketio"].get("connected_clients", 0)
                            click.echo(f"   - Connected clients: {clients}")
                        if "screenshots" in data:
                            count = data["screenshots"].get("count", 0)
                            click.echo(f"   - Screenshots stored: {count}")
                except Exception:
                    # If detailed API is not available, just show the basic info
                    pass
                    
                return
        except Exception:
            continue
            
    # If we get here, server is not running on any of the expected ports
    click.echo("❌ Server status: Not running")
    sys.exit(1)


@cli.command()
def stop():
    """Stop the Chrome Cap server"""
    if not check_server_running():
        click.echo("Server is not running")
        return

    try:
        response = requests.post(f"{SERVER_URL}/shutdown")
        if response.status_code == 200:
            click.echo("Server stopped successfully")
        else:
            click.echo(f"Failed to stop server: {response.text}")
    except Exception as e:
        click.echo(f"Error stopping server: {e}")


def spinner_animation(stop_event):
    """Simple spinner animation for CLI."""
    spinner = cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
    while not stop_event.is_set():
        sys.stdout.write(next(spinner))  # write the next character
        sys.stdout.flush()              # flush stdout buffer (actual character display)
        sys.stdout.write('\b')          # erase the last written char
        time.sleep(0.1)


def check_and_set_api_keys():
    """Check for API keys in environment, prompt user to input if missing, and set them."""
    anthropic_key = os.environ.get('ANTHROPIC_API_KEY')
    openai_key = os.environ.get('OPENAI_API_KEY')
    
    if not anthropic_key and not openai_key:
        print("No API keys found in environment variables.")
        print("Please select an API provider to use for image analysis:")
        print("1. Anthropic (Claude)")
        print("2. OpenAI (GPT)")
        
        choice = input("Enter your choice (1 or 2): ").strip()
        
        if choice == "1":
            api_key = input("Enter your ANTHROPIC_API_KEY: ").strip()
            var_name = "ANTHROPIC_API_KEY"
        elif choice == "2":
            api_key = input("Enter your OPENAI_API_KEY: ").strip()
            var_name = "OPENAI_API_KEY"
        else:
            print("Invalid choice. Please run again and select 1 or 2.")
            sys.exit(1)
        
        # Set in current process environment
        os.environ[var_name] = api_key
        
        # Export to shell environment
        shell_cmd = f"export {var_name}='{api_key}'"
        print(f"Setting {var_name} in your environment.")
        print(f"You can add this to your shell profile to make it permanent:")
        print(f"  {shell_cmd}")
        
        # Try to export to shell environment
        try:
            subprocess.run(shell_cmd, shell=True, check=True)
        except subprocess.SubprocessError:
            print("Note: Could not automatically export the variable to your shell environment.")
            print("You may need to manually add it to your shell profile.")
        
        return var_name, api_key
    
    elif anthropic_key:
        return "ANTHROPIC_API_KEY", anthropic_key
    else:
        return "OPENAI_API_KEY", openai_key


def analyze_image(image_path, query, debug=False, save_to_file=False):
    """Analyze an image using cursor-agent-tools if available."""
    if not CURSOR_AGENT_AVAILABLE:
        print("cursor-agent-tools is not available. Cannot analyze image.")
        return

    # Check for required API keys and prompt user if missing
    var_name, api_key = check_and_set_api_keys()
    
    try:
        
        async def run_analysis():
            # Select model based on available API keys
            if var_name == "ANTHROPIC_API_KEY":
                model = 'claude-3-5-sonnet-latest'
                if debug:
                    print(f"Using Anthropic model: {model}")
            else:  # var_name == "OPENAI_API_KEY"
                model = 'gpt-4o'
                if debug:
                    print(f"Using OpenAI model: {model}")
            
            agent = create_agent(model=model)
            
            # Set system prompt for UI expert analysis
            agent.system_prompt = """You are a UI/UX expert with a keen eye for visual design and layout. Your role is to analyze UI elements and provide precise, actionable feedback.

When analyzing UI elements:
1. Be direct and concise in your responses
2. Focus on specific, measurable aspects (alignment, spacing, contrast, etc.)
3. Provide exact values for adjustments when needed (e.g., "move 5px left", "increase padding by 10px")
4. Prioritize functional improvements over subjective preferences
5. Consider accessibility and usability in your analysis

For specific queries:
- If asked about alignment: Check exact positioning and provide precise adjustment values
- If asked about spacing: Measure gaps and suggest specific padding/margin values
- If asked about contrast: Evaluate color ratios and suggest specific color adjustments
- If asked about improvements: List specific, actionable changes with exact values

Example responses:
- "Logo is misaligned by 3px to the right. Move it 3px left to center it."
- "Navigation menu items need 15px more spacing between them for better readability."
- "Text contrast ratio is 3.2:1, below WCAG standards. Increase contrast by using #333333 instead of #666666."
- "Improvements needed: 1) Increase button padding to 12px 24px, 2) Add 20px margin below header, 3) Reduce font size from 18px to 16px for better hierarchy."

Keep responses focused on visual elements and provide exact values for any suggested changes."""

            # Query the image with system prompt included
            full_query = f"""As a UI/UX expert, analyze this image and provide precise, actionable feedback. 
Focus on specific, measurable aspects and provide exact values for any adjustments needed.
Be direct and concise in your response.

{query}"""

            response = await agent.query_image(
                image_paths=[image_path],
                query=full_query
            )
            return response
        
        # Run the async function in the event loop
        if sys.platform == 'win32':
            # Windows requires a specific event loop policy
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
        result = asyncio.run(run_analysis())


        if save_to_file:
            analysis_path = f"{os.path.splitext(image_path)[0]}.txt"
            with open(analysis_path, 'w') as f:
                f.write(result)
            print(f"Analysis saved to: {analysis_path}")
        else:
            print("\nScreenshot/Visual Analysis Result:")
            print("=" * 40)
            print(result)
            print("=" * 40)
    except Exception as e:
        print(f"Error analyzing image: {e}")


def ensure_server_running():
    """Ensure that the server is running, starting it if necessary."""
    # Try to read the saved port from the temporary file
    port_file = Path(tempfile.gettempdir()) / "chromecap_port.txt"
    server_port = SERVER_PORT
    try:
        if port_file.exists():
            with open(port_file, 'r') as f:
                saved_port_str = f.read().strip()
                if saved_port_str and saved_port_str.isdigit():
                    server_port = int(saved_port_str)
                    server_url = f"http://{SERVER_HOST}:{server_port}"
                    # Check if a server is running on the saved port
                    try:
                        response = requests.get(f"{server_url}/status", timeout=2)
                        if response.status_code == 200:
                            click.echo(f"Server is already running at {server_url}")
                            return
                    except Exception:
                        # Saved port is not responsive, will fall back to default behavior
                        pass
    except Exception:
        # If there's any error reading the saved port, just continue with the default
        pass
    
    # Check if default server is running
    if check_server_running():
        click.echo(f"Server is already running at {SERVER_URL}")
        return

    # Start a new server
    click.echo("No running server found. Starting server...")

    # Find an available port
    if is_port_in_use(server_port):
        server_port = find_available_port(start_port=server_port)
    
    server_url = f"http://{SERVER_HOST}:{server_port}"
    click.echo(f"Using port {server_port} for server")

    # Start the server process
    cmd = [
        sys.executable, "-m", "uvicorn", "server.app.main:socket_app",
        "--host", SERVER_HOST, "--port", str(server_port),
        "--limit-max-requests", "1000",
        "--timeout-keep-alive", "60"
    ]
    # Create log file for server output
    log_file = os.path.join(BASE_DIR, "chromecap.log")
    with open(log_file, 'w') as f:
        server_process = subprocess.Popen(
            cmd, stdout=f, stderr=f
        )

    # Wait for server to start
    click.echo(f"Starting server on {server_url}")

    # Check with timeout
    start_time = time.time()
    max_wait_time = 15  # seconds
    server_started = False

    while time.time() - start_time < max_wait_time:
        # Try to connect to the server
        try:
            response = requests.get(f"{server_url}/status", timeout=2)
            if response.status_code == 200:
                server_started = True
                break
        except Exception:
            pass

        # Check if the process is still running
        if server_process.poll() is not None:
            break

        time.sleep(0.5)

    if server_started:
        click.echo(f"Server started successfully on {server_url}")
        
        # Save the port for future use
        try:
            with open(port_file, 'w') as f:
                f.write(str(server_port))
        except Exception:
            pass
            
        return
    else:
        click.echo("Server failed to start properly.")
        if server_process.poll() is None:
            click.echo("Terminating server process...")
            server_process.terminate()
            time.sleep(0.5)

        # Capture output if available
        stdout, stderr = server_process.communicate()
        if stdout:
            click.echo("Server stdout:")
            click.echo(stdout.decode('utf-8', errors='replace'))
        if stderr:
            click.echo("Server stderr:")
            click.echo(stderr.decode('utf-8', errors='replace'))

    click.echo("Failed to start server.")
    click.echo("Please check your network configuration and try again later.")
    sys.exit(1)


@cli.command()
@click.argument('url', required=True)
@click.option(
    '--extension-type',
    type=click.Choice(['STANDARD', 'BGPT']),
    default='BGPT',
    help='Type of extension to use for capturing (STANDARD or BGPT)'
)
@click.option(
    '--output',
    type=click.Path(),
    help='Save screenshot directly to this file path'
)
@click.option(
    '--timeout',
    type=int,
    default=10,
    help='Maximum time to wait for screenshot in seconds'
)
@click.option(
    '--debug',
    is_flag=True,
    help='Enable debugging mode with more verbose output'
)
@click.option(
    '--redirect',
    help='URL to redirect to after capturing screenshot'
)
@click.option(
    '--force-http',
    is_flag=True,
    help='Force using HTTP mode even if Socket.IO clients are available'
)
@click.option(
    '--query',
    help='Query string to analyze the captured image using cursor-agent-tools'
)
@click.option(
    '--socket-timeout',
    type=int,
    default=5,
    help='Seconds to wait for Socket.IO before falling back to HTTP'
)
@click.option(
    '--perform',
    help='Actions to perform on the page before capturing (e.g., "click the login button")'
)
@click.option(
    '--log',
    help='Capture console logs to specified file (e.g., "logs.txt")'
)
def capture(
        url,
        extension_type,
        output,
        timeout,
        debug,
        redirect,
        force_http,
        query,
        socket_timeout,
        perform,
        log):
    """Capture a screenshot of the specified URL and optionally analyze it"""
    # Check for API keys if query is provided
    if query and CURSOR_AGENT_AVAILABLE:
        # Use the check_and_set_api_keys function instead of the old check
        var_name, api_key = check_and_set_api_keys()
        
        if debug:
            if var_name == "ANTHROPIC_API_KEY":
                print("Using Anthropic API for image analysis")
            else:
                print("Using OpenAI API for image analysis")
    
    # Ensure server is running, starting it if necessary
    ensure_server_running()
    server_url = SERVER_URL

    # Generate a unique request ID for this capture
    request_id = str(uuid.uuid4())
    start_time = time.time()
    show_spinner = not debug

    # Validate log file path if provided
    if log:
        # Check if log file path is valid
        log_dir = os.path.dirname(log) if os.path.dirname(log) else "."
        if not os.path.exists(log_dir):
            print(f"ERROR: Log file directory does not exist: {log_dir}")
            sys.exit(1)
        
        # Create log file if it doesn't exist and check if we can write to it
        try:
            with open(log, 'w') as f:
                f.write("")  # Test write
            print(f"✅ Log file created/validated: {log}")
        except (PermissionError, OSError) as e:
            print(f"ERROR: Cannot write to log file {log}: {e}")
            sys.exit(1)

    if debug:
        print(f"Generated request ID: {request_id}")
        print(f"Target URL: {url}")
        print(f"Server URL: {server_url}")
        print(f"Output file: {output}")
        print(f"Timeout: {timeout} seconds")
        print(f"Socket timeout: {socket_timeout} seconds")
        if log:
            print(f"Log file: {log}")
        if redirect:
            print(f"Redirect URL: {redirect}")
        if query:
            print(f"Image analysis query: {query}")

    # Check server status and get Socket.IO info
    try:
        server_status = requests.get(f"{server_url}/api/status").json()
        if debug:
            print(f"Server status: {server_status}")

        socketio_clients = server_status.get('socketio', {}).get('connected_clients', 0)
        if debug:
            print(f"Socket.IO clients connected: {socketio_clients}")
    except requests.RequestException as e:
        print(f"ERROR: Failed to connect to server: {e}")
        sys.exit(1)

    # Initiate the capture request
    try:
        if log:
            # Use log capture flow
            payload = {
                'url': url,
                'log_file': log,
                'request_id': request_id,
                'extension_type': extension_type,
                'timeout': timeout,
            }
            
            capture_response = requests.get(
                f"{server_url}/api/capture-logs",
                params=payload
            )
        elif perform:
            # Use new chromeCapExecute flow
            payload = {
                'url': url,
                'actions': perform,
                'request_id': request_id,
                'extension_type': extension_type,
                'timeout': timeout,
            }
            
            capture_response = requests.get(
                f"{server_url}/api/capture-with-actions",
                params=payload
            )
        else:
            # Use existing capture flow
            payload = {
                'url': url,
                'request_id': request_id,
                'extension_type': extension_type,
                'timeout': timeout,
            }
            
            capture_response = requests.get(
                f"{server_url}/api/capture",
                params=payload
            )
        
        if capture_response.status_code != 200:
            print(f"ERROR: Failed to request capture. Server response: {capture_response.text}")
            sys.exit(1)
            
        capture_data = capture_response.json()
        if debug:
            print(f"Capture request response: {capture_data}")
            
        # Check if the response indicates Socket.IO broadcasting or HTTP fallback
        status = capture_data.get('status', '')
        if status == 'task_broadcasted':
            if log:
                if debug:
                    print(f"Log capture task broadcasted via Socket.IO to {capture_data.get('connected_clients', 0)} client(s)")
                    print("Waiting for extension to capture logs...")
                # Poll for log file creation
                success = poll_for_log_results(request_id, log, server_url, debug)
                if success:
                    return  # Exit successfully
                else:
                    sys.exit(1)  # Exit with error
            else:
                if debug:
                    print(f"Screenshot task broadcasted via Socket.IO to {capture_data.get('connected_clients', 0)} client(s)")
                    print("Waiting for extension to capture and return the screenshot...")
        elif status == 'fallback_http' or force_http:
            client_url = capture_data.get('client_url')
            if client_url:
                if log:
                    print("\n🌐 HTTP Fallback Mode - Log Capture")
                    print("=" * 50)
                    print("📋 No Socket.IO clients connected.")
                    print("🔧 Please ensure BrowserGPT extension is installed and connected.")
                    print(f"\n🔗 Open this URL in Chrome: {client_url}")
                    # Automatically open the URL in default browser
                    webbrowser.open(client_url)
                    print("🚀 URL opened in default browser")
                    print("\n⏳ Waiting for log capture to complete...")
                    # Poll for log file creation
                    success = poll_for_log_results(request_id, log, server_url, debug)
                    if success:
                        return  # Exit successfully
                    else:
                        sys.exit(1)  # Exit with error
                else:
                    print("\nNOTE: No Socket.IO clients connected. You need to use the Chrome extension.")
                    print("1. Make sure the BrowserGPT Chrome extension is installed")
                    print("2. Make sure the extension is running and connected")
                    
                    print(f"\nTo capture, open this URL in Chrome with the extension: {client_url}")
                    # Automatically open the URL in default browser to help with capture
                    webbrowser.open(client_url)
                    print("Please manually allow the extension to capture the tab when prompted.")
        else:
            if debug:
                print(f"Unknown response status: {status}")
    except Exception as e:
        if debug:
            print(f"ERROR: Failed to initiate capture request: {e}")
        else:
            print("ERROR: Failed to initiate capture request. Run with --debug for details.")

    # Display a helpful message to user
    if log:
        print(f"\nWaiting for log capture from {url}...", end='')
    else:
        print(f"\nWaiting for screenshot of {url}...", end='')
    if debug:
        print(f" (request_id: {request_id})")
    else:
        print("")

    # Wait for the capture to complete
    spinner_chars = '|/-\\'
    spinner_idx = 0
    progress_timer = start_time

    while True:
        try:
            # Poll for the result
            poll_url = f"{server_url}/api/screenshots"
            if debug:
                print(f"[DEBUG] Polling URL: {poll_url}")
                print(f"[DEBUG] Polling params: request_id={request_id}")
            response = requests.get(
                poll_url,
                params={"request_id": request_id},  # Add explicit request_id filtering parameter
                timeout=5,
            )

            response_data = response.json()
            screenshots = response_data.get("screenshots", [])
            
            # Debug logging
            if debug:
                print(f"\n[DEBUG] CLI received response: {response_data}")
                print(f"[DEBUG] Response status: {response_data.get('status')}")
                print(f"[DEBUG] Response request_id: {response_data.get('request_id')}")
                print(f"[DEBUG] Expected request_id: {request_id}")
            
            # Check if there's an error response for this request
            if response_data.get("status") == "error" and response_data.get("request_id") == request_id:
                error_msg = response_data.get("error", "Unknown error")
                print(f"\nChromeCap Execute failed: {error_msg}")
                return False
            
            if debug and len(screenshots) > 0:
                print(f"\n[DEBUG] Found {len(screenshots)} screenshots matching request_id: {request_id}")
                for s in screenshots[:3]:  # Show top 3 for debugging
                    print(f"  - ID: {s.get('id')}, Request ID: {s.get('request_id')}")
            elif debug:
                print(f"\n[DEBUG] Found 0 screenshots matching request_id: {request_id}")
                # Check if there are any screenshots at all to help with debugging
                all_screenshots = requests.get(
                    f"{server_url}/api/screenshots",
                    timeout=5,
                ).json().get("screenshots", [])
                
                if all_screenshots:
                    print(f"[DEBUG] However, there are {len(all_screenshots)} screenshots in total:")
                    for s in all_screenshots[:3]:
                        print(f"  - ID: {s.get('id')}, Request ID: {s.get('request_id', 'unknown')}")

            # Look for a screenshot with our request ID
            matching_screenshots = [
                s for s in screenshots
                if s.get("request_id") == request_id
            ]

            if matching_screenshots:
                screenshot = matching_screenshots[0]
                screenshot_id = screenshot.get("id")

                if debug:
                    print(f"\nFound screenshot with ID: {screenshot_id}")
                    print(f"Request ID: {screenshot.get('request_id')}")
                    print(f"Target URL: {screenshot.get('target_url', 'unknown')}")
                else:
                    print("\nScreenshot captured successfully!")

                # Get the raw image data
                image_response = requests.get(
                    f"{server_url}/api/raw-screenshot/{screenshot_id}",
                    timeout=5
                )

                if image_response.status_code == 200:
                    output_filename = output
                    # Save to output file if specified
                    if output:
                        with open(output, "wb") as f:
                            f.write(image_response.content)
                        print(f"Screenshot saved to {output}")
                    else:
                        # Save to temp file
                        temp_file = tempfile.NamedTemporaryFile(
                            suffix=".png", delete=False
                        )
                        temp_file.write(image_response.content)
                        temp_file.close()
                        output_filename = temp_file.name
                        print(f"Screenshot saved to temporary file: {output_filename}")

                    # Perform any requested post-processing or redirection
                    if redirect:
                        print(f"Redirecting to {redirect}")
                        webbrowser.open(redirect)

                    # If using cursor-agent-tools for image analysis
                    if query and CURSOR_AGENT_AVAILABLE:

                    
                        analyze_image(output_filename, query, debug=debug)
                    else:

                        print("Cursor agent available:", CURSOR_AGENT_AVAILABLE)
                        print("No query provided or cursor-agent-tools not available, skipping image analysis")
                    return True
                else:
                    if debug:
                        print(f"\n[DEBUG] Failed to download screenshot: {image_response.status_code}")
                        print(f"Response text: {image_response.text[:200]}")

            # If we're still here, the screenshot isn't ready yet
            if show_spinner:
                current_time = time.time()
                if current_time - progress_timer >= 1.0:
                    # Update spinner every second
                    spinner_char = spinner_chars[spinner_idx % len(spinner_chars)]
                    if log:
                        sys.stdout.write(f"\rWaiting for log capture... {spinner_char} ")
                    else:
                        sys.stdout.write(f"\rWaiting for screenshot... {spinner_char} ")
                    sys.stdout.flush()
                    spinner_idx += 1
                    progress_timer = current_time
            else:
                if debug and time.time() - progress_timer >= 3.0:
                    # In debug mode, print status updates every 3 seconds
                    print(f"\n[DEBUG] Still waiting for screenshot, elapsed time: {int(time.time() - start_time)}s")
                    print(f"[DEBUG] Found {len(screenshots)} screenshots, but none matching request_id: {request_id}")
                    progress_timer = time.time()

            time.sleep(0.5)

            # Use longer timeout for perform operations
            effective_timeout = 180 if perform else timeout  # 3 minutes for perform, original timeout for regular capture
            
            # Check if we've exceeded the timeout
            elapsed_time = time.time() - start_time
            if elapsed_time > effective_timeout:
                print("\nTimed out waiting for screenshot")
                print("\nPossible reasons for timeout:")
                print("1. The Chrome extension is not installed or not connected")
                print("2. The extension doesn't have permission to capture the tab")
                print("3. The browser is not on the target URL")
                print("\nTry running with --debug flag for more information")
                return False

        except KeyboardInterrupt:
            print("\nCapture cancelled by user")
            return False
        except Exception as e:
            if debug:
                print(f"\nError polling for results: {e}")
            time.sleep(1)

            # Check if we've exceeded the timeout
            if time.time() - start_time > effective_timeout:
                print("\nTimed out waiting for screenshot")
                return False


@cli.command()
def list():
    """List all captured screenshots"""
    # Ensure server is running, starting it if necessary
    ensure_server_running()
    
    try:
        response = requests.get(f"{SERVER_URL}/api/screenshots")
        if response.status_code == 200:
            screenshots = response.json().get("screenshots", [])
            if not screenshots:
                click.echo("No screenshots found")
                return

            click.echo(f"Found {len(screenshots)} screenshots:")
            for i, screenshot in enumerate(screenshots, 1):
                # Get relevant data from the screenshot object
                screenshot_id = screenshot.get('id', 'unknown')
                target_url = screenshot.get('target_url', 'unknown')
                request_id = screenshot.get('request_id', 'unknown')
                timestamp = screenshot.get('timestamp', 'unknown')
                
                click.echo(f"{i}. ID: {screenshot_id}")
                click.echo(f"   URL: {target_url}")
                click.echo(f"   Request ID: {request_id}")
                click.echo(f"   Timestamp: {timestamp}")
                click.echo("")
        else:
            click.echo(f"Failed to get screenshots: {response.text}")
    except Exception as e:
        click.echo(f"Error listing screenshots: {e}")


@cli.command()
@click.argument('screenshot_id')
@click.option(
    '--output',
    type=click.Path(),
    help='Save screenshot to this file path'
)
@click.option('--debug', is_flag=True, help='Enable debug mode')
def get(screenshot_id, output, debug=False):
    """Get a specific screenshot by ID"""
    # Ensure server is running, starting it if necessary
    ensure_server_running()
    
    try:
        # First try to get the metadata via the JSON API
        metadata_url = f"{SERVER_URL}/api/screenshots"
        if debug:
            click.echo(f"Fetching screenshots from: {metadata_url}")
            
        metadata_response = requests.get(metadata_url)

        if metadata_response.status_code == 200:
            # Find the screenshot with the matching ID
            screenshots = metadata_response.json().get("screenshots", [])
            
            if debug:
                click.echo(f"Found {len(screenshots)} screenshots in total")
                
            matching_screenshots = [s for s in screenshots if s.get('id') == screenshot_id]
            
            if not matching_screenshots:
                click.echo(f"Screenshot with ID {screenshot_id} not found")
                sys.exit(1)
                
            screenshot = matching_screenshots[0]

            # Print screenshot info
            click.echo(f"Screenshot ID: {screenshot.get('id')}")
            click.echo(f"Target URL: {screenshot.get('target_url', 'unknown')}")
            if 'timestamp' in screenshot:
                click.echo(f"Timestamp: {screenshot.get('timestamp')}")
            if 'request_id' in screenshot:
                click.echo(f"Request ID: {screenshot.get('request_id')}")

            # If output path is specified, download the image
            if output:
                # Get the raw image data
                raw_url = f"{SERVER_URL}/api/raw-screenshot/{screenshot_id}"
                if debug:
                    click.echo(f"Downloading from: {raw_url}")

                raw_response = requests.get(raw_url)

                if raw_response.status_code == 200:
                    # Create output directory if it doesn't exist
                    output_path = Path(output)
                    output_path.parent.mkdir(parents=True, exist_ok=True)

                    # Write the binary image data directly
                    with open(output_path, 'wb') as f:
                        f.write(raw_response.content)

                    click.echo(f"Screenshot saved to {output}")
                else:
                    click.echo(f"Failed to download screenshot: {raw_response.status_code}")
                    if debug:
                        click.echo(f"Response: {raw_response.text[:200]}")
                    sys.exit(1)
        else:
            click.echo(f"Failed to get screenshots: {metadata_response.text}")
            sys.exit(1)
    except Exception as e:
        click.echo(f"Error getting screenshot: {e}")
        if debug:
            import traceback
            click.echo(traceback.format_exc())
        sys.exit(1)


def poll_for_log_results(request_id, log_file, server_url, debug=False):
    """Poll for log file creation and display results"""
    import time
    import json
    
    max_wait_time = 300  # 5 minutes max wait
    poll_interval = 2    # Poll every 2 seconds
    start_time = time.time()
    
    if debug:
        print(f"🔍 Polling for log file: {log_file}")
        print(f"🔍 Request ID: {request_id}")
        print(f"🔍 Max wait time: {max_wait_time} seconds")
    
    while time.time() - start_time < max_wait_time:
        try:
            # First check for errors in the server's error_responses
            try:
                error_response = requests.get(f"{server_url}/api/debug/error-responses")
                if error_response.status_code == 200:
                    response_text = error_response.text.strip()
                    if response_text:  # Only try to parse if there's content
                        error_data = error_response.json()
                        if request_id in error_data.get('error_responses', {}):
                            error_info = error_data['error_responses'][request_id]
                            print(f"\n❌ Log capture failed!")
                            print(f"📁 Log file: {log_file}")
                            print(f"🎯 Target URL: {error_info.get('target_url', 'Unknown')}")
                            print(f"❌ Error: {error_info.get('error', 'Unknown error')}")
                            print(f"🕒 Error time: {error_info.get('timestamp', 'Unknown')}")
                            return False
            except Exception as e:
                if debug:
                    print(f"⚠️ Error checking for error responses: {e}")
            
            # Check if log file exists and has content
            if os.path.exists(log_file):
                try:
                    with open(log_file, 'r') as f:
                        content = f.read().strip()
                        if not content:  # Empty file
                            time.sleep(poll_interval)
                            continue
                        log_data = json.loads(content)
                        if log_data.get('metadata', {}).get('request_id') == request_id:
                            # Log capture completed successfully
                            metadata = log_data.get('metadata', {})
                            logs = log_data.get('logs', [])
                            
                            print(f"\n✅ Log capture completed!")
                            print(f"📁 Log file: {log_file}")
                            print(f"📊 Total logs: {len(logs)}")
                            print(f"⏱️ Duration: {metadata.get('duration_ms', 0) / 1000:.1f} seconds")
                            print(f"🎯 Target URL: {metadata.get('target_url', 'Unknown')}")
                            print(f"🌐 Global logs: {'Enabled' if metadata.get('global_logs', False) else 'Disabled'}")
                            print(f"🕒 Capture time: {metadata.get('capture_time', 'Unknown')}")
                            
                            if debug and logs:
                                print(f"\n📋 Sample logs (first 3):")
                                for i, log_entry in enumerate(logs[:3]):
                                    print(f"  {i+1}. [{log_entry.get('level', 'LOG')}] {log_entry.get('message', '')[:100]}...")
                            
                            print(f"\n🎉 Log capture completed successfully!")
                            return True
                except Exception as e:
                    if debug:
                        print(f"⚠️ Error reading log file: {e}")
            
            time.sleep(poll_interval)
            
        except KeyboardInterrupt:
            print(f"\n❌ Log capture cancelled by user")
            return False
        except Exception as e:
            if debug:
                print(f"⚠️ Error polling for log results: {e}")
            time.sleep(poll_interval)
    
    print(f"\n⏰ Log capture timed out after {max_wait_time} seconds")
    print(f"📁 Check if log file was created: {log_file}")
    return False


@cli.command()
@click.argument('screenshot_id')
def delete(screenshot_id):
    """Delete a specific screenshot by ID"""
    if not check_server_running():
        click.echo("Server is not running. Start it with 'python server/cli.py start'")
        sys.exit(1)

    try:
        response = requests.delete(
            f"{SERVER_URL}/api/screenshots/{screenshot_id}"
        )
        if response.status_code == 200:
            click.echo(f"Screenshot {screenshot_id} deleted successfully")
        else:
            click.echo(f"Failed to delete screenshot: {response.text}")
    except Exception as e:
        click.echo(f"Error deleting screenshot: {e}")


@cli.command()
@click.argument("image_path", type=click.Path(exists=True))
@click.argument("query", required=True)
@click.option("--debug", is_flag=True, help="Show detailed debug information")
@click.option(
    "--save-to-file",
    is_flag=True,
    help="Save analysis result to a text file"
)
def analyze(image_path, query, debug, save_to_file):
    """Analyze an existing image using cursor-agent-tools"""
    # Call the analyze_image function directly
    analyze_image(image_path, query, debug, save_to_file=save_to_file)


@cli.command()
def clear():
    """Delete all screenshots from the server"""
    if not check_server_running():
        click.echo("Server is not running. Start it with 'chromecap start'")
        sys.exit(1)

    try:
        response = requests.delete(f"{SERVER_URL}/api/screenshots")
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                deleted_count = result.get('deleted_count', 0)
                click.echo(f"Successfully cleared {deleted_count} screenshots")
            else:
                click.echo(f"Failed to clear screenshots: {result.get('message', 'Unknown error')}")
        else:
            click.echo(f"Failed to clear screenshots: {response.text}")
    except Exception as e:
        click.echo(f"Error clearing screenshots: {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli()
