# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
from ..database import get_db
from ..models import Employee, User, OperationLog
from ..schemas import EmployeeCreate, EmployeeUpdate, ApiResponse
from ..utils.auth import require_admin

router = APIRouter()


@router.get("/", response_model=ApiResponse)
async def list_employees(
    keyword: Optional[str] = Query(None),
    position: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    query = db.query(Employee)
    if keyword:
        query = query.filter(Employee.name.like(f"%{keyword}%") | Employee.phone.like(f"%{keyword}%"))
    if position:
        query = query.filter(Employee.position == position)
    if status:
        query = query.filter(Employee.status == status)

    total = query.count()
    employees = query.order_by(desc(Employee.id)).offset((page - 1) * page_size).limit(page_size).all()

    result = []
    for e in employees:
        user = db.query(User).filter(User.employee_id == e.id).first()
        result.append({
            "id": e.id, "name": e.name, "gender": e.gender, "phone": e.phone,
            "position": e.position, "hire_date": str(e.hire_date) if e.hire_date else None,
            "salary": float(e.salary), "status": e.status,
            "username": user.username if user else None,
            "role": user.role if user else None
        })
    return ApiResponse(data={"total": total, "page": page, "page_size": page_size, "data": result})


@router.get("/{employee_id}", response_model=ApiResponse)
async def get_employee(employee_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    e = db.query(Employee).filter(Employee.id == employee_id).first()
    if not e:
        raise HTTPException(status_code=404, detail="员工不存在")
    user = db.query(User).filter(User.employee_id == employee_id).first()
    return ApiResponse(data={
        "id": e.id, "name": e.name, "gender": e.gender, "phone": e.phone,
        "position": e.position, "hire_date": str(e.hire_date) if e.hire_date else None,
        "salary": float(e.salary), "status": e.status,
        "username": user.username if user else None, "role": user.role if user else None
    })


@router.post("/", response_model=ApiResponse)
async def create_employee(data: EmployeeCreate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    emp = Employee(**data.model_dump())
    db.add(emp)
    db.commit()
    db.refresh(emp)

    log = OperationLog(user_id=admin.id, username=admin.username, action="创建员工",
                       target_type="Employee", target_id=emp.id, detail=data.name)
    db.add(log)
    db.commit()
    return ApiResponse(data={"id": emp.id})


@router.put("/{employee_id}", response_model=ApiResponse)
async def update_employee(employee_id: int, data: EmployeeUpdate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    e = db.query(Employee).filter(Employee.id == employee_id).first()
    if not e:
        raise HTTPException(status_code=404, detail="员工不存在")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(e, key, value)
    db.commit()
    return ApiResponse(message="更新成功")


@router.delete("/{employee_id}", response_model=ApiResponse)
async def delete_employee(employee_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    e = db.query(Employee).filter(Employee.id == employee_id).first()
    if not e:
        raise HTTPException(status_code=404, detail="员工不存在")
    user = db.query(User).filter(User.employee_id == employee_id).first()
    if user:
        db.delete(user)
    db.delete(e)
    db.commit()
    log = OperationLog(user_id=admin.id, username=admin.username, action="删除员工",
                       target_type="Employee", target_id=employee_id)
    db.add(log)
    db.commit()
    return ApiResponse(message="删除成功")


@router.get("/logs/all", response_model=ApiResponse)
async def get_operation_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    query = db.query(OperationLog)
    total = query.count()
    logs = query.order_by(desc(OperationLog.created_at)).offset((page - 1) * page_size).limit(page_size).all()
    result = [{
        "id": l.id, "username": l.username, "action": l.action,
        "target_type": l.target_type, "detail": l.detail,
        "created_at": str(l.created_at)
    } for l in logs]
    return ApiResponse(data={"total": total, "page": page, "page_size": page_size, "data": result})
