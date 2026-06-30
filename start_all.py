import http.server
import socketserver
import os
import json
import urllib.request
import threading

PORT = 3000
API_BASE = "http://localhost:8000"
FRONTEND_DIR = r"E:\Cloudbook_git\supermarket\frontend"

class FrontendHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=FRONTEND_DIR, **kwargs)
    
    def log_message(self, format, *args):
        pass

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

def start_frontend():
    os.chdir(FRONTEND_DIR)
    with socketserver.TCPServer(("", PORT), FrontendHandler) as httpd:
        print(f"Frontend running on http://localhost:{PORT}")
        httpd.serve_forever()

t = threading.Thread(target=start_frontend, daemon=True)
t.start()

# Start backend
import subprocess, sys
os.chdir(r"E:\Cloudbook_git\supermarket\backend")
proc = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
)
print(f"Backend started (PID: {proc.pid})")

print()
print("=" * 46)
print("  超市管理系统")
print("=" * 46)
print("  Login:  http://localhost:" + str(PORT))
print("  Backend: http://localhost:8000")
print("  User:    admin / admin123")
print("=" * 46)
print("  Press Ctrl+C to stop")
print("=" * 46)
print()

try:
    proc.wait()
except KeyboardInterrupt:
    proc.terminate()
    proc.wait()
    print("Services stopped.")
