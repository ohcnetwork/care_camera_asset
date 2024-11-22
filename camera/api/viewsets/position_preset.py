from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from camera.api.serializers.position_preset import (
    PositionPresetSerializer,
)
from camera.models.position_preset import PositionPreset
from care.utils.queryset.asset_bed import (
    get_asset_bed_queryset,
    get_asset_queryset,
    get_bed_queryset,
)


class AssetBedCameraPositionPresetViewSet(ModelViewSet):
    serializer_class = PositionPresetSerializer
    queryset = PositionPreset.objects.all().select_related(
        "asset_bed", "created_by", "updated_by"
    )
    lookup_field = "external_id"
    permission_classes = (IsAuthenticated,)

    def get_asset_bed_obj(self):
        assetbed_external_id = self.request.query_params.get("assetbed_external_id")
        if not assetbed_external_id:
            raise ValidationError(
                detail="'assetbed_external_id' must be provided."
            )
        queryset = get_asset_bed_queryset(self.request.user).filter(
            external_id=assetbed_external_id
        )
        return get_object_or_404(queryset)

    def get_queryset(self):
        assetbed_external_id = self.request.query_params.get("assetbed_external_id")
        if not assetbed_external_id:
            raise ValidationError(
                detail="'assetbed_external_id' must be provided."
            )
        return super().get_queryset().filter(asset_bed=self.get_asset_bed_obj())

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["asset_bed"] = self.get_asset_bed_obj()
        return context


class PresetPositionViewSet(GenericViewSet, ListModelMixin):
    serializer_class = PositionPresetSerializer
    queryset = PositionPreset.objects.all().select_related(
        "asset_bed", "created_by", "updated_by"
    )
    lookup_field = "external_id"
    permission_classes = (IsAuthenticated,)

    def get_bed_obj(self, external_id: str):
        queryset = get_bed_queryset(self.request.user).filter(external_id=external_id)
        return get_object_or_404(queryset)

    def get_asset_obj(self, external_id: str):
        queryset = get_asset_queryset(self.request.user).filter(external_id=external_id)
        return get_object_or_404(queryset)

    def get_queryset(self):
        queryset = super().get_queryset()
        asset_external_id = self.request.query_params.get("asset_external_id")
        bed_external_id = self.request.query_params.get("bed_external_id")

        if not (asset_external_id or bed_external_id):
            raise ValidationError(
                detail="Either 'asset_external_id' or 'bed_external_id' must be provided."
            )

        if asset_external_id:
            return queryset.filter(
                asset_bed__asset=self.get_asset_obj(asset_external_id)
            )
        if bed_external_id:
            return queryset.filter(asset_bed__bed=self.get_bed_obj(bed_external_id))
        raise NotFound
