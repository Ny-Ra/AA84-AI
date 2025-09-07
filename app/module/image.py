import os
import base64
import io
import logging
from fastapi import UploadFile, HTTPException
from fastapi.responses import JSONResponse
import anthropic
from PIL import Image

logger = logging.getLogger(__name__)

def get_anthropic_client():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
    return anthropic.Anthropic(api_key=api_key)

async def describe_image(file: UploadFile):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Le fichier doit être une image")
    
    try:
        contents = await file.read()
        
        try:
            image = Image.open(io.BytesIO(contents))
            image.verify()
        except Exception:
            raise HTTPException(status_code=400, detail="Format d'image invalide")
        
        base64_image = base64.b64encode(contents).decode('utf-8')
        
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
                                "media_type": file.content_type,
                                "data": base64_image,
                            },
                        },
                        {
                            "type": "text",
                            "text": "Décris en détail ce que tu vois dans cette image en français."
                        }
                    ],
                }
            ],
        )
        
        description = message.content[0].text
        
        return JSONResponse(content={
            "description": description,
            "filename": file.filename,
            "content_type": file.content_type
        })
        
    except anthropic.APIError as e:
        logger.error(f"Erreur API Anthropic: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de l'analyse de l'image")
    except Exception as e:
        logger.error(f"Erreur inattendue: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")