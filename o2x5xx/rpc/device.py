import xmlrpc.client


class DeviceConfig(object):
    def __init__(self, editURL, mainAPI):
        self.editURL = editURL
        self.mainAPI = mainAPI
        self.deviceConfigURL = self.editURL + "/device/"
        self.rpc = xmlrpc.client.ServerProxy(self.deviceConfigURL)

    def activatePassword(self, password) -> None:
        """
        Set a password and activate it for the next edit-session.
        Making this change presistant requires to call "save" on the DeviceConfig.
        Requirement SW: 660606-5088

        :param password: (str) password for the next edit-session
        :return: None
        """
        self.rpc.activatePassword(password)

    def disablePassword(self):
        """
        Disables the password-protection.
        Making this change presistant requires to call "save" on the DeviceConfig.
        Requirement SW: 660606-5089

        :return: None
        """
        self.rpc.disablePassword()

    def save(self) -> None:
        """
        Store current configuration in persistent memory.
        If this is not called after changing device-parameters, changes will get lost on reboot.

        :return: None
        """
        self.rpc.save()

    def __getattr__(self, name):
        # Forward otherwise undefined method calls to XMLRPC proxy
        return getattr(self.rpc, name)
