from rest_framework.routers import DefaultRouter
from camera.api.viewsets.position_preset import PositionPresetViewSet

camera_router = DefaultRouter()

camera_router.register(
    r"position-presets",
    PositionPresetViewSet,
    basename="camera-position-presets",
)


urlpatterns = camera_router.urls
