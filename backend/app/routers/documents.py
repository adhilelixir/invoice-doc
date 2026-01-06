from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.routers.auth import get_current_user
from app.services.enhanced_pdf_service import pdf_service
from app.services.storage_service import storage_service

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
)

@router.post("/invoices/generate", response_model=schemas.InvoiceResponse)
def generate_invoice(
    order_id: int,
    template_id: int = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # 1. Fetch Order
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # 2. Check if invoice exists
    if order.invoice:
        return order.invoice

    # 3. Prepare invoice data
    invoice_data = {
        "customer_name": order.customer.full_name if order.customer else "Guest",
        "customer_email": order.customer.email if order.customer else "",
        "total_amount": order.total_amount,
        "subtotal": order.total_amount,  # Simplified, should calculate from items
        "items": [
            {
                "name": item.product_sku,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
            }
            for item in order.items
        ],
        "invoice_number": f"INV-{order.id}",
        "issue_date": order.created_at,
        "due_date": order.created_at,  # Should add logic for payment terms
        "currency": "USD",
    }
    
    # 4. Generate PDF using template or default
    try:
        if template_id:
            # Use specific template
            template = db.query(models.DocumentTemplate).filter(models.DocumentTemplate.id == template_id).first()
            if not template:
                raise HTTPException(status_code=404, detail="Template not found")
            
            # Get assets
            assets = db.query(models.TemplateAsset).filter(models.TemplateAsset.template_id == template_id).all()
            assets_list = [
                {
                    'asset_type': asset.asset_type,
                    'file_path': asset.file_path,
                    'mime_type': asset.mime_type,
                    'width': asset.width,
                    'height': asset.height,
                    'is_default': asset.is_default,
                    'display_config': asset.display_config or {}
                }
                for asset in assets
            ]
            
            pdf_bytes = pdf_service.generate_pdf(
                html_content=template.html_content,
                context=invoice_data,
                css_content=template.css_content,
                assets=assets_list,
                branding_config=template.branding_config or {}
            )
        else:
            # Use default template
            pdf_bytes = pdf_service.generate_pdf(
                template_name="invoice_modern.html",
                context=invoice_data
            )
        
        # 5. Save PDF
        pdf_path = storage_service.save_document(pdf_bytes, f"INV-{order.id}")
        pdf_url = f"/api/v1/documents/files/{pdf_path.split('/')[-1]}"
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")
    
    # 6. Create Invoice Record
    db_invoice = models.Invoice(
        order_id=order.id,
        invoice_number=f"INV-{order.id}",
        pdf_url=pdf_url,
        status="issued",
        template_id=template_id
    )
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)
    
    return db_invoice

@router.get("/invoices/{invoice_id}/download")
def download_invoice(invoice_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    invoice = db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
        
    # In a real app we'd fetch the file content from storage
    # Here we regenerate for demo purposes
    invoice_data = {
        "invoice_number": invoice.invoice_number,
        # ... fetch other data
    }
    pdf_bytes = pdf_service.create_invoice_pdf(invoice_data)
    
    return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=invoice_{invoice.invoice_number}.pdf"})
