from app.routes.courses import router as courses_router
from app.routes.universities import router as universities_router
from app.routes.health import router as health_router

__all__ = ["courses_router", "universities_router", "health_router"]
