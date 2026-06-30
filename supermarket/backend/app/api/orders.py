# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc
from datetime import datetime, date
from typing import Optional
from decimal import Decimal
from ..database import get_db
from ..models import Order, OrderDetail, Product, Customer, StockRecord, OperationLog, User
from ..schemas import OrderCreate, OrderStatusUpdate, ApiResponse
from ..utils.auth import require_admin

router = APIRouter()


def generate_order_no() -> str:
    return f"DD{datetime.now().strftime('%Y%m%d%H%M%S%f')[:17]}"


@router.get("/", response_model=ApiResponse)
async def list_orders(
    status: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Order)
    if status:
        query = query.filter(Order.status == status)
    if keyword:
        query = query.join(Customer).filter(
            Customer.name.like(f"%{keyword}%") | Customer.phone.like(f"%{keyword}%") |
            Order.order_no.like(f"%{keyword}%")
        )
    if start_date:
        query = query.filter(Order.order_time >= datetime.strptime(start_date, "%Y-%m-%d"))
    if end_date:
        from datetime import timedelta
        query = query.filter(Order.order_time <= datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1))

    total = query.count()
    orders = query.order_by(desc(Order.order_time)).offset((page - 1) * page_size).limit(page_size).all()

    result = []
    for o in orders:
        result.append({
            "id": o.id, "order_no": o.order_no,
            "customer_name": o.customer.name if o.customer else None,
            "customer_phone": o.customer.phone if o.customer else None,
            "total_amount": float(o.total_amount),
            "status": o.status.value if o.status else None,
            "payment_method": o.payment_method,
            "order_time": str(o.order_time),
            "receiver_name": o.receiver_name,
            "receiver_phone": o.receiver_phone,
            "detail_count": len(o.details)
        })
    return ApiResponse(data={"total": total, "page": page, "page_size": page_size, "data": result})


@router.get("/{order_id}", response_model=ApiResponse)
async def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    details = []
    for d in order.details:
        details.append({
            "id": d.id, "product_id": d.product_id, "product_name": d.product_name,
            "quantity": d.quantity, "unit_price": float(d.unit_price), "subtotal": float(d.subtotal)
        })
    return ApiResponse(data={
        "id": order.id, "order_no": order.order_no,
        "customer_id": order.customer_id,
        "customer_name": order.customer.name if order.customer else None,
        "customer_phone": order.customer.phone if order.customer else None,
        "total_amount": float(order.total_amount),
        "status": order.status.value if order.status else None,
        "payment_method": order.payment_method,
        "receiver_name": order.receiver_name, "receiver_phone": order.receiver_phone,
        "receiver_address": order.receiver_address, "remark": order.remark,
        "order_time": str(order.order_time), "payment_time": str(order.payment_time) if order.payment_time else None,
        "shipping_time": str(order.shipping_time) if order.shipping_time else None,
        "completed_time": str(order.completed_time) if order.completed_time else None,
        "details": details
    })


@router.post("/", response_model=ApiResponse)
async def create_order(data: OrderCreate, db: Session = Depends(get_db)):
    """顾客下单"""
    customer = db.query(Customer).filter(Customer.id == data.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="顾客不存在")

    order_no = generate_order_no()
    order = Order(
        order_no=order_no, customer_id=data.customer_id,
        receiver_name=data.receiver_name, receiver_phone=data.receiver_phone,
        receiver_address=data.receiver_address, remark=data.remark,
        payment_method=data.payment_method
    )
    db.add(order)
    db.flush()

    total_amount = Decimal("0.00")
    for item in data.details:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"商品ID {item.product_id} 不存在")
        if product.status != "上架":
            raise HTTPException(status_code=400, detail=f"商品 {product.name} 已下架")
        if product.stock_quantity < item.quantity:
            raise HTTPException(status_code=400, detail=f"商品 {product.name} 库存不足")

        subtotal = item.unit_price * item.quantity
        detail = OrderDetail(
            order_id=order.id, product_id=item.product_id,
            product_name=product.name, quantity=item.quantity,
            unit_price=item.unit_price, subtotal=subtotal
        )
        db.add(detail)
        total_amount += subtotal

        # 扣减库存
        before = product.stock_quantity
        product.stock_quantity -= item.quantity
        record = StockRecord(
            product_id=item.product_id, change_quantity=-item.quantity,
            change_type="销售出库", before_quantity=before,
            after_quantity=product.stock_quantity,
            related_order_no=order_no, operator="系统"
        )
        db.add(record)

    order.total_amount = total_amount
    db.commit()
    db.refresh(order)
    return ApiResponse(data={"order_no": order.order_no, "id": order.id, "total_amount": float(total_amount)})


@router.put("/{order_id}/status", response_model=ApiResponse)
async def update_order_status(order_id: int, data: OrderStatusUpdate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    now = datetime.now()
    order.status = data.status
    if data.status == "已发货":
        order.shipping_time = now
    elif data.status == "已完成":
        order.completed_time = now
        # 更新顾客消费金额和积分
        customer = order.customer
        if customer:
            customer.total_consumption = (customer.total_consumption or 0) + order.total_amount
            customer.points = (customer.points or 0) + int(order.total_amount) * 10  # 消费1元得10积分
            # 自动升级会员
            if customer.total_consumption >= 5000:
                customer.member_level = "金卡会员"
            elif customer.total_consumption >= 1000:
                customer.member_level = "银卡会员"
    elif data.status == "已取消":
        # 取消订单,恢复库存
        for d in order.details:
            product = db.query(Product).filter(Product.id == d.product_id).first()
            if product:
                before = product.stock_quantity
                product.stock_quantity += d.quantity
                record = StockRecord(
                    product_id=d.product_id, change_quantity=d.quantity,
                    change_type="订单取消恢复", before_quantity=before,
                    after_quantity=product.stock_quantity,
                    related_order_no=order.order_no, operator=admin.username
                )
                db.add(record)

    db.commit()
    log = OperationLog(user_id=admin.id, username=admin.username, action="更新订单状态",
                       target_type="Order", target_id=order_id, detail=f"状态变更为: {data.status}")
    db.add(log)
    db.commit()
    return ApiResponse(message="订单状态已更新")
