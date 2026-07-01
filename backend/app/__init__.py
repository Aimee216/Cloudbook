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


def _seed_data():
    """首次启动时填充示例数据"""
    from .models import User, Employee, Category, Supplier, Product, Customer
    from .utils.auth import hash_password
    from datetime import date, datetime
    from decimal import Decimal
    from sqlalchemy import exists

    db = SessionLocal()
    try:
        # 检查是否已初始化（以分类是否有数据为准）
        if db.query(exists().where(Category.id.isnot(None))).scalar():
            return

        print("[Seed] 开始填充示例数据...")

        # === 用户 ===
        emp = Employee(name="系统管理员", gender="未知", position="超级管理员", hire_date=date.today(), salary=0, status="在职")
        db.add(emp)
        db.flush()
        db.add(User(username="admin", password=hash_password("admin123"), role="超级管理员", status="正常", employee_id=emp.id))

        emp2 = Employee(name="张三", gender="男", phone="13800138000", position="收银员", hire_date=date.today(), salary=5000, status="在职")
        db.add(emp2)
        db.flush()
        db.add(User(username="员工", password=hash_password("123456"), role="普通员工", status="正常", employee_id=emp2.id))

        # === 分类 ===
        cats = []
        for name, sort in [("饮料",1),("零食",2),("日用品",3),("粮油调味",4),("生鲜水果",5),("酒类",6),("文具办公",7),("洗护用品",8)]:
            c = Category(name=name, sort_order=sort)
            db.add(c)
            cats.append(c)
        db.flush()
        cid = {c.name: c.id for c in cats}

        # === 供应商 ===
        suppliers_data = [
            ("农夫山泉股份有限公司","张经理","13800138001","浙江省杭州市","饮料",5),
            ("统一集团","李经理","13800138002","上海市","饮料/零食",4),
            ("康师傅控股","王经理","13800138003","天津市","饮料/方便面",5),
            ("宝洁中国","赵经理","13800138004","广东省广州市","日用品/洗护",4),
            ("青岛啤酒","孙经理","13800138005","山东省青岛市","酒类",5),
            ("中粮集团","周经理","13800138006","北京市","粮油调味",4),
            ("本地果业合作社","吴经理","13800138007","本地农产品基地","生鲜水果",3),
            ("晨光文具","郑经理","13800138008","上海市","文具办公",4),
        ]
        sups = []
        for name, cp, phone, addr, scat, rating in suppliers_data:
            s = Supplier(name=name, contact_person=cp, phone=phone, address=addr, supply_category=scat, rating=rating)
            db.add(s)
            sups.append(s)
        db.flush()
        sid = [s.id for s in sups]

        # === 商品 ===
        products_data = [
            ("农夫山泉矿泉水550ml","6901010100011",cid["饮料"],"瓶",Decimal("1.20"),Decimal("2.00"),500,50,sid[0]),
            ("统一冰红茶500ml","6901010100028",cid["饮料"],"瓶",Decimal("2.50"),Decimal("3.50"),300,30,sid[1]),
            ("康师傅方便面红烧牛肉","6901010100035",cid["零食"],"桶",Decimal("3.00"),Decimal("4.50"),200,20,sid[2]),
            ("乐事薯片原味40g","6901010100042",cid["零食"],"包",Decimal("4.00"),Decimal("6.00"),150,15,sid[1]),
            ("奥利奥饼干原味97g","6901010100059",cid["零食"],"包",Decimal("5.00"),Decimal("7.50"),120,10,sid[1]),
            ("海飞丝去屑洗发露200ml","6901010100066",cid["洗护用品"],"瓶",Decimal("18.00"),Decimal("28.00"),80,10,sid[3]),
            ("舒肤佳香皂纯白清香","6901010100073",cid["洗护用品"],"块",Decimal("3.50"),Decimal("5.50"),200,20,sid[3]),
            ("金龙鱼花生油5L","6901010100080",cid["粮油调味"],"桶",Decimal("55.00"),Decimal("79.90"),50,5,sid[5]),
            ("东北大米10kg","6901010100097",cid["粮油调味"],"袋",Decimal("35.00"),Decimal("49.90"),40,5,sid[5]),
            ("青岛啤酒经典10听装","6901010100103",cid["酒类"],"听",Decimal("3.00"),Decimal("5.00"),300,30,sid[4]),
            ("红富士苹果1kg","6901010100110",cid["生鲜水果"],"袋",Decimal("6.00"),Decimal("9.90"),60,10,sid[6]),
            ("晨光签字笔12支装","6901010100127",cid["文具办公"],"盒",Decimal("8.00"),Decimal("12.00"),100,10,sid[7]),
            ("清风抽纸3层100抽*6包","6901010100134",cid["日用品"],"提",Decimal("10.00"),Decimal("15.90"),90,10,sid[3]),
            ("可口可乐330ml*6罐装","6901010100141",cid["饮料"],"组",Decimal("7.00"),Decimal("10.00"),250,25,sid[1]),
            ("海天上等蚝油510g","6901010100158",cid["粮油调味"],"瓶",Decimal("4.50"),Decimal("7.00"),120,10,sid[5]),
        ]
        for name, barcode, cat, unit, pp, sp, stock, lower, supplier in products_data:
            db.add(Product(name=name, barcode=barcode, category_id=cat, unit=unit,
                           purchase_price=pp, selling_price=sp, stock_quantity=stock,
                           stock_lower_limit=lower, supplier_id=supplier, status="上架"))

        # === 顾客 ===
        for name, phone in [("张三","13900000001"),("李四","13900000002"),("王五","13900000003"),
                            ("赵六","13900000004"),("钱七","13900000005")]:
            db.add(Customer(name=name, phone=phone, password=hash_password("123456")))

        db.commit()
        print("[Seed] 示例数据填充完毕 (8分类, 8供应商, 15商品, 2用户, 5顾客)")
    finally:
        db.close()


@app.on_event("startup")
async def startup():
    init_db()
    _seed_data()


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
