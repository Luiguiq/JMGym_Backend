from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.auth_routes import router as auth_router
from app.routes.class_routes import router as class_router
from app.routes.reservation_routes import router as reservation_router
from app.routes.payment_routes import router as payment_router
from app.routes.admin_routes import router as admin_router
from app.routes.admin_auth_routes import router as admin_auth_router

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

app.include_router(auth_router)
app.include_router(class_router)
app.include_router(reservation_router)
app.include_router(payment_router)
app.include_router(admin_router)
app.include_router(admin_auth_router)

@app.get("/")
def root():
    return {
        "message": "API funcionando"
    }