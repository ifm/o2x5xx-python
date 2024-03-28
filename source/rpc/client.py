from .proxy import MainProxy, SessionProxy, EditProxy, ApplicationProxy, ImagerProxy
from .session import Session
from .edit import Edit
from .application import Application
from .imager import Imager
from .utils import timeout
from ..device.client import (O2x5xxPCICDevice, SOCKET_TIMEOUT)
from ..static.devices import DevicesMeta
import xmlrpc.client
import json
import io
import time
import numpy as np
import matplotlib.image as mpimg


class O2x5xxRPCDevice(object):
    """
    Main API class
    """
    def __init__(self, address="192.168.0.69", api_path="/api/rpc/v1/", timeout=SOCKET_TIMEOUT):
        self.address = address
        self.api_path = api_path
        self.timeout = timeout
        self.baseURL = "http://" + self.address + self.api_path
        self.mainURL = self.baseURL + "com.ifm.efector/"
        self.mainProxy = MainProxy(url=self.mainURL, timeout=self.timeout, device=self)
        self.tcpIpPort = int(self.getParameter("PcicTcpPort"))
        self.deviceMeta = self._getDeviceMeta()
        self._session = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.mainProxy.close()

    @property
    def sessionProxy(self) -> SessionProxy:
        return getattr(self, "_sessionProxy")

    @property
    def editProxy(self) -> [EditProxy, None]:
        try:
            return getattr(self, "_editProxy")
        except AttributeError:
            return None

    @property
    def applicationProxy(self) -> ApplicationProxy:
        return getattr(self, "_applicationProxy")

    @property
    def imagerProxy(self) -> ImagerProxy:
        return getattr(self, "_imagerProxy")

    @property
    def session(self) -> Session:
        if self.sessionProxy:
            return Session(sessionProxy=self.sessionProxy, device=self)

    @property
    def edit(self) -> Edit:
        if self.editProxy:
            return Edit(editProxy=self.editProxy,  device=self)
        else:
            raise AttributeError("No editProxy available! Please first create an editProxy "
                                 "with method self.device.session.requestOperatingMode(Mode=1) before using Edit!")

    @property
    def application(self) -> Application:
        if self.applicationProxy:
            return Application(applicationProxy=self.applicationProxy, device=self)

    @property
    def imager(self) -> Imager:
        if self.imagerProxy:
            return Imager(imagerProxy=self.imagerProxy, device=self)

    def _getDeviceMeta(self):
        _deviceType = self.getParameter(value="DeviceType")
        result = DevicesMeta.getData(key="DeviceType", value=_deviceType)
        if not result:
            _articleNumber = self.getParameter(value="ArticleNumber")
            raise TypeError("Device {} with DeviceType {} is not supported by this library!"
                            .format(_articleNumber, _deviceType))
        return result

    def getParameter(self, value: str) -> str:
        """
        Returns the current value of the parameter. For an overview which parameters can be request use
        the method get_all_parameters().

        :param value: (str) name of the input parameter
        :return: (str) value of parameter
        """
        try:
            result = self.mainProxy.getParameter(value)
            return result
        except xmlrpc.client.Fault as e:
            if e.faultCode == 101000:
                available_parameters = list(self.getAllParameters().keys())
                print("Here is a list of available parameters:\n{}".format(available_parameters))
            raise e

    def getAllParameters(self) -> dict:
        """
        Returns all parameters of the object in one data-structure.

        :return: (dict) name contains parameter-name, value the stringified parameter-value
        """
        result = self.mainProxy.getAllParameters()
        return result

    def getSWVersion(self) -> dict:
        """
        Returns version-information of all software components.

        :return: (dict) struct of strings
        """
        result = self.mainProxy.getSWVersion()
        return result

    def getHWInfo(self) -> dict:
        """
        Returns hardware-information of all components.

        :return: (dict) struct of strings
        """
        result = self.mainProxy.getHWInfo()
        return result

    def getDmesgData(self) -> str:
        """
        Returns content of the message buffer of the kernel.

        :return: (str) List of kernel messages
        """
        result = self.mainProxy.getDmesgData()
        return result

    def getClientCompatibilityList(self) -> list:
        """
        The device must be able to define which type and version of operating program is compatible with it.

        :return: (list) Array of strings
        """
        result = self.mainProxy.getClientCompatibilityList()
        return result

    def getApplicationList(self) -> list:
        """
        Delivers basic information of all Application stored on the device.

        :return: (dict) array list of structs
        """
        result = self.mainProxy.getApplicationList()
        return result

    def reboot(self, mode: int = 0) -> None:
        """
        Reboot system, parameter defines which mode/system will be booted.

        :param mode: (int) type of system that should be booted after shutdown
                      0: productive-mode (default)
                      1: recovery-mode (not implemented)
        :return: None
        """
        if mode == 0:
            print("Rebooting sensor {} ...".format(self.getParameter(value="Name")))
            self.mainProxy.reboot(mode)
        else:
            raise ValueError("Reboot mode {} not available.".format(str(mode)))

    def switchApplication(self, applicationIndex: int) -> None:
        """
        Change active application when device is in run-mode.

        :param applicationIndex: (int) Index of new application (Range 1-32)
        :return: None
        """
        self.mainProxy.switchApplication(applicationIndex)
        self.waitForConfigurationDone()

    def getTraceLogs(self, nLogs: int = 0) -> list:
        """
        Returns entries from internal log buffer of device. These can contain informational, error or trace messages.

        :param nLogs: (int) max. number of logs to fetch from IOM
                            0: all logs are fetched
        :return: (list) Array of strings
        """
        result = self.mainProxy.getTraceLogs(nLogs)
        return result

    def getApplicationStatisticData(self, applicationIndex: int) -> dict:
        """
        Returns a Chunk which contains the statistic data requested.The data is itself is updated every 15 seconds.
        The main intend is to request Statistics of inactive applications.
        For the latest statistics refer to PCIC instead.

        :param applicationIndex: (int) Index of application (Range 1-32)
        :return: (dict)
        """
        result = json.loads(self.mainProxy.getApplicationStatisticData(applicationIndex))
        return result

    def getReferenceImage(self) -> np.ndarray:
        """
        Returns the active application's reference image, if there is no fault.

        :return: (np.ndarray) a JPEG decompressed image
        """
        b = bytearray()
        b.extend(map(ord, str(self.mainProxy.getReferenceImage())))
        result = mpimg.imread(io.BytesIO(b), format='jpg')
        return result

    def isConfigurationDone(self) -> bool:
        """
        After an application (or imager configuration or model) parameter has been changed,
        this method can be used to check when the new configuration has been applied within the imager process.

        :return: (bool) True or False
        """
        result = self.mainProxy.isConfigurationDone()
        return result

    def waitForConfigurationDone(self):
        """
        After an application (or imager configuration or model) parameter has been changed,
        this method can be used to check when the new configuration has been applied within the imager process.
        This call blocks until configuration has been finished.

        :return: None
        """
        self.mainProxy.waitForConfigurationDone()

    def measure(self, measureInput: dict) -> dict:
        """
        Measure geometric properties according to the currently valid calibration.

        :param measureInput: (dict) measure input is a stringified json object
        :return: (dict) measure result
        """
        input_stringified = json.dumps(measureInput)
        result = json.loads(self.mainProxy.measure(input_stringified))
        return result

    def trigger(self) -> str:
        """
        Executes trigger and read answer.

        :return: (str) process interface output (TCP/IP)
        """
        with O2x5xxPCICDevice(address=self.address, port=self.tcpIpPort) as pcicDevice:
            while self.getParameter("OperatingMode") != "0":
                Warning("Sensor is not in Run Mode. Please finish parametrization first.")
                time.sleep(0.1)
            self.mainProxy.trigger()
            # This is required since there is no lock for application evaluation process within the trigger()-method.
            # After an answer is provided by the PCIC interface you can be sure,
            # that the trigger count was incremented correctly and the evaluation process finished.
            ticket, answer = pcicDevice.read_next_answer()
            self.waitForConfigurationDone()
            pcicDevice.close()
            return answer.decode()

    @timeout(2)
    def doPing(self) -> str:
        """
        Ping sensor device and check reachability in network.

        :return: - "up" sensor is reachable through network
                 - "down" sensor is not reachable through network
        """
        result = self.mainProxy.doPing()
        return result

    def requestSession(self, password='', session_id='0' * 32) -> Session:
        """
        Request a session-object for access to the configuration and for changing device operating-mode.
        This should block parallel editing and allows to put editing behind password.
        The ID could optionally be defined from the external system, but it must be the defined format (32char "hex").
        If it is called with only one parameter, the device will generate a SessionID.

        :param password: (str) session password (optional)
        :param session_id: (str) session ID (optional)
        :return: Session object
        """
        _sessionId = self.__getattr__('requestSession')(password, session_id)
        setattr(self, "_sessionId", _sessionId)
        _sessionURL = self.mainURL + 'session_' + _sessionId + '/'
        setattr(self, "_sessionURL", _sessionURL)
        _sessionProxy = SessionProxy(url=_sessionURL, device=self)
        setattr(self, "_sessionProxy", _sessionProxy)
        return self.session

    def __getattr__(self, name):
        """Pass given name to the actual xmlrpc.client.ServerProxy.

        Args:
            name (str): name of attribute
        Returns:
            Attribute of xmlrpc.client.ServerProxy
        """
        return self.mainProxy.__getattr__(name)
