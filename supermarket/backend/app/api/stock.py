# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
from typing import Optional
from ..database import get_db
from ..models import Product, StockRecord, StockCheck, StockCheckDetail, Supplier, OperationLog, User
from ..schemas import StockRecordCreate, ApiResponse
from ..utils.auth import require_admin

router = APIRouter()


@router.get("/", response_model=ApiResponse)
async def get_stock_list(
    keyword: Optional[str] = Query(None),
    category_id: Optional[int] = Query(None),
    alert_only: bool = Query(False),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """实时库存查询"""
    query = db.query(Product)
    if keyword:
        query = query.filter(Product.name.like(f"%{keyword}%"))
    if category_id:
        query = query.filter(Product.category_id == category_id)
    if alert_only:
        query = query.filter(
            (Product.stock_quantity <= Product.stock_lower_limit) |
            (Product.stock_quantity >= Product.stock_upper_limit)
        )
    total = query.count()
    products = query.order_by(Product.id.desc()).offset((page - 1) * page_size).limit(page_size).all()

    result = []
    for p in products:
        is_low = p.stock_quantity <= p.stock_lower_limit
        is_high = p.stock_quantity >= p.stock_upper_limit
        result.append({
            "id": p.id, "name": p.name, "barcode": p.barcode,
            "stock_quantity": p.stock_quantity,
            "stock_lower_limit": p.stock_lower_limit, "stock_upper_limit": p.stock_upper_limit,
            "unit": p.unit, "selling_price": float(p.selling_price),
            "status": "库存不足" if is_low else ("库存过多" if is_high else "正常"),
            "is_alert": is_low or is_high
        })
    return ApiResponse(data={"total": total, "page": page, "page_size": page_size, "data": result})


@router.post("/inbound", response_model=ApiResponse)
async def stock_inbound(data: StockRecordCreate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    """采购入库"""
    if data.change_quantity <= 0:
        raise HTTPException(status_code=400, detail="入库数量必须大于0")
    product = db.query(Product).filter(Product.id == data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")

    before = product.stock_quantity
    product.stock_quantity += data.change_quantity
    record = StockRecord(
        product_id=data.product_id, change_quantity=data.change_quantity,
        change_type=data.change_type or "采购入库",
        before_quantity=before, after_quantity=product.stock_quantity,
        supplier_id=data.supplier_id, operator=data.operator or admin.username,
        remark=data.remark
    )
    db.add(record)
    db.commit()

    log = OperationLog(user_id=admin.id, username=admin.username, action="入库",
                       target_type="Stock", target_id=product.id,
                       detail=f"商品:{product.name}, 数量:{data.change_quantity}")
    db.add(log)
    db.commit()
    return ApiResponse(message="入库成功", data={"after_quantity": product.stock_quantity})


@router.post("/outbound", response_model=ApiResponse)
async def stock_outbound(data: StockRecordCreate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    """手动出库(报损/调拨等)"""
    if data.change_quantity <= 0:
        raise HTTPException(status_code=400, detail="出库数量必须大于0")
    product = db.query(Product).filter(Product.id == data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    if product.stock_quantity < data.change_quantity:
        raise HTTPException(status_code=400, detail=f"库存不足，当前库存: {product.stock_quantity}")

    before = product.stock_quantity
    product.stock_quantity -= data.change_quantity
    record = StockRecord(
        product_id=data.product_id, change_quantity=-data.change_quantity,
        change_type=data.change_type or "手动出库",
        before_quantity=before, after_quantity=product.stock_quantity,
        supplier_id=data.supplier_id, operator=data.operator or admin.username,
        remark=data.remark
    )
    db.add(record)
    db.commit()

    log = OperationLog(user_id=admin.id, username=admin.username, action="出库",
                       target_type="Stock", target_id=product.id,
                       detail=f"商品:{product.name}, 数量:-{data.change_quantity}")
    db.add(log)
    db.commit()
    return ApiResponse(message="出库成功", data={"after_quantity": product.stock_quantity})


@router.get("/records", response_model=ApiResponse)
async def get_stock_records(
    product_id: Optional[int] = Query(None),
    change_type: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """库存流水"""
    query = db.query(StockRecord)
    if product_id:
        query = query.filter(StockRecord.product_id == product_id)
    if change_type:
        query = query.filter(StockRecord.change_type == change_type)
    if start_date:
        query = query.filter(StockRecord.created_at >= datetime.strptime(start_date, "%Y-%m-%d"))
    if end_date:
        query = query.filter(StockRecord.created_at <= datetime.strptime(end_date, "%Y-%m-%d") + __import__("datetime").timedelta(days=1))

    total = query.count()
    records = query.order_by(desc(StockRecord.created_at)).offset((page - 1) * page_size).limit(page_size).all()

    result = []
    for r in records:
        result.append({
            "id": r.id, "product_id": r.product_id,
            "product_name": r.product.name if r.product else None,
            "change_quantity": r.change_quantity, "change_type": r.change_type,
            "before_quantity": r.before_quantity, "after_quantity": r.after_quantity,
            "supplier_name": r.supplier_ref.name if r.supplier_ref else None,
            "operator": r.operator, "remark": r.remark,
            "created_at": str(r.created_at)
        })
    return ApiResponse(data={"total": total, "page": page, "page_size": page_size, "data": result})


@router.post("/check", response_model=ApiResponse)
async def create_stock_check(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    """创建盘点单"""
    from datetime import date
    check_no = f"PD{date.today().strftime('%Y%m%d%H%M%S')}"
    check = StockCheck(check_no=check_no, check_date=date.today(), operator=admin.username)
    db.add(check)
    db.commit()
    db.refresh(check)

    products = db.query(Product).all()
    for p in products:
        detail = StockCheckDetail(check_id=check.id, product_id=p.id, book_quantity=p.stock_quantity)
        db.add(detail)
    db.commit()
    return ApiResponse(data={"id": check.id, "check_no": check_no})


@router.put("/check/{check_id}", response_model=ApiResponse)
async def finish_stock_check(check_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    """完成盘点,更新库存"""
    check = db.query(StockCheck).filter(StockCheck.id == check_id).first()
    if not check:
        raise HTTPException(status_code=404, detail="盘点单不存在")
    details = db.query(StockCheckDetail).filter(StockCheckDetail.check_id == check_id).all()
    for d in details:
        d.difference = d.actual_quantity - d.book_quantity
        if d.difference != 0:
            product = db.query(Product).filter(Product.id == d.product_id).first()
            if product:
                before = product.stock_quantity
                product.stock_quantity = d.actual_quantity
                record = StockRecord(
                    product_id=d.product_id, change_quantity=d.difference,
                    change_type="盘点", before_quantity=before,
                    after_quantity=d.actual_quantity, operator=admin.username,
                    remark=f"盘点单: {check.check_no}"
                )
                db.add(record)
    check.status = "已完成"
    db.commit()
    return ApiResponse(message="盘点完成")
