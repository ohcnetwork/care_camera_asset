ONVIF_META = {
    "type": "object",
    "required": ["local_ip_address", "camera_access_key"],
    "properties": {
        "local_ip_address": {"type": "string"},
        "middleware_hostname": {"type": "string"},
        "camera_access_key": {"type": "string"},
        "camera_type": {"type": "string"},
        "asset_type": {"type": "string"},
        "insecure_connection": {"type": "boolean"},
    },
    "additionalProperties": False,
}

