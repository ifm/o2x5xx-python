from unittest import TestCase
from o2x5xx import O2x5xxRPCDevice
from tests.utils import *
import unittest
import time
import sys
import os

SENSOR_ADDRESS = '192.168.0.69'


class TestRPC_SessionObject(TestCase):
    config_backup = None
    config_file = None
    app_import_file = None
    active_application_backup = None
    pin_layout = None

    @classmethod
    def setUpClass(cls):
        setUpRPC = O2x5xxRPCDevice(SENSOR_ADDRESS)
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
        tearDownRPC = O2x5xxRPCDevice(SENSOR_ADDRESS)
        tearDownSession = tearDownRPC.requestSession()
        tearDownSession.importConfig(cls.config_backup, global_settings=True, network_settings=False, applications=True)
        if cls.active_application_backup != "0":
            tearDownRPC.switchApplication(cls.active_application_backup)
        tearDownSession.cancelSession()

    def setUp(self):
        self.rpc = O2x5xxRPCDevice(SENSOR_ADDRESS)
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
        app = self.session.readConfigFile(self.app_import_file)
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
        self.rpc.switchApplication(applicationIndex=2)
        self.session.resetStatistics()
        for i in range(10):
            self.rpc.trigger()
        result = self.rpc.getApplicationStatisticData(applicationIndex=2)
        self.assertTrue(result['number_of_frames'] == 10)
        self.session.resetStatistics()
        time.sleep(0.5)
        result = self.rpc.getApplicationStatisticData(applicationIndex=2)
        self.assertTrue(result['number_of_frames'] == 0)

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


if __name__ == '__main__':
    try:
        SENSOR_ADDRESS = sys.argv[1]
        LOGFILE = sys.argv[2]
    except IndexError:
        raise ValueError("Argument(s) are missing. Here is an example for running the unittests with logfile:\n"
                         "python test_rpc.py 192.168.0.69 True\n"
                         "Here is an example for running the unittests without an logfile:\n"
                         "python test_rpc.py 192.168.0.69")

    device_rpc = O2x5xxRPCDevice(address=SENSOR_ADDRESS)
    PCIC_TCP_PORT = device_rpc.getParameter(value="PcicTcpPort")

    if LOGFILE:
        FIRMWARE_VERSION = device_rpc.getSWVersion()["IFM_Software"]
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        logfile = os.path.join('logs', '{timestamp}_{firmware}_rpc_unittests_o2x5xx.log'
                               .format(timestamp=timestamp, firmware=FIRMWARE_VERSION))

        logfile = open(logfile, 'w')
        sys.stdout = logfile

        suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
        unittest.TextTestRunner(sys.stdout, verbosity=2).run(suite)

        logfile.close()

    else:
        suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
        unittest.TextTestRunner(verbosity=2).run(suite)
