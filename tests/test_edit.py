from unittest import TestCase
from source import O2x5xxRPCDevice
from tests.utils import *
from .config import *


class TestRPC_EditObject(TestCase):
    config_backup = None
    config_file = None
    app_import_file = None
    active_application_backup = None

    @classmethod
    def setUpClass(cls) -> None:
        with O2x5xxRPCDevice(deviceAddress) as rpc:
            with rpc.mainProxy.requestSession():
                cls.config_backup = rpc.session.exportConfig()
                cls.active_application_backup = rpc.getParameter("ActiveApplication")
                cls.config_file = getImportSetupByPinLayout(rpc=rpc)['config_file']
                cls.app_import_file = getImportSetupByPinLayout(rpc=rpc)['app_import_file']
                _configFile = rpc.session.readDeviceConfigFile(configFile=cls.config_file)
                rpc.session.importConfig(_configFile, global_settings=True, network_settings=False,
                                         applications=True)

    @classmethod
    def tearDownClass(cls) -> None:
        with O2x5xxRPCDevice(deviceAddress) as rpc:
            with rpc.mainProxy.requestSession():
                rpc.session.importConfig(cls.config_backup, global_settings=True, network_settings=False,
                                         applications=True)
                if cls.active_application_backup != "0":
                    rpc.switchApplication(cls.active_application_backup)

    def setUp(self) -> None:
        with O2x5xxRPCDevice(deviceAddress) as self.rpc:
            self.rpc.switchApplication(1)

    def tearDown(self) -> None:
        pass

    def test_editApplication(self):
        with O2x5xxRPCDevice(deviceAddress) as self.rpc, self.rpc.mainProxy.requestSession():
            with self.rpc.sessionProxy.setOperatingMode(mode=1), self.rpc.editProxy.editApplication(app_index=1):
                self.assertTrue(self.rpc.application)

    def test_createApplication(self):
        with O2x5xxRPCDevice(deviceAddress) as self.rpc, self.rpc.mainProxy.requestSession():
            with self.rpc.sessionProxy.setOperatingMode(mode=1):
                newApplicationIndex = self.rpc.edit.createApplication()
                app_idx = [x["Index"] for x in self.rpc.getApplicationList()]
                self.assertTrue(newApplicationIndex in app_idx)
                self.rpc.edit.deleteApplication(applicationIndex=newApplicationIndex)

    def test_copyApplication(self):
        with O2x5xxRPCDevice(deviceAddress) as self.rpc, self.rpc.mainProxy.requestSession():
            with self.rpc.sessionProxy.setOperatingMode(mode=1):
                newAppIndex = self.rpc.edit.copyApplication(applicationIndex=1)
                app_idx = [x["Index"] for x in self.rpc.getApplicationList()]
                self.assertTrue(newAppIndex in app_idx)
                self.rpc.edit.deleteApplication(applicationIndex=newAppIndex)

    def test_deleteApplication(self):
        with O2x5xxRPCDevice(deviceAddress) as self.rpc, self.rpc.mainProxy.requestSession():
            with self.rpc.sessionProxy.setOperatingMode(mode=1):
                app = self.rpc.session.readApplicationConfigFile(self.app_import_file)
                app_idx_list = []
                for i in range(2):
                    app_index = self.rpc.session.importApplication(application=app)
                    app_idx_list.append(app_index)
                for x in app_idx_list:
                    self.rpc.edit.deleteApplication(applicationIndex=x)
                app_idx = [x["Index"] for x in self.rpc.getApplicationList()]
                for x in app_idx_list:
                    self.assertFalse(x in app_idx)

    def test_changeNameAndDescription(self):
        with O2x5xxRPCDevice(deviceAddress) as self.rpc, self.rpc.mainProxy.requestSession():
            with self.rpc.sessionProxy.setOperatingMode(mode=1):
                app = self.rpc.session.readApplicationConfigFile(self.app_import_file)
                appIndex = self.rpc.session.importApplication(application=app)
                newName = "TestName"
                newDescription = "TestDescription"
                self.rpc.edit.changeNameAndDescription(applicationIndex=appIndex,
                                                       name=newName,
                                                       description=newDescription)
                newAppDetails = self.rpc.session.getApplicationDetails(applicationIndex=appIndex)
                self.assertEqual(newName, newAppDetails["Name"])
                self.assertEqual(newDescription, newAppDetails["Description"])
                self.rpc.edit.deleteApplication(applicationIndex=appIndex)
                app_idx = [x["Index"] for x in self.rpc.getApplicationList()]
                self.assertTrue(appIndex not in app_idx)

    def test_moveApplications(self):
        with O2x5xxRPCDevice(deviceAddress) as self.rpc, self.rpc.mainProxy.requestSession():
            with self.rpc.sessionProxy.setOperatingMode(mode=1):
                app = self.rpc.session.readApplicationConfigFile(self.app_import_file)
                appIndex = self.rpc.session.importApplication(application=app)
                # Move app from app_index to position 30
                self.rpc.edit.moveApplications(applicationIndexFrom=appIndex,
                                               applicationIndexTo=30)
                app_idx = [x["Index"] for x in self.rpc.getApplicationList()]
                self.assertTrue(appIndex not in app_idx)
                self.assertTrue(30 in app_idx)
                # Move app from index 30 to 20
                self.rpc.edit.moveApplications(applicationIndexFrom=30,
                                               applicationIndexTo=20)
                app_idx = [x["Index"] for x in self.rpc.getApplicationList()]
                self.assertTrue(30 not in app_idx)
                self.assertTrue(20 in app_idx)
                self.rpc.edit.deleteApplication(applicationIndex=20)
                app_idx = [x["Index"] for x in self.rpc.getApplicationList()]
                self.assertTrue(20 not in app_idx)
