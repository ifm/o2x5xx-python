import socket
import xmlrpc.client
from contextlib import contextmanager
from threading import Timer
# from .session import Session
# from .edit import Edit
# from .application import Application
# from .imager import Imager

SOCKET_TIMEOUT = 10


class BaseProxy(object):
    """Base class for all proxies."""

    def __init__(self, url, timeout=SOCKET_TIMEOUT):
        """Initialize the actual xmlrpc.client.ServerProxy from given url.

        Args:
            url (str): url for xmlrpc.client.ServerProxy
        """
        try:
            socket.setdefaulttimeout(timeout)
            self.__transport = xmlrpc.client.Transport()
            self.__proxy = xmlrpc.client.ServerProxy(uri=url, transport=self.__transport)
        except TimeoutError:
            socket.setdefaulttimeout(None)

    @property
    def timeout(self):
        if self.__transport._connection[1]:
            return self.__transport._connection[1].timeout
        return socket.getdefaulttimeout

    @timeout.setter
    def timeout(self, value):
        if self.__transport._connection[1]:
            self.__transport._connection[1].timeout = value

    @property
    def proxy(self):
        return self.__proxy

    def __getattr__(self, name):
        """Pass given name to the actual xmlrpc.client.ServerProxy.

        Args:
            name (str): name of attribute
        Returns:
            Attribute of xmlrpc.client.ServerProxy
        """
        return self.__proxy.__getattr__(name)

    def close(self):
        self.__transport.close()
        self.__transport = None
        self.__proxy = None


class MainProxy(BaseProxy):
    """Proxy representing mainProxy."""

    def __init__(self, url, timeout, device):
        """Initialize main proxy member, device and baseURL.

        Args:
            url (str): url for BaseProxy
            device (obj): device
        """
        self.baseURL = url
        self.device = device

        super(MainProxy, self).__init__(url, timeout)

    @contextmanager
    def requestSession(self, password='', session_id='0' * 32):
        """Generator for requestSession to be used in with statement.

        Args:
            password (str): password for session
            session_id (str): session id
        """
        try:
            self.device._sessionId = self.__getattr__('requestSession')(password, session_id)
            self.device._sessionURL = self.baseURL + 'session_' + session_id + '/'
            self.device._sessionProxy = SessionProxy(url=self.device._sessionURL, device=self.device)
            yield
        finally:
            try:
                if self.device._sessionProxy.autoHeartbeatTimer:
                    self.device._sessionProxy.autoHeartbeatTimer.cancel()
            except AttributeError:
                pass
            self.device._sessionProxy.cancelSession()
            self.device._sessionProxy.close()
            self.device._sessionProxy = None
            self.device._sessionURL = None
            self.device._sessionId = None


class SessionProxy(BaseProxy):
    """Proxy representing sessionProxy."""

    def __init__(self, url, device, autoHeartbeat=True, autoHeartbeatInterval=30):
        self.baseURL = url
        self.device = device
        self.autoHeartbeat = autoHeartbeat
        self.autoHeartbeatInterval = autoHeartbeatInterval

        super().__init__(url)

        if self.autoHeartbeat:
            self.heartbeat(self.autoHeartbeatInterval)
            self.autoHeartbeatTimer = Timer(self.autoHeartbeatInterval - 1, self.doAutoHeartbeat)
            self.autoHeartbeatTimer.start()
        else:
            self.heartbeat(300)

        # self.device._session = Session(sessionProxy=self.proxy, device=self.device)

    def heartbeat(self, heartbeatInterval: int) -> int:
        """
        Extend the live time of edit-session If the given value is outside the range of "SessionTimeout",
        the saved default timeout will be used.

        :param heartbeatInterval: (int) requested timeout-interval till next heartbeat, in seconds
        :return: (int) the used timeout-interval, in seconds
        """
        result = self.proxy.heartbeat(heartbeatInterval)
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

    @contextmanager
    def setOperatingMode(self, mode):
        """Generator for setOperatingMode to be used in with statement.

        Args:
            mode (int): operating mode
        """
        try:
            self.__getattr__('setOperatingMode')(mode)
            self.device._editURL = self.baseURL + 'edit/'
            self.device._editProxy = EditProxy(url=self.device._editURL,
                                               device=self.device)
            yield
        finally:
            self.__getattr__('setOperatingMode')(0)
            self.device._editProxy.close()
            self.device._editURL = None
            self.device._editProxy = None


class EditProxy(BaseProxy):
    """Proxy representing editProxy."""

    def __init__(self, url, device):
        self.baseURL = url
        self.device = device

        super().__init__(url)

        # self.device._edit = Edit(editProxy=self.proxy,  device=self.device)

    @contextmanager
    def editApplication(self, app_index):
        """Generator for editApplication to be used in with statement.

        Args:
            app_index (int): application index
        """
        try:
            self.__getattr__('editApplication')(app_index)
            self.device._applicationURL = self.baseURL + "application/"
            self.device._applicationProxy = ApplicationProxy(url=self.device._applicationURL,
                                                             device=self.device)
            yield
        finally:
            self.__getattr__('stopEditingApplication')()
            self.device._applicationProxy.close()
            self.device._applicationURL = None
            self.device._applicationProxy = None


class ApplicationProxy(BaseProxy):
    """Proxy representing editProxy."""

    def __init__(self, url, device):
        self.baseURL = url
        self.device = device

        super().__init__(url)

        # self.device._application = Application(applicationProxy=self.proxy, device=self.device)

    @contextmanager
    def editImager(self, imager_index):
        """Generator for editImager to be used in with statement.

        Args:
            imager_index (int): imager index
        """
        try:
            imager_IDs = [int(x["Id"]) for x in self.proxy.getImagerConfigList()]
            if int(imager_index) not in imager_IDs:
                raise ValueError("Image index {} not available. Choose one imageIndex from following"
                                 "ImagerConfigList or create a new one with method createImagerConfig():\n{}"
                                 .format(imager_index, self.proxy.getImagerConfigList()))
            self.device._imagerURL = self.baseURL + 'imager_{0:03d}/'.format(imager_index)
            self.device._imagerProxy = ImagerProxy(url=self.device._imagerURL, device=self.device)
            yield
        finally:
            self.device._imagerProxy.close()
            self.device._imagerURL = None
            self.device._imager = None


class ImagerProxy(BaseProxy):
    """Proxy representing editProxy."""

    def __init__(self, url, device):
        self.baseURL = url
        self.device = device

        super().__init__(url)

        # self.device._imager = Imager(imagerProxy=self.proxy, device=self.device)
