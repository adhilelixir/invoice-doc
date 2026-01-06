import os
import shutil
from pathlib import Path
from typing import Optional, BinaryIO
from datetime import datetime
import hashlib
from PIL import Image
import io


class StorageService:
    """
    File storage abstraction for template assets.
    Supports local file system storage with optional future support for cloud storage.
    """
    
    def __init__(self, base_path: str = "uploads"):
        self.base_path = Path(base_path)
        self.assets_path = self.base_path / "assets"
        self.documents_path = self.base_path / "documents"
        self.temp_path = self.base_path / "temp"
        
        # Create directories if they don't exist
        self.assets_path.mkdir(parents=True, exist_ok=True)
        self.documents_path.mkdir(parents=True, exist_ok=True)
        self.temp_path.mkdir(parents=True, exist_ok=True)
    
    def save_asset(
        self,
        file: BinaryIO,
        filename: str,
        asset_type: str = "image",
        optimize: bool = True
    ) -> dict:
        """
        Save an uploaded asset (logo, image, etc.)
        
        Args:
            file: File-like object with read() method
            filename: Original filename
            asset_type: Type of asset (logo, image, signature, watermark)
            optimize: Whether to optimize images
            
        Returns:
            dict with file_path, file_size, mime_type, width, height
        """
        # Generate unique filename using hash
        file_content = file.read()
        file_hash = hashlib.md5(file_content).hexdigest()[:12]
        file_ext = Path(filename).suffix.lower()
        
        # Validate file extension
        allowed_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp'}
        if file_ext not in allowed_extensions:
            raise ValueError(f"File type {file_ext} not allowed. Allowed: {allowed_extensions}")
        
        # Create subdirectory for asset type
        type_dir = self.assets_path / asset_type
        type_dir.mkdir(exist_ok=True)
        
        # Generate final filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"{timestamp}_{file_hash}{file_ext}"
        file_path = type_dir / unique_filename
        
        # Process image
        metadata = {
            "file_path": str(file_path),
            "file_size": len(file_content),
            "mime_type": self._get_mime_type(file_ext)
        }
        
        # Save and optionally optimize
        if optimize and file_ext in {'.png', '.jpg', '.jpeg', '.webp'}:
            img = Image.open(io.BytesIO(file_content))
            
            # Store original dimensions
            metadata["width"], metadata["height"] = img.size
            
            # Optimize image
            if img.mode in ("RGBA", "LA"):
                # Keep transparency
                img.save(file_path, optimize=True, quality=85)
            else:
                # Convert to RGB for better compression
                rgb_img = img.convert("RGB")
                rgb_img.save(file_path, optimize=True, quality=85)
        else:
            # Save without optimization (SVG, GIF, etc.)
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            # Try to get dimensions
            try:
                img = Image.open(io.BytesIO(file_content))
                metadata["width"], metadata["height"] = img.size
            except:
                metadata["width"], metadata["height"] = None, None
        
        return metadata
    
    def save_document(self, pdf_content: bytes, filename: str) -> str:
        """
        Save a generated PDF document
        
        Args:
            pdf_content: PDF file content as bytes
            filename: Desired filename
            
        Returns:
            str: Path to saved document
        """
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_hash = hashlib.md5(pdf_content).hexdigest()[:8]
        safe_filename = Path(filename).stem
        unique_filename = f"{safe_filename}_{timestamp}_{file_hash}.pdf"
        
        file_path = self.documents_path / unique_filename
        
        with open(file_path, 'wb') as f:
            f.write(pdf_content)
        
        return str(file_path)
    
    def get_asset(self, file_path: str) -> bytes:
        """Read and return asset file content"""
        with open(file_path, 'rb') as f:
            return f.read()
    
    def delete_asset(self, file_path: str) -> bool:
        """Delete an asset file"""
        try:
            os.remove(file_path)
            return True
        except FileNotFoundError:
            return False
    
    def get_asset_url(self, file_path: str) -> str:
        """
        Generate URL for asset access.
        In production, this would return a CDN or cloud storage URL.
        """
        # For local development, return relative path
        return f"/api/v1/assets/{Path(file_path).name}"
    
    def _get_mime_type(self, file_ext: str) -> str:
        """Map file extension to MIME type"""
        mime_types = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.svg': 'image/svg+xml',
            '.webp': 'image/webp'
        }
        return mime_types.get(file_ext.lower(), 'application/octet-stream')
    
    def optimize_image(
        self,
        file_path: str,
        max_width: Optional[int] = None,
        max_height: Optional[int] = None,
        quality: int = 85
    ) -> None:
        """
        Optimize an existing image file
        
        Args:
            file_path: Path to image file
            max_width: Maximum width (maintains aspect ratio)
            max_height: Maximum height (maintains aspect ratio)
            quality: JPEG quality (1-100)
        """
        img = Image.open(file_path)
        
        # Resize if dimensions specified
        if max_width or max_height:
            img.thumbnail((max_width or img.width, max_height or img.height), Image.Resampling.LANCZOS)
        
        # Save optimized
        if img.mode in ("RGBA", "LA"):
            img.save(file_path, optimize=True, quality=quality)
        else:
            rgb_img = img.convert("RGB")
            rgb_img.save(file_path, optimize=True, quality=quality)


# Global storage service instance
storage_service = StorageService()
