from rest_framework.routers import DefaultRouter
from camera.api.viewsets.position_preset import (
    AssetBedCameraPositionPresetViewSet,
    PresetPositionViewSet,
)

camera_router = DefaultRouter()

camera_router.register(
    r"assetbed/position_presets",
    AssetBedCameraPositionPresetViewSet,
    basename="assetbed-camera-presets",
)

camera_router.register(
    r"position_presets",
    PresetPositionViewSet,
    basename="camera-presets",
)


urlpatterns = camera_router.urls
