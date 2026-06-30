# -*- coding: utf-8 -*-
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .config import settings
from .database import init_db
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


@app.get("/")
async def root():
    return {"message": f"{settings.APP_NAME} API is running", "version": settings.APP_VERSION}

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
# ===== END frontend =====

