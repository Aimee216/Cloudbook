import re

# Update index.html - use relative API path when served from same origin
index_path = r"E:\Cloudbook_git\supermarket\frontend\index.html"
with open(index_path, "r", encoding="utf-8") as f:
    content = f.read()

# Change API_BASE to empty string (same origin)
content = content.replace(
    "const API_BASE = window.location.port === '5500' || window.location.port === '8080'",
    "const API_BASE = (window.location.port === '3000' || window.location.port === '5500')"
)
content = content.replace(
    "? 'http://localhost:8000' : ''",
    "? 'http://localhost:8000' : ''"
)

with open(index_path, "w", encoding="utf-8") as f:
    f.write(content)

# Update dashboard.html
dash_path = r"E:\Cloudbook_git\supermarket\frontend\dashboard.html"
with open(dash_path, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace(
    "const API_BASE = 'http://localhost:8000';",
    "const API_BASE = window.location.port === '3000' ? 'http://localhost:8000' : '';"
)

with open(dash_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Frontend updated for same-origin serving")
