Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "E:\Cloudbook_git\supermarket\backend"
WshShell.Run "D:\Python\python.exe -m uvicorn app:app --host 0.0.0.0 --port 8000", 0, False
