import xmlrpc.client
import json
import ast
import io
import os
import time
import base64
import numpy as np
import matplotlib.image as mpimg
from .session import Session
# import requests
# import functools


class O2x5xxRPCDevice(object):
    def __init__(self, address="192.168.0.69", api_path="/api/rpc/v1/"):
        self.baseURL = "http://" + address + api_path
        self.mainURL = self.baseURL + "com.ifm.efector/"
        try:
            self.rpc = xmlrpc.client.ServerProxy(self.mainURL)
        except Exception as e:
            print(e)

        # self.timeout = 2
        # self.request = requests.Session()
        # self.request.request = functools.partial(self.request.request, timeout=self.timeout)

    def get_parameter(self, parameter_name: str) -> str:
        """
        Returns the current value of the parameter. For a overview which parameters can be request use
        the method get_all_parameters().

        :param parameter_name: (str) name of the input parameter
        :return: (str) value of parameter
        """
        try:
            result = self.rpc.getParameter(parameter_name)
            return result
        except xmlrpc.client.Fault as e:
            if e.faultCode == 101000:
                available_parameters = list(self.get_all_parameters().keys())
                print("Here is a list of available parameters:\n{}".format(available_parameters))
            raise e

    def get_all_parameters(self) -> dict:
        """
        Returns all parameters of the object in one data-structure.

        :return: (dict) name contains parameter-name, value the stringified parameter-value
        """
        result = self.rpc.getAllParameters()
        return result

    def get_sw_version(self) -> dict:
        """
        Returns version-information of all software components.

        :return: (dict) struct of strings
        """
        result = self.rpc.getSWVersion()
        return result

    def get_hw_info(self) -> dict:
        """
        Returns hardware-information of all components.

        :return: (dict) struct of strings
        """
        result = self.rpc.getHWInfo()
        return result

    def get_application_list(self) -> list:
        """
        Delivers basic information of all Application stored on the device.

        :return: (dict) array list of structs
        """
        result = self.rpc.getApplicationList()
        return result

    def reboot(self, mode: int = 0) -> None:
        """
        Reboot system, parameter defines which mode/system will be booted.

        :param mode: (int) type of system that should be booted after shutdown <br />
                      0: productive-mode (default) <br />
                      1: recovery-mode (not implemented)
        :return: None
        """
        if mode == 0:
            print("Rebooting sensor {} ...".format(self.get_parameter(parameter_name="Name")))
            self.rpc.reboot(mode)
        else:
            raise ValueError("Reboot mode {} not available.".format(str(mode)))

    def is_configuration_done(self) -> bool:
        """
        After an application (or imager configuration or model) parameter has been changed,
        this method can be used to check when the new configuration has been applied within the imager process.

        :return: (bool) True or False
        """
        result = self.rpc.isConfigurationDone()
        return result

    def wait_for_configuration_done(self):
        """
        After an application (or imager configuration or model) parameter has been changed,
        this method can be used to check when the new configuration has been applied within the imager process.
        This call blocks until configuration has been finished.

        :return: None
        """
        self.rpc.waitForConfigurationDone()

    def switch_application(self, application_index: int) -> None:
        """
        Change active application when device is in run-mode.

        :param application_index: (int) Index of new application (Range 1-32)
        :return: None
        """
        self.rpc.switchApplication(application_index)

    def get_application_statistic_data(self, application_id: int) -> dict:
        """
        Returns a Chunk which contains the statistic data requested.The data is itself is updated every 15 seconds.
        The main intend is to request Statistics of inactive applications.
        For the latest statistics refer to PCIC instead.

        :param application_id: (int) Index of application (Range 1-32)
        :return: dict
        """
        result = self.rpc.getApplicationStatisticData(application_id)
        result = ast.literal_eval(result)
        return result

    def reset_statistics(self) -> None:
        """
        Resets the statistic data of current active application.

        :return: None
        """
        session = self._requestSession()
        try:
            session.resetStatistics()
        finally:
            session.cancelSession()

    def get_reference_image(self) -> np.ndarray:
        """
        Returns the active application's reference image, if there is no fault.

        :return: (np.ndarray) a JPEG decompressed image
        """
        b = bytearray()
        b.extend(map(ord, str(self.rpc.getReferenceImage())))
        result = mpimg.imread(io.BytesIO(b), format='jpg')
        return result

    def measure(self, input_parameter: dict) -> dict:
        """
        Measure geometric properties according to the currently valid calibration.

        :param input_parameter: (dict) measure input is a stringified json object
        :return: (dict) measure result
        """
        input_stringified = json.dumps(input_parameter)
        result = self.rpc.measure(input_stringified)
        result = ast.literal_eval(result)
        return result

    def trigger(self) -> None:
        """
        Executes trigger.

        :return: None
        """
        try:
            self.rpc.trigger()
        except xmlrpc.client.Fault as fault:
            # error code 101024: device is in an operation mode which does not allow to perform a software trigger
            if fault.faultCode == 101024:
                time.sleep(0.1)
                self.trigger()

    def doPing(self) -> str:
        """
        Ping sensor device and check reachability in network.

        :return: - "up" sensor is reachable through network <br />
                 - "down" sensor is not reachable through network
        """
        result = self.rpc.doPing()
        return result

    def _requestSession(self, password: str = "", session_id: str = ""):
        """
        Request a session-object for access to the configuration and for changing device operating-mode.

        :param password: (str) session password (optional)
        :param session_id: (str) session ID (optional)
        :return:
        """
        self.sessionID = self.rpc.requestSession(password, session_id)
        self.sessionURL = self.mainURL + 'session_' + self.sessionID + '/'
        self.session = Session(self.sessionURL)
        return self.session

    def _export_application_bytes(self, application_id):
        """
        Exports one application-config.

        :param application_id: (int) application index
        :return: (data-blob :binary/base64) application-config
        """
        session = self._requestSession()
        try:
            config = session.exportApplication(application_id)
            b = bytearray()
            b.extend(map(ord, str(config)))
            return b
        finally:
            session.cancelSession()

    def export_application(self, application_file, application_id):
        """
        Exports one application-config and stores it as an o2x5xxapp-file in the desired path.

        :param application_file: (str) application file path as str
        :param application_id: (int) application index
        :return: None
        """
        application_bytes = self._export_application_bytes(application_id)
        with open(application_file, "wb") as f:
            f.write(application_bytes)

    def import_application(self, application) -> int:
        """
        Imports an application-config and creates a new application with it.

        :param application: (application-config as one-data-blob: binary/base64 OR application file path as str)
        :return: (int) index of new application in list
        """
        session = self._requestSession()
        try:
            if isinstance(application, str):
                if os.path.exists(os.path.dirname(application)):
                    with open(application, "rb") as f:
                        encodedZip = base64.b64encode(f.read())
                        session.setOperatingMode(mode=1)
                        application_decoded = encodedZip.decode()
                else:
                    raise FileExistsError("Application file {} does not exist!".format(application))
            elif isinstance(application, bytearray):
                application_decoded = application
            else:
                raise ValueError("Application {} not usable for importing the application!".format(application))
            index = int(session.importApplication(application_decoded))
            return index
        finally:
            session.setOperatingMode(mode=0)
            session.cancelSession()

    def delete_application(self, application_id: int) -> None:
        """
        Deletes the application from sensor. If the deleted application was the active one,
        the sensor will have no active application anymore until the user picks one.

        :param application_id: (int) application index
        :return: None
        """
        session = self._requestSession()
        try:
            session.setOperatingMode(mode=1)
            session.edit.deleteApplication(application_id)
        finally:
            session.setOperatingMode(mode=0)
            session.cancelSession()

    def move_applications(self, id_from: int, id_into: int) -> None:
        """
        Moves an application with know list index to other index.

        :param id_from: (int) application id in application list
        :param id_into: (int) desired application id in application list
        :return: None
        """
        session = self._requestSession()
        try:
            session.setOperatingMode(mode=1)
            app_list = self.get_application_list()
            move_list = []
            for app in app_list:
                if int(app["Index"]) == int(id_from):
                    app["Index"] = int(id_into)
                move_list.append({'Id': app['Id'], 'Index': app['Index']})
            session.edit.moveApplications(move_list)
        finally:
            session.setOperatingMode(mode=0)
            session.cancelSession()

    def _export_config_bytes(self) -> bytearray:
        """
        Exports the whole configuration of the sensor-device.

        :return: (data-blob :binary/base64) configuration
        """
        session = self._requestSession()
        try:
            config = session.exportConfig()
            b = bytearray()
            b.extend(map(ord, str(config)))
            return b
        finally:
            session.cancelSession()

    def export_config(self, config_file) -> None:
        """
        Exports the whole configuration of the sensor-device and stores it at the desired path.

        :param config_file: (str) path where the config file will be stored
        :return: None
        """
        config_bytes = self._export_config_bytes()
        with open(config_file, "wb") as f:
            f.write(config_bytes)

    def import_config(self, config, global_settings=True, network_settings=False, applications=True) -> None:
        """
        Import whole configuration, with the option to skip specific parts.

        :param config:              The config file (*.o2d5xxcfg) as string path or Binary/base64 data
        :param global_settings:     (bool) Include Globale-Configuration (Name, Description, Location, ...)
        :param network_settings:    (bool) Include Network-Configuration (IP, DHCP, ...)
        :param applications:        (bool) Include All Application-Configurations
        :return:                    None
        """
        session = self._requestSession()
        try:
            if isinstance(config, str):
                if os.path.exists(os.path.dirname(config)):
                    with open(config, "rb") as f:
                        encodedZip = base64.b64encode(f.read())
                        config_decoded = encodedZip.decode()
                else:
                    raise FileExistsError("Config file {} does not exist!".format(config))
            elif isinstance(config, bytearray):
                config_decoded = config  # .decode()
            else:
                raise ValueError("Config {} not usable for importing the configuration!".format(config))
            if global_settings:
                session.importConfig(config_decoded, 0x0001)
            if network_settings:
                session.importConfig(config_decoded, 0x0002)
            if applications:
                session.importConfig(config_decoded, 0x0010)
        finally:
            session.cancelSession()
