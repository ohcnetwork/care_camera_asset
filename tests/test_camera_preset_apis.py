from rest_framework import status
from rest_framework.test import APITestCase

from care.users.models import User
from care.utils.assetintegration.asset_classes import AssetClasses
from care.utils.tests.test_utils import TestUtils


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
        return f"/api/camera/assetbed/{asset_bed_id or self.asset_bed1.external_id}/camera_presets/"

    def test_create_camera_preset_without_position(self):
        print("\n"*10)
        print(self.get_base_url())
        print("\n"*10)
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
            f"/api/v1/asset/{asset_bed.asset.external_id}/camera_presets/"
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertContains(res, preset_external_id)

        # Check if preset in bed preset list
        res = self.client.get(
            f"/api/v1/bed/{asset_bed.bed.external_id}/camera_presets/"
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
