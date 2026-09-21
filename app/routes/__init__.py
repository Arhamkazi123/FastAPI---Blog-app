from fastapi import APIRouter
from app.routes.auth import router as auth_router
from app.routes.posts import router as post_router
from app.routes.comments import router as comment_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(post_router)
router.include_router(comment_router)