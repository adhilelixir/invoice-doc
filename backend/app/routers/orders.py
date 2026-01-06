from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import models, schemas
from app.routers.auth import get_current_user

router = APIRouter(
    prefix="/orders",
    tags=["orders"],
)

class OrderResponse(schemas.BaseModel):
    id: int
    external_order_id: str
    total_amount: float
    status: str
    customer_name: str

    class Config:
        from_attributes = True

@router.get("/", response_model=List[OrderResponse])
def read_orders(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    orders = db.query(models.Order).offset(skip).limit(limit).all()
    return [
        OrderResponse(
            id=o.id,
            external_order_id=o.external_order_id,
            total_amount=o.total_amount,
            status=o.status,
            customer_name=o.customer.full_name if o.customer else "Unknown"
        )
        for o in orders
    ]
