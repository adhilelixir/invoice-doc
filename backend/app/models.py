from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    SALES_REP = "sales_rep"
    CUSTOMER = "customer"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    role = Column(String, default=UserRole.CUSTOMER)
    is_active = Column(Boolean, default=True)
    
    orders = relationship("Order", back_populates="customer")

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, index=True, nullable=False)
    description = Column(Text)
    base_price = Column(Float, nullable=False)
    
    inventory = relationship("Inventory", back_populates="product", uselist=False)

class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), unique=True)
    quantity = Column(Integer, default=0)
    bulk_pricing_tiers = Column(JSON) # e.g. [{"min": 1, "max": 100, "price": 10}, {"min": 101, "price": 8}]
    
    product = relationship("Product", back_populates="inventory")

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.id"))
    external_order_id = Column(String, unique=True, index=True) # ID from Shopify/WooCommerce
    status = Column(String, default="pending")
    total_amount = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    customer = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")
    invoice = relationship("Invoice", back_populates="order", uselist=False)
    agreement = relationship("Agreement", back_populates="order", uselist=False)

class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_sku = Column(String) # Store SKU in case product is deleted
    quantity = Column(Integer)
    unit_price = Column(Float)
    
    order = relationship("Order", back_populates="items")

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), unique=True)
    invoice_number = Column(String, unique=True, index=True)
    pdf_url = Column(String)
    issued_at = Column(DateTime(timezone=True), server_default=func.now())
    due_date = Column(DateTime(timezone=True))
    status = Column(String, default="issued") # issued, paid, overdue
    
    # Template and metadata support
    template_id = Column(Integer, nullable=True)  # References document_templates
    document_metadata = Column(JSON)  # Custom metadata for this document
    
    order = relationship("Order", back_populates="invoice")

class Agreement(Base):
    __tablename__ = "agreements"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), unique=True)
    agreement_text = Column(Text) # The full text or template reference
    pdf_url = Column(String)
    signed_at = Column(DateTime(timezone=True))
    version = Column(Integer, default=1)
    
    # Template and metadata support
    template_id = Column(Integer, nullable=True)  # References document_templates
    document_metadata = Column(JSON)  # Custom metadata for this document
    
    order = relationship("Order", back_populates="agreement")


# Template Management Models

class DocumentType(str, enum.Enum):
    """Supported document types"""
    INVOICE = "invoice"
    AGREEMENT = "agreement"
    QUOTE = "quote"
    RECEIPT = "receipt"
    PURCHASE_ORDER = "purchase_order"
    DELIVERY_NOTE = "delivery_note"


class AssetType(str, enum.Enum):
    """Asset file types"""
    LOGO = "logo"
    IMAGE = "image"
    SIGNATURE = "signature"
    WATERMARK = "watermark"


class DocumentTemplate(Base):
    """
    Document template with customizable layout, styling, and metadata.
    Supports versioning for tracking template changes over time.
    """
    __tablename__ = "document_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    title = Column(String, nullable=False)  # Display title
    description = Column(Text)
    document_type = Column(String, nullable=False)  # DocumentType enum value
    
    # Template content
    html_content = Column(Text, nullable=False)  # Jinja2 HTML template
    css_content = Column(Text)  # Custom CSS styling
    
    # Configuration
    variables = Column(JSON)  # List of available template variables with descriptions
    default_metadata = Column(JSON)  # Default metadata for documents created from this template
    
    # Branding configuration
    branding_config = Column(JSON)  # Logo position, colors, fonts, etc.
    
    # Version management
    version = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    parent_template_id = Column(Integer, ForeignKey("document_templates.id"), nullable=True)
    
    # Audit fields
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    assets = relationship("TemplateAsset", back_populates="template", cascade="all, delete-orphan")
    metadata_fields = relationship("TemplateMetadata", back_populates="template", cascade="all, delete-orphan")
    parent_template = relationship("DocumentTemplate", remote_side=[id], backref="versions")
    creator = relationship("User", foreign_keys=[created_by])


class TemplateAsset(Base):
    """
    Assets (logos, images, signatures) associated with templates.
    Stores file paths and metadata for embedded resources.
    """
    __tablename__ = "template_assets"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("document_templates.id"), nullable=False)
    
    # Asset details
    asset_type = Column(String, nullable=False)  # AssetType enum value
    name = Column(String, nullable=False)
    description = Column(Text)
    
    # File information
    file_path = Column(String, nullable=False)  # Path to file on disk or cloud storage
    file_size = Column(Integer)  # Size in bytes
    mime_type = Column(String)  # e.g., image/png, image/jpeg
    width = Column(Integer)  # Image width in pixels
    height = Column(Integer)  # Image height in pixels
    
    # Display configuration
    display_config = Column(JSON)  # Position, size, alignment, etc.
    
    # Metadata
    is_default = Column(Boolean, default=False)  # Default asset for this type
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    template = relationship("DocumentTemplate", back_populates="assets")


class TemplateMetadata(Base):
    """
    Flexible key-value metadata for templates.
    Allows custom fields without schema changes.
    """
    __tablename__ = "template_metadata"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("document_templates.id"), nullable=False)
    
    # Metadata fields
    key = Column(String, nullable=False, index=True)
    value = Column(Text)
    data_type = Column(String, default="string")  # string, number, date, boolean, json
    
    # Field configuration
    label = Column(String)  # Human-readable label
    description = Column(Text)
    is_required = Column(Boolean, default=False)
    default_value = Column(Text)
    validation_rules = Column(JSON)  # e.g., {"min": 0, "max": 100, "pattern": "regex"}
    
    # Display order
    display_order = Column(Integer, default=0)
    
    # Relationships
    template = relationship("DocumentTemplate", back_populates="metadata_fields")
