import time
from threading import Timer
import xmlrpc.client
from .edit import Edit
from .utils import firmwareWarning
import json
import os
import base64


class Session(object):
    """
    Session object
    """

    def __init__(self, sessionURL, mainAPI, autoHeartbeat=True, autoHeartbeatInterval=10):
        self.url = sessionURL
        self.mainAPI = mainAPI
        self.defaultAutoHeartbeatInterval = autoHeartbeatInterval
        self.rpc = xmlrpc.client.ServerProxy(self.url)
        self.connected = True
        self._edit = None
        if autoHeartbeat:
            self.rpc.heartbeat(autoHeartbeatInterval)
            self.autoHeartbeatInterval = autoHeartbeatInterval
            self.autoHeartbeatTimer = Timer(autoHeartbeatInterval - 1, self.doAutoHeartbeat)
            self.autoHeartbeatTimer.start()
        else:
            self.rpc.heartbeat(300)

    def __del__(self):
        self.cancelSession()

    @property
    def OperatingMode(self):
        """
        Get the current operation mode for the session.

        :return: (int)
                 0: run mode
                 1: edit mode
        """
        result = int(self.mainAPI.getParameter("OperatingMode"))
        return result

    @property
    def edit(self) -> Edit:
        """
        Requesting an Edit object with this property. If the edit mode is False at the moment,
        the edit mode will be activated with this request with the function setOperationMode(1).

        :return: Edit object
        """
        if not self.OperatingMode:
            return self.setOperatingMode(mode=1)
        else:
            self._edit = Edit(editURL=self.url + 'edit/',
                              sessionAPI=self,
                              mainAPI=self.mainAPI)
            return self._edit

    def startEdit(self) -> Edit:
        """
        Starting the edit mode and requesting an Edit object.

        :return:
        """
        self.rpc.setOperatingMode(1)
        self._edit = Edit(editURL=self.url + 'edit/',
                          sessionAPI=self,
                          mainAPI=self.mainAPI)
        return self._edit

    def stopEdit(self) -> None:
        """
        Stopping the edit mode.

        :return: None
        """
        self.rpc.setOperatingMode(0)
        self._edit = None

    def heartbeat(self, heartbeatInterval: int) -> int:
        """
        Extend the live time of edit-session If the given value is outside the range of "SessionTimeout",
        the saved default timeout will be used.

        :param heartbeatInterval: (int) requested timeout-interval till next heartbeat, in seconds
        :return: (int) the used timeout-interval, in seconds
        """
        result = self.rpc.heartbeat(heartbeatInterval)
        return result

    def doAutoHeartbeat(self) -> None:
        """
        Auto Heartbeat Timer for automatic extending the live time of edit-session.
        If the given value is outside the range of "SessionTimeout", the saved default timeout will be used.

        :return: None
        """
        newHeartbeatInterval = self.heartbeat(self.autoHeartbeatInterval)
        self.autoHeartbeatInterval = newHeartbeatInterval
        # schedule event a little ahead of time
        self.autoHeartbeatTimer = Timer(self.autoHeartbeatInterval - 1, self.doAutoHeartbeat)
        self.autoHeartbeatTimer.start()

    def cancelSession(self) -> None:
        """
        Explicit stopping this session If an application is still in edit-mode, it will implicit do the same
        as "stopEditingApplication". If an import or export is still being processed, the session is kept alive
        until the import/export has finished, although the method returns immediately.

        :return: None
        """
        if self.autoHeartbeatTimer:
            self.autoHeartbeatTimer.cancel()
            self.autoHeartbeatTimer.join()
            self.autoHeartbeatTimer = None
        if self.connected:
            self.rpc.cancelSession()
            self.connected = False

    def exportConfig(self) -> bytearray:
        """
        Exports the whole configuration of the sensor-device and stores it at the desired path.

        :return: (bytearray) configuration as one data-blob :binary/base64
        """
        # increase heartbeat interval which will prevent a closed session after the "long" export progress
        self.heartbeat(heartbeatInterval=30)
        config = self.rpc.exportConfig()
        config_bytes = bytearray()
        config_bytes.extend(map(ord, str(config)))
        while self.getExportProgress() < 1.0:
            time.sleep(1)
        self.cleanupExport()
        self.mainAPI.waitForConfigurationDone()
        return config_bytes

    def importConfig(self, config: str, global_settings=True, network_settings=False, applications=True) -> None:
        """
        Import whole configuration, with the option to skip specific parts.

        :param config:              (str) The config file (*.o2d5xxcfg) as a Binary/base64 data
        :param global_settings:     (bool) Include Globale-Configuration (Name, Description, Location, ...)
        :param network_settings:    (bool) Include Network-Configuration (IP, DHCP, ...)
        :param applications:        (bool) Include All Application-Configurations
        :return:                    None
        """
        # This is required due to the long import progress which may take longer than 10 seconds (default)
        self.heartbeat(heartbeatInterval=30)
        if global_settings:
            self.rpc.importConfig(config, 0x0001)
        if network_settings:
            self.rpc.importConfig(config, 0x0002)
        if applications:
            self.rpc.importConfig(config, 0x0010)
        while self.getImportProgress() < 1.0:
            time.sleep(1)
        self.mainAPI.waitForConfigurationDone()

    def exportApplication(self, applicationIndex: int) -> bytearray:
        """
        Exports one application-config.

        :param applicationIndex: (int) application index
        :return: None
        """
        config = self.rpc.exportApplication(applicationIndex)
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
        if not self.OperatingMode:
            self.setOperatingMode(mode=1)
            index = int(self.rpc.importApplication(application))
            while self.getImportProgress() < 1.0:
                time.sleep(1)
            self.setOperatingMode(mode=0)
        else:
            index = int(self.rpc.importApplication(application))
            while self.getImportProgress() < 1.0:
                time.sleep(1)
        self.mainAPI.waitForConfigurationDone()
        return index

    def getImportProgress(self) -> float:
        """
        Get the progress of the asynchronous configuration import (yields 1.0 when the last import has finished).
        Returns xmlrpc errors occurring during import.

        :return: (float) progress (0.0 to 1.0)
        """
        try:
            result = self.rpc.getImportProgress()
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
            result = self.rpc.getExportProgress()
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
        self.rpc.cleanupExport()

    def getApplicationDetails(self, applicationIndex: [int, str]) -> dict:
        """
        The method returns details about the application line ApplicationType,
        TemplateInfo and Models with Type and Name.

        :param applicationIndex: (int) application Index
        :return: (dict) json-string containing application parameters, models and image settings
        """
        result = json.loads(self.rpc.getApplicationDetails(applicationIndex))
        return result

    def resetStatistics(self) -> None:
        """
        Resets the statistic data of current active application.

        :return: None
        """
        self.rpc.resetStatistics()
        self.mainAPI.waitForConfigurationDone()

    @staticmethod
    def writeApplicationConfigFile(applicationName: str, data: bytearray) -> None:
        """
        Stores the application data as an o2d5xxapp-file in the desired path.

        :param applicationName: (str) application name as str
        :param data: (bytearray) application data
        :return: None
        """
        extension = ".o2d5xxapp"
        filename, file_extension = os.path.splitext(applicationName)
        if not file_extension == extension:
            applicationName = filename + extension
        with open(applicationName, "wb") as f:
            f.write(data)

    @staticmethod
    def writeConfigFile(configName: str, data: bytearray) -> None:
        """
        Stores the config data as an o2d5xxcfg-file in the desired path.

        :param configName: (str) application file path as str
        :param data: (bytearray) application data
        :return: None
        """
        extension = ".o2d5xxcfg"
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
        result = self.readConfigFile(configFile=applicationFile)
        return result

    @firmwareWarning
    def readConfigFile(self, configFile: str) -> str:
        """
        Read and decode a device-config file.

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

    def setOperatingMode(self, mode) -> [None, Edit]:
        """
        Changes the operation mode of the device. Setting this to "edit" will enable the "EditMode"-object on RPC.

        :param mode: 1 digit 
                     0: run mode 
                     1: edit mode 
                     2: simulation mode (Not implemented!)
        :return: None or Edit object
        """
        if mode == 0:  # stop edit mode
            self.stopEdit()
        elif mode == 1:  # start edit mode
            return self.startEdit()
        else:
            raise ValueError("Invalid operating mode")

    def __getattr__(self, name):
        # Forward otherwise undefined method calls to XMLRPC proxy
        return getattr(self.rpc, name)
