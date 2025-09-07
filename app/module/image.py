import os
import base64
import io
import logging
from fastapi import UploadFile, HTTPException
from fastapi.responses import JSONResponse
import anthropic
from PIL import Image
from .image_utils import compress_image, get_image_info, should_compress

logger = logging.getLogger(__name__)

def get_anthropic_client():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
    return anthropic.Anthropic(api_key=api_key)

async def describe_image(file: UploadFile):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        contents = await file.read()
        
        try:
            image = Image.open(io.BytesIO(contents))
            image.verify()
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid image format")
        
        # Get original image information
        original_info = get_image_info(contents)
        logger.info(f"Image originale: {original_info}")
        
        # Compress if necessary
        processed_contents = contents
        processed_content_type = file.content_type
        
        if should_compress(contents):
            logger.info("Compressing image...")
            processed_contents, processed_content_type = compress_image(contents)
            compressed_info = get_image_info(processed_contents)
            logger.info(f"Image compressée: {compressed_info}")
        
        base64_image = base64.b64encode(processed_contents).decode('utf-8')
        
        client = get_anthropic_client()
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": processed_content_type,
                                "data": base64_image,
                            },
                        },
                        {
                            "type": "text",
                            "text": "Describe in detail what you see in this image."
                        }
                    ],
                }
            ],
        )
        
        description = message.content[0].text
        
        response_data = {
            "description": description,
            "filename": file.filename,
            "content_type": file.content_type,
            "original_size_mb": original_info["size_mb"]
        }
        
        if should_compress(contents):
            response_data["compressed_size_mb"] = compressed_info["size_mb"]
            response_data["compression_ratio"] = round(
                (1 - compressed_info["size_bytes"] / original_info["size_bytes"]) * 100, 1
            )
        
        return JSONResponse(content=response_data)
        
    except anthropic.APIError as e:
        logger.error(f"Anthropic API error: {e}")
        raise HTTPException(status_code=500, detail="Error analyzing image")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")