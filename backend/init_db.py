#!/usr/bin/env python
"""
Initialize database with sample data
"""
from database import engine, SessionLocal, Base
from models import Category, User, Product
from auth import get_password_hash
import random

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Check if admin user exists
    admin = db.query(User).filter(User.email == "admin@warhammer.store").first()
    if not admin:
        admin = User(
            email="admin@warhammer.store",
            hashed_password=get_password_hash("admin123"),
            full_name="Store Admin",
            is_admin=True
        )
        db.add(admin)
        db.commit()
        print("Created admin user: admin@warhammer.store / admin123")

    # Create sample categories
    categories_data = [
        {"name": "Warhammer 40K", "description": "Sci-fi miniature wargame"},
        {"name": "Warhammer Age of Sigmar", "description": "Fantasy miniature wargame"},
        {"name": "Warhammer Space Marines", "description": "Imperial super soldiers"},
        {"name": "Warhammer Orks", "description": "Green skinned raiders"},
        {"name": "Warhammer Eldar", "description": "Ancient space elves"},
        {"name": "Warhammer Tyranids", "description": "Alien hive mind"},
        {"name": "Warhammer Necrons", "description": "Ancient robotic undead"},
        {"name": "Custom 3D Prints", "description": "Custom printed miniatures and terrain"},
        {"name": "3D Terrain", "description": "Printed terrain pieces"},
        {"name": "Warhammer Chaos", "description": "Traitor legions and daemon-touched warriors"},
        {"name": "Warhammer Tau", "description": "Advanced alien coalition of the Greater Good"},
        {"name": "Warhammer Imperial Guard", "description": "The Astra Militarum, endless human regiments"},
    ]

    for cat_data in categories_data:
        category = db.query(Category).filter(Category.name == cat_data["name"]).first()
        if not category:
            new_category = Category(**cat_data)
            db.add(new_category)
            db.commit()
            print(f"Created category: {cat_data['name']}")

    # Create sample products
    wh40k_category = db.query(Category).filter(Category.name == "Warhammer 40K").first()
    if wh40k_category:
        sample_products = [
            {
                "name": "Space Marine Intercessor Squad",
                "description": "5-man squad of Space Marine Intercessors with bolt rifles",
                "price": 45.99,
                "cost_price": 25.00,
                "sku": "WH40K-001",
                "stock_quantity": 50,
                "min_stock_level": 10,
                "category_id": wh40k_category.id,
                "manufacturer": "Games Workshop",
                "material": "Plastic",
                "scale": "28mm",
                "is_3d_print": False,
                "image_urls": ["/assets/emblems/space-marines.svg"]
            },
            {
                "name": "Ork Boyz Mob",
                "description": "10 Ork Boyz with shootas and sluggas",
                "price": 38.99,
                "cost_price": 20.00,
                "sku": "WH40K-002",
                "stock_quantity": 35,
                "min_stock_level": 8,
                "category_id": db.query(Category).filter(Category.name == "Warhammer Orks").first().id,
                "manufacturer": "Games Workshop",
                "material": "Plastic",
                "scale": "28mm",
                "is_3d_print": False,
                "image_urls": ["/assets/emblems/orks.svg"]
            },
            {
                "name": "Craftworld Eldar Aspect Warriors",
                "description": "10 Howling Banshees",
                "price": 52.99,
                "cost_price": 28.00,
                "sku": "WH40K-003",
                "stock_quantity": 20,
                "min_stock_level": 5,
                "category_id": db.query(Category).filter(Category.name == "Warhammer Eldar").first().id,
                "manufacturer": "Games Workshop",
                "material": "Plastic",
                "scale": "28mm",
                "is_3d_print": False,
                "image_urls": ["/assets/emblems/eldar.svg"]
            },
            {
                "name": "3D Printed Ruined Building",
                "description": "25mm scale ruined building for 40K terrain",
                "price": 18.99,
                "cost_price": 5.00,
                "sku": "3D-001",
                "stock_quantity": 100,
                "min_stock_level": 20,
                "category_id": db.query(Category).filter(Category.name == "3D Terrain").first().id,
                "manufacturer": "Custom Print",
                "material": "Resin",
                "scale": "28mm",
                "is_3d_print": True,
                "print_time_hours": 4.5,
                "resin_type": "Standard Resin",
                "image_urls": ["/assets/emblems/terrain.svg"]
            },
            {
                "name": "Custom Sci-Fi Barricade Set",
                "description": "Set of 5 barricades, 3D printed",
                "price": 12.99,
                "cost_price": 3.50,
                "sku": "3D-002",
                "stock_quantity": 75,
                "min_stock_level": 15,
                "category_id": db.query(Category).filter(Category.name == "Custom 3D Prints").first().id,
                "manufacturer": "Custom Print",
                "material": "Resin",
                "scale": "28mm",
                "is_3d_print": True,
                "print_time_hours": 2.0,
                "resin_type": "Grey Resin",
                "image_urls": ["/assets/emblems/custom-print.svg"]
            },
            {
                "name": "Chaos Space Marines",
                "description": "Traitor legionaries corrupted by the ruinous powers",
                "price": 48.99,
                "cost_price": 26.00,
                "sku": "WH40K-004",
                "stock_quantity": 30,
                "min_stock_level": 8,
                "category_id": db.query(Category).filter(Category.name == "Warhammer Chaos").first().id,
                "manufacturer": "Games Workshop",
                "material": "Plastic",
                "scale": "28mm",
                "is_3d_print": False,
                "image_urls": ["/assets/emblems/chaos.svg"]
            },
            {
                "name": "Tau Fire Warriors",
                "description": "10 Fire Warriors with pulse rifles",
                "price": 42.99,
                "cost_price": 23.00,
                "sku": "WH40K-005",
                "stock_quantity": 25,
                "min_stock_level": 6,
                "category_id": db.query(Category).filter(Category.name == "Warhammer Tau").first().id,
                "manufacturer": "Games Workshop",
                "material": "Plastic",
                "scale": "28mm",
                "is_3d_print": False,
                "image_urls": ["/assets/emblems/tau.svg"]
            },
            {
                "name": "Imperial Guard Squad",
                "description": "10-man Astra Militarum infantry squad with lasguns",
                "price": 36.99,
                "cost_price": 19.00,
                "sku": "WH40K-006",
                "stock_quantity": 40,
                "min_stock_level": 10,
                "category_id": db.query(Category).filter(Category.name == "Warhammer Imperial Guard").first().id,
                "manufacturer": "Games Workshop",
                "material": "Plastic",
                "scale": "28mm",
                "is_3d_print": False,
                "image_urls": ["/assets/emblems/imperial-guard.svg"]
            },
            {
                "name": "Necron Warrior Squad",
                "description": "10 Necron Warriors with gauss flayers",
                "price": 44.99,
                "cost_price": 24.00,
                "sku": "WH40K-007",
                "stock_quantity": 22,
                "min_stock_level": 5,
                "category_id": db.query(Category).filter(Category.name == "Warhammer Necrons").first().id,
                "manufacturer": "Games Workshop",
                "material": "Plastic",
                "scale": "28mm",
                "is_3d_print": False,
                "image_urls": ["/assets/emblems/necrons.svg"]
            },
        ]

        for product_data in sample_products:
            existing = db.query(Product).filter(Product.sku == product_data["sku"]).first()
            if not existing:
                product = Product(**product_data)
                db.add(product)
                db.commit()
                print(f"Created product: {product_data['name']}")

    db.close()
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_db()
