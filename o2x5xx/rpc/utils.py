import os
import base64


def writeApplicationConfigFile(application_file: str, data: bytearray) -> None:
    """
    Stores the application data as an o2x5xxapp-file in the desired path.

    :param application_file: (str) application file path as str
    :param data: (bytearray) application data
    :return: None
    """
    with open(application_file, "wb") as f:
        f.write(data)


def writeConfigFile(config_file: str, data: bytearray) -> None:
    """
    Stores the config data as an o2x5xxcfg-file in the desired path.

    :param config_file: (str) application file path as str
    :param data: (bytearray) application data
    :return: None
    """
    with open(config_file, "wb") as f:
        f.write(data)


def readConfigFile(config_file: str) -> bytearray:
    """
    Read and decode an application-config file.

    :param config_file: (str) config file path
    :return: (int) index of new application in list
    """
    if isinstance(config_file, str):
        if os.path.exists(os.path.dirname(config_file)):
            with open(config_file, "rb") as f:
                encodedZip = base64.b64encode(f.read())
                application_decoded = encodedZip.decode()
                return bytearray(application_decoded)
        else:
            raise FileExistsError("Config file {} does not exist!".format(config_file))
