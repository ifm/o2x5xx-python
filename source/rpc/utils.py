import zipfile
import json
import warnings


def firmwareWarning(function):
    """Formware warning decorator."""

    def wrapper(self, *args, **kwargs):
        keyArgName = list(kwargs.keys())[0]
        zipOpen = zipfile.ZipFile(kwargs[keyArgName], "r")
        zipFiles = zipOpen.namelist()
        if "device.json" in zipFiles:
            tmp = "device.json"
        elif "application.json" in zipFiles:
            tmp = "application.json"
        else:
            raise ImportError("Unknown config file in zip: {}".format(str(zipFiles)))
        jsonData = json.loads(zipOpen.open(tmp).read())
        minConfigFileFirmware = jsonData["Firmware"]
        sensorFirmware = self._device.getSWVersion()["IFM_Software"]
        if int(sensorFirmware.replace(".", "")) < int(minConfigFileFirmware.replace(".", "")):
            message = "Missmatch in firmware versions: Sensor firmware {} is lower than {} firmware {}. " \
                      "Import of may will fail!".format(sensorFirmware, tmp, minConfigFileFirmware)
            warnings.warn(message, UserWarning)
        return function(self, *args, **kwargs)
    return wrapper
