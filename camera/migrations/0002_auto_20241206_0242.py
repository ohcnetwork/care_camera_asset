# Generated by Django 5.1.3 on 2024-12-05 21:12

from django.db import migrations

def migrate_camera_preset_to_position_preset(apps, schema_editor):
    try:
        CameraPreset = apps.get_model("facility", "CameraPreset")
    except LookupError:
        # If CameraPreset model doesn't exist, skip the migration
        return

    PositionPreset = apps.get_model("camera", "PositionPreset")

    camera_presets = CameraPreset.objects.all()

    position_presets = [
        PositionPreset(
            external_id=preset.external_id,
            name=preset.name,
            asset_bed=preset.asset_bed,
            position=preset.position,
            created_by=preset.created_by,
            updated_by=preset.updated_by,
            is_migrated=preset.is_migrated,
            created_date=preset.created_date,
            modified_date=preset.modified_date
        )
        for preset in camera_presets
    ]

    PositionPreset.objects.bulk_create(position_presets)


class Migration(migrations.Migration):

    dependencies = [
        ('camera', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(migrate_camera_preset_to_position_preset),
    ]
