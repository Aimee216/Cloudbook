# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
from ..database import get_db
from ..models import Supplier, Product, User, OperationLog
from ..schemas import SupplierCreate, SupplierUpdate, ApiResponse
from ..utils.auth import require_admin

router = APIRouter()


@router.get("/", response_model=ApiResponse)
async def list_suppliers(
    keyword: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Supplier)
    if keyword:
        query = query.filter(Supplier.name.like(f"%{keyword}%") | Supplier.contact_person.like(f"%{keyword}%"))
    total = query.count()
    suppliers = query.order_by(desc(Supplier.created_at)).offset((page - 1) * page_size).limit(page_size).all()

    result = []
    for s in suppliers:
        product_count = db.query(Product).filter(Product.supplier_id == s.id).count()
        result.append({
            "id": s.id, "name": s.name, "contact_person": s.contact_person,
            "phone": s.phone, "address": s.address, "supply_category": s.supply_category,
            "rating": s.rating, "delivery_rate": s.delivery_rate, "remark": s.remark,
            "product_count": product_count, "created_at": str(s.created_at)
        })
    return ApiResponse(data={"total": total, "page": page, "page_size": page_size, "data": result})


@router.get("/{supplier_id}", response_model=ApiResponse)
async def get_supplier(supplier_id: int, db: Session = Depends(get_db)):
    s = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="供应商不存在")
    products = db.query(Product).filter(Product.supplier_id == supplier_id).all()
    return ApiResponse(data={
        "id": s.id, "name": s.name, "contact_person": s.contact_person,
        "phone": s.phone, "address": s.address, "supply_category": s.supply_category,
        "rating": s.rating, "delivery_rate": s.delivery_rate, "remark": s.remark,
        "products": [{"id": p.id, "name": p.name, "barcode": p.barcode, "selling_price": float(p.selling_price)} for p in products]
    })


@router.post("/", response_model=ApiResponse)
async def create_supplier(data: SupplierCreate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    supplier = Supplier(**data.model_dump())
    db.add(supplier)
    db.commit()
    db.refresh(supplier)

    log = OperationLog(user_id=admin.id, username=admin.username, action="创建供应商",
                       target_type="Supplier", target_id=supplier.id, detail=data.name)
    db.add(log)
    db.commit()
    return ApiResponse(data={"id": supplier.id})


@router.put("/{supplier_id}", response_model=ApiResponse)
async def update_supplier(supplier_id: int, data: SupplierUpdate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    s = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="供应商不存在")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(s, key, value)
    db.commit()
    return ApiResponse(message="更新成功")


@router.delete("/{supplier_id}", response_model=ApiResponse)
async def delete_supplier(supplier_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    s = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="供应商不存在")
    product_count = db.query(Product).filter(Product.supplier_id == supplier_id).count()
    if product_count > 0:
        raise HTTPException(status_code=400, detail=f"该供应商下还有{product_count}个商品,无法删除")
    db.delete(s)
    db.commit()
    log = OperationLog(user_id=admin.id, username=admin.username, action="删除供应商",
                       target_type="Supplier", target_id=supplier_id)
    db.add(log)
    db.commit()
    return ApiResponse(message="删除成功")
