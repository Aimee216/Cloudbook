# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, Employee, OperationLog
from ..schemas import UserLogin, UserCreate, UserOut, ApiResponse
from ..utils.auth import hash_password, verify_password, create_access_token, require_admin

router = APIRouter()


@router.post("/login", response_model=ApiResponse)
async def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    if user.status != "正常":
        raise HTTPException(status_code=403, detail="账号已被禁用")
    token = create_access_token({"sub": user.username, "role": user.role})
    return ApiResponse(data={
        "token": token,
        "user": {"id": user.id, "username": user.username, "role": user.role}
    })


@router.post("/register", response_model=ApiResponse)
async def register(data: UserCreate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    if admin.role not in ["超级管理员"]:
        raise HTTPException(status_code=403, detail="仅超级管理员可创建用户")
    exist = db.query(User).filter(User.username == data.username).first()
    if exist:
        raise HTTPException(status_code=400, detail="用户名已存在")
    user = User(username=data.username, password=hash_password(data.password), role=data.role, employee_id=data.employee_id)
    db.add(user)
    db.commit()
    db.refresh(user)

    log = OperationLog(user_id=admin.id, username=admin.username, action="创建系统用户",
                       target_type="User", target_id=user.id, detail=f"用户名: {data.username}, 角色: {data.role}")
    db.add(log)
    db.commit()
    return ApiResponse(data={"id": user.id, "username": user.username})


@router.get("/me", response_model=ApiResponse)
async def get_me(current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.id == current_user.employee_id).first()
    return ApiResponse(data={
        "id": current_user.id,
        "username": current_user.username,
        "role": current_user.role,
        "employee": {"name": emp.name, "position": emp.position} if emp else None
    })
