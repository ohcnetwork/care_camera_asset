from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

PLUGIN_NAME = "camera"


class CameraConfig(AppConfig):
    name = PLUGIN_NAME
    verbose_name = _("Camera")

    def ready(self):
        """
        Import models, signals, and other dependencies here to ensure
        Django's app registry is fully initialized before use.
        """
        from care.facility.models.asset import Asset
        from care.facility.models.json_schema.asset import AssetMetaRegistry
        from care.utils.assetintegration.asset_classes import AssetClasses
        from camera.utils.onvif import OnvifAsset
        from camera.utils.onvif_schema import ONVIF_META

        AssetClasses.register("ONVIF", OnvifAsset)
        AssetMetaRegistry.register_meta("onvif", ONVIF_META)

        Asset.CSV_MAPPING['meta__camera_access_key'] = "Config: Camera Access Key"

        import camera.signals