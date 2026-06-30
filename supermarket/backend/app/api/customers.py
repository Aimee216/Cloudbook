# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
from ..database import get_db
from ..models import Customer, Order, User, OperationLog
from ..schemas import CustomerRegister, CustomerLogin, ApiResponse
from ..utils.auth import hash_password, verify_password, create_access_token, require_admin

router = APIRouter()


@router.post("/register", response_model=ApiResponse)
async def customer_register(data: CustomerRegister, db: Session = Depends(get_db)):
    exist = db.query(Customer).filter(Customer.phone == data.phone).first()
    if exist:
        raise HTTPException(status_code=400, detail="手机号已注册")
    customer = Customer(phone=data.phone, password=hash_password(data.password), name=data.name)
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return ApiResponse(data={"id": customer.id})


@router.post("/login", response_model=ApiResponse)
async def customer_login(data: CustomerLogin, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.phone == data.phone).first()
    if not customer or not verify_password(data.password, customer.password):
        raise HTTPException(status_code=401, detail="手机号或密码错误")
    if customer.status != "正常":
        raise HTTPException(status_code=403, detail="账号已被冻结")
    token = create_access_token({"sub": customer.phone, "type": "customer"})
    return ApiResponse(data={
        "token": token, "customer": {
            "id": customer.id, "name": customer.name, "phone": customer.phone,
            "member_level": customer.member_level, "points": customer.points
        }
    })


@router.get("/", response_model=ApiResponse)
async def list_customers(
    keyword: Optional[str] = Query(None),
    member_level: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    query = db.query(Customer)
    if keyword:
        query = query.filter(Customer.name.like(f"%{keyword}%") | Customer.phone.like(f"%{keyword}%"))
    if member_level:
        query = query.filter(Customer.member_level == member_level)

    total = query.count()
    customers = query.order_by(desc(Customer.register_time)).offset((page - 1) * page_size).limit(page_size).all()

    result = []
    for c in customers:
        result.append({
            "id": c.id, "name": c.name, "phone": c.phone, "gender": c.gender,
            "register_time": str(c.register_time),
            "total_consumption": float(c.total_consumption or 0),
            "member_level": c.member_level, "points": c.points, "status": c.status
        })
    return ApiResponse(data={"total": total, "page": page, "page_size": page_size, "data": result})


@router.get("/{customer_id}", response_model=ApiResponse)
async def get_customer(customer_id: int, db: Session = Depends(get_db)):
    c = db.query(Customer).filter(Customer.id == customer_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="顾客不存在")
    orders = db.query(Order).filter(Order.customer_id == customer_id).order_by(desc(Order.order_time)).limit(20).all()
    order_list = [{
        "id": o.id, "order_no": o.order_no, "total_amount": float(o.total_amount),
        "status": o.status.value if o.status else None, "order_time": str(o.order_time)
    } for o in orders]
    return ApiResponse(data={
        "id": c.id, "name": c.name, "phone": c.phone, "gender": c.gender,
        "register_time": str(c.register_time), "total_consumption": float(c.total_consumption or 0),
        "member_level": c.member_level, "points": c.points, "status": c.status,
        "orders": order_list
    })
