from fastapi import APIRouter, UploadFile, File
from module.image import describe_image

router = APIRouter(prefix="/api", tags=["image"])

@router.post("/describe-image")
async def describe_image_endpoint(file: UploadFile = File(...)):
    return await describe_image(file)