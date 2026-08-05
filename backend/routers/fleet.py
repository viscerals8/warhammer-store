from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
import schemas, crud, models, auth
from database import get_db

router = APIRouter(prefix="/fleet", tags=["fleet"])

@router.get("/zones", response_model=List[schemas.DeliveryZoneResponse])
def list_zones(db: Session = Depends(get_db)):
    return crud.get_delivery_zones(db)

@router.get("/vehicles", response_model=List[schemas.VehicleResponse])
def list_vehicles(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_admin_user)
):
    return crud.get_vehicles(db)
