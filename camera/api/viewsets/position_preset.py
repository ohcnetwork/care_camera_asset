from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from camera.api.serializers.position_preset import PositionPresetSerializer
from camera.models.position_preset import PositionPreset
from care.utils.queryset.asset_bed import (
    get_asset_bed_queryset,
    get_asset_queryset,
    get_bed_queryset,
)


class PositionPresetViewSet(ModelViewSet):
    serializer_class = PositionPresetSerializer
    queryset = PositionPreset.objects.all().select_related(
        "asset_bed", "created_by", "updated_by"
    )
    lookup_field = "external_id"
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="assetbed_external_id",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description="External ID of the asset bed",
            ),
        ]
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="assetbed_external_id",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="External ID of the asset bed",
            ),
            OpenApiParameter(
                name="asset_external_id",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="External ID of the asset",
            ),
            OpenApiParameter(
                name="bed_external_id",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="External ID of the bed",
            ),
        ],
        description="At least one of assetbed_external_id, asset_external_id, or bed_external_id must be provided",
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_asset_bed_obj(self, external_id: str):
        queryset = get_asset_bed_queryset(self.request.user).filter(
            external_id=external_id
        )
        return get_object_or_404(queryset)

    def get_bed_obj(self, external_id: str):
        queryset = get_bed_queryset(self.request.user).filter(external_id=external_id)
        return get_object_or_404(queryset)

    def get_asset_obj(self, external_id: str):
        queryset = get_asset_queryset(self.request.user).filter(external_id=external_id)
        return get_object_or_404(queryset)

    def get_queryset(self):
        queryset = super().get_queryset()
        assetbed_external_id = self.request.query_params.get("assetbed_external_id")
        asset_external_id = self.request.query_params.get("asset_external_id")
        bed_external_id = self.request.query_params.get("bed_external_id")

        if self.action == "create":
            if not assetbed_external_id:
                raise ValidationError(detail="'assetbed_external_id' must be provided.")

        if self.action == "list":
            if not (assetbed_external_id or asset_external_id or bed_external_id):
                raise ValidationError(
                    detail="'assetbed_external_id' or 'asset_external_id' or 'bed_external_id' must be provided."
                )

        if assetbed_external_id:
            return queryset.filter(
                asset_bed=self.get_asset_bed_obj(assetbed_external_id)
            )
        if asset_external_id:
            return queryset.filter(
                asset_bed__asset=self.get_asset_obj(asset_external_id)
            )
        if bed_external_id:
            return queryset.filter(asset_bed__bed=self.get_bed_obj(bed_external_id))

        raise NotFound

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.action == "create":
            context["asset_bed"] = self.get_asset_bed_obj(
                self.request.query_params.get("assetbed_external_id")
            )
        return context

    def perform_create(self, serializer):
        serializer.save(
            asset_bed=self.get_asset_bed_obj(
                self.request.query_params.get("assetbed_external_id")
            ),
            created_by=self.request.user,
        )

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
