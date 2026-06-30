import subprocess, sys, os, time

os.chdir(r"E:\Cloudbook_git\supermarket\backend")
f_out = open(r"E:\Cloudbook_git\supermarket\backend\server_stdout.log", "w")
f_err = open(r"E:\Cloudbook_git\supermarket\backend\server_stderr.log", "w")
proc = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"],
    stdout=f_out, stderr=f_err, cwd=r"E:\Cloudbook_git\supermarket\backend"
)
time.sleep(5)

if proc.poll() is None:
    print(f"RUNNING PID={proc.pid}")
    import urllib.request, json
    resp = urllib.request.urlopen("http://localhost:8000/", timeout=5)
    print(f"GET / => {resp.status}")
    login_data = json.dumps({"username":"admin","password":"admin123"}).encode()
    req = urllib.request.Request("http://localhost:8000/api/auth/login",
        data=login_data, headers={"Content-Type": "application/json"})
    resp2 = urllib.request.urlopen(req, timeout=5)
    print(f"POST /api/auth/login => {resp2.status}")
    # Keep checking it's alive
    for i in range(3):
        time.sleep(3)
        if proc.poll() is not None:
            print(f"DIED after {i*3+3}s with code {proc.poll()}")
            break
    else:
        print("Still alive after 14s")
else:
    print(f"EXITED with code {proc.poll()}")
f_out.close()
f_err.close()
err = open(r"E:\Cloudbook_git\supermarket\backend\server_stderr.log").read()
print(f"STDERR: {err[-300:]}")
