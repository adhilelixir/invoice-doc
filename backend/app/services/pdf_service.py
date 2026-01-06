from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import os

# Create a simple template loader
# In a real app, this should probably point to a templates directory
template_env = Environment(loader=FileSystemLoader("app/templates"))

def generate_pdf_from_html(html_content: str) -> bytes:
    return HTML(string=html_content).write_pdf()

def render_template(template_name: str, context: dict) -> str:
    # Ensure templates directory exists or handle it
    # For now, we'll return a basic HTML string if template not found
    try:
        template = template_env.get_template(template_name)
        return template.render(context)
    except Exception:
        # Fallback for testing without template files
        return f"<html><body><h1>Document for {context.get('customer_name', 'Customer')}</h1><p>Total: {context.get('total_amount', 0)}</p></body></html>"

def create_invoice_pdf(invoice_data: dict) -> bytes:
    html = render_template("invoice.html", invoice_data)
    return generate_pdf_from_html(html)

def create_agreement_pdf(agreement_data: dict) -> bytes:
    html = render_template("agreement.html", agreement_data)
    return generate_pdf_from_html(html)
