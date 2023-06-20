import xmlrpc.client


class NetworkConfig(object):
    def __init__(self, editURL, mainAPI):
        self.editURL = editURL
        self.mainAPI = mainAPI
        self.networkConfigURL = self.editURL + "/device/network/"
        self.rpc = xmlrpc.client.ServerProxy(self.networkConfigURL)

    def __getattr__(self, name):
        # Forward otherwise undefined method calls to XMLRPC proxy
        return getattr(self.rpc, name)
