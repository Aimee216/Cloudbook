import os

backend_init = r"E:\Cloudbook_git\supermarket\backend\app\__init__.py"

with open(backend_init, "r", encoding="utf-8") as f:
    content = f.read()

# Add modules.js route before the END marker
old = '# ===== END frontend ====='
new = """
@app.get("/modules.js", response_class=FileResponse, include_in_schema=False)
async def serve_modules():
    return FileResponse(os.path.join(_frontend_dir, "modules.js"))
# ===== END frontend =====
"""

content = content.replace(old, new)

with open(backend_init, "w", encoding="utf-8") as f:
    f.write(content)

print("modules.js route added")
