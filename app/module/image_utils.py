import io
from PIL import Image
from typing import Tuple, Optional

def compress_image(
    image_bytes: bytes,
    max_size: Tuple[int, int] = (1568, 1568),
    quality: int = 85,
    max_file_size_mb: float = 5.0
) -> Tuple[bytes, str]:
    """
    Compress an image to optimize sending to Claude.
    
    Args:
        image_bytes: Original image bytes
        max_size: Maximum size (width, height) in pixels
        quality: JPEG compression quality (1-100)
        max_file_size_mb: Maximum file size in MB
        
    Returns:
        Tuple (compressed bytes, content_type)
    """
    with Image.open(io.BytesIO(image_bytes)) as img:
        # Convert RGBA to RGB if necessary
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize if image is too large
        if img.width > max_size[0] or img.height > max_size[1]:
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Progressively compress until reaching target size
        output = io.BytesIO()
        current_quality = quality
        max_file_size_bytes = max_file_size_mb * 1024 * 1024
        
        while current_quality > 10:
            output.seek(0)
            output.truncate()
            img.save(output, format='JPEG', quality=current_quality, optimize=True)
            
            if output.tell() <= max_file_size_bytes:
                break
                
            current_quality -= 10
        
        output.seek(0)
        return output.read(), "image/jpeg"

def get_image_info(image_bytes: bytes) -> dict:
    """
    Get information about an image.
    
    Args:
        image_bytes: Image bytes
        
    Returns:
        Dict with image information
    """
    with Image.open(io.BytesIO(image_bytes)) as img:
        return {
            "width": img.width,
            "height": img.height,
            "mode": img.mode,
            "format": img.format,
            "size_bytes": len(image_bytes),
            "size_mb": round(len(image_bytes) / (1024 * 1024), 2)
        }

def should_compress(image_bytes: bytes, threshold_mb: float = 1.0) -> bool:
    """
    Determine if an image should be compressed.
    
    Args:
        image_bytes: Image bytes
        threshold_mb: Threshold in MB above which to compress
        
    Returns:
        True if the image should be compressed
    """
    size_mb = len(image_bytes) / (1024 * 1024)
    
    with Image.open(io.BytesIO(image_bytes)) as img:
        return (
            size_mb > threshold_mb or
            img.width > 2000 or 
            img.height > 2000 or
            img.format not in ['JPEG', 'JPG']
        )