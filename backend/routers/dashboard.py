from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import schemas, crud, auth
from database import get_db

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/stats", response_model=schemas.DashboardStats)
def get_stats(
    db: Session = Depends(get_db),
    current_user: auth.User = Depends(auth.get_current_admin_user)
):
    stats = crud.get_dashboard_stats(db)
    top_selling = crud.get_top_selling_products(db, limit=10)
    monthly_sales = crud.get_monthly_sales(db)

    return {
        **stats,
        "top_selling_products": top_selling,
        "monthly_sales": monthly_sales
    }

@router.get("/top-products", response_model=List[schemas.TopSellingProduct])
def get_top_products(
    month: Optional[str] = None,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: auth.User = Depends(auth.get_current_admin_user)
):
    return crud.get_top_selling_products(db, month=month, limit=limit)

@router.get("/monthly-sales")
def get_sales_history(
    year: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: auth.User = Depends(auth.get_current_admin_user)
):
    return crud.get_monthly_sales(db, year=year)
