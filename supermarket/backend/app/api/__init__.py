# -*- coding: utf-8 -*-
from fastapi import APIRouter

router = APIRouter()

from .auth import router as auth_router
from .products import router as product_router
from .categories import router as category_router
from .stock import router as stock_router
from .orders import router as order_router
from .customers import router as customer_router
from .suppliers import router as supplier_router
from .employees import router as employee_router
from .stats import router as stats_router
from .upload import router as upload_router
from .export import router as export_router

router.include_router(auth_router, prefix="/auth", tags=["认证管理"])
router.include_router(category_router, prefix="/categories", tags=["分类管理"])
router.include_router(product_router, prefix="/products", tags=["商品管理"])
router.include_router(stock_router, prefix="/stock", tags=["库存管理"])
router.include_router(order_router, prefix="/orders", tags=["订单管理"])
router.include_router(customer_router, prefix="/customers", tags=["顾客管理"])
router.include_router(supplier_router, prefix="/suppliers", tags=["供应商管理"])
router.include_router(employee_router, prefix="/employees", tags=["员工管理"])
router.include_router(stats_router, prefix="/stats", tags=["数据报表"])
router.include_router(upload_router, prefix="/upload", tags=["文件管理"])
router.include_router(export_router, prefix="/export", tags=["数据导出"])
