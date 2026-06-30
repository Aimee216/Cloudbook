import subprocess, time, json, sys, os

os.chdir(r"E:\Cloudbook_git\supermarket\backend")
proc = subprocess.Popen([sys.executable, "run.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(5)

import urllib.request

# 1. Login to get token
req = urllib.request.Request("http://localhost:8000/api/auth/login", 
    data=json.dumps({"username":"admin","password":"admin123"}).encode(),
    headers={"Content-Type": "application/json"})
resp = json.loads(urllib.request.urlopen(req, timeout=5).read().decode())
token = resp["data"]["token"]
print(f"[200] /api/auth/login -> token obtained, role: {resp['data']['user']['role']}")

# 2. Test protected endpoints with token
auth_header = {"Authorization": f"Bearer {token}"}
protected = [
    "/api/customers",
    "/api/employees", 
    "/api/stats/overview",
    "/api/orders",
    "/api/stock",
]

for ep in protected:
    try:
        req = urllib.request.Request(f"http://localhost:8000{ep}", headers=auth_header)
        resp = urllib.request.urlopen(req, timeout=5)
        data = json.loads(resp.read().decode())
        data_str = json.dumps(data, ensure_ascii=False)[:100]
        print(f"[{resp.status}] {ep} -> {data_str}")
    except Exception as e:
        print(f"[ERR] {ep} -> {str(e)[:80]}")

# 3. Test /api/me
try:
    req = urllib.request.Request("http://localhost:8000/api/auth/me", headers=auth_header)
    resp = urllib.request.urlopen(req, timeout=5)
    data = json.loads(resp.read().decode())
    print(f"[{resp.status}] /api/auth/me -> {json.dumps(data, ensure_ascii=False)[:80]}")
except Exception as e:
    print(f"[ERR] /api/auth/me -> {str(e)[:80]}")

proc.terminate()
proc.wait(timeout=5)
