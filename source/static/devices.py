import enum


class DeviceMode(enum.Enum):
    PRODUCTIVE = "PRODUCTIVE-MODE"
    BOOTING = "BOOTING"
    RECOVERY = "RECOVERY-MODE"


class DevicesMeta(enum.Enum):
    O2D5xx = {"ArticleNumber": ["O2D5xx",
                                "O2D500", "O2D502", "O2D504",
                                "O2D510", "O2D512", "O2D514",
                                "O2D520", "O2D522", "O2D524",
                                "O2D530", "O2D532", "O2D534",
                                "O2D540", "O2D542", "O2D544",
                                "O2D550", "O2D552", "O2D554"],
              "DeviceType": ["1:320", 0x140],
              "ApplicationExtension": ".o2d5xxapp",
              "ConfigExtension": ".o2d5xxcfg"}
    O2I5xx = {"ArticleNumber": ["O2I5xx"],
              "DeviceType": ["1:256", 0x100],
              "ApplicationExtension": ".o2i5xxapp",
              "ConfigExtension": ".o2i5xxcfg"}

    @classmethod
    def getData(cls, key, value):
        for s in DevicesMeta:
            _data = s.value[key]
            if isinstance(_data, list):
                for v in _data:
                    if v == value:
                        return s
            else:
                if _data == value:
                    return s
