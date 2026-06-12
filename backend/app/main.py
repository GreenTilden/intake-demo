from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import CORS_ORIGINS
from app.routers import intakes, auth, staff, categories, dashboard

app = FastAPI(
    title="Northwind Legal - Intake System",
    description="Secure intake management for civil rights organizations",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(intakes.router, prefix="/api")
app.include_router(staff.router, prefix="/api")
app.include_router(categories.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "intake-demo"}
