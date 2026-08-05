from sqlalchemy.orm import Session
from typing import List, Optional
import models, schemas
from datetime import datetime
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Category CRUD
def get_category(db: Session, category_id: int):
    return db.query(models.Category).filter(models.Category.id == category_id).first()

def get_categories(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Category).order_by(models.Category.id).offset(skip).limit(limit).all()

def create_category(db: Session, category: schemas.CategoryCreate):
    db_category = models.Category(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

# Product CRUD
def get_product(db: Session, product_id: int):
    return db.query(models.Product).filter(models.Product.id == product_id).first()

def get_products(db: Session, skip: int = 0, limit: int = 100, category_id: Optional[int] = None, is_active: Optional[bool] = True):
    query = db.query(models.Product)
    if category_id is not None:
        query = query.filter(models.Product.category_id == category_id)
    if is_active is not None:
        query = query.filter(models.Product.is_active == is_active)
    return query.order_by(models.Product.id).offset(skip).limit(limit).all()

def search_products(db: Session, search_term: str, skip: int = 0, limit: int = 100):
    return db.query(models.Product).filter(
        (models.Product.name.contains(search_term)) |
        (models.Product.sku.contains(search_term)) |
        (models.Product.description.contains(search_term))
    ).order_by(models.Product.id).offset(skip).limit(limit).all()

def create_product(db: Session, product: schemas.ProductCreate):
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def update_product(db: Session, product_id: int, product: schemas.ProductUpdate):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if db_product:
        update_data = product.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_product, key, value)
        db.commit()
        db.refresh(db_product)
    return db_product

def delete_product(db: Session, product_id: int):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if db_product:
        db.delete(db_product)
        db.commit()
        return True
    return False

def get_low_stock_products(db: Session, threshold: int = 5):
    return db.query(models.Product).filter(
        models.Product.stock_quantity <= models.Product.min_stock_level
    ).all()

# User CRUD
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Cart CRUD
def get_cart_items(db: Session, user_id: int):
    return db.query(models.CartItem).filter(models.CartItem.user_id == user_id).all()

def add_to_cart(db: Session, user_id: int, cart_item: schemas.CartItemCreate):
    # Check if product already in cart
    existing = db.query(models.CartItem).filter(
        models.CartItem.user_id == user_id,
        models.CartItem.product_id == cart_item.product_id
    ).first()
    if existing:
        existing.quantity += cart_item.quantity
        db.commit()
        db.refresh(existing)
        return existing
    else:
        db_cart_item = models.CartItem(
            user_id=user_id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity
        )
        db.add(db_cart_item)
        db.commit()
        db.refresh(db_cart_item)
        return db_cart_item

def update_cart_item(db: Session, cart_item_id: int, quantity: int):
    db_cart_item = db.query(models.CartItem).filter(models.CartItem.id == cart_item_id).first()
    if db_cart_item:
        if quantity <= 0:
            db.delete(db_cart_item)
        else:
            db_cart_item.quantity = quantity
        db.commit()
        return db_cart_item
    return None

def remove_from_cart(db: Session, cart_item_id: int):
    db_cart_item = db.query(models.CartItem).filter(models.CartItem.id == cart_item_id).first()
    if db_cart_item:
        db.delete(db_cart_item)
        db.commit()
        return True
    return False

def clear_cart(db: Session, user_id: int):
    db.query(models.CartItem).filter(models.CartItem.user_id == user_id).delete()
    db.commit()

# Order CRUD
def create_order(db: Session, user_id: int, order: schemas.OrderCreate):
    # Get cart items
    cart_items = db.query(models.CartItem).filter(models.CartItem.user_id == user_id).all()
    if not cart_items:
        return None

    total_amount = 0
    order_items = []

    # Calculate total and create order items
    for cart_item in cart_items:
        product = db.query(models.Product).filter(models.Product.id == cart_item.product_id).first()
        if not product or product.stock_quantity < cart_item.quantity:
            continue

        item_total = product.price * cart_item.quantity
        total_amount += item_total
        order_items.append({
            "product_id": product.id,
            "quantity": cart_item.quantity,
            "unit_price": product.price,
            "total_price": item_total
        })

    shipping_cost = 0.0
    if order.zone_id:
        zone = db.query(models.DeliveryZone).filter(models.DeliveryZone.id == order.zone_id).first()
        if zone:
            shipping_cost = zone.shipping_cost
    total_amount += shipping_cost

    # Create order
    db_order = models.Order(
        user_id=user_id,
        total_amount=total_amount,
        shipping_address=order.shipping_address,
        payment_method=order.payment_method,
        notes=order.notes,
        zone_id=order.zone_id,
        shipping_cost=shipping_cost
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    # Create order items and update stock
    for item_data in order_items:
        db_order_item = models.OrderItem(
            order_id=db_order.id,
            **item_data
        )
        db.add(db_order_item)

        # Update stock
        product = db.query(models.Product).filter(models.Product.id == item_data["product_id"]).first()
        product.stock_quantity -= item_data["quantity"]

        # Create sale record
        month_year = datetime.now().strftime("%Y-%m")
        db_sale = models.Sale(
            product_id=item_data["product_id"],
            order_id=db_order.id,
            quantity=item_data["quantity"],
            unit_price=item_data["unit_price"],
            total_amount=item_data["total_price"],
            month_year=month_year
        )
        db.add(db_sale)

    db.commit()

    # Clear cart
    clear_cart(db, user_id)

    return db_order

def get_order(db: Session, order_id: int, user_id: Optional[int] = None):
    query = db.query(models.Order).filter(models.Order.id == order_id)
    if user_id:
        query = query.filter(models.Order.user_id == user_id)
    return query.first()

def get_orders(db: Session, user_id: Optional[int] = None, skip: int = 0, limit: int = 100):
    query = db.query(models.Order)
    if user_id:
        query = query.filter(models.Order.user_id == user_id)
    return query.order_by(models.Order.created_at.desc()).offset(skip).limit(limit).all()

def get_all_orders(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Order).order_by(models.Order.created_at.desc()).offset(skip).limit(limit).all()

def update_order_status(db: Session, order_id: int, status: models.OrderStatus):
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if db_order:
        db_order.status = status
        db.commit()
        db.refresh(db_order)
    return db_order

# Analytics / Dashboard
def get_top_selling_products(db: Session, month: Optional[str] = None, limit: int = 10):
    from sqlalchemy import func
    query = db.query(
        models.Sale.product_id,
        func.sum(models.Sale.quantity).label("total_quantity"),
        func.sum(models.Sale.total_amount).label("total_revenue")
    )
    if month:
        query = query.filter(models.Sale.month_year == month)
    query = query.group_by(models.Sale.product_id).order_by(func.sum(models.Sale.quantity).desc()).limit(limit)

    results = query.all()
    top_products = []
    for result in results:
        product = db.query(models.Product).filter(models.Product.id == result.product_id).first()
        if product:
            top_products.append({
                "product_id": product.id,
                "product_name": product.name,
                "sku": product.sku,
                "total_quantity": result.total_quantity,
                "total_revenue": result.total_revenue
            })
    return top_products

def get_monthly_sales(db: Session, year: Optional[int] = None):
    from sqlalchemy import func
    query = db.query(
        models.Sale.month_year,
        func.sum(models.Sale.total_amount).label("total_sales"),
        func.count(func.distinct(models.Sale.order_id)).label("total_orders")
    )
    if year:
        query = query.filter(models.Sale.month_year.like(f"{year}%"))
    query = query.group_by(models.Sale.month_year).order_by(models.Sale.month_year)

    results = query.all()
    return [
        {
            "month": r.month_year,
            "total_sales": r.total_sales,
            "total_orders": r.total_orders
        }
        for r in results
    ]

# Delivery zones / fleet CRUD
def get_delivery_zones(db: Session):
    return db.query(models.DeliveryZone).order_by(models.DeliveryZone.id).all()

def get_vehicles(db: Session):
    return db.query(models.Vehicle).order_by(models.Vehicle.id).all()

def simulate_vehicle_tick(db: Session):
    import random
    vehicles = db.query(models.Vehicle).all()
    for v in vehicles:
        # occasionally pick a new random heading, otherwise keep drifting the same way
        if random.random() < 0.15 or (v.heading_lat == 0 and v.heading_lng == 0):
            v.heading_lat = random.uniform(-1, 1) * 0.0025
            v.heading_lng = random.uniform(-1, 1) * 0.0025
        v.lat += v.heading_lat
        v.lng += v.heading_lng
    db.commit()

def get_dashboard_stats(db: Session):
    from sqlalchemy import func

    total_revenue = db.query(func.sum(models.Order.total_amount)).filter(
        models.Order.status != models.OrderStatus.cancelled
    ).scalar() or 0

    total_orders = db.query(models.Order).count()
    total_products = db.query(models.Product).filter(models.Product.is_active == True).count()
    total_customers = db.query(models.User).filter(models.User.is_admin == False).count()
    low_stock = db.query(models.Product).filter(
        models.Product.stock_quantity <= models.Product.min_stock_level
    ).count()

    return {
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "total_products": total_products,
        "total_customers": total_customers,
        "low_stock_products": low_stock
    }
