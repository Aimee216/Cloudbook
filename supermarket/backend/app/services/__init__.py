# -*- coding: utf-8 -*-
from datetime import datetime, timedelta, date
from decimal import Decimal
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc, extract

from ..models import (
    Product, Category, StockRecord, StockCheck, StockCheckDetail,
    Supplier, Order, OrderDetail, Customer, Employee, User, OperationLog
)


# ==================== 商品 ====================

def get_product_list(
    db: Session,
    keyword: Optional[str] = None,
    category_id: Optional[int] = None,
    barcode: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20
) -> Tuple[int, list]:
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
    return total, products


def product_to_dict(p: Product) -> dict:
    return {
        "id": p.id, "name": p.name, "barcode": p.barcode,
        "category_id": p.category_id, "unit": p.unit,
        "purchase_price": float(p.purchase_price),
        "selling_price": float(p.selling_price),
        "stock_quantity": p.stock_quantity,
        "stock_lower_limit": p.stock_lower_limit,
        "stock_upper_limit": p.stock_upper_limit,
        "image": p.image,
        "status": p.status.value if p.status else "上架",
        "supplier_id": p.supplier_id, "description": p.description,
        "created_at": str(p.created_at), "updated_at": str(p.updated_at),
        "category_name": p.category_ref.name if p.category_ref else None,
        "supplier_name": p.supplier.name if p.supplier else None,
    }


# ==================== 分类 ====================

def get_category_tree(db: Session) -> list:
    categories = db.query(Category).filter(Category.parent_id.is_(None)).order_by(Category.sort_order).all()

    def build_tree(cats):
        result = []
        for c in cats:
            children = db.query(Category).filter(
                Category.parent_id == c.id
            ).order_by(Category.sort_order).all()
            setattr(c, "children", build_tree(children))
            result.append(c)
        return result

    return build_tree(categories)


# ==================== 库存 ====================

def stock_change(
    db: Session,
    product_id: int,
    change_quantity: int,
    change_type: str,
    operator: str,
    supplier_id: Optional[int] = None,
    remark: Optional[str] = None,
    related_order_no: Optional[str] = None,
) -> StockRecord:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise ValueError("商品不存在")
    before = product.stock_quantity
    after = before + change_quantity
    if after < 0:
        raise ValueError(f"库存不足，当前库存: {before}")
    product.stock_quantity = after
    record = StockRecord(
        product_id=product_id, change_quantity=change_quantity,
        change_type=change_type, before_quantity=before,
        after_quantity=after, supplier_id=supplier_id,
        operator=operator, remark=remark,
        related_order_no=related_order_no,
    )
    db.add(record)
    return record


# ==================== 订单 ====================

def generate_order_no() -> str:
    return f"DD{datetime.now().strftime('%Y%m%d%H%M%S%f')[:17]}"


def create_order(
    db: Session,
    customer_id: int,
    receiver_name: str,
    receiver_phone: str,
    receiver_address: str,
    remark: Optional[str],
    payment_method: str,
    details_data: list,
) -> Order:
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise ValueError("顾客不存在")

    order_no = generate_order_no()
    order = Order(
        order_no=order_no, customer_id=customer_id,
        receiver_name=receiver_name, receiver_phone=receiver_phone,
        receiver_address=receiver_address, remark=remark,
        payment_method=payment_method,
    )
    db.add(order)
    db.flush()

    total_amount = Decimal("0.00")
    for item in details_data:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise ValueError(f"商品ID {item.product_id} 不存在")
        if product.status.value != "上架":
            raise ValueError(f"商品 {product.name} 已下架")
        if product.stock_quantity < item.quantity:
            raise ValueError(f"商品 {product.name} 库存不足 (库存: {product.stock_quantity})")

        subtotal = item.unit_price * item.quantity
        detail = OrderDetail(
            order_id=order.id, product_id=item.product_id,
            product_name=product.name, quantity=item.quantity,
            unit_price=item.unit_price, subtotal=subtotal,
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
            related_order_no=order_no, operator="系统",
        )
        db.add(record)

    order.total_amount = total_amount
    return order


