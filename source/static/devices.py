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
              "LogicGraphConfigExtension": ".o2xlgc",
              "ApplicationConfigExtension": ".o2d5xxapp",
              "DeviceConfigExtension": ".o2d5xxcfg",
              "PCICConfigExtension": ".o2xpcic"}
    O2I5xx = {"ArticleNumber": ["O2I5xx",
                                "O2I510", "O2I511", "O2I512",
                                "O2I513", "O2I514", "O2I500",
                                "O2I515", "O2I501", "O2I502",
                                "O2I503", "O2I504", "O2I505"],
              "DeviceType": ["1:256", 0x100],
              "LogicGraphConfigExtension": ".o2xlgc",
              "ApplicationConfigExtension": ".o2i5xxapp",
              "DeviceConfigExtension": ".o2i5xxcfg",
              "PCICConfigExtension": ".o2xpcic"}
    O2I4xx = {"ArticleNumber": ["O2I4xx",
                                "O2I410", "O2I412", "O2I414",
                                "O2I400", "O2I420", "O2I402",
                                "O2I422", "O2I404", "O2I424"],
              "DeviceType": ["1:319", 0x104],
              "LogicGraphConfigExtension": ".o2xlgc",
              "ApplicationConfigExtension": ".o2i4xxapp",
              "DeviceConfigExtension": ".o2i4xxcfg",
              "PCICConfigExtension": ".o2xpcic"}
    O2U5xx = {"ArticleNumber": ["O2U5xx",
                                "O2U530", "O2U532", "O2U534",
                                "O2U540", "O2U542", "O2U544"],
              "DeviceType": ["1:384", 0x180],
              "LogicGraphConfigExtension": ".o2xlgc",
              "ApplicationConfigExtension": ".o2u5xxapp",
              "DeviceConfigExtension": ".o2u5xxcfg",
              "PCICConfigExtension": ".o2xpcic"}

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
