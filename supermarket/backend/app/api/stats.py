# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, extract
from datetime import datetime, timedelta
from typing import Optional
from ..database import get_db
from ..models import Order, OrderDetail, Product, StockRecord
from ..schemas import ApiResponse
from ..services import get_dashboard_summary

router = APIRouter()


@router.get("/dashboard", response_model=ApiResponse)
async def dashboard_summary(db: Session = Depends(get_db)):
    """首页看板汇总数据"""
    return ApiResponse(data=get_dashboard_summary(db))


@router.get("/sales", response_model=ApiResponse)
async def sales_report(
    period: str = Query("day", description="day/week/month/year"),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """销售报表"""
    now = datetime.now()
    if period == "day":
        group_expr = func.date(Order.order_time)
        if not start_date:
            start_date = now.strftime("%Y-%m-%d")
            end_date = start_date
    elif period == "week":
        group_expr = func.date(Order.order_time)
        if not start_date:
            start = now - timedelta(days=now.weekday())
            start_date = start.strftime("%Y-%m-%d")
            end_date = (start + timedelta(days=6)).strftime("%Y-%m-%d")
    elif period == "month":
        group_expr = func.date(Order.order_time)
        if not start_date:
            start_date = now.replace(day=1).strftime("%Y-%m-%d")
            end_date = now.strftime("%Y-%m-%d")
    else:  # year
        group_expr = extract("year", Order.order_time)
        if not start_date:
            start_date = now.replace(month=1, day=1).strftime("%Y-%m-%d")
            end_date = now.strftime("%Y-%m-%d")

    query = db.query(
        group_expr.label("date_group"),
        func.count(Order.id).label("order_count"),
        func.sum(Order.total_amount).label("total_sales"),
        func.avg(Order.total_amount).label("avg_order_amount")
    ).filter(Order.status.in_(["已完成", "已发货"]))

    if start_date:
        query = query.filter(Order.order_time >= datetime.strptime(start_date, "%Y-%m-%d"))
    if end_date:
        query = query.filter(Order.order_time <= datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1))

    query = query.group_by(group_expr).order_by(group_expr)
    results = query.all()

    data = [{
        "date": str(r.date_group),
        "order_count": r.order_count,
        "total_sales": float(r.total_sales or 0),
        "avg_order_amount": float(r.avg_order_amount or 0)
    } for r in results]

    total_sales = sum(d["total_sales"] for d in data)
    total_orders = sum(d["order_count"] for d in data)

    return ApiResponse(data={
        "details": data,
        "summary": {
            "total_sales": total_sales,
            "total_orders": total_orders,
            "avg_order_amount": round(total_sales / total_orders, 2) if total_orders > 0 else 0
        }
    })


@router.get("/top-products", response_model=ApiResponse)
async def top_products(top_n: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    """商品销售排行"""
    results = db.query(
        OrderDetail.product_id,
        Product.name,
        func.sum(OrderDetail.quantity).label("total_quantity"),
        func.sum(OrderDetail.subtotal).label("total_amount")
    ).join(Product, OrderDetail.product_id == Product.id)\
     .join(Order, OrderDetail.order_id == Order.id)\
     .filter(Order.status.in_(["已完成", "已发货"]))\
     .group_by(OrderDetail.product_id, Product.name)\
     .order_by(desc("total_quantity"))\
     .limit(top_n).all()

    top = [{
        "product_id": r.product_id, "product_name": r.name,
        "total_quantity": int(r.total_quantity), "total_amount": float(r.total_amount or 0)
    } for r in results]

    sold_ids = [r.product_id for r in results]
    slow_moving = db.query(Product).filter(~Product.id.in_(sold_ids)).limit(top_n).all()

    return ApiResponse(data={
        "top_products": top,
        "slow_moving_products": [
            {"id": p.id, "name": p.name, "stock_quantity": p.stock_quantity}
            for p in slow_moving
        ]
    })


@router.get("/inventory-analysis", response_model=ApiResponse)
async def inventory_analysis(db: Session = Depends(get_db)):
    """库存分析"""
    total_products = db.query(Product).count()
    low_stock = db.query(Product).filter(Product.stock_quantity <= Product.stock_lower_limit).count()
    over_stock = db.query(Product).filter(Product.stock_quantity >= Product.stock_upper_limit).count()

    thirty_days_ago = datetime.now() - timedelta(days=30)
    total_out = db.query(func.sum(StockRecord.change_quantity)).filter(
        StockRecord.change_quantity < 0,
        StockRecord.created_at >= thirty_days_ago
    ).scalar() or 0

    total_stock = db.query(func.sum(Product.stock_quantity)).scalar() or 1
    turnover_rate = abs(float(total_out)) / float(total_stock)

    return ApiResponse(data={
        "total_products": total_products,
        "low_stock_count": low_stock,
        "over_stock_count": over_stock,
        "normal_stock_count": total_products - low_stock - over_stock,
        "turnover_rate": round(turnover_rate, 4),
        "low_stock_ratio": round(low_stock / total_products * 100, 2) if total_products > 0 else 0
    })


@router.get("/finance", response_model=ApiResponse)
async def finance_report(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """财务报表"""
    now = datetime.now()
    if not start_date:
        start_date = now.replace(day=1).strftime("%Y-%m-%d")
    if not end_date:
        end_date = now.strftime("%Y-%m-%d")

    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)

    sales_revenue = db.query(func.sum(Order.total_amount)).filter(
        Order.status.in_(["已完成", "已发货"]),
        Order.order_time >= start,
        Order.order_time <= end
    ).scalar() or 0

    sales_cost = db.query(func.sum(OrderDetail.quantity * Product.purchase_price)).join(
        Product, OrderDetail.product_id == Product.id
    ).join(Order, OrderDetail.order_id == Order.id).filter(
        Order.status.in_(["已完成", "已发货"]),
        Order.order_time >= start,
        Order.order_time <= end
    ).scalar() or 0

    gross_profit = float(sales_revenue) - float(sales_cost)
    gross_margin = round(gross_profit / float(sales_revenue) * 100, 2) if float(sales_revenue) > 0 else 0

    return ApiResponse(data={
        "period": {"start": start_date, "end": end_date},
        "sales_revenue": float(sales_revenue),
        "sales_cost": float(sales_cost),
        "gross_profit": gross_profit,
        "gross_margin": gross_margin
    })
