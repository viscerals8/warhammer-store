from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import schemas, crud, auth, models
from database import get_db

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("/", response_model=schemas.OrderResponse)
def create_order(
    order: schemas.OrderCreate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    db_order = crud.create_order(db, user_id=current_user.id, order=order)
    if db_order is None:
        raise HTTPException(status_code=400, detail="Cannot create order. Cart may be empty or insufficient stock.")
    return db_order

@router.get("/", response_model=List[schemas.OrderResponse])
def list_orders(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    orders = crud.get_orders(db, user_id=current_user.id, skip=skip, limit=limit)
    return orders

@router.get("/admin", response_model=List[schemas.OrderResponse])
def list_all_orders(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(auth.get_current_admin_user),
    db: Session = Depends(get_db)
):
    return crud.get_all_orders(db, skip=skip, limit=limit)

@router.get("/{order_id}", response_model=schemas.OrderResponse)
def get_order(
    order_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    order = crud.get_order(db, order_id=order_id, user_id=current_user.id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.put("/{order_id}/status", response_model=schemas.OrderResponse)
def update_order_status(
    order_id: int,
    status: models.OrderStatus,
    current_user: models.User = Depends(auth.get_current_admin_user),
    db: Session = Depends(get_db)
):
    order = crud.update_order_status(db, order_id=order_id, status=status)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
