from unittest import TestCase
from source import O2x5xxRPCDevice
from tests.utils import *
from .config import *
import os
import warnings


class TestRPC_SessionObject(TestCase):
    config_backup = None
    config_file = None
    app_import_file = None
    active_application_backup = None
    pin_layout = None

    @classmethod
    def setUpClass(cls):
        setUpRPC = O2x5xxRPCDevice(deviceAddress)
        setUpSession = setUpRPC.requestSession()
        cls.config_backup = setUpSession.exportConfig()
        cls.active_application_backup = setUpRPC.getParameter("ActiveApplication")
        cls.config_file = getImportSetupByPinLayout(rpc=setUpRPC)['config_file']
        cls.app_import_file = getImportSetupByPinLayout(rpc=setUpRPC)['app_import_file']
        _config_file_data = setUpSession.readConfigFile(configFile=cls.config_file)
        setUpSession.importConfig(_config_file_data, global_settings=True, network_settings=False, applications=True)
        setUpRPC.switchApplication(1)
        setUpSession.cancelSession()

    @classmethod
    def tearDownClass(cls):
        tearDownRPC = O2x5xxRPCDevice(deviceAddress)
        tearDownSession = tearDownRPC.requestSession()
        tearDownSession.importConfig(cls.config_backup, global_settings=True, network_settings=False, applications=True)
        if cls.active_application_backup != "0":
            tearDownRPC.switchApplication(cls.active_application_backup)
        tearDownSession.cancelSession()

    def setUp(self):
        warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed.*<ssl.SSLSocket.*>")
        warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed <socket.socket.*>")
        warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed running multiprocessing pool.*>")
        self.rpc = O2x5xxRPCDevice(deviceAddress)
        self.rpc.switchApplication(1)
        self.session = self.rpc.requestSession()
        ping = self.rpc.doPing()
        self.assertEqual(ping, "up")

    def tearDown(self):
        self.session.cancelSession()

    def test_exportConfig(self):
        config = self.session.exportConfig()
        self.assertIsInstance(config, bytearray)
        self.assertTrue(len(config) > 1000)

    def test_importConfig(self):
        config = self.session.readConfigFile(configFile=self.config_file)
        self.session.importConfig(config, global_settings=True, network_settings=False, applications=True)
        self.assertTrue(config)
        self.assertIsInstance(config, str)
        result = self.rpc.getApplicationList()
        self.assertTrue(len(result) == 6)

    def test_exportApplication(self):
        app = self.session.exportApplication(applicationIndex=1)
        self.assertTrue(app)
        self.assertIsInstance(app, bytearray)

    def test_importApplication(self):
        app = self.session.readApplicationConfigFile(self.app_import_file)
        newAppIndex = self.session.importApplication(application=app)
        app_idx = [x["Index"] for x in self.rpc.getApplicationList()]
        self.assertTrue(newAppIndex in app_idx)
        self.session.setOperatingMode(mode=1)
        self.session.edit.deleteApplication(applicationIndex=newAppIndex)
        self.session.setOperatingMode(mode=0)

    def test_getApplicationDetails(self):
        details = self.session.getApplicationDetails(applicationIndex=1)
        self.assertTrue(details)
        self.assertIsInstance(details, dict)

    def test_resetStatistics(self):
        triggerNum = 20
        self.rpc.switchApplication(applicationIndex=2)
        self.session.resetStatistics()
        for i in range(triggerNum):
            answer = self.rpc.trigger()
            self.assertTrue(answer)
        result = self.rpc.getApplicationStatisticData(applicationIndex=2)
        self.assertEqual(result['number_of_frames'], triggerNum)
        self.session.resetStatistics()
        result = self.rpc.getApplicationStatisticData(applicationIndex=2)
        self.assertEqual(result['number_of_frames'], 0)

    def test_writeApplicationConfigFile(self):
        appFilename = "./DELETE_THIS.o2d5xxapp"
        # Check if file already exists
        self.assertFalse(os.path.exists(appFilename))
        app = self.session.exportApplication(applicationIndex=1)
        self.session.writeApplicationConfigFile(applicationName=appFilename, data=app)
        self.assertTrue(os.path.exists(appFilename))
        os.remove(appFilename)
        self.assertFalse(os.path.exists(appFilename))
        appFilename = "./DELETE_THIS"
        # Check if file already exists
        self.assertFalse(os.path.exists(appFilename))
        app = self.session.exportApplication(applicationIndex=1)
        self.session.writeApplicationConfigFile(applicationName=appFilename, data=app)
        self.assertTrue(os.path.exists(appFilename + ".o2d5xxapp"))
        os.remove(appFilename + ".o2d5xxapp")

    def test_writeConfigFile(self):
        cfgFilename = "./DELETE_THIS.o2d5xxcfg"
        # Check if file already exists
        self.assertFalse(os.path.exists(cfgFilename))
        cfg = self.session.exportConfig()
        self.session.writeConfigFile(configName=cfgFilename, data=cfg)
        self.assertTrue(os.path.exists(cfgFilename))
        os.remove(cfgFilename)
        self.assertFalse(os.path.exists(cfgFilename))
        cfgFilename = "./DELETE_THIS"
        # Check if file already exists
        self.assertFalse(os.path.exists(cfgFilename))
        cfg = self.session.exportConfig()
        self.session.writeConfigFile(configName=cfgFilename + ".o2d5xxcfg", data=cfg)
        self.assertTrue(os.path.exists(cfgFilename + ".o2d5xxcfg"))
        os.remove(cfgFilename + ".o2d5xxcfg")

    def test_readApplicationConfigFile(self):
        appFilename = "./DELETE_THIS.o2d5xxapp"
        app1 = self.session.exportApplication(applicationIndex=1)
        self.session.writeApplicationConfigFile(applicationName=appFilename, data=app1)
        appData = self.session.readApplicationConfigFile(applicationFile=appFilename)
        newAppIndex = self.session.importApplication(application=appData)
        app2 = self.session.exportApplication(applicationIndex=newAppIndex)
        self.assertEqual(app1, app2)
        self.session.setOperatingMode(mode=1)
        self.session.edit.deleteApplication(applicationIndex=newAppIndex)
        self.session.setOperatingMode(mode=0)
        os.remove(appFilename)

    def test_readConfigFile(self):
        cfg = self.session.exportConfig()
        self.assertTrue(cfg)
        self.assertIsInstance(cfg, bytearray)
