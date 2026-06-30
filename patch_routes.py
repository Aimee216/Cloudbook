import os

backend_init = r"E:\Cloudbook_git\supermarket\backend\app\__init__.py"

with open(backend_init, "r", encoding="utf-8") as f:
    content = f.read()

# Remove old frontend routes
lines = content.split("\n")
new_lines = []
skip = False
for line in lines:
    if "# ===== Serve frontend static pages" in line:
        skip = True
    if skip and "# ===== END frontend" in line:
        skip = False
        continue
    if not skip:
        new_lines.append(line)

content = "\n".join(new_lines)

# Add new frontend routes
patch = """
# ===== Serve frontend static pages =====
from fastapi.responses import FileResponse, RedirectResponse
from fastapi import Request
import os

_frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "frontend")

@app.get("/", include_in_schema=False)
@app.get("/login", response_class=FileResponse, include_in_schema=False)
async def login_page():
    return FileResponse(os.path.join(_frontend_dir, "index.html"))

@app.get("/dashboard", response_class=FileResponse, include_in_schema=False)
async def dashboard_page():
    return FileResponse(os.path.join(_frontend_dir, "dashboard.html"))

@app.get("/dashboard.html", include_in_schema=False)
async def redirect_dashboard():
    return RedirectResponse(url="/dashboard")
# ===== END frontend =====
"""

content += patch

with open(backend_init, "w", encoding="utf-8") as f:
    f.write(content)

print("Frontend routes updated!")
