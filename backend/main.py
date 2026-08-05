import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routers import auth, products, categories, cart, orders, dashboard, fleet
from database import engine, Base, SessionLocal
import models
import crud
import os

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Warhammer Store API",
    description="API for Warhammer and 3D printed figures store",
    version="1.0.0"
)

# Serve static media files
MEDIA_DIR = os.path.join(os.path.dirname(__file__), "media")
app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # Angular dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(categories.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(cart.router, prefix="/api")
app.include_router(orders.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(fleet.router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Warhammer Store API"}

async def _vehicle_simulation_loop():
    while True:
        await asyncio.sleep(3)
        db = SessionLocal()
        try:
            crud.simulate_vehicle_tick(db)
        except Exception:
            pass
        finally:
            db.close()

@app.on_event("startup")
async def start_vehicle_simulation():
    asyncio.create_task(_vehicle_simulation_loop())
