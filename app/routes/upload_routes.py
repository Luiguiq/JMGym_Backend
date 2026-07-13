import os
import uuid
from pathlib import Path

import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, UploadFile, File, HTTPException, status

from app.core.config import (
    CLOUDINARY_CLOUD_NAME,
    CLOUDINARY_API_KEY,
    CLOUDINARY_API_SECRET,
)

router = APIRouter(prefix="/upload", tags=["Upload"])

cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET,
)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".mp4", ".mov", ".webm", ".avi"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


@router.post("")
async def upload_file(file: UploadFile = File(...)):
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato no permitido. Usa: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo excede el tamaño máximo de 5 MB",
        )

    result = cloudinary.uploader.upload(
        contents,
        folder="jmgym/classes",
        resource_type="auto",
        public_id=uuid.uuid4().hex,
    )

    return {"url": result["secure_url"]}
