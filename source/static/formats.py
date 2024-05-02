import enum

# These are the error codes with the corresponding error message
error_codes = {
    000000000: "No error detected",
    100000001: "Maximum number of connections exceeded",
    100000002: "Internal failure during a D-Bus call",
    100000003: "Unspecified internal error",
    100000004: "Generic invalid parameter",
    100000005: "Invalid command",
    100001000: "Application configuration does not allow Process interface trigger",
    100001001: "Video mode does not allow Process interface trigger",
    100001002: "There is no application configured",
    100001003: "Invalid image id in I? command",
    100001006: "Invalid conversion type selected",
    100001007: "No trigger was run yet",
    100001008: "Missed decoded frame",
    100001009: "No more segments left",
    100001010: "Command bit 4 not reset to 0",
    110001001: "Boot timeout",
    110001002: "Fatal software error",
    110001003: "Unknown hardware",
    100001004: "Invalid pin id in o/O? command",
    100001005: "Invalid pin configuration in o/O? command",
    110001006: "Trigger overrun",
    110001007: "Ethernet configuration was changed. The socket is going to be closed.",
    110002000: "Short circuit on Ready for Trigger",
    110002001: "Short circuit on OUT1",
    110002002: "Short circuit on OUT2",
    110002003: "Reverse feeding",
    110003000: "Vled overvoltage",
    110003001: "Vled undervoltage",
    110003002: "Vmod overvoltage",
    110003003: "Vmod undervoltage",
    110003004: "Mainboard overvoltage",
    110003005: "Mainboard undervoltage",
    110003006: "Supply overvoltage",
    110003007: "Supply undervoltage",
    110003008: "VFEMon alarm",
    110003009: "PMIC supply alarm",
    110004000: "Illumination overtemperature",
    120000001: "NTP server not available",
    120000002: "other NTP error"}

# This is the serialization format of binary data with header version 3.
serialization_format = {
    0x0000: ["CHUNK_TYPE", "Defines the type of the chunk.", 4],
    0x0004: ["CHUNK_SIZE", "Size of the whole image chunk in bytes.", 4],
    0x0008: ["HEADER_SIZE", "Number of bytes starting from 0x0000 until BINARY_DATA."
                            "The number of bytes must be a multiple of 16, and the minimum value is 0x40 (64).", 4],
    0x000C: ["HEADER_VERSION", "Version number of the header (=3).", 4],
    0x0010: ["IMAGE_WIDTH", "Image width in pixel. Applies only if BINARY_DATA contains an image. "
                            "Otherwise this is set to the length of BINARY_DATA.", 4],
    0x0014: ["IMAGE_HEIGHT", "Image height in pixel. Applies only if BINARY_DATA contains an image. "
                             "Otherwise this is set to 1.", 4],
    0x0018: ["PIXEL_FORMAT", "Pixel format. Applies only to image binary data. For generic binary data "
                             "this is set to FORMAT_8U unless specified otherwise for a particular chunk type.", 4],
    0x001C: ["TIME_STAMP", "Timestamp in uS", 4],
    0x0020: ["FRAME_COUNT", "Continuous frame count.", 4],
    0x0024: ["STATUS_CODE", "This field is used to communicate errors on the device.", 4],
    0x0028: ["TIME_STAMP_SEC", "Timestamp seconds", 4],
    0x002C: ["TIME_STAMP_NSEC", "Timestamp nanoseconds", 4],
    0x0030: ["META_DATA", "UTF-8 encoded null-terminated JSON object. The content of the JSON object is depending "
                          "on the CHUNK_TYPE.", 4]}

trigger_modes = {
    1: "free run (continuous mode)",
    2: "process interface",
    3: "positive edge",
    4: "negative edge",
    5: "positive and negative edge",
    6: "gated HW",
    7: "gated process interface",
    8: "time controlled gated HW"
}

illumination_types = {
    0: "no illumination active",
    1: "internal illumination shall be used",
    2: "external illumination shall be used",
    3: "internal and external illumination shall be used together"
}


class ChunkType(enum.IntEnum):
    MONOCHROME_2D_8BIT = 251
    JPEG_IMAGE = 260
