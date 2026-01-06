from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import models, schemas
from app.routers.auth import get_current_user

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
)

from app.core import cache

@router.get("/products", response_model=List[schemas.ProductResponse])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    products = db.query(models.Product).offset(skip).limit(limit).all()
    # Enrich with cache if needed, but for list sticking to DB or bulk cache
    # For simplicity, we just return DB, but individual SKU reads use Cache
    return products

@router.post("/products", response_model=schemas.ProductResponse)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_product = models.Product(
        sku=product.sku,
        name=product.name,
        description=product.description,
        base_price=product.base_price
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    if product.inventory:
        db_inventory = models.Inventory(
            product_id=db_product.id,
            quantity=product.inventory.quantity,
            bulk_pricing_tiers=product.inventory.bulk_pricing_tiers
        )
        db.add(db_inventory)
        db.commit()
        db.refresh(db_product) # Refresh to load relationship
        
    return db_product

@router.get("/products/{sku}", response_model=schemas.ProductResponse)
def read_product(sku: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Check cache for inventory quantity
    cached_qty = cache.get_inventory_cache(sku)
    
    product = db.query(models.Product).filter(models.Product.sku == sku).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # If cache exists, override DB value (assuming cache is source of truth for high frequency)
    if cached_qty is not None and product.inventory:
        product.inventory.quantity = int(cached_qty)
        
    return product

@router.put("/products/{sku}/inventory", response_model=schemas.ProductResponse)
def update_inventory(sku: str, inventory: schemas.InventoryBase, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    product = db.query(models.Product).filter(models.Product.sku == sku).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
        
    if product.inventory:
        product.inventory.quantity = inventory.quantity
        product.inventory.bulk_pricing_tiers = inventory.bulk_pricing_tiers
    else:
        db_inventory = models.Inventory(
            product_id=product.id,
            quantity=inventory.quantity,
            bulk_pricing_tiers=inventory.bulk_pricing_tiers
        )
        db.add(db_inventory)
        
    db.commit()
    db.refresh(product)
    
    # Update Cache
    cache.set_inventory_cache(sku, inventory.quantity)
    
    return product
