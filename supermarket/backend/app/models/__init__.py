# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, BigInteger, Enum, ForeignKey, Date, DECIMAL
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from ..database import Base


class ProductStatus(str, enum.Enum):
    ON = "上架"
    OFF = "下架"


# 商品分类表
class Category(Base):
    __tablename__ = "t_category"
    id = Column(Integer, primary_key=True, autoincrement=True, comment="分类ID")
    name = Column(String(100), nullable=False, comment="分类名称")
    parent_id = Column(Integer, ForeignKey("t_category.id"), nullable=True, comment="父级分类ID")
    sort_order = Column(Integer, default=0, comment="排序")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    parent = relationship("Category", remote_side=[id], backref="children")
    products = relationship("Product", backref="category_ref")


# 商品表
class Product(Base):
    __tablename__ = "t_product"
    id = Column(Integer, primary_key=True, autoincrement=True, comment="商品ID")
    name = Column(String(200), nullable=False, comment="商品名称")
    barcode = Column(String(50), unique=True, nullable=True, comment="条形码")
    category_id = Column(Integer, ForeignKey("t_category.id"), nullable=True, comment="分类ID")
    unit = Column(String(20), default="个", comment="规格单位")
    purchase_price = Column(DECIMAL(10, 2), default=0.00, comment="进价")
    selling_price = Column(DECIMAL(10, 2), default=0.00, comment="售价")
    stock_quantity = Column(Integer, default=0, comment="当前库存量")
    stock_lower_limit = Column(Integer, default=0, comment="库存下限")
    stock_upper_limit = Column(Integer, default=99999, comment="库存上限")
    image = Column(String(500), nullable=True, comment="商品图片URL")
    status = Column(Enum(ProductStatus), default=ProductStatus.ON, comment="状态")
    supplier_id = Column(Integer, ForeignKey("t_supplier.id"), nullable=True, comment="供应商ID")
    description = Column(Text, nullable=True, comment="商品描述")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    stock_records = relationship("StockRecord", backref="product")
    order_details = relationship("OrderDetail", backref="product")


# 库存记录表
class StockRecord(Base):
    __tablename__ = "t_stock_record"
    id = Column(Integer, primary_key=True, autoincrement=True, comment="记录ID")
    product_id = Column(Integer, ForeignKey("t_product.id"), nullable=False, comment="商品ID")
    change_quantity = Column(Integer, nullable=False, comment="变动数量(正数入库/负数出库)")
    change_type = Column(String(50), comment="变动类型(采购入库/销售出库/报损/调拨/盘点)")
    before_quantity = Column(Integer, default=0, comment="变动前库存")
    after_quantity = Column(Integer, default=0, comment="变动后库存")
    related_order_no = Column(String(50), nullable=True, comment="关联订单号")
    supplier_id = Column(Integer, ForeignKey("t_supplier.id"), nullable=True, comment="供应商ID")
    operator = Column(String(100), comment="操作人")
    remark = Column(String(500), nullable=True, comment="备注")
    created_at = Column(DateTime, default=datetime.now, comment="操作时间")


# 供应商表
class Supplier(Base):
    __tablename__ = "t_supplier"
    id = Column(Integer, primary_key=True, autoincrement=True, comment="供应商ID")
    name = Column(String(200), nullable=False, comment="供应商名称")
    contact_person = Column(String(100), comment="联系人")
    phone = Column(String(20), comment="联系电话")
    address = Column(String(500), comment="地址")
    supply_category = Column(String(200), comment="供货品类")
    rating = Column(Integer, default=0, comment="评价等级(1-5)")
    delivery_rate = Column(Integer, default=0, comment="交货及时率(百分比)")
    remark = Column(Text, nullable=True, comment="备注")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    products = relationship("Product", backref="supplier")
    stock_records = relationship("StockRecord", backref="supplier_ref")


# 顾客表
class Customer(Base):
    __tablename__ = "t_customer"
    id = Column(Integer, primary_key=True, autoincrement=True, comment="顾客ID")
    name = Column(String(100), comment="姓名")
    phone = Column(String(20), unique=True, nullable=False, comment="手机号")
    password = Column(String(200), nullable=False, comment="密码(加密)")
    gender = Column(String(10), default="未知", comment="性别")
    avatar = Column(String(500), nullable=True, comment="头像")
    register_time = Column(DateTime, default=datetime.now, comment="注册时间")
    total_consumption = Column(DECIMAL(12, 2), default=0.00, comment="累计消费金额")
    member_level = Column(String(20), default="普通会员", comment="会员等级")
    points = Column(Integer, default=0, comment="积分")
    status = Column(String(10), default="正常", comment="状态(正常/冻结)")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    orders = relationship("Order", backref="customer")


class OrderStatus(str, enum.Enum):
    PENDING_PAYMENT = "待支付"
    PENDING_SHIPPING = "待发货"
    SHIPPED = "已发货"
    COMPLETED = "已完成"
    CANCELLED = "已取消"


# 订单表
class Order(Base):
    __tablename__ = "t_order"
    id = Column(Integer, primary_key=True, autoincrement=True, comment="订单ID")
    order_no = Column(String(50), unique=True, nullable=False, comment="订单号")
    customer_id = Column(Integer, ForeignKey("t_customer.id"), nullable=False, comment="顾客ID")
    total_amount = Column(DECIMAL(12, 2), default=0.00, comment="总金额")
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING_PAYMENT, comment="订单状态")
    payment_method = Column(String(50), default="模拟支付", comment="支付方式")
    receiver_name = Column(String(100), comment="收货人姓名")
    receiver_phone = Column(String(20), comment="收货人电话")
    receiver_address = Column(String(500), comment="收货地址")
    remark = Column(String(500), nullable=True, comment="订单备注")
    order_time = Column(DateTime, default=datetime.now, comment="下单时间")
    payment_time = Column(DateTime, nullable=True, comment="支付时间")
    shipping_time = Column(DateTime, nullable=True, comment="发货时间")
    completed_time = Column(DateTime, nullable=True, comment="完成时间")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    details = relationship("OrderDetail", backref="order", cascade="all, delete-orphan")


# 订单明细表
class OrderDetail(Base):
    __tablename__ = "t_order_detail"
    id = Column(Integer, primary_key=True, autoincrement=True, comment="明细ID")
    order_id = Column(Integer, ForeignKey("t_order.id"), nullable=False, comment="订单ID")
    product_id = Column(Integer, ForeignKey("t_product.id"), nullable=False, comment="商品ID")
    product_name = Column(String(200), comment="商品名称(快照)")
    quantity = Column(Integer, nullable=False, comment="数量")
    unit_price = Column(DECIMAL(10, 2), nullable=False, comment="单价")
    subtotal = Column(DECIMAL(12, 2), nullable=False, comment="小计金额")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")


# 员工表
class Employee(Base):
    __tablename__ = "t_employee"
    id = Column(Integer, primary_key=True, autoincrement=True, comment="员工ID")
    name = Column(String(100), nullable=False, comment="姓名")
    gender = Column(String(10), default="未知", comment="性别")
    phone = Column(String(20), comment="手机号")
    position = Column(String(100), comment="职位")
    hire_date = Column(Date, comment="入职日期")
    salary = Column(DECIMAL(10, 2), default=0.00, comment="薪资")
    status = Column(String(10), default="在职", comment="状态(在职/离职)")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    user = relationship("User", backref="employee", uselist=False)


# 系统用户表
class User(Base):
    __tablename__ = "t_user"
    id = Column(Integer, primary_key=True, autoincrement=True, comment="用户ID")
    employee_id = Column(Integer, ForeignKey("t_employee.id"), nullable=True, comment="员工ID")
    username = Column(String(100), unique=True, nullable=False, comment="用户名")
    password = Column(String(200), nullable=False, comment="密码(加密)")
    role = Column(String(50), default="普通员工", comment="角色(超级管理员/主管/普通员工)")
    status = Column(String(10), default="正常", comment="状态(正常/禁用)")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")


# 操作日志表
class OperationLog(Base):
    __tablename__ = "t_operation_log"
    id = Column(Integer, primary_key=True, autoincrement=True, comment="日志ID")
    user_id = Column(Integer, ForeignKey("t_user.id"), nullable=True, comment="操作用户ID")
    username = Column(String(100), comment="用户名")
    action = Column(String(200), comment="操作动作")
    target_type = Column(String(50), comment="操作对象类型")
    target_id = Column(Integer, nullable=True, comment="操作对象ID")
    detail = Column(Text, nullable=True, comment="操作详情")
    ip_address = Column(String(50), nullable=True, comment="IP地址")
    created_at = Column(DateTime, default=datetime.now, comment="操作时间")


# 库存盘点表
class StockCheck(Base):
    __tablename__ = "t_stock_check"
    id = Column(Integer, primary_key=True, autoincrement=True, comment="盘点ID")
    check_no = Column(String(50), unique=True, nullable=False, comment="盘点单号")
    check_date = Column(Date, comment="盘点日期")
    status = Column(String(20), default="进行中", comment="状态(进行中/已完成)")
    operator = Column(String(100), comment="盘点人")
    remark = Column(String(500), nullable=True, comment="备注")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")


# 盘点明细表
class StockCheckDetail(Base):
    __tablename__ = "t_stock_check_detail"
    id = Column(Integer, primary_key=True, autoincrement=True, comment="明细ID")
    check_id = Column(Integer, ForeignKey("t_stock_check.id"), nullable=False, comment="盘点ID")
    product_id = Column(Integer, ForeignKey("t_product.id"), nullable=False, comment="商品ID")
    book_quantity = Column(Integer, default=0, comment="账面库存")
    actual_quantity = Column(Integer, default=0, comment="实际库存")
    difference = Column(Integer, default=0, comment="差异数量")
    remark = Column(String(500), nullable=True, comment="备注")
