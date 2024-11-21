import enum

from rest_framework.exceptions import ValidationError

from care.utils.assetintegration.base import ActionParams, BaseAssetIntegration


class OnvifAsset(BaseAssetIntegration):
    _name = "onvif"

    class OnvifActions(enum.Enum):
        GET_CAMERA_STATUS = "get_status"
        GET_PRESETS = "get_presets"
        GOTO_PRESET = "goto_preset"
        ABSOLUTE_MOVE = "absolute_move"
        RELATIVE_MOVE = "relative_move"
        GET_STREAM_TOKEN = "get_stream_token"

    def __init__(self, meta):
        try:
            super().__init__(meta)
            self.username = self.meta["camera_access_key"].split(":")[0]
            self.password = self.meta["camera_access_key"].split(":")[1]
            self.access_key = self.meta["camera_access_key"].split(":")[2]
        except KeyError as e:
            raise ValidationError(
                {key: f"{key} not found in asset metadata" for key in e.args}
            ) from e

    def handle_action(self, **kwargs: ActionParams):
        action_type = kwargs["type"]
        action_data = kwargs.get("data", {})
        timeout = kwargs.get("timeout")

        request_body = {
            "hostname": self.host,
            "port": 80,
            "username": self.username,
            "password": self.password,
            "accessKey": self.access_key,
            **action_data,
        }

        if action_type == self.OnvifActions.GET_CAMERA_STATUS.value:
            return self.api_get(self.get_url("status"), request_body, timeout)

        if action_type == self.OnvifActions.GET_PRESETS.value:
            return self.api_get(self.get_url("presets"), request_body, timeout)

        if action_type == self.OnvifActions.GOTO_PRESET.value:
            return self.api_post(self.get_url("gotoPreset"), request_body, timeout)

        if action_type == self.OnvifActions.ABSOLUTE_MOVE.value:
            return self.api_post(self.get_url("absoluteMove"), request_body, timeout)

        if action_type == self.OnvifActions.RELATIVE_MOVE.value:
            return self.api_post(self.get_url("relativeMove"), request_body, timeout)

        if action_type == self.OnvifActions.GET_STREAM_TOKEN.value:
            return self.api_post(
                self.get_url("api/stream/getToken/videoFeed"),
                {
                    "stream_id": self.access_key,
                },
                timeout,
            )

        raise ValidationError({"action": "invalid action type"})

    @classmethod
    def get_action_choices(cls):
        choices = []
        choices += [(e.value, e.name) for e in cls.OnvifActions]
        return choices

    @staticmethod
    def is_movable():
        return False

    @staticmethod
    def can_be_linked_to_asset_bed():
        return True

    @staticmethod
    def can_be_linked_to_consultation_bed():
        return False

    def get_asset_status(self):
        try:
            # TODO: Remove this block after all assets are migrated to the new middleware
            asset_config = self.meta["camera_access_key"].split(":")
            assets_config = [
                {
                    "hostname": self.meta.get("local_ip_address"),
                    "port": 80,
                    "username": asset_config[0],
                    "password": asset_config[1],
                }
            ]
            return self.api_post(
                self.get_url("cameras/status"), data=assets_config
            )
        except Exception:
            return self.api_get(
                self.get_url("cameras/status")
            )
