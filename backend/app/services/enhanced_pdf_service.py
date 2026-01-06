from jinja2 import Environment, FileSystemLoader, Template
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
import os
import base64
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
import qrcode
from io import BytesIO
from app.core.config import settings


class EnhancedPDFService:
    """
    Advanced PDF generation service with support for:
    - Image and logo embedding
    - Custom fonts and styling
    - QR codes
    - Watermarks
    - Rich HTML templates
    """
    
    def __init__(self, templates_dir: str = "app/templates"):
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=True
        )
        
        # Add custom filters
        self.jinja_env.filters['b64encode'] = self._b64_encode_filter
        self.jinja_env.filters['format_currency'] = self._format_currency
        self.jinja_env.filters['format_date'] = self._format_date
        
        # Font configuration for WeasyPrint
        self.font_config = FontConfiguration()
    
    def generate_pdf(
        self,
        template_name: Optional[str] = None,
        html_content: Optional[str] = None,
        context: Dict[str, Any] = None,
        css_content: Optional[str] = None,
        assets: Optional[List[Dict[str, Any]]] = None,
        branding_config: Optional[Dict[str, Any]] = None,
        include_qr: bool = False,
        qr_data: Optional[str] = None,
        watermark_text: Optional[str] = None
    ) -> bytes:
        """
        Generate PDF from template or HTML content
        
        Args:
            template_name: Name of Jinja2 template file
            html_content: Direct HTML content (if not using template)
            context: Template variables
            css_content: Custom CSS styling
            assets: List of asset dictionaries with file_path, type, etc.
            branding_config: Branding configuration (colors, fonts, logo position)
            include_qr: Whether to include QR code
            qr_data: Data to encode in QR code
            watermark_text: Optional watermark text
            
        Returns:
            bytes: PDF content
        """
        context = context or {}
        branding_config = branding_config or {}
        
        # Process assets (logos, images) and convert to base64 for embedding
        if assets:
            context['assets'] = self._process_assets(assets)
        
        # Generate QR code if requested
        if include_qr and qr_data:
            context['qr_code'] = self._generate_qr_code(qr_data)
        
        # Add branding configuration to context
        context['branding'] = self._get_branding_config(branding_config)
        
        # Add watermark if specified
        if watermark_text or branding_config.get('show_watermark'):
            context['watermark'] = watermark_text or branding_config.get('watermark_text', 'DRAFT')
        
        # Render HTML
        if template_name:
            html = self._render_template(template_name, context)
        elif html_content:
            # Render HTML content as Jinja2 template
            template = Template(html_content)
            html = template.render(context)
        else:
            raise ValueError("Either template_name or html_content must be provided")
        
        # Generate CSS
        css = self._generate_css(branding_config, css_content)
        
        # Generate PDF
        pdf_bytes = self._html_to_pdf(html, css)
        
        return pdf_bytes
    
    def _process_assets(self, assets: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Convert asset file paths to base64 encoded data URLs"""
        processed = {}
        
        for asset in assets:
            asset_type = asset.get('asset_type', 'image')
            file_path = asset.get('file_path')
            
            if not file_path or not os.path.exists(file_path):
                continue
            
            # Read and encode file
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            mime_type = asset.get('mime_type', 'image/png')
            base64_data = base64.b64encode(file_content).decode('utf-8')
            data_url = f"data:{mime_type};base64,{base64_data}"
            
            # Store by type (logo, signature, etc.)
            if asset_type == 'logo' or asset.get('is_default'):
                processed['logo'] = {
                    'data_url': data_url,
                    'width': asset.get('width'),
                    'height': asset.get('height'),
                    'display_config': asset.get('display_config', {})
                }
            else:
                # Store in images list
                if 'images' not in processed:
                    processed['images'] = []
                processed['images'].append({
                    'data_url': data_url,
                    'name': asset.get('name'),
                    'width': asset.get('width'),
                    'height': asset.get('height')
                })
        
        return processed
    
    def _generate_qr_code(self, data: str, size: int = 150) -> str:
        """Generate QR code and return as base64 data URL"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_bytes = buffer.getvalue()
        base64_data = base64.b64encode(img_bytes).decode('utf-8')
        
        return f"data:image/png;base64,{base64_data}"
    
    def _get_branding_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get branding configuration with defaults"""
        return {
            'primary_color': config.get('primary_color', '#1E40AF'),
            'secondary_color': config.get('secondary_color', '#64748B'),
            'accent_color': config.get('accent_color', '#F59E0B'),
            'font_family': config.get('font_family', settings.DEFAULT_FONT_FAMILY),
            'logo_position': config.get('logo_position', 'header-left'),
            'logo_width': config.get('logo_width', 150),
        }
    
    def _generate_css(self, branding_config: Dict[str, Any], custom_css: Optional[str] = None) -> str:
        """Generate CSS with branding and custom styles"""
        branding = self._get_branding_config(branding_config)
        
        base_css = f"""
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        @page {{
            size: {settings.PDF_PAGE_SIZE};
            margin: 2cm;
            
            @bottom-right {{
                content: "Page " counter(page) " of " counter(pages);
                font-size: 9pt;
                color: #64748B;
            }}
        }}
        
        body {{
            font-family: {branding['font_family']};
            font-size: 11pt;
            line-height: 1.6;
            color: #1E293B;
        }}
        
        .header {{
            margin-bottom: 2rem;
            padding-bottom: 1rem;
            border-bottom: 2px solid {branding['primary_color']};
        }}
        
        .logo {{
            max-width: {branding['logo_width']}px;
            height: auto;
        }}
        
        h1, h2, h3, h4, h5, h6 {{
            color: {branding['primary_color']};
            margin-top: 1.5rem;
            margin-bottom: 0.75rem;
            font-weight: 600;
        }}
        
        h1 {{ font-size: 24pt; }}
        h2 {{ font-size: 18pt; }}
        h3 {{ font-size: 14pt; }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1.5rem 0;
        }}
        
        th, td {{
            padding: 0.75rem;
            text-align: left;
            border-bottom: 1px solid #E2E8F0;
        }}
        
        th {{
            background-color: #F1F5F9;
            color: {branding['primary_color']};
            font-weight: 600;
        }}
        
        .total-row {{
            background-color: #F8FAFC;
            font-weight: 600;
            font-size: 12pt;
        }}
        
        .highlight {{
            background-color: {branding['accent_color']}20;
            padding: 1rem;
            border-left: 4px solid {branding['accent_color']};
            margin: 1rem 0;
        }}
        
        .footer {{
            margin-top: 3rem;
            padding-top: 1rem;
            border-top: 1px solid #E2E8F0;
            font-size: 9pt;
            color: #64748B;
        }}
        
        .watermark {{
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) rotate(-45deg);
            font-size: 72pt;
            font-weight: 700;
            color: rgba(0, 0, 0, 0.05);
            z-index: -1;
            white-space: nowrap;
            pointer-events: none;
        }}
        
        .qr-code {{
            max-width: 150px;
            height: auto;
        }}
        
        .text-right {{ text-align: right; }}
        .text-center {{ text-align: center; }}
        .mt-4 {{ margin-top: 2rem; }}
        .mb-4 {{ margin-bottom: 2rem; }}
        """
        
        # Add custom CSS if provided
        if custom_css:
            base_css += f"\n\n/* Custom CSS */\n{custom_css}"
        
        return base_css
    
    def _render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render Jinja2 template with context"""
        try:
            template = self.jinja_env.get_template(template_name)
            return template.render(context)
        except Exception as e:
            raise ValueError(f"Template rendering failed: {str(e)}")
    
    def _html_to_pdf(self, html: str, css: str) -> bytes:
        """Convert HTML and CSS to PDF bytes"""
        html_doc = HTML(string=html)
        css_doc = CSS(string=css, font_config=self.font_config)
        
        pdf_bytes = html_doc.write_pdf(
            stylesheets=[css_doc],
            font_config=self.font_config
        )
        
        return pdf_bytes
    
    # Custom Jinja2 filters
    def _b64_encode_filter(self, value: bytes) -> str:
        """Base64 encode filter for templates"""
        return base64.b64encode(value).decode('utf-8')
    
    def _format_currency(self, value: float, currency: str = "USD") -> str:
        """Format currency filter"""
        symbols = {'USD': '$', 'EUR': '€', 'GBP': '£', 'INR': '₹'}
        symbol = symbols.get(currency, currency)
        return f"{symbol}{value:,.2f}"
    
    def _format_date(self, value: datetime, format_str: str = "%B %d, %Y") -> str:
        """Format date filter"""
        if isinstance(value, str):
            value = datetime.fromisoformat(value.replace('Z', '+00:00'))
        return value.strftime(format_str)


# Global PDF service instance
pdf_service = EnhancedPDFService()
