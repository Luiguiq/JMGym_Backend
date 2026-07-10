from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import not_

from app.security import get_db, get_current_admin
from app.models.admin_model import Administrador
from app.models.class_model import Clase
from app.models.instructor_model import Instructor
from app.models.genre_model import GeneroClase
from app.services.pexels_service import search_image, search_video

router = APIRouter(prefix="/admin/media", tags=["Admin Media"])


@router.post("/seed-classes")
async def seed_class_images(
    db: Session = Depends(get_db),
    admin: Administrador = Depends(get_current_admin),
):
    clases = (
        db.query(Clase)
        .filter(
            not_(Clase.nombre_clase.ilike("test_%")),
            not_(Clase.nombre_clase.ilike("Test Fidelizacion%")),
            Clase.imagen_clase.is_(None),
        )
        .all()
    )

    if not clases:
        return {"message": "Todas las clases ya tienen imagen o no hay clases pendientes", "updated": 0}

    updated = 0
    errors = 0
    for cls in clases:
        keywords = []
        if cls.genero and cls.genero.nombre_genero:
            keywords.append(cls.genero.nombre_genero)
        keywords.append(cls.nombre_clase)
        query = " ".join(keywords)

        try:
            results = await search_image(query, per_page=1)
            if results:
                cls.imagen_clase = results[0]["url"]
                updated += 1
            else:
                # fallback con solo el genero
                if cls.genero:
                    results = await search_image(cls.genero.nombre_genero, per_page=1)
                    if results:
                        cls.imagen_clase = results[0]["url"]
                        updated += 1
        except Exception:
            errors += 1

    if updated:
        db.commit()

    return {
        "message": f"Procesadas {len(clases)} clases",
        "updated": updated,
        "errors": errors,
        "pending": len(clases) - updated - errors,
    }


@router.post("/seed-instructors")
async def seed_instructor_media(
    db: Session = Depends(get_db),
    admin: Administrador = Depends(get_current_admin),
):
    instructores = (
        db.query(Instructor)
        .filter(
            not_(Instructor.nombre_completo.ilike("test_%")),
        )
        .all()
    )

    if not instructores:
        return {"message": "No hay instructores disponibles", "updated_photos": 0, "updated_videos": 0}

    updated_photos = 0
    updated_videos = 0
    errors = 0

    for inst in instructores:
        query = inst.especialidad or inst.nombre_completo

        if not inst.foto:
            try:
                results = await search_image(query, per_page=1)
                if results:
                    inst.foto = results[0]["url"]
                    updated_photos += 1
            except Exception:
                errors += 1

        if not inst.video_presentacion:
            try:
                results = await search_video(query, per_page=1)
                if results:
                    inst.video_presentacion = results[0]["url"]
                    updated_videos += 1
            except Exception:
                errors += 1

    if updated_photos or updated_videos:
        db.commit()

    return {
        "message": f"Procesados {len(instructores)} instructores",
        "updated_photos": updated_photos,
        "updated_videos": updated_videos,
        "errors": errors,
    }
