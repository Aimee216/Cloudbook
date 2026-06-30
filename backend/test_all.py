import subprocess, time, json, sys, os

os.chdir(r"E:\Cloudbook_git\supermarket\backend")
proc = subprocess.Popen([sys.executable, "run.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(5)

import urllib.request

# Login
req = urllib.request.Request("http://localhost:8000/api/auth/login", 
    data=json.dumps({"username":"admin","password":"admin123"}).encode(),
    headers={"Content-Type": "application/json"})
resp = json.loads(urllib.request.urlopen(req, timeout=5).read().decode())
token = resp["data"]["token"]
auth_header = {"Authorization": f"Bearer {token}"}

all_endpoints = [
    ("GET", "/", None),
    ("POST", "/api/auth/login", {"username":"admin","password":"admin123"}),
    ("GET", "/api/auth/me", None, auth_header),
    ("GET", "/api/products", None, auth_header),
    ("GET", "/api/categories", None, auth_header),
    ("GET", "/api/suppliers", None, auth_header),
    ("GET", "/api/customers", None, auth_header),
    ("GET", "/api/employees", None, auth_header),
    ("GET", "/api/orders", None, auth_header),
    ("GET", "/api/stock", None, auth_header),
    ("GET", "/api/stats/dashboard", None, auth_header),
    ("GET", "/api/stats/sales", None, auth_header),
    ("GET", "/api/stats/top-products", None, auth_header),
    ("GET", "/api/stats/inventory-analysis", None, auth_header),
    ("GET", "/api/stats/finance", None, auth_header),
]

for ep in all_endpoints:
    method, path, *rest = ep
    body = rest[0] if rest else None
    headers = rest[1] if len(rest) > 1 else ({} if not body else {"Content-Type": "application/json"})
    
    try:
        data_bytes = json.dumps(body).encode() if body else None
        req = urllib.request.Request(f"http://localhost:8000{path}", 
            data=data_bytes,
            headers=headers if headers else {})
        resp = urllib.request.urlopen(req, timeout=5)
        data = json.loads(resp.read().decode())
        status = data.get("code", resp.status)
        print(f"[{resp.status}] {path} -> code={status}, success")
    except Exception as e:
        status = getattr(e, "code", "ERR")
        print(f"[{status}] {path} -> {str(e)[:70]}")

proc.terminate()
proc.wait(timeout=5)