def update_order_status(
    db: Session,
    order_id: int,
    new_status: str,
    operator: str,
) -> Order:
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise ValueError("订单不存在")

    now = datetime.now()
    order.status = new_status

    if new_status == "已发货":
        order.shipping_time = now
    elif new_status == "已完成":
        order.completed_time = now
        customer = order.customer
        if customer:
            customer.total_consumption = (customer.total_consumption or 0) + order.total_amount
            customer.points = (customer.points or 0) + int(order.total_amount) * 10
            if customer.total_consumption >= 5000:
                customer.member_level = "金卡会员"
            elif customer.total_consumption >= 1000:
                customer.member_level = "银卡会员"
    elif new_status == "已取消":
        for d in order.details:
            product = db.query(Product).filter(Product.id == d.product_id).first()
            if product:
                before = product.stock_quantity
                product.stock_quantity += d.quantity
                record = StockRecord(
                    product_id=d.product_id, change_quantity=d.quantity,
                    change_type="订单取消恢复", before_quantity=before,
                    after_quantity=product.stock_quantity,
                    related_order_no=order.order_no, operator=operator,
                )
                db.add(record)

    return order


# ==================== 报表统计 ====================

def get_sales_report(
    db: Session,
    period: str = "day",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> dict:
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
    else:
        group_expr = extract("year", Order.order_time)
        if not start_date:
            start_date = now.replace(month=1, day=1).strftime("%Y-%m-%d")
            end_date = now.strftime("%Y-%m-%d")

    query = db.query(
        group_expr.label("date_group"),
        func.count(Order.id).label("order_count"),
        func.sum(Order.total_amount).label("total_sales"),
        func.avg(Order.total_amount).label("avg_order_amount"),
    ).filter(Order.status.in_(["已完成", "已发货"]))

    if start_date:
        query = query.filter(Order.order_time >= datetime.strptime(start_date, "%Y-%m-%d"))
    if end_date:
        query = query.filter(
            Order.order_time <= datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
        )

    query = query.group_by(group_expr).order_by(group_expr)
    results = query.all()

    data = [{
        "date": str(r.date_group),
        "order_count": r.order_count,
        "total_sales": float(r.total_sales or 0),
        "avg_order_amount": float(r.avg_order_amount or 0),
    } for r in results]

    total_sales = sum(d["total_sales"] for d in data)
    total_orders = sum(d["order_count"] for d in data)

    return {
        "details": data,
        "summary": {
            "total_sales": total_sales,
            "total_orders": total_orders,
            "avg_order_amount": round(total_sales / total_orders, 2) if total_orders > 0 else 0,
        },
    }


def get_dashboard_summary(db: Session) -> dict:
    """首页看板汇总数据"""
    today = date.today()
    now = datetime.now()

    # 今日销售
    today_sales = db.query(func.sum(Order.total_amount)).filter(
        func.date(Order.order_time) == today,
        Order.status.in_(["已完成", "已发货"]),
    ).scalar() or 0

    today_orders = db.query(func.count(Order.id)).filter(
        func.date(Order.order_time) == today,
    ).scalar() or 0

    # 本月销售
    month_start = today.replace(day=1)
    month_sales = db.query(func.sum(Order.total_amount)).filter(
        Order.order_time >= month_start,
        Order.status.in_(["已完成", "已发货"]),
    ).scalar() or 0

    # 商品统计
    total_products = db.query(func.count(Product.id)).scalar() or 0
    low_stock = db.query(func.count(Product.id)).filter(
        Product.stock_quantity <= Product.stock_lower_limit,
    ).scalar() or 0

    # 顾客/供应商统计
    total_customers = db.query(func.count(Customer.id)).scalar() or 0
    total_suppliers = db.query(func.count(Supplier.id)).scalar() or 0

    # 待处理订单
    pending_orders = db.query(func.count(Order.id)).filter(
        Order.status == "待发货",
    ).scalar() or 0

    # 近7日销售趋势
    trend_data = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        daily_sales = db.query(func.sum(Order.total_amount)).filter(
            func.date(Order.order_time) == d,
            Order.status.in_(["已完成", "已发货"]),
        ).scalar() or 0
        trend_data.append({"date": d.strftime("%Y-%m-%d"), "sales": float(daily_sales)})

    return {
        "today_sales": float(today_sales),
        "today_orders": today_orders,
        "month_sales": float(month_sales),
        "total_products": total_products,
        "low_stock_products": low_stock,
        "total_customers": total_customers,
        "total_suppliers": total_suppliers,
        "pending_orders": pending_orders,
        "sales_trend_7days": trend_data,
    }


def log_operation(
    db: Session,
    user_id: int,
    username: str,
    action: str,
    target_type: str,
    target_id: Optional[int] = None,
    detail: Optional[str] = None,
):
    log = OperationLog(
        user_id=user_id, username=username, action=action,
        target_type=target_type, target_id=target_id, detail=detail,
    )
    db.add(log)
