from aiogram import Router
from . import start, analyze, profile

router = Router()
router.include_router(start.router)
router.include_router(analyze.router)
router.include_router(profile.router)

__all__ = ["router"]
