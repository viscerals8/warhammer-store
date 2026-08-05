from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import schemas, crud, auth, models
from database import get_db

router = APIRouter(prefix="/cart", tags=["cart"])

@router.get("/", response_model=schemas.CartResponse)
def get_cart(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    cart_items = crud.get_cart_items(db, user_id=current_user.id)
    total = sum(
        db.query(models.Product).filter(models.Product.id == item.product_id).first().price * item.quantity
        for item in cart_items if db.query(models.Product).filter(models.Product.id == item.product_id).first()
    )

    items_response = []
    for item in cart_items:
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        if product:
            items_response.append({
                "id": item.id,
                "product": product,
                "quantity": item.quantity
            })

    return {"items": items_response, "total": total}

@router.post("/", response_model=schemas.CartItemResponse)
def add_to_cart(
    cart_item: schemas.CartItemCreate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    product = db.query(models.Product).filter(models.Product.id == cart_item.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.stock_quantity < cart_item.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")

    db_cart_item = crud.add_to_cart(db, user_id=current_user.id, cart_item=cart_item)
    return {
        "id": db_cart_item.id,
        "product": product,
        "quantity": db_cart_item.quantity
    }

@router.put("/{cart_item_id}", response_model=schemas.CartItemResponse)
def update_cart_item(
    cart_item_id: int,
    quantity: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    cart_item = crud.update_cart_item(db, cart_item_id=cart_item_id, quantity=quantity)
    if cart_item is None:
        raise HTTPException(status_code=404, detail="Cart item not found")
    product = db.query(models.Product).filter(models.Product.id == cart_item.product_id).first()
    return {
        "id": cart_item.id,
        "product": product,
        "quantity": cart_item.quantity
    }

@router.delete("/{cart_item_id}")
def remove_from_cart(
    cart_item_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    success = crud.remove_from_cart(db, cart_item_id=cart_item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Cart item not found")
    return {"message": "Item removed from cart"}

@router.delete("/")
def clear_cart(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    crud.clear_cart(db, user_id=current_user.id)
    return {"message": "Cart cleared"}
