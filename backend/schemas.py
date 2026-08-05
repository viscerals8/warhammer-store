from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List
from enum import Enum

class ProductCategory(str, Enum):
    warhammer_40k = "warhammer_40k"
    warhammer_ageof_sigmar = "warhammer_ageof_sigmar"
    warhammer_sistersof_battle = "warhammer_sistersof_battle"
    warhammer_adeptus_mechanicus = "warhammer_adeptus_mechanicus"
    warhammer_eldar = "warhammer_eldar"
    warhammer_orcs = "warhammer_orks"
    warhammer_tyranids = "warhammer_tyranids"
    warhammer_necrons = "warhammer_necrons"
    warhammer_tau = "warhammer_tau"
    warhammer_dark_eldar = "warhammer_darkeldar"
    warhammer_imperial_guard = "warhammer_imperialguard"
    warhammer_space_marine = "warhammer_spacemarine"
    custom_3d_print = "custom_3d_print"
    terrain_3d = "terrain_3d"
    bases_objets = "bases_objets"

class OrderStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"

# User schemas
class UserBase(BaseModel):
    email: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_admin: bool

    model_config = ConfigDict(from_attributes=True)

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Category schemas
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    parent_id: Optional[int] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

# Product schemas
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    cost_price: Optional[float] = 0.0
    sku: str
    stock_quantity: int = 0
    min_stock_level: int = 5
    category_id: int
    manufacturer: Optional[str] = None
    material: Optional[str] = None
    scale: Optional[str] = None
    is_3d_print: bool = False
    print_time_hours: Optional[float] = None
    resin_type: Optional[str] = None
    image_urls: Optional[List[str]] = []
    is_active: bool = True

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    cost_price: Optional[float] = None
    stock_quantity: Optional[int] = None
    min_stock_level: Optional[int] = None
    category_id: Optional[int] = None
    manufacturer: Optional[str] = None
    material: Optional[str] = None
    scale: Optional[str] = None
    is_3d_print: Optional[bool] = None
    print_time_hours: Optional[float] = None
    resin_type: Optional[str] = None
    image_urls: Optional[List[str]] = None
    is_active: Optional[bool] = None

class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    category: Optional[CategoryResponse] = None

    model_config = ConfigDict(from_attributes=True)

class ProductListItem(BaseModel):
    id: int
    name: str
    price: float
    sku: str
    stock_quantity: int
    is_active: bool
    image_urls: Optional[List[str]] = []
    category: Optional[CategoryResponse] = None

    model_config = ConfigDict(from_attributes=True)

# Cart schemas
class CartItemBase(BaseModel):
    product_id: int
    quantity: int = 1

class CartItemCreate(CartItemBase):
    pass

class CartItemUpdate(BaseModel):
    quantity: int

class CartItemResponse(BaseModel):
    id: int
    product: ProductResponse
    quantity: int

    model_config = ConfigDict(from_attributes=True)

class CartResponse(BaseModel):
    items: List[CartItemResponse]
    total: float

# Order schemas
class OrderItemBase(BaseModel):
    product_id: int
    quantity: int

class OrderItemCreate(OrderItemBase):
    pass

class OrderCreate(BaseModel):
    shipping_address: dict
    payment_method: Optional[str] = None
    notes: Optional[str] = None
    zone_id: Optional[int] = None

class OrderItemResponse(BaseModel):
    id: int
    product: ProductResponse
    quantity: int
    unit_price: float
    total_price: float

    model_config = ConfigDict(from_attributes=True)

class OrderResponse(BaseModel):
    id: int
    user_id: int
    total_amount: float
    status: OrderStatus
    shipping_address: dict
    payment_method: Optional[str]
    tracking_number: Optional[str]
    notes: Optional[str]
    zone_id: Optional[int] = None
    shipping_cost: Optional[float] = 0.0
    created_at: datetime
    items: List[OrderItemResponse]

    model_config = ConfigDict(from_attributes=True)

# Delivery zone schemas
class DeliveryZoneResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    center_lat: float
    center_lng: float
    radius_km: float
    shipping_cost: float
    color: str

    model_config = ConfigDict(from_attributes=True)

# Vehicle schemas
class VehicleResponse(BaseModel):
    id: int
    name: str
    plate: Optional[str] = None
    driver_name: Optional[str] = None
    status: str
    lat: float
    lng: float
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# Dashboard schemas
class TopSellingProduct(BaseModel):
    product_id: int
    product_name: str
    sku: str
    total_quantity: int
    total_revenue: float

    model_config = ConfigDict(from_attributes=True)

class MonthlySales(BaseModel):
    month: str
    total_sales: float
    total_orders: int

    model_config = ConfigDict(from_attributes=True)

class DashboardStats(BaseModel):
    total_revenue: float
    total_orders: int
    total_products: int
    total_customers: int
    low_stock_products: int
    top_selling_products: List[TopSellingProduct]
    monthly_sales: List[MonthlySales]
