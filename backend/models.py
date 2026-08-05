from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from database import Base

class ProductCategory(enum.Enum):
    warhammer_40k = "warhammer_40k"
    warhammer_ageof_sigmar = "warhammer_ageof_sigmar"
    warhammer_sistersof_battle = "warhammer_sistersof_battle"
    warhammer_adeptus_mechanicus = "warhammer_adeptus_mechanicus"
    warhammer_eldar = "warhammer_eldar"
    warhammer_orcs = "warhammer_orcs"
    warhammer_tyranids = "warhammer_tyranids"
    warhammer_necrons = "warhammer_necrons"
    warhammer_tau = "warhammer_tau"
    warhammer_dark_eldar = "warhammer_dark_eldar"
    warhammer_imperial_guard = "warhammer_imperial_guard"
    warhammer_space_marine = "warhammer_space_marine"
    custom_3d_print = "custom_3d_print"
    terrain_3d = "terrain_3d"
    bases_objets = "bases_objets"

class OrderStatus(enum.Enum):
    pending = "pending"
    processing = "processing"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"

class VehicleStatus(enum.Enum):
    idle = "idle"
    delivering = "delivering"
    returning = "returning"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    cart_items = relationship("CartItem", back_populates="owner", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="owner")

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)

    products = relationship("Product", back_populates="category")
    subcategories = relationship("Category")

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    price = Column(Float, nullable=False)
    cost_price = Column(Float, default=0.0)
    sku = Column(String(100), unique=True, nullable=False)
    stock_quantity = Column(Integer, default=0)
    min_stock_level = Column(Integer, default=5)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    manufacturer = Column(String(100))
    material = Column(String(100))
    scale = Column(String(50))
    is_3d_print = Column(Boolean, default=False)
    print_time_hours = Column(Float)
    resin_type = Column(String(100))
    image_urls = Column(JSON)  # List of image URLs
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    category = relationship("Category", back_populates="products")
    cart_items = relationship("CartItem", back_populates="product", cascade="all, delete-orphan")
    order_items = relationship("OrderItem", back_populates="product")

class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="cart_items")
    product = relationship("Product", back_populates="cart_items")

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    total_amount = Column(Float, nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.pending)
    shipping_address = Column(JSON)
    payment_method = Column(String(100))
    tracking_number = Column(String(255))
    notes = Column(Text)
    zone_id = Column(Integer, ForeignKey("delivery_zones.id"), nullable=True)
    shipping_cost = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    owner = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")

class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    sale_date = Column(DateTime(timezone=True), server_default=func.now())
    month_year = Column(String(7))  # Format: YYYY-MM

    product = relationship("Product")

class DeliveryZone(Base):
    __tablename__ = "delivery_zones"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    center_lat = Column(Float, nullable=False)
    center_lng = Column(Float, nullable=False)
    radius_km = Column(Float, nullable=False)
    shipping_cost = Column(Float, nullable=False)
    color = Column(String(20), default="#d4af37")

class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    plate = Column(String(20))
    driver_name = Column(String(100))
    status = Column(Enum(VehicleStatus), default=VehicleStatus.idle)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    heading_lat = Column(Float, default=0.0)
    heading_lng = Column(Float, default=0.0)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
