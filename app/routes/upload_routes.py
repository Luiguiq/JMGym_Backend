import os
import uuid
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException, status

router = APIRouter(prefix="/upload", tags=["Upload"])

_ON_VERCEL = os.environ.get("VERCEL")
if _ON_VERCEL:
    UPLOAD_DIR = Path("/tmp/uploads")
else:
    UPLOAD_DIR = Path(os.path.join(os.path.dirname(__file__), "..", "uploads")).resolve()
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

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

    filename = f"{uuid.uuid4().hex}{ext}"
    file_path = UPLOAD_DIR / filename
    with open(file_path, "wb") as f:
        f.write(contents)

    url = f"/uploads/{filename}"
    return {"url": url}
