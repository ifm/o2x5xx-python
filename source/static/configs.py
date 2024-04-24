images_config = {
    "elements": [
        {
            "id": "start_string",
            "type": "string",
            "value": "star"
        },
        {
            "id": "delimiter",
            "type": "string",
            "value": ";"
        },
        {
            "elements": [
                {
                    "id": "ID",
                    "type": "uint8"
                },
                {
                    "id": "delimiter",
                    "type": "string",
                    "value": ";"
                }
            ],
            "id": "Images",
            "type": "records"
        },
        {
            "id": "end_string",
            "type": "string",
            "value": "stop"
        },
        {
            "elements": [
                {
                    "id": "jpeg_image",
                    "type": "blob"
                },
                {
                    "id": "raw_image",
                    "type": "blob"
                }
            ],
            "id": "Images",
            "type": "records"
        }
    ],
    "format": {
        "dataencoding": "ascii"
    },
    "layouter": "flexible"
}