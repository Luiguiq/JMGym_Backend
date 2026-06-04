from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.auth_routes import router as auth_router
from app.routes.class_routes import router as class_router
from app.routes.reservation_routes import router as reservation_router
from app.routes.payment_routes import router as payment_router
from app.routes.admin_routes import router as admin_router
from app.routes.admin_auth_routes import router as admin_auth_router
from app.routes.instructor_routes import router as instructor_router
from app.routes.genre_routes import router as genre_router
from app.routes.admin_user_routes import router as admin_user_router
from app.routes.user_routes import router as user_router

app = FastAPI(
    title="JMGym API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api")
app.include_router(class_router, prefix="/api")
app.include_router(reservation_router, prefix="/api")
app.include_router(payment_router, prefix="/api")
app.include_router(admin_router, prefix="/api")
app.include_router(admin_auth_router, prefix="/api")
app.include_router(instructor_router, prefix="/api")
app.include_router(genre_router, prefix="/api")
app.include_router(admin_user_router, prefix="/api")
app.include_router(user_router, prefix="/api")

@app.get("/")
def root():
    return {
        "message": "API funcionando"
    }