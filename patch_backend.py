import os

backend_init = r"E:\Cloudbook_git\supermarket\backend\app\__init__.py"

with open(backend_init, "r", encoding="utf-8") as f:
    content = f.read()

if "serve_frontend" not in content:
    patch = """
# ===== Serve frontend static pages =====
from fastapi.responses import FileResponse
import os

_frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "frontend")

@app.get("/login", response_class=FileResponse, include_in_schema=False)
async def login_page():
    return FileResponse(os.path.join(_frontend_dir, "index.html"))

@app.get("/dashboard", response_class=FileResponse, include_in_schema=False)
async def dashboard_page():
    return FileResponse(os.path.join(_frontend_dir, "dashboard.html"))
"""
    with open(backend_init, "a", encoding="utf-8") as f:
        f.write(patch)
    print("Frontend routes added to backend!")
else:
    print("Already patched")
