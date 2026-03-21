from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router

# Import all models early so SQLAlchemy registry configures relations without KeyErrors
from app.db import base 

app = FastAPI(
    title="Social Network API",
    description="Backend profesional para una Red Social con FastAPI. Incluye Multimedia, Notificaciones, Email y RBAC.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuración de CORS para Next.js / Angular / React
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Incluimos las rutas de la versión 1
app.include_router(api_router, prefix="/api/v1")

@app.get("/", tags=["health"])
def root():
    return {"message": "Bienvenido a la API de la Red Social"}
