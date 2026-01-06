
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "B2B Document & Inventory Nexus"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "postgresql://user:invoice_doc@localhost:5435/invoice_doc"
    SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Upload and Storage Settings
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10 MB
    ALLOWED_IMAGE_TYPES: list = [".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"]
    
    # PDF Generation Settings
    DEFAULT_FONT_FAMILY: str = "Inter, -apple-system, BlinkMacSystemFont, sans-serif"
    PDF_PAGE_SIZE: str = "A4"  # A4, Letter, Legal
    
    class Config:
        env_file = ".env"

settings = Settings()
