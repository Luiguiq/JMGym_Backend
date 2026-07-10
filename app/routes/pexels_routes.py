from fastapi import APIRouter, Query, HTTPException, status

from app.services.pexels_service import search_image, search_video

router = APIRouter(prefix="/pexels", tags=["Pexels"])


@router.get("/image")
async def get_pexels_images(query: str = Query(min_length=2)):
    try:
        results = await search_image(query)
        return {"results": results}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error al consultar Pexels: {str(e)}",
        )


@router.get("/video")
async def get_pexels_videos(query: str = Query(min_length=2)):
    try:
        results = await search_video(query)
        return {"results": results}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error al consultar Pexels: {str(e)}",
        )
