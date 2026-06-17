#!/usr/bin/env python3
"""
Lexpresso Backend Server
Handles user data persistence to local files
"""

import json
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

USER_STATS_DIR = 'user_stats'

class LexpressoHandler(SimpleHTTPRequestHandler):
    """Custom handler for Lexpresso with API endpoints"""

    def end_headers(self):
        """Add CORS headers to allow API access"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        """Handle preflight CORS requests"""
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)

        if parsed_path.path == '/api/load_user':
            # Load user data from file
            params = parse_qs(parsed_path.query)
            username = params.get('username', [None])[0]

            if not username:
                self.send_error(400, "Username required")
                return

            # Sanitize username
            username = username.lower().strip()
            filepath = os.path.join(USER_STATS_DIR, f'{username}.json')

            if os.path.exists(filepath):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        user_data = json.load(f)

                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(user_data).encode('utf-8'))
                    print(f"[OK] Loaded user: {username}")
                except ConnectionAbortedError:
                    # Client disconnected, ignore
                    pass
                except Exception as e:
                    self.send_error(500, f"Error loading user: {str(e)}")
            else:
                # User doesn't exist yet
                try:
                    self.send_response(404)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'User not found'}).encode('utf-8'))
                except ConnectionAbortedError:
                    # Client disconnected, ignore
                    pass

        elif parsed_path.path == '/api/test':
            # Simple test endpoint to verify server is reachable
            try:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'OK', 'message': 'Server is working!'}).encode('utf-8'))
            except ConnectionAbortedError:
                pass

        elif parsed_path.path == '/api/list_users':
            # List all users
            try:
                if not os.path.exists(USER_STATS_DIR):
                    os.makedirs(USER_STATS_DIR)

                users = [f.replace('.json', '') for f in os.listdir(USER_STATS_DIR)
                         if f.endswith('.json')]

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'users': users}).encode('utf-8'))
            except Exception as e:
                self.send_error(500, f"Error listing users: {str(e)}")

        else:
            # Serve static files normally
            super().do_GET()

    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)

        if parsed_path.path == '/api/save_user':
            # Save user data to file
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)

            try:
                user_data = json.loads(post_data.decode('utf-8'))
                username = user_data.get('username')

                if not username:
                    self.send_error(400, "Username required in data")
                    return

                # Sanitize username
                username = username.lower().strip()

                # Ensure user_stats directory exists
                if not os.path.exists(USER_STATS_DIR):
                    os.makedirs(USER_STATS_DIR)

                # Save to file
                filepath = os.path.join(USER_STATS_DIR, f'{username}.json')
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(user_data, f, indent=2, ensure_ascii=False)

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': True}).encode('utf-8'))
                print(f"[OK] Saved user: {username} ({len(user_data.get('words', {}))} words)")

            except ConnectionAbortedError:
                # Client disconnected, but file was saved successfully
                pass
            except Exception as e:
                self.send_error(500, f"Error saving user: {str(e)}")

        else:
            self.send_error(404, "Endpoint not found")

    def log_message(self, format, *args):
        """Suppress default logging except for errors"""
        if self.command in ['GET', 'POST'] and '/api/' in self.path:
            # Only log API requests
            return
        # Let static file requests be silent
        return

def get_local_ip():
    """Get the local network IP address"""
    import socket
    try:
        # Create a socket to find the local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "127.0.0.1"

def run_server(port=8000):
    """Start the Lexpresso server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, LexpressoHandler)

    local_ip = get_local_ip()

    print(f"""
============================================================
              Lexpresso Server Running
============================================================
  Local:      http://localhost:{port}
  Network:    http://{local_ip}:{port}

  User data saved to: {USER_STATS_DIR}/
  Press Ctrl+C to stop
============================================================

To access from your smartphone:
   1. Make sure your phone is on the same WiFi network
   2. Open: http://{local_ip}:{port}
    """)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\nServer stopped.")

if __name__ == '__main__':
    # Use PORT from environment variable (for cloud platforms) or default to 80 for web hosting
    port = int(os.environ.get('PORT', 80))
    run_server(port)
