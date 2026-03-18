from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, posts, notifications, notification_api, admin, messages, reports, sessions, two_factor, blocks, privacy

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(two_factor.router, prefix="/auth/2fa", tags=["two_factor"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(posts.router, prefix="/posts", tags=["posts"])
api_router.include_router(messages.router, prefix="/messages", tags=["messages"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
api_router.include_router(notifications.router, tags=["notifications"])
api_router.include_router(notification_api.router, prefix="/notifications", tags=["notifications_history"])
api_router.include_router(blocks.router, prefix="/blocks", tags=["blocks"])
api_router.include_router(privacy.router, prefix="/privacy", tags=["privacy"])
