from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel
from decimal import Decimal


# ========== 分类 ==========
class CategoryBase(BaseModel):
    name: str
    parent_id: Optional[int] = None
    sort_order: int = 0

class CategoryCreate(CategoryBase): pass
class CategoryUpdate(CategoryBase): pass

class CategoryOut(CategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime
    children: List["CategoryOut"] = []
    class Config: from_attributes = True


# ========== 商品 ==========
class ProductBase(BaseModel):
    name: str
    barcode: Optional[str] = None
    category_id: Optional[int] = None
    unit: str = "个"
    purchase_price: Decimal = Decimal("0.00")
    selling_price: Decimal = Decimal("0.00")
    stock_lower_limit: int = 0
    stock_upper_limit: int = 99999
    image: Optional[str] = None
    status: str = "上架"
    supplier_id: Optional[int] = None
    description: Optional[str] = None

class ProductCreate(ProductBase): pass

class ProductUpdate(ProductBase):
    name: Optional[str] = None
    selling_price: Optional[Decimal] = None
    status: Optional[str] = None

class ProductOut(ProductBase):
    id: int
    stock_quantity: int
    created_at: datetime
    updated_at: datetime
    class Config: from_attributes = True

class ProductSearch(BaseModel):
    keyword: Optional[str] = None
    category_id: Optional[int] = None
    barcode: Optional[str] = None
    status: Optional[str] = None
    page: int = 1
    page_size: int = 20


# ========== 库存 ==========
class StockRecordCreate(BaseModel):
    product_id: int
    change_quantity: int
    change_type: str
    supplier_id: Optional[int] = None
    remark: Optional[str] = None
    operator: str = "系统"

class StockRecordOut(BaseModel):
    id: int
    product_id: int
    change_quantity: int
    change_type: str
    before_quantity: int
    after_quantity: int
    related_order_no: Optional[str]
    supplier_id: Optional[int]
    operator: str
    remark: Optional[str]
    created_at: datetime
    class Config: from_attributes = True


# ========== 订单 ==========
class OrderDetailCreate(BaseModel):
    product_id: int
    quantity: int
    unit_price: Decimal

class OrderCreate(BaseModel):
    customer_id: int
    receiver_name: str
    receiver_phone: str
    receiver_address: str
    remark: Optional[str] = None
    payment_method: str = "模拟支付"
    details: List[OrderDetailCreate]

class OrderStatusUpdate(BaseModel):
    status: str

class OrderOut(BaseModel):
    id: int
    order_no: str
    customer_id: int
    total_amount: Decimal
    status: str
    payment_method: str
    receiver_name: str
    receiver_phone: str
    receiver_address: str
    remark: Optional[str]
    order_time: datetime
    details: List = []
    class Config: from_attributes = True


# ========== 顾客 ==========
class CustomerRegister(BaseModel):
    phone: str
    password: str
    name: Optional[str] = None

class CustomerLogin(BaseModel):
    phone: str
    password: str

class CustomerOut(BaseModel):
    id: int
    name: Optional[str]
    phone: str
    gender: str
    register_time: datetime
    total_consumption: Decimal
    member_level: str
    points: int
    class Config: from_attributes = True


# ========== 供应商 ==========
class SupplierBase(BaseModel):
    name: str
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    supply_category: Optional[str] = None
    remark: Optional[str] = None

class SupplierCreate(SupplierBase): pass
class SupplierUpdate(SupplierBase): pass

class SupplierOut(SupplierBase):
    id: int
    rating: int
    delivery_rate: int
    created_at: datetime
    class Config: from_attributes = True


# ========== 员工 ==========
class EmployeeBase(BaseModel):
    name: str
    gender: str = "未知"
    phone: Optional[str] = None
    position: Optional[str] = None
    hire_date: Optional[date] = None
    salary: Decimal = Decimal("0.00")

class EmployeeCreate(EmployeeBase): pass
class EmployeeUpdate(EmployeeBase): pass

class EmployeeOut(EmployeeBase):
    id: int
    status: str
    created_at: datetime
    class Config: from_attributes = True


# ========== 系统用户 ==========
class UserCreate(BaseModel):
    username: str
    password: str
    employee_id: Optional[int] = None
    role: str = "普通员工"

class UserLogin(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    role: str
    employee_id: Optional[int]
    status: str
    class Config: from_attributes = True


# ========== 通用 ==========
class PageResult(BaseModel):
    total: int
    page: int
    page_size: int
    data: List

class ApiResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: object = None
