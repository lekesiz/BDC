#!/usr/bin/env python3
import http.server
import socketserver
import os
import subprocess
import time
import threading
import webbrowser
import signal
import sys

# Configure ports
HTML_PORT = 8090
API_PORT = 9888

# Directory containing the client files
CLIENT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "client")

# Function to run the API server
def run_api_server():
    api_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "server", "complete_test_api.py")
    try:
        print(f"Starting API server on port {API_PORT}...")
        # Modify the script to use the new port
        with open(api_script, 'r') as f:
            content = f.read()
        
        # Temporarily modify the port in the API script
        content = content.replace("app.run(host='0.0.0.0', port=8888, debug=True)", 
                                f"app.run(host='0.0.0.0', port={API_PORT}, debug=True)")
        
        temp_script = api_script + ".temp"
        with open(temp_script, 'w') as f:
            f.write(content)
        
        # Execute the modified script
        api_process = subprocess.Popen(["python3", temp_script])
        
        return api_process, temp_script
    except Exception as e:
        print(f"Error starting API server: {e}")
        return None, None

# Handle CTRL+C to terminate all processes
def signal_handler(sig, frame):
    print("Shutting down servers...")
    
    # Clean up temp file if exists
    if os.path.exists(temp_api_script):
        os.remove(temp_api_script)
    
    # Terminate API server if running
    if api_process:
        api_process.terminate()
    
    sys.exit(0)

if __name__ == "__main__":
    # Update URLs in HTML files
    os.chdir(CLIENT_DIR)
    
    # Start the API server
    api_process, temp_api_script = run_api_server()
    
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Create a handler that serves files from the client directory
    handler = http.server.SimpleHTTPRequestHandler
    
    # Create a server
    print(f"Starting HTML server on port {HTML_PORT}...")
    with socketserver.TCPServer(("", HTML_PORT), handler) as httpd:
        print(f"Serving the enhanced login UI at http://localhost:{HTML_PORT}/enhanced-login.html")
        print(f"API server should be running at http://localhost:{API_PORT}")
        print("Press Ctrl+C to stop the servers")
        
        # Open the login page in a browser
        webbrowser.open(f"http://localhost:{HTML_PORT}/enhanced-login.html")
        
        # Start serving
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            # Cleanup
            httpd.server_close()
            if api_process:
                api_process.terminate()
            if os.path.exists(temp_api_script):
                os.remove(temp_api_script)