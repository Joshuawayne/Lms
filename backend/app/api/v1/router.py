"""Compose the version-one API without embedding business rules."""

from fastapi import APIRouter

from app.api.v1.health import router as health_router
from app.modules.programs.api import router as programs_router

router = APIRouter(prefix="/api/v1")
router.include_router(health_router)
router.include_router(programs_router)
