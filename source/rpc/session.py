import time
import xmlrpc.client
from .utils import firmwareWarning
import json
import os
import base64


class Session(object):
    """
    Session object
    """

    def __init__(self, sessionProxy, device):
        self._sessionProxy = sessionProxy
        self._device = device

    def exportConfig(self) -> bytearray:
        """
        Exports the whole configuration of the sensor-device and stores it at the desired path.

        :return: (bytearray) configuration as one data-blob :binary/base64
        """
        # increase heartbeat interval which will prevent a closed session after the "long" export progress
        self._device.sessionProxy.heartbeat(heartbeatInterval=30)
        config = self._sessionProxy.exportConfig()
        config_bytes = bytearray()
        config_bytes.extend(map(ord, str(config)))
        while self.getExportProgress() < 1.0:
            time.sleep(1)
        self.cleanupExport()
        self._device.waitForConfigurationDone()
        return config_bytes

    def importConfig(self, config: str, global_settings=True, network_settings=False, applications=True) -> None:
        """
        Import whole configuration, with the option to skip specific parts.

        :param config:              (str) The config file (*.o2d5xxcfg) as a Binary/base64 data
        :param global_settings:     (bool) Include Global-Configuration (Name, Description, Location, ...)
        :param network_settings:    (bool) Include Network-Configuration (IP, DHCP, ...)
        :param applications:        (bool) Include All Application-Configurations
        :return:                    None
        """
        # This is required due to the long import progress which may take longer than 10 seconds (default)
        self._device.sessionProxy.heartbeat(heartbeatInterval=30)
        if global_settings:
            self._sessionProxy.importConfig(config, 0x0001)
        if network_settings:
            self._sessionProxy.importConfig(config, 0x0002)
        if applications:
            self._sessionProxy.importConfig(config, 0x0010)
        while self.getImportProgress() < 1.0:
            time.sleep(1)
        self._device.waitForConfigurationDone()

    def exportApplication(self, applicationIndex: int) -> bytearray:
        """
        Exports one application-config.

        :param applicationIndex: (int) application index
        :return: None
        """

        config = self._sessionProxy.exportApplication(applicationIndex)
        application_bytes = bytearray()
        application_bytes.extend(map(ord, str(config)))
        while self.getExportProgress() < 1.0:
            time.sleep(1)
        else:
            self.cleanupExport()
        return application_bytes

    def importApplication(self, application: str) -> int:
        """
        Imports an application-config and creates a new application with it.

        :param application: (str) application-config as one-data-blob: binary/base64
        :return: (int) index of new application in list
        """

        index = int(self._sessionProxy.importApplication(application))
        while self.getImportProgress() < 1.0:
            time.sleep(1)
        return index

    def getImportProgress(self) -> float:
        """
        Get the progress of the asynchronous configuration import (yields 1.0 when the last import has finished).
        Returns xmlrpc errors occurring during import.

        :return: (float) progress (0.0 to 1.0)
        """
        try:
            result = self._sessionProxy.getImportProgress()
            return result
        except xmlrpc.client.Fault as fault:
            if fault.faultCode == 101107:
                return 1.0

    def getExportProgress(self) -> float:
        """
        Returns the progress of the ongoing export (configuration or application). After the export is done
        this method returns 1.0 until the cleanupExport() is called.

        :return: (float) progress (0.0 to 1.0)
        """
        try:
            result = self._sessionProxy.getExportProgress()
            return result
        except xmlrpc.client.Fault as fault:
            if fault.faultCode == 101110:
                return 1.0
        finally:
            self.cleanupExport()

    def cleanupExport(self) -> None:
        """
        Removes the exported configuration/application binary archive file from the device tmpfs.
        Shall be called after the file is fully downloaded by the user with HTTP GET request.

        :return: None
        """
        self._sessionProxy.cleanupExport()

    def getApplicationDetails(self, applicationIndex: [int, str]) -> dict:
        """
        The method returns details about the application line ApplicationType,
        TemplateInfo and Models with Type and Name.

        :param applicationIndex: (int) application Index
        :return: (dict) json-string containing application parameters, models and image settings
        """
        result = json.loads(self._sessionProxy.getApplicationDetails(applicationIndex))
        return result

    def resetStatistics(self) -> None:
        """
        Resets the statistic data of current active application.

        :return: None
        """
        self._sessionProxy.resetStatistics()
        self._device.waitForConfigurationDone()

    def writeApplicationConfigFile(self, applicationName: str, data: bytearray) -> None:
        """
        Stores the application data as an o2d5xxapp-file in the desired path.

        :param applicationName: (str) application name as str
        :param data: (bytearray) application data
        :return: None
        """
        extension = self._device.deviceMeta.value["ApplicationConfigExtension"]
        filename, file_extension = os.path.splitext(applicationName)
        if not file_extension == extension:
            applicationName = filename + extension
        with open(applicationName, "wb") as f:
            f.write(data)

    def writeDeviceConfigFile(self, configName: str, data: bytearray) -> None:
        """
        Stores the config data as an o2d5xxcfg-file in the desired path.

        :param configName: (str) application file path as str
        :param data: (bytearray) application data
        :return: None
        """
        extension = self._device.deviceMeta.value["DeviceConfigExtension"]
        filename, file_extension = os.path.splitext(configName)
        if not file_extension == extension:
            configName = filename + extension
        with open(configName, "wb") as f:
            f.write(data)

    def readApplicationConfigFile(self, applicationFile: str) -> str:
        """
        Read and decode an application-config file.

        :param applicationFile: (str) application config file path
        :return: (str) application data
        """
        result = self._readConfigFile(configFile=applicationFile)
        return result

    def readDeviceConfigFile(self, configFile: str) -> str:
        """
        Read and decode an device-config file.

        :param configFile: (str) device config file path
        :return: (str) application data
        """
        result = self._readConfigFile(configFile=configFile)
        return result

    @firmwareWarning
    def _readConfigFile(self, configFile: str) -> str:
        """
        Read and decode a device- or application-config file.

        :param configFile: (str) config file path
        :return: (str) config data
        """
        if isinstance(configFile, str):
            if os.path.exists(os.path.dirname(configFile)):
                with open(configFile, "rb") as f:
                    encodedZip = base64.b64encode(f.read())
                    decoded = encodedZip.decode()
                    return decoded
            else:
                raise FileExistsError("File {} does not exist!".format(configFile))
