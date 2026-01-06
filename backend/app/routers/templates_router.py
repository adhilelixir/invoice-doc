from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Response
from sqlalchemy.orm import Session
from typing import List, Optional
import json
from app.database import get_db
from app import models
from app.schemas import (
    DocumentTemplateCreate,
    DocumentTemplateUpdate,
    DocumentTemplateResponse,
    DocumentTemplateListResponse,
    TemplateAssetCreate,
    TemplateAssetResponse,
    TemplateAssetUpdate,
    DocumentGenerationRequest,
    DocumentGenerationResponse
)
from app.routers.auth import get_current_user
from app.services.storage_service import storage_service
from app.services.enhanced_pdf_service import pdf_service


router = APIRouter(
    prefix="/templates",
    tags=["templates"],
)


@router.post("/", response_model=DocumentTemplateResponse, status_code=201)
def create_template(
    template: DocumentTemplateCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Create a new document template"""
    
    # Create template
    db_template = models.DocumentTemplate(
        name=template.name,
        title=template.title,
        description=template.description,
        document_type=template.document_type.value,
        html_content=template.html_content,
        css_content=template.css_content,
        variables=template.variables if template.variables else [],
        default_metadata=template.default_metadata,
        branding_config=template.branding_config.dict() if template.branding_config else {},
        created_by=current_user.id
    )
    
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    
    return db_template


@router.get("/", response_model=List[DocumentTemplateListResponse])
def list_templates(
    document_type: Optional[str] = None,
    is_active: Optional[bool] = True,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """List all document templates with optional filtering"""
    
    query = db.query(models.DocumentTemplate)
    
    if document_type:
        query = query.filter(models.DocumentTemplate.document_type == document_type)
    
    if is_active is not None:
        query = query.filter(models.DocumentTemplate.is_active == is_active)
    
    templates = query.offset(skip).limit(limit).all()
    
    # Create simplified response with asset count
    result = []
    for template in templates:
        result.append(DocumentTemplateListResponse(
            id=template.id,
            name=template.name,
            title=template.title,
            description=template.description,
            document_type=template.document_type,
            version=template.version,
            is_active=template.is_active,
            created_at=template.created_at,
            asset_count=len(template.assets)
        ))
    
    return result


@router.get("/{template_id}", response_model=DocumentTemplateResponse)
def get_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get a specific template by ID"""
    
    template = db.query(models.DocumentTemplate).filter(models.DocumentTemplate.id == template_id).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return template


@router.put("/{template_id}", response_model=DocumentTemplateResponse)
def update_template(
    template_id: int,
    template_update: DocumentTemplateUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Update an existing template"""
    
    db_template = db.query(models.DocumentTemplate).filter(models.DocumentTemplate.id == template_id).first()
    
    if not db_template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Update fields
    update_data = template_update.dict(exclude_unset=True)
    
    if 'branding_config' in update_data and update_data['branding_config']:
        update_data['branding_config'] = update_data['branding_config'].dict()
    
    for field, value in update_data.items():
        setattr(db_template, field, value)
    
    db.commit()
    db.refresh(db_template)
    
    return db_template


@router.delete("/{template_id}", status_code=204)
def delete_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Delete a template (soft delete by setting is_active=False)"""
    
    db_template = db.query(models.DocumentTemplate).filter(models.DocumentTemplate.id == template_id).first()
    
    if not db_template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Soft delete
    db_template.is_active = False
    db.commit()
    
    return Response(status_code=204)


@router.post("/{template_id}/duplicate", response_model=DocumentTemplateResponse, status_code=201)
def duplicate_template(
    template_id: int,
    new_name: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Duplicate an existing template"""
    
    original = db.query(models.DocumentTemplate).filter(models.DocumentTemplate.id == template_id).first()
    
    if not original:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Create duplicate
    duplicate = models.DocumentTemplate(
        name=new_name,
        title=f"{original.title} (Copy)",
        description=original.description,
        document_type=original.document_type,
        html_content=original.html_content,
        css_content=original.css_content,
        variables=original.variables,
        default_metadata=original.default_metadata,
        branding_config=original.branding_config,
        created_by=current_user.id
    )
    
    db.add(duplicate)
    db.commit()
    db.refresh(duplicate)
    
    return duplicate


# Asset Management Endpoints
@router.post("/{template_id}/assets", response_model=TemplateAssetResponse, status_code=201)
async def upload_asset(
    template_id: int,
    file: UploadFile = File(...),
    asset_type: str = Form(...),
    name: str = Form(...),
    description: Optional[str] = Form(None),
    is_default: bool = Form(False),
    display_config: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Upload an asset (logo, image, signature) for a template"""
    
    # Verify template exists
    template = db.query(models.DocumentTemplate).filter(models.DocumentTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Validate asset type
    try:
        models.AssetType(asset_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid asset type: {asset_type}")
    
    # Save file
    try:
        file_metadata = storage_service.save_asset(
            file=file.file,
            filename=file.filename,
            asset_type=asset_type,
            optimize=True
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Parse display config if provided
    display_config_dict = None
    if display_config:
        try:
            display_config_dict = json.loads(display_config)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid display_config JSON")
    
    # Create asset record
    db_asset = models.TemplateAsset(
        template_id=template_id,
        asset_type=asset_type,
        name=name,
        description=description,
        file_path=file_metadata['file_path'],
        file_size=file_metadata['file_size'],
        mime_type=file_metadata['mime_type'],
        width=file_metadata.get('width'),
        height=file_metadata.get('height'),
        display_config=display_config_dict,
        is_default=is_default
    )
    
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    
    return db_asset


@router.get("/{template_id}/assets", response_model=List[TemplateAssetResponse])
def list_assets(
    template_id: int,
    asset_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """List all assets for a template"""
    
    query = db.query(models.TemplateAsset).filter(models.TemplateAsset.template_id == template_id)
    
    if asset_type:
        query = query.filter(models.TemplateAsset.asset_type == asset_type)
    
    return query.all()


@router.delete("/{template_id}/assets/{asset_id}", status_code=204)
def delete_asset(
    template_id: int,
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Delete an asset"""
    
    asset = db.query(models.TemplateAsset).filter(
        models.TemplateAsset.id == asset_id,
        models.TemplateAsset.template_id == template_id
    ).first()
    
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    # Delete file from storage
    storage_service.delete_asset(asset.file_path)
    
    # Delete database record
    db.delete(asset)
    db.commit()
    
    return Response(status_code=204)


# Preview and Generation Endpoints
@router.post("/{template_id}/preview")
async def preview_template(
    template_id: int,
    data: dict,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Generate a preview PDF for a template with sample data"""
    
    template = db.query(models.DocumentTemplate).filter(models.DocumentTemplate.id == template_id).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    try:
        # Get template assets
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
        
        # Generate PDF
        pdf_bytes = pdf_service.generate_pdf(
            html_content=template.html_content,
            context=data,
            css_content=template.css_content,
            assets=assets_list,
            branding_config=template.branding_config or {},
            watermark_text="PREVIEW"
        )
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"inline; filename=preview_{template.name}.pdf"}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


@router.post("/generate", response_model=DocumentGenerationResponse)
async def generate_document(
    request: DocumentGenerationRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Generate a document from a template"""
    
    template = db.query(models.DocumentTemplate).filter(models.DocumentTemplate.id == request.template_id).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    try:
        # Get template assets
        assets = db.query(models.TemplateAsset).filter(models.TemplateAsset.template_id == request.template_id).all()
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
        
        # Generate PDF
        pdf_bytes = pdf_service.generate_pdf(
            html_content=template.html_content,
            context=request.data,
            css_content=template.css_content,
            assets=assets_list,
            branding_config=template.branding_config or {}
        )
        
        # Save PDF
        filename = request.output_filename or f"{template.name}_{template.document_type}"
        pdf_path = storage_service.save_document(pdf_bytes, filename)
        
        return DocumentGenerationResponse(
            success=True,
            pdf_url=pdf_path,
            pdf_size=len(pdf_bytes),
            message="Document generated successfully"
        )
    
    except Exception as e:
        return DocumentGenerationResponse(
            success=False,
            message=f"Document generation failed: {str(e)}"
        )
