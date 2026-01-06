from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    is_active: Optional[bool] = True
    role: str = "customer"

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Product/Inventory Schemas
class InventoryBase(BaseModel):
    quantity: int = 0
    bulk_pricing_tiers: Optional[List[Dict[str, Any]]] = None

class ProductBase(BaseModel):
    sku: str
    name: str
    description: Optional[str] = None
    base_price: float

class ProductCreate(ProductBase):
    inventory: Optional[InventoryBase] = None

class ProductResponse(ProductBase):
    id: int
    inventory: Optional[InventoryBase] = None

    class Config:
        from_attributes = True

# Invoice/Document Schemas
class InvoiceBase(BaseModel):
    invoice_number: str
    due_date: datetime
    status: str

class InvoiceCreate(InvoiceBase):
    template_id: Optional[int] = None
    document_metadata: Optional[Dict[str, Any]] = None

class InvoiceResponse(InvoiceBase):
    id: int
    pdf_url: Optional[str] = None
    issued_at: datetime
    template_id: Optional[int] = None
    document_metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

class AgreementBase(BaseModel):
    agreement_text: str
    version: int = 1

class AgreementCreate(AgreementBase):
    template_id: Optional[int] = None
    document_metadata: Optional[Dict[str, Any]] = None

class AgreementResponse(AgreementBase):
    id: int
    pdf_url: Optional[str] = None
    signed_at: Optional[datetime] = None
    template_id: Optional[int] = None
    document_metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

# Webhook Schemas
class WebhookPayload(BaseModel):
    event: str # "order.created", "order.paid", etc.
    data: Dict[str, Any]
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class DocumentTypeEnum(str, Enum):
    """Document types"""
    INVOICE = "invoice"
    AGREEMENT = "agreement"
    QUOTE = "quote"
    RECEIPT = "receipt"
    PURCHASE_ORDER = "purchase_order"
    DELIVERY_NOTE = "delivery_note"


class AssetTypeEnum(str, Enum):
    """Asset types"""
    LOGO = "logo"
    IMAGE = "image"
    SIGNATURE = "signature"
    WATERMARK = "watermark"


# Template Metadata Schemas
class TemplateMetadataBase(BaseModel):
    key: str
    value: Optional[str] = None
    data_type: str = "string"
    label: Optional[str] = None
    description: Optional[str] = None
    is_required: bool = False
    default_value: Optional[str] = None
    validation_rules: Optional[Dict[str, Any]] = None
    display_order: int = 0


class TemplateMetadataCreate(TemplateMetadataBase):
    pass


class TemplateMetadataUpdate(BaseModel):
    value: Optional[str] = None
    label: Optional[str] = None
    description: Optional[str] = None
    is_required: Optional[bool] = None
    default_value: Optional[str] = None
    validation_rules: Optional[Dict[str, Any]] = None
    display_order: Optional[int] = None


class TemplateMetadataResponse(TemplateMetadataBase):
    id: int
    template_id: int

    class Config:
        from_attributes = True


# Template Asset Schemas
class TemplateAssetBase(BaseModel):
    asset_type: AssetTypeEnum
    name: str
    description: Optional[str] = None
    display_config: Optional[Dict[str, Any]] = None
    is_default: bool = False


class TemplateAssetCreate(TemplateAssetBase):
    # File will be uploaded separately
    pass


class TemplateAssetUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    display_config: Optional[Dict[str, Any]] = None
    is_default: Optional[bool] = None


class TemplateAssetResponse(TemplateAssetBase):
    id: int
    template_id: int
    file_path: str
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Document Template Schemas
class BrandingConfig(BaseModel):
    """Configuration for template branding"""
    primary_color: Optional[str] = "#1E40AF"
    secondary_color: Optional[str] = "#64748B"
    accent_color: Optional[str] = "#F59E0B"
    font_family: Optional[str] = "Inter, sans-serif"
    logo_position: Optional[str] = "header-left"  # header-left, header-center, header-right
    logo_width: Optional[int] = 150  # pixels
    show_watermark: bool = False
    watermark_text: Optional[str] = None


class TemplateVariable(BaseModel):
    """Definition of a template variable"""
    name: str
    description: str
    example: str
    data_type: str = "string"
    required: bool = False


class DocumentTemplateBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    document_type: DocumentTypeEnum


class DocumentTemplateCreate(DocumentTemplateBase):
    html_content: str = Field(..., min_length=1)
    css_content: Optional[str] = None
    variables: Optional[List[TemplateVariable]] = None
    default_metadata: Optional[Dict[str, Any]] = None
    branding_config: Optional[BrandingConfig] = None


class DocumentTemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    html_content: Optional[str] = None
    css_content: Optional[str] = None
    variables: Optional[List[TemplateVariable]] = None
    default_metadata: Optional[Dict[str, Any]] = None
    branding_config: Optional[BrandingConfig] = None
    is_active: Optional[bool] = None


class DocumentTemplateResponse(DocumentTemplateBase):
    id: int
    html_content: str
    css_content: Optional[str] = None
    variables: Optional[List[TemplateVariable]] = None
    default_metadata: Optional[Dict[str, Any]] = None
    branding_config: Optional[BrandingConfig] = None
    version: int
    is_active: bool
    parent_template_id: Optional[int] = None
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Include related data
    assets: List[TemplateAssetResponse] = []
    metadata_fields: List[TemplateMetadataResponse] = []

    class Config:
        from_attributes = True


class DocumentTemplateListResponse(BaseModel):
    """Simplified response for list views"""
    id: int
    name: str
    title: str
    description: Optional[str] = None
    document_type: DocumentTypeEnum
    version: int
    is_active: bool
    created_at: datetime
    asset_count: int = 0

    class Config:
        from_attributes = True


# Document Generation Schemas
class DocumentGenerationRequest(BaseModel):
    """Request to generate a document from a template"""
    template_id: int
    data: Dict[str, Any]  # Template variable values
    metadata: Optional[Dict[str, Any]] = None
    output_filename: Optional[str] = None


class DocumentGenerationResponse(BaseModel):
    """Response after generating a document"""
    success: bool
    pdf_url: Optional[str] = None
    pdf_size: Optional[int] = None
    message: Optional[str] = None
    document_id: Optional[int] = None  # ID of created Invoice/Agreement if applicable
