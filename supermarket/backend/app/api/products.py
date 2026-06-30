# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from ..database import get_db
from ..models import Product, Category, StockRecord, Supplier, OperationLog, User
from ..schemas import ProductCreate, ProductUpdate, ProductOut, ApiResponse, PageResult
from ..utils.auth import require_admin

router = APIRouter()


def product_to_dict(p: Product) -> dict:
    return {
        "id": p.id, "name": p.name, "barcode": p.barcode,
        "category_id": p.category_id, "unit": p.unit,
        "purchase_price": float(p.purchase_price), "selling_price": float(p.selling_price),
        "stock_quantity": p.stock_quantity,
        "stock_lower_limit": p.stock_lower_limit, "stock_upper_limit": p.stock_upper_limit,
        "image": p.image, "status": p.status.value if p.status else "上架",
        "supplier_id": p.supplier_id, "description": p.description,
        "created_at": str(p.created_at), "updated_at": str(p.updated_at),
        "category_name": p.category_ref.name if p.category_ref else None,
        "supplier_name": p.supplier.name if p.supplier else None
    }


@router.get("/", response_model=ApiResponse)
async def list_products(
    keyword: Optional[str] = Query(None),
    category_id: Optional[int] = Query(None),
    barcode: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Product)
    if keyword:
        query = query.filter(Product.name.like(f"%{keyword}%"))
    if category_id:
        query = query.filter(Product.category_id == category_id)
    if barcode:
        query = query.filter(Product.barcode == barcode)
    if status:
        query = query.filter(Product.status == status)

    total = query.count()
    products = query.order_by(Product.id.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return ApiResponse(data={
        "total": total, "page": page, "page_size": page_size,
        "data": [product_to_dict(p) for p in products]
    })


@router.get("/{product_id}", response_model=ApiResponse)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="商品不存在")
    return ApiResponse(data=product_to_dict(p))


@router.post("/", response_model=ApiResponse)
async def create_product(data: ProductCreate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    product = Product(**data.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)

    log = OperationLog(user_id=admin.id, username=admin.username, action="创建商品",
                       target_type="Product", target_id=product.id, detail=product.name)
    db.add(log)
    db.commit()
    return ApiResponse(data={"id": product.id})


@router.put("/{product_id}", response_model=ApiResponse)
async def update_product(product_id: int, data: ProductUpdate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(product, key, value)
    db.commit()
    return ApiResponse(message="更新成功")


@router.delete("/{product_id}", response_model=ApiResponse)
async def delete_product(product_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    db.delete(product)
    db.commit()

    log = OperationLog(user_id=admin.id, username=admin.username, action="删除商品",
                       target_type="Product", target_id=product_id)
    db.add(log)
    db.commit()
    return ApiResponse(message="删除成功")
