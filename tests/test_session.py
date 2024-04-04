from unittest import TestCase
from source import O2x5xxRPCDevice, O2x5xxPCICDevice
from tests.utils import *
from .config import *


class TestRPC_SessionObject(TestCase):
    config_file = None
    config_backup = None
    app_import_file = None
    active_application_backup = None

    @classmethod
    def setUpClass(cls) -> None:
        with O2x5xxRPCDevice(deviceAddress) as rpc:
            cls.config_file = getImportSetupByPinLayout(rpc=rpc)['config_file']
            cls.app_import_file = getImportSetupByPinLayout(rpc=rpc)['app_import_file']
            if importDeviceConfigUnittests:
                cls.active_application_backup = rpc.getParameter("ActiveApplication")
                with rpc.mainProxy.requestSession():
                    cls.config_backup = rpc.session.exportConfig()
                    _configFile = rpc.session.readDeviceConfigFile(configFile=cls.config_file)
                    rpc.session.importConfig(_configFile, global_settings=True, network_settings=False,
                                             applications=True)

    @classmethod
    def tearDownClass(cls) -> None:
        if importDeviceConfigUnittests:
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

    def test_exportConfig(self):
        with O2x5xxRPCDevice(deviceAddress) as self.rpc:
            with self.rpc.mainProxy.requestSession():
                config = self.rpc.session.exportConfig()
                self.assertIsInstance(config, bytearray)
                self.assertTrue(len(config) > 1000)

    def test_importConfig(self):
        with O2x5xxRPCDevice(deviceAddress) as self.rpc:
            with self.rpc.mainProxy.requestSession():
                config = self.rpc.session.readDeviceConfigFile(configFile=self.config_file)
                self.rpc.session.importConfig(config, global_settings=True, network_settings=False, applications=True)
                self.assertTrue(config)
                self.assertIsInstance(config, str)
                result = self.rpc.getApplicationList()
                self.assertTrue(len(result) == 6)

    def test_exportApplication(self):
        with O2x5xxRPCDevice(deviceAddress) as self.rpc, self.rpc.mainProxy.requestSession():
            app = self.rpc.session.exportApplication(applicationIndex=1)
            self.assertTrue(app)
            self.assertIsInstance(app, bytearray)

    def test_importApplication(self):
        with O2x5xxRPCDevice(deviceAddress) as self.rpc, self.rpc.mainProxy.requestSession():
            app = self.rpc.session.readApplicationConfigFile(self.app_import_file)
            with self.rpc.sessionProxy.setOperatingMode(mode=1):
                newAppIndex = self.rpc.session.importApplication(application=app)
                app_idx = [x["Index"] for x in self.rpc.getApplicationList()]
                self.assertTrue(newAppIndex in app_idx)
                self.rpc.edit.deleteApplication(applicationIndex=newAppIndex)

    def test_getApplicationDetails(self):
        with O2x5xxRPCDevice(deviceAddress) as self.rpc:
            with self.rpc.mainProxy.requestSession():
                details = self.rpc.session.getApplicationDetails(applicationIndex=1)
                self.assertTrue(details)
                self.assertIsInstance(details, dict)

    def test_resetStatistics(self):
        with O2x5xxRPCDevice(deviceAddress) as self.rpc, self.rpc.mainProxy.requestSession():
            triggerNum = 20
            self.rpc.switchApplication(applicationIndex=2)
            self.rpc.session.resetStatistics()
            with O2x5xxPCICDevice(deviceAddress, pcicTcpPort) as pcic:
                for i in range(triggerNum):
                    answer = pcic.execute_synchronous_trigger()
                    self.assertTrue(answer)
            result = self.rpc.getApplicationStatisticData(applicationIndex=2)
            self.assertEqual(result['number_of_frames'], triggerNum)
            self.rpc.session.resetStatistics()
            result = self.rpc.getApplicationStatisticData(applicationIndex=2)
            self.assertEqual(result['number_of_frames'], 0)

    def test_writeApplicationConfigFile(self):
        with O2x5xxRPCDevice(deviceAddress) as self.rpc:
            with self.rpc.mainProxy.requestSession():
                appFilename = "./DELETE_THIS.o2d5xxapp"
                # Check if file already exists
                self.assertFalse(os.path.exists(appFilename))
                with self.rpc.sessionProxy.setOperatingMode(mode=1):
                    app = self.rpc.session.exportApplication(applicationIndex=1)
                self.rpc.session.writeApplicationConfigFile(applicationName=appFilename, data=app)
                self.assertTrue(os.path.exists(appFilename))
                os.remove(appFilename)
                self.assertFalse(os.path.exists(appFilename))
                appFilename = "./DELETE_THIS"
                # Check if file already exists
                self.assertFalse(os.path.exists(appFilename))
                with self.rpc.sessionProxy.setOperatingMode(mode=1):
                    app = self.rpc.session.exportApplication(applicationIndex=1)
                self.rpc.session.writeApplicationConfigFile(applicationName=appFilename, data=app)
                self.assertTrue(os.path.exists(appFilename + ".o2d5xxapp"))
                os.remove(appFilename + ".o2d5xxapp")

    def test_writeDeviceConfigFile(self):
        with O2x5xxRPCDevice(deviceAddress) as self.rpc:
            with self.rpc.mainProxy.requestSession():
                cfgFilename = "./DELETE_THIS.o2d5xxcfg"
                # Check if file already exists
                self.assertFalse(os.path.exists(cfgFilename))
                cfg = self.rpc.session.exportConfig()
                self.rpc.session.writeDeviceConfigFile(configName=cfgFilename, data=cfg)
                self.assertTrue(os.path.exists(cfgFilename))
                os.remove(cfgFilename)
                self.assertFalse(os.path.exists(cfgFilename))
                cfgFilename = "./DELETE_THIS"
                # Check if file already exists
                self.assertFalse(os.path.exists(cfgFilename))
                cfg = self.rpc.session.exportConfig()
                self.rpc.session.writeDeviceConfigFile(configName=cfgFilename + ".o2d5xxcfg", data=cfg)
                self.assertTrue(os.path.exists(cfgFilename + ".o2d5xxcfg"))
                os.remove(cfgFilename + ".o2d5xxcfg")

    def test_readApplicationConfigFile(self):
        with O2x5xxRPCDevice(deviceAddress) as self.rpc:
            with self.rpc.mainProxy.requestSession():
                appFilename = "./DELETE_THIS.o2d5xxapp"
                app1 = self.rpc.session.exportApplication(applicationIndex=1)
                self.rpc.session.writeApplicationConfigFile(applicationName=appFilename, data=app1)
                appData = self.rpc.session.readApplicationConfigFile(applicationFile=appFilename)
                with self.rpc.sessionProxy.setOperatingMode(mode=1):
                    newAppIndex = self.rpc.session.importApplication(application=appData)
                    app2 = self.rpc.session.exportApplication(applicationIndex=newAppIndex)
                    self.assertEqual(app1, app2)
                    self.rpc.edit.deleteApplication(applicationIndex=newAppIndex)
                os.remove(appFilename)

    def test_readDeviceConfigFile(self):
        with O2x5xxRPCDevice(deviceAddress) as self.rpc:
            with self.rpc.mainProxy.requestSession():
                cfg = self.rpc.session.readDeviceConfigFile(configFile=self.config_file)
                self.assertTrue(cfg)
                self.assertIsInstance(cfg, str)
