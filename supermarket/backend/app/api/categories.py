# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Category, OperationLog, User
from ..schemas import CategoryCreate, CategoryUpdate, CategoryOut, ApiResponse
from ..utils.auth import require_admin

router = APIRouter()


@router.get("/", response_model=ApiResponse)
async def list_categories(db: Session = Depends(get_db)):
    categories = db.query(Category).order_by(Category.sort_order).all()
    data = []
    for c in categories:
        data.append({"id": c.id, "name": c.name, "parent_id": c.parent_id, "sort_order": c.sort_order})
    return ApiResponse(data=data)


@router.post("/", response_model=ApiResponse)
async def create_category(data: CategoryCreate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    cat = Category(name=data.name, parent_id=data.parent_id, sort_order=data.sort_order)
    db.add(cat)
    db.commit()
    db.refresh(cat)

    log = OperationLog(user_id=admin.id, username=admin.username, action="创建分类",
                       target_type="Category", target_id=cat.id, detail=data.name)
    db.add(log)
    db.commit()
    return ApiResponse(data={"id": cat.id})


@router.put("/{category_id}", response_model=ApiResponse)
async def update_category(category_id: int, data: CategoryUpdate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="分类不存在")
    cat.name = data.name
    cat.parent_id = data.parent_id
    cat.sort_order = data.sort_order
    db.commit()
    return ApiResponse(message="更新成功")


@router.delete("/{category_id}", response_model=ApiResponse)
async def delete_category(category_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="分类不存在")
    # 检查是否有子分类
    children = db.query(Category).filter(Category.parent_id == category_id).count()
    if children > 0:
        raise HTTPException(status_code=400, detail="该分类下有子分类，请先删除子分类")
    db.delete(cat)
    db.commit()

    log = OperationLog(user_id=admin.id, username=admin.username, action="删除分类",
                       target_type="Category", target_id=category_id)
    db.add(log)
    db.commit()
    return ApiResponse(message="删除成功")
