from django.db.models.signals import post_delete
from django.dispatch import receiver

from care.facility.models import AssetBed


@receiver(post_delete, sender=AssetBed)
def soft_delete_camera_presets(sender, instance, **kwargs):
    """
    Soft delete connected camera presets when an AssetBed is deleted.
    """
    if hasattr(instance, "camera_position_presets"):
        instance.camera_presets.update(deleted=True)
