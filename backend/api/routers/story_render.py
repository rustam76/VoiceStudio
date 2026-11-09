"""Stories uses the shared longform renderer without the book-import workspace."""
from fastapi import APIRouter
from api.routers.audiobook import router as shared_longform

router = APIRouter()
_STORY_ROUTES = {
    "/longform/render", "/audiobook/preview", "/audiobook/cover", "/audiobook/jobs",
    "/audiobook/resume/{job_id}",
}
# Keep the original APIRoutes and their authorization/consumer dependencies.
router.routes.extend(route for route in shared_longform.routes if route.path in _STORY_ROUTES)
