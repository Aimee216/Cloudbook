import subprocess, time, urllib.request, json, sys, os

os.chdir("E:\\Cloudbook_git\\supermarket\\backend")
proc = subprocess.Popen([sys.executable, "run.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(5)

endpoints = [
    ("GET", "http://localhost:8000/", None),
    ("GET", "http://localhost:8000/api/products", None),
    ("GET", "http://localhost:8000/api/categories", None),
    ("GET", "http://localhost:8000/api/customers", None),
    ("GET", "http://localhost:8000/api/suppliers", None),
    ("GET", "http://localhost:8000/api/employees", None),
    ("GET", "http://localhost:8000/api/stats", None),
    ("POST", "http://localhost:8000/api/auth/login", json.dumps({"username":"admin","password":"admin123"}).encode()),
]

for method, url, body in endpoints:
    try:
        req = urllib.request.Request(url, method=method, data=body,
            headers={"Content-Type": "application/json"} if body else {})
        resp = urllib.request.urlopen(req, timeout=5)
        data = json.loads(resp.read().decode())
        data_str = json.dumps(data, ensure_ascii=False)[:120]
        print(f"[{resp.status}] {url} -> {data_str}")
    except Exception as e:
        print(f"[ERR] {url} -> {str(e)[:100]}")

proc.terminate()
proc.wait(timeout=5)
print("Server stopped.")
