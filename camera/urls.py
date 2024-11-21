from django.urls import include, path
from rest_framework.routers import DefaultRouter
from django.shortcuts import HttpResponse
from camera.api.viewsets.position_preset import (
    AssetBedCameraPositionPresetViewSet,
    PresetPositionViewSet,
)

router = DefaultRouter()

# AssetBed: Supports all CRUD operations
router.register(
    r"assetbed/<str:assetbed_external_id>/camera_presets",
    AssetBedCameraPositionPresetViewSet,
    basename="assetbed-camera-presets",
)

# Asset: Only GET requests
router.register(
    r"asset/<str:asset_external_id>/camera_presets",
    PresetPositionViewSet,
    basename="asset-camera-presets",
)

# Bed: Only GET requests
router.register(
    r"bed/<str:bed_external_id>/camera_presets",
    PresetPositionViewSet,
    basename="bed-camera-presets",
)

def healthy(request):
    return HttpResponse("Hello from care hcx")

urlpatterns = [
    path("", include(router.urls)),
    path("health", healthy),
]