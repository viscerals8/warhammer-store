export interface User {
  id: number;
  email: string;
  full_name: string;
  is_admin: boolean;
}

export interface Category {
  id: number;
  name: string;
  description?: string;
  parent_id?: number;
}

export interface Product {
  id: number;
  name: string;
  description?: string;
  price: number;
  cost_price: number;
  sku: string;
  stock_quantity: number;
  min_stock_level: number;
  category_id: number;
  manufacturer?: string;
  material?: string;
  scale?: string;
  is_3d_print: boolean;
  print_time_hours?: number;
  resin_type?: string;
  image_urls?: string[];
  is_active: boolean;
  created_at: string;
  updated_at?: string;
  category?: Category;
}

export interface CartItem {
  id: number;
  product: Product;
  quantity: number;
}

export interface Cart {
  items: CartItem[];
  total: number;
}

export interface OrderItem {
  id: number;
  product: Product;
  quantity: number;
  unit_price: number;
  total_price: number;
}

export interface Order {
  id: number;
  user_id: number;
  total_amount: number;
  status: 'pending' | 'processing' | 'shipped' | 'delivered' | 'cancelled';
  shipping_address: any;
  payment_method?: string;
  tracking_number?: string;
  notes?: string;
  created_at: string;
  items: OrderItem[];
}

export interface TopSellingProduct {
  product_id: number;
  product_name: string;
  sku: string;
  total_quantity: number;
  total_revenue: number;
}

export interface MonthlySale {
  month: string;
  total_sales: number;
  total_orders: number;
}

export interface DeliveryZone {
  id: number;
  name: string;
  description?: string;
  center_lat: number;
  center_lng: number;
  radius_km: number;
  shipping_cost: number;
  color: string;
}

export interface Vehicle {
  id: number;
  name: string;
  plate?: string;
  driver_name?: string;
  status: 'idle' | 'delivering' | 'returning';
  lat: number;
  lng: number;
  updated_at?: string;
}

export interface DashboardStats {
  total_revenue: number;
  total_orders: number;
  total_products: number;
  total_customers: number;
  low_stock_products: number;
  top_selling_products: TopSellingProduct[];
  monthly_sales: MonthlySale[];
}
