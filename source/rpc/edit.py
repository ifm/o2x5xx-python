from .proxy import ApplicationProxy


class Edit(object):
    """
    Edit object
    """

    def __init__(self, editProxy, device):
        self._editProxy = editProxy
        self._device = device

    def editApplication(self, app_index):
        """Generator for editApplication to be used in with statement.

        Args:
            app_index (int): application index
        """
        self.__getattr__('editApplication')(app_index)
        _applicationURL = self._editProxy.baseURL + "application/"
        setattr(self._device, "_applicationURL", _applicationURL)
        _applicationProxy = ApplicationProxy(url=_applicationURL, device=self._device)
        setattr(self._device, "_applicationProxy", _applicationProxy)
        return self._device.application

    def createApplication(self, deviceType="WithModels") -> int:
        """
        Creates an "empty" application.

        :param deviceType: (str) could be "Camera", "WithModels"
        :return: (int) Index of new application
        """
        if deviceType not in ["Camera", "WithModels"]:
            raise AttributeError("Device type must be either value \"Camera\" or \"WithModels\"!")
        appIndex = self._editProxy.createApplication(deviceType)
        return appIndex

    def copyApplication(self, applicationIndex: int) -> int:
        """
        Creates a new application by copying the configuration of another application.
        The device will generate an ID for the new application and put it on a free Index.

        :param applicationIndex: (int) Index of application which should be copied
        :return: (int) Index of new application
        """
        appIndex = self._editProxy.copyApplication(applicationIndex)
        return appIndex

    def deleteApplication(self, applicationIndex: int) -> None:
        """
        Deletes the application from sensor. If the deleted application was the active one,
        the sensor will have no active application anymore until the user picks one.

        :param applicationIndex: (int) application index
        :return: None
        """
        self._editProxy.deleteApplication(applicationIndex)

    def changeNameAndDescription(self, applicationIndex: int, name: str = "", description: str = "") -> None:
        """
        Change the name and description of an application.

        :param applicationIndex: (int) Application index
        :param name: (str) new name of the application (utf8, max. 64 character)
        :param description: (str) new description of the application (utf8, max. 500 character)
        :return: None
        """
        max_chars = 64
        if name.__len__() > max_chars:
            raise ValueError("Max. {} characters for name.".format(max_chars))
        max_chars = 500
        if description.__len__() > 500:
            raise ValueError("Max. {} characters for description".format(max_chars))
        self._editProxy.changeNameAndDescription(applicationIndex, name, description)

    def moveApplications(self, applicationIndexFrom: int, applicationIndexTo: int) -> None:
        """
        Moves an application with know list index to other index.

        :param applicationIndexFrom: (int) application id in application list
        :param applicationIndexTo: (int) desired application id in application list
        :return: None
        """
        app_list = self._device.mainProxy.getApplicationList()
        move_list = []
        for app in app_list:
            if int(app["Index"]) == int(applicationIndexFrom):
                app["Index"] = int(applicationIndexTo)
            move_list.append({'Id': app['Id'], 'Index': app['Index']})
        self._editProxy.moveApplications(move_list)

    def __getattr__(self, name):
        """Pass given name to the actual xmlrpc.client.ServerProxy.

        Args:
            name (str): name of attribute
        Returns:
            Attribute of xmlrpc.client.ServerProxy
        """
        return self._editProxy.__getattr__(name)
