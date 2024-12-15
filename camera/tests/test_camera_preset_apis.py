from care.users.models import User
from care.utils.assetintegration.asset_classes import AssetClasses
from care.utils.tests.test_utils import TestUtils
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.exceptions import ValidationError
from camera.utils.onvif import OnvifAsset


class AssetBedCameraPresetViewSetTestCase(TestUtils, APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.state = cls.create_state()
        cls.district = cls.create_district(cls.state)
        cls.local_body = cls.create_local_body(cls.district)
        cls.super_user = cls.create_super_user("su", cls.district)
        cls.facility = cls.create_facility(cls.super_user, cls.district, cls.local_body)
        cls.user = cls.create_user(
            User.TYPE_VALUE_MAP["DistrictAdmin"],
            cls.district,
            home_facility=cls.facility,
        )
        cls.asset_location = cls.create_asset_location(cls.facility)
        cls.asset1 = cls.create_asset(
            cls.asset_location, asset_class=AssetClasses.ONVIF.name
        )
        cls.asset2 = cls.create_asset(
            cls.asset_location, asset_class=AssetClasses.ONVIF.name
        )
        cls.bed = cls.create_bed(cls.facility, cls.asset_location)
        cls.asset_bed1 = cls.create_assetbed(cls.bed, cls.asset1)
        cls.asset_bed2 = cls.create_assetbed(cls.bed, cls.asset2)

    def get_base_url(self, asset_bed_id=None):
        return f"/api/camera/position-presets/?assetbed_external_id={asset_bed_id or self.asset_bed1.external_id}"

    def validate_invalid_meta(self, asset_class, meta):
        with self.assertRaises(ValidationError):
            asset_class(meta)

    def test_create_camera_preset_without_position(self):
        res = self.client.post(
            self.get_base_url(),
            {
                "name": "Preset without position",
                "position": {},
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_camera_preset_with_missing_required_keys_in_position(self):
        res = self.client.post(
            self.get_base_url(),
            {
                "name": "Preset with invalid position",
                "position": {"key": "value"},
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_camera_preset_with_position_not_number(self):
        res = self.client.post(
            self.get_base_url(),
            {
                "name": "Preset with invalid position",
                "position": {
                    "x": "not a number",
                    "y": 1,
                    "zoom": 1,
                },
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_camera_preset_with_position_values_as_string(self):
        res = self.client.post(
            self.get_base_url(),
            {
                "name": "Preset with invalid position",
                "position": {
                    "x": "1",
                    "y": "1",
                    "zoom": "1",
                },
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_camera_preset_and_presence_in_various_preset_list_apis(self):
        asset_bed = self.asset_bed1
        res = self.client.post(
            self.get_base_url(asset_bed.external_id),
            {
                "name": "Preset with proper position",
                "position": {
                    "x": 1.0,
                    "y": 1.0,
                    "zoom": 1.0,
                },
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        preset_external_id = res.data["id"]

        # Check if preset in asset-bed preset list
        res = self.client.get(self.get_base_url(asset_bed.external_id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertContains(res, preset_external_id)

        # Check if preset in asset preset list
        res = self.client.get(
            f"/api/camera/position-presets/?asset_external_id={asset_bed.asset.external_id}"
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertContains(res, preset_external_id)

        # Check if preset in bed preset list
        res = self.client.get(
            f"/api/camera/position-presets/?bed_external_id={asset_bed.bed.external_id}"
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertContains(res, preset_external_id)

    def test_create_camera_preset_with_same_name_in_same_bed(self):
        data = {
            "name": "Duplicate Preset Name",
            "position": {
                "x": 1.0,
                "y": 1.0,
                "zoom": 1.0,
            },
        }
        self.client.post(
            self.get_base_url(self.asset_bed1.external_id), data, format="json"
        )
        res = self.client.post(
            self.get_base_url(self.asset_bed2.external_id), data, format="json"
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_bed_with_deleted_assetbed(self):
        res = self.client.post(
            self.get_base_url(self.asset_bed1.external_id),
            {
                "name": "Preset with proper position",
                "position": {
                    "x": 1.0,
                    "y": 1.0,
                    "zoom": 1.0,
                },
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        res = self.client.post(
            self.get_base_url(self.asset_bed2.external_id),
            {
                "name": "Preset with proper position 2",
                "position": {
                    "x": 1.0,
                    "y": 1.0,
                    "zoom": 1.0,
                },
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        
        res = self.client.get(f"/api/camera/position-presets/?bed_external_id={self.bed.external_id}")
        self.assertEqual(len(res.json()["results"]), 2)

        self.asset_bed1.delete()
        self.asset_bed1.refresh_from_db()
        res = self.client.get(f"/api/camera/position-presets/?bed_external_id={self.bed.external_id}")
        self.assertEqual(len(res.json()["results"]), 1)
    
    def test_meta_validations_for_onvif_asset(self):
        valid_meta = {
            "local_ip_address": "192.168.0.1",
            "camera_access_key": "username:password:access_key",
            "middleware_hostname": "middleware.local",
            "insecure_connection": True,
        }
        onvif_asset = OnvifAsset(valid_meta)
        self.assertEqual(onvif_asset.middleware_hostname, "middleware.local")
        self.assertEqual(onvif_asset.host, "192.168.0.1")
        self.assertEqual(onvif_asset.username, "username")
        self.assertEqual(onvif_asset.password, "password")
        self.assertEqual(onvif_asset.access_key, "access_key")
        self.assertTrue(onvif_asset.insecure_connection)

        invalid_meta_cases = [
            # Invalid format for camera_access_key
            {
                "id": "123",
                "local_ip_address": "192.168.0.1",
                "middleware_hostname": "middleware.local",
                "camera_access_key": "invalid_format",
            },
            # Missing username/password in camera_access_key
            {
                "local_ip_address": "192.168.0.1",
                "middleware_hostname": "middleware.local",
                "camera_access_key": "invalid_format",
            },
            # Missing middleware_hostname
            {
                "local_ip_address": "192.168.0.1",
                "camera_access_key": "username:password:access_key",
            },
            # Missing local_ip_address
            {
                "middleware_hostname": "middleware.local",
                "camera_access_key": "username:password:access_key",
            },
            # Invalid value for insecure_connection
            {
                "local_ip_address": "192.168.0.1",
                "camera_access_key": "username:password:access_key",
                "middleware_hostname": "middleware.local",
                "insecure_connection": "invalid_value",
            },
        ]
        for meta in invalid_meta_cases:
            self.validate_invalid_meta(OnvifAsset, meta)
