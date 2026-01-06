from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.services import pdf_service

router = APIRouter(
    prefix="/integrations",
    tags=["integrations"],
)

def process_new_order(order_id: int, db: Session):
    # This might be a background task
    # 1. Generate Agreement
    # 2. Email Customer?
    pass

@router.post("/webhook", status_code=200)
async def handle_webhook(payload: schemas.WebhookPayload, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    if payload.event == "order.created":
        order_data = payload.data
        # Create order in our DB
        # Check if user exists or create one
        customer_email = order_data.get("customer_email")
        customer = db.query(models.User).filter(models.User.email == customer_email).first()
        if not customer:
            customer = models.User(email=customer_email, hashed_password="placeholder", full_name=order_data.get("customer_name"), role="customer")
            db.add(customer)
            db.commit()
            db.refresh(customer)
        
        # Create Order
        new_order = models.Order(
            customer_id=customer.id,
            external_order_id=str(order_data.get("id")),
            total_amount=order_data.get("total_price"),
            status="pending"
        )
        db.add(new_order)
        db.commit()
        db.refresh(new_order)
        
        # Add items and decrement inventory (simplified)
        for item in order_data.get("items", []):
            product = db.query(models.Product).filter(models.Product.sku == item.get("sku")).first()
            if product:
                order_item = models.OrderItem(
                    order_id=new_order.id,
                    product_sku=product.sku,
                    quantity=item.get("quantity"),
                    unit_price=item.get("price")
                )
                db.add(order_item)
                
                # Decrement inventory
                if product.inventory:
                    product.inventory.quantity -= item.get("quantity")
                    
        db.commit()
        
        # Trigger background processing
        background_tasks.add_task(process_new_order, new_order.id, db)
        
    return {"status": "received"}
