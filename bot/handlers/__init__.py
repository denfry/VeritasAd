from aiogram import Router
from . import start, analyze, profile, link

router = Router()
router.include_router(start.router)
router.include_router(analyze.router)
router.include_router(profile.router)
router.include_router(link.router)

__all__ = ["router"]
