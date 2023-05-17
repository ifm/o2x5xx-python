from __future__ import (absolute_import, division, print_function, unicode_literals)
import xmlrpc.client
# from .application import *


class Edit:
    def __init__(self, edit_url):
        self.url = edit_url
        self.rpc = xmlrpc.client.ServerProxy(self.url)
        self.deviceURL = self.url + 'device/'
        self.device = xmlrpc.client.ServerProxy(self.deviceURL)
        self.networkURL = self.deviceURL + 'network/'
        self.network = xmlrpc.client.ServerProxy(self.networkURL)
        self.application = None

    # def editApplication(self, app_index):
    #     self.rpc.editApplication(app_index)
    #     self.application = Application(self.url + 'application/')
    #     return self.application
    #
    # def stopEditingApplication(self):
    #     self.rpc.stopEditingApplication()
    #     self.application = None

    def __getattr__(self, name):
        # Forward otherwise undefined method calls to XMLRPC proxy
        return getattr(self.rpc, name)
