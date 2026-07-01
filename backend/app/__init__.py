# -*- coding: utf-8 -*-
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .config import settings
from .database import init_db, SessionLocal
from .api import router as api_router

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

# 静态文件服务
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
uploads_dir = os.path.join(BASE_DIR, settings.UPLOAD_DIR)
exports_dir = os.path.join(BASE_DIR, "exports")

os.makedirs(uploads_dir, exist_ok=True)
os.makedirs(exports_dir, exist_ok=True)

app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")
app.mount("/exports", StaticFiles(directory=exports_dir), name="exports")


@app.on_event("startup")
async def startup():
    init_db()
    # 自动创建默认账号（仅首次启动）
    from .models import User, Employee
    from .utils.auth import hash_password
    from datetime import date
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.username == "admin").first():
            emp = Employee(name="系统管理员", gender="未知", position="超级管理员", hire_date=date.today(), salary=0, status="在职")
            db.add(emp)
            db.flush()
            admin = User(username="admin", password=hash_password("admin123"), role="超级管理员", status="正常", employee_id=emp.id)
            db.add(admin)
            db.commit()
            print("[Seed] 默认管理员已创建: admin / admin123")

        if not db.query(User).filter(User.username == "员工").first():
            emp2 = Employee(name="张三", gender="男", phone="13800138000", position="收银员", hire_date=date.today(), salary=5000, status="在职")
            db.add(emp2)
            db.flush()
            user2 = User(username="员工", password=hash_password("123456"), role="普通员工", status="正常", employee_id=emp2.id)
            db.add(user2)
            db.commit()
            print("[Seed] 默认员工已创建: 员工 / 123456")
    finally:
        db.close()


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

@app.get("/modules.js", response_class=FileResponse, include_in_schema=False)
async def serve_modules():
    return FileResponse(os.path.join(_frontend_dir, "modules.js"))

@app.get("/api/health")
async def root():
    return {"message": f"{settings.APP_NAME} API is running", "version": settings.APP_VERSION}
# ===== END frontend =====
