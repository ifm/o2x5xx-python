import xmlrpc.client
from contextlib import contextmanager
from threading import Timer

SOCKET_TIMEOUT = 10


class BaseProxy(object):
    """Base class for all proxies."""

    def __init__(self, url, device, timeout=SOCKET_TIMEOUT):
        """Initialize the actual xmlrpc.client.ServerProxy from given url.

        Args:
            url (str): url for xmlrpc.client.ServerProxy
            device (obj): device
            timeout (float): Timeout values which is valid for the BaseProxy.
            Argument can be a non-negative floating point number expressing seconds, or None.
            If None, SOCKET_TIMEOUT value is used as default
        """
        try:
            self.__proxy = xmlrpc.client.ServerProxy(uri=url, allow_none=True)
            self.__transport = self.__proxy("transport")
            self.__transport.make_connection(host=device.address)
            getattr(self.__transport, "_connection")[1].timeout = timeout
        except TimeoutError:
            self.close()

    @property
    def timeout(self):
        if getattr(self.__transport, "_connection")[1]:
            return getattr(self.__transport, "_connection")[1].timeout

    @timeout.setter
    def timeout(self, value):
        if getattr(self.__transport, "_connection")[1]:
            getattr(self.__transport, "_connection")[1].timeout = value

    @property
    def proxy(self):
        return self.__proxy

    def close(self):
        self.__transport.close()
        self.__transport = None
        self.__proxy = None


class MainProxy(BaseProxy):
    """Proxy representing mainProxy."""

    def __init__(self, url, device, timeout):
        """Initialize main proxy member, device and baseURL.

        Args:
            url (str): url for BaseProxy
            device (obj): device
            timeout (float): Timeout values which is valid for the MainProxy.
            Argument can be a non-negative floating point number expressing seconds, or None.
            If None, SOCKET_TIMEOUT value is used as default
        """
        self.baseURL = url
        self.device = device

        super(MainProxy, self).__init__(url, device, timeout)

    @contextmanager
    def requestSession(self, password='', session_id='0' * 32, timeout=SOCKET_TIMEOUT):
        """Generator for requestSession to be used in with statement.

        Args:
            password (str): password for session
            session_id (str): session id
            timeout (float): Timeout values which is valid for the SessionProxy.
            Argument can be a non-negative floating point number expressing seconds, or None.
            If None, SOCKET_TIMEOUT value is used as default
        """
        try:
            self.device._sessionId = self.proxy.requestSession(password, session_id)
            self.device._sessionURL = self.baseURL + 'session_' + session_id + '/'
            self.device._sessionProxy = SessionProxy(url=self.device._sessionURL,
                                                     device=self.device, timeout=timeout)
            yield
        finally:
            try:
                if self.device._sessionProxy.autoHeartbeatTimer:
                    self.device._sessionProxy.autoHeartbeatTimer.cancel()
            except AttributeError:
                pass
            self.device._sessionProxy.proxy.cancelSession()
            self.device._sessionProxy.close()
            self.device._sessionProxy = None
            self.device._sessionURL = None
            self.device._sessionId = None


class SessionProxy(BaseProxy):
    """Proxy representing sessionProxy."""

    def __init__(self, url, device, timeout=SOCKET_TIMEOUT, autoHeartbeat=True, autoHeartbeatInterval=30):
        self.baseURL = url
        self.device = device
        self.autoHeartbeat = autoHeartbeat
        self.autoHeartbeatInterval = autoHeartbeatInterval

        super().__init__(url, device, timeout)

        if self.autoHeartbeat:
            self.heartbeat(self.autoHeartbeatInterval)
            self.autoHeartbeatTimer = Timer(self.autoHeartbeatInterval - 1, self.doAutoHeartbeat)
            self.autoHeartbeatTimer.start()
        else:
            self.heartbeat(300)

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
    def setOperatingMode(self, mode, timeout=SOCKET_TIMEOUT):
        """Generator for setOperatingMode to be used in with statement.

        Args:
            mode (int): operating mode
            timeout (float): Timeout values which is valid for the EditProxy.
            Argument can be a non-negative floating point number expressing seconds, or None.
            If None, SOCKET_TIMEOUT value is used as default
        """
        try:
            self.proxy.setOperatingMode(mode)
            self.device._editURL = self.baseURL + 'edit/'
            self.device._editProxy = EditProxy(url=self.device._editURL, device=self.device, timeout=timeout)
            yield
        finally:
            self.proxy.setOperatingMode(0)
            self.device._editProxy.close()
            self.device._editURL = None
            self.device._editProxy = None


class EditProxy(BaseProxy):
    """Proxy representing editProxy."""

    def __init__(self, url, device, timeout=SOCKET_TIMEOUT):
        self.baseURL = url
        self.device = device

        super().__init__(url, device, timeout)

    @contextmanager
    def editApplication(self, app_index, timeout=SOCKET_TIMEOUT):
        """Generator for editApplication to be used in with statement.

        Args:
            app_index (int): application index
            timeout (float): Timeout values which is valid for the ApplicationProxy.
            Argument can be a non-negative floating point number expressing seconds, or None.
            If None, SOCKET_TIMEOUT value is used as default
        """
        try:
            self.proxy.editApplication(app_index)
            self.device._applicationURL = self.baseURL + "application/"
            self.device._applicationProxy = ApplicationProxy(url=self.device._applicationURL, device=self.device,
                                                             timeout=timeout)
            yield
        finally:
            self.proxy.stopEditingApplication()
            self.device._applicationProxy.close()
            self.device._applicationURL = None
            self.device._applicationProxy = None


class ApplicationProxy(BaseProxy):
    """Proxy representing editProxy."""

    def __init__(self, url, device, timeout=SOCKET_TIMEOUT):
        self.baseURL = url
        self.device = device

        super().__init__(url, device, timeout)

    @contextmanager
    def editImager(self, imager_index, timeout=SOCKET_TIMEOUT):
        """Generator for editImager to be used in with statement.

        Args:
            imager_index (int): imager index
            timeout (float): Timeout values which is valid for the ImagerProxy.
            Argument can be a non-negative floating point number expressing seconds, or None.
            If None, SOCKET_TIMEOUT value is used as default
        """
        try:
            imager_IDs = [int(x["Id"]) for x in self.proxy.getImagerConfigList()]
            if int(imager_index) not in imager_IDs:
                raise ValueError("Image index {} not available. Choose one imageIndex from following"
                                 "ImagerConfigList or create a new one with method createImagerConfig():\n{}"
                                 .format(imager_index, self.proxy.getImagerConfigList()))
            self.device._imagerURL = self.baseURL + 'imager_{0:03d}/'.format(imager_index)
            self.device._imagerProxy = ImagerProxy(url=self.device._imagerURL, device=self.device,
                                                   timeout=timeout)
            yield
        finally:
            self.device._imagerProxy.close()
            self.device._imagerURL = None
            self.device._imager = None


class ImagerProxy(BaseProxy):
    """Proxy representing editProxy."""

    def __init__(self, url, device, timeout=SOCKET_TIMEOUT):
        self.baseURL = url
        self.device = device

        super().__init__(url, device, timeout)
