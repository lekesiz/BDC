#!/usr/bin/env python3
"""Simple HTTP server to serve test files."""

import http.server
import socketserver
import os
import sys
import webbrowser
import threading
import time

PORT = 8080

class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()

def serve_files():
    """Serve files from current directory."""
    os.chdir('/Users/mikail/Desktop/BDC')
    
    with socketserver.TCPServer(("", PORT), CORSHTTPRequestHandler) as httpd:
        print(f"🌐 Serving test files at http://localhost:{PORT}")
        print(f"📄 Test file: http://localhost:{PORT}/test_auth_security.html")
        
        # Open browser after a short delay
        def open_browser():
            time.sleep(1)
            webbrowser.open(f'http://localhost:{PORT}/test_auth_security.html')
        
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Stopping test server...")
            httpd.shutdown()

if __name__ == "__main__":
    serve_files()