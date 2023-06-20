from __future__ import (absolute_import, division, print_function, unicode_literals)
import xmlrpc.client
from .application import ApplicationConfig
# from .device_config import DeviceConfig
# from .network_config import NetworkConfig


class Edit(object):
    # https://stackoverflow.com/questions/51896862/how-to-create-singleton-class-with-arguments-in-python
    __instance = None

    def __new__(cls, *args, **kwargs):
        # print(cls.__instance)
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self, editURL, sessionAPI, mainAPI):
        self.url = editURL
        self.sessionAPI = sessionAPI
        self.mainAPI = mainAPI
        self.rpc = xmlrpc.client.ServerProxy(self.url)
        self.applicationURL = self.url + 'application/'
        self.deviceURL = self.url + 'device/'
        # self.device = xmlrpc.client.ServerProxy(self.deviceURL)
        self.networkURL = self.deviceURL + 'network/'
        # self.network = xmlrpc.client.ServerProxy(self.networkURL)
        self._device = None
        self._network = None
        self._application = None
        self._editApplicationIndexActive = None

    @property
    def application(self) -> ApplicationConfig:
        """
        Puts a specified Application into edit-status.
        This will attach an application-object to the RPC interface.
        The name of the object will be application independent.
        This does not change the "ActiveApplication"-parameter.

        :return: ApplicationConfig object
        """
        # self.rpc.editApplication(applicationIndex)
        self._application = ApplicationConfig(applicationURL=self.applicationURL,
                                              mainAPI=self.mainAPI)
        return self._application

    def editApplication(self, applicationIndex: int):
        """
        Puts a specified Application into edit-status. This will attach an application-object to the RPC interface.
        The name of the object will be application independent. This does not change the "ActiveApplication"-parameter.

        :param applicationIndex: (int) Application index
        :return: ApplicationConfig object
        """
        if not self.sessionAPI.editMode:
            self.sessionAPI.setOperationMode(mode=1)
        if not self._editApplicationIndexActive:
            if applicationIndex in range(1, 32):  # start edit mode for application
                self.rpc.editApplication(applicationIndex)
                self._application = ApplicationConfig(applicationURL=self.applicationURL,
                                                      mainAPI=self.mainAPI)
                self._editApplicationIndexActive = applicationIndex
                return self._application
            else:
                raise ValueError("Invalid application index")
        else:
            raise PermissionError("Application with index {} is already in Edit-Mode. Please first stop the Edit-Mode"
                                  "for this application.".format(self._editApplicationIndexActive))

    def stopEditingApplication(self) -> None:
        """
        Tells the device that editing this application was finished. Unsaved changed should be discarded.
        HINT: The device must also call this implicit, when an edit-session timed out or was closed by "cancelSession".

        :return: None
        """
        self.rpc.stopEditingApplication()
        self._application = None
        self._editApplicationIndexActive = None

    def createApplication(self) -> int:
        """
        Creates an "empty" application.

        :return: (int) Index of new application
        """
        appIndex = self.rpc.createApplication()
        return appIndex

    def copyApplication(self, applicationIndex: int) -> int:
        """
        Creates a new application by copying the configuration of another application.
        The device will generate an ID for the new application and put it on a free Index.

        :param applicationIndex: (int) Index of application which should be copied
        :return: (int) Index of new application
        """
        appIndex = self.rpc.copyApplication(applicationIndex)
        return appIndex

    def deleteApplication(self, applicationIndex: int) -> None:
        """
        Deletes the application from sensor. If the deleted application was the active one,
        the sensor will have no active application anymore until the user picks one.

        :param applicationIndex: (int) application index
        :return: None
        """
        self.rpc.deleteApplication(applicationIndex)

    def changeNameAndDescription(self, applicationIndex: int, name: str = "", description: str = ""):
        """
        Change the name and description of an application.

        :param applicationIndex: (int) Application index
        :param name: (str) new name of the application (utf8, max. 64 character)
        :param description: (str) new description of the application (utf8, max. 500 character)
        :return:
        """
        max_chars = 64
        if name.__len__() > max_chars:
            raise ValueError("Max. {} characters for name.".format(max_chars))
        max_chars = 500
        if description.__len__() > 500:
            raise ValueError("Max. {} characters for description".format(max_chars))
        self.rpc.changeNameAndDescription(applicationIndex, name, description)

    def moveApplications(self, applicationIndexFrom: int, applicationIndexTo: int) -> None:
        """
        Moves an application with know list index to other index.

        :param applicationIndexFrom: (int) application id in application list
        :param applicationIndexTo: (int) desired application id in application list
        :return: None
        """
        app_list = self.mainAPI.getApplicationList()
        move_list = []
        for app in app_list:
            if int(app["Index"]) == int(applicationIndexFrom):
                app["Index"] = int(applicationIndexTo)
            move_list.append({'Id': app['Id'], 'Index': app['Index']})
        self.rpc.moveApplications(move_list)

    def __getattr__(self, name):
        # Forward otherwise undefined method calls to XMLRPC proxy
        return getattr(self.rpc, name)
