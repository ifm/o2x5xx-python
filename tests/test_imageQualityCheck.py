from unittest import TestCase
from o2x5xx import O2x5xxRPCDevice
from tests.utils import *
import unittest
import time
import sys
import os

SENSOR_ADDRESS = '192.168.0.69'


class TestRPC_ImageQualityObject(TestCase):
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
        self.edit = self.session.setOperatingMode(mode=1)
        self.newAppIndex = self.session.edit.createApplication()
        self.application = self.edit.editApplication(applicationIndex=self.newAppIndex)
        self.image001 = self.application.editImage(imageIndex=1)
        self.imageQuality = self.image001.ImageQualityCheckConfig
        self.imageQuality.enabled = True
        ping = self.rpc.doPing()
        self.assertEqual(ping, "up")

    def tearDown(self):
        self.edit.stopEditingApplication()
        self.edit.deleteApplication(applicationIndex=self.newAppIndex)
        # cancelSession() will implicitly set operation mode = 0
        self.session.cancelSession()

    def test_enabled(self):
        self.assertTrue(self.imageQuality.enabled)
        self.imageQuality.enabled = False
        self.assertFalse(self.imageQuality.enabled)
        self.imageQuality.enabled = True
        self.assertTrue(self.imageQuality.enabled)

    def test_sharpness_thresholdMinMax(self):
        value = {"min": 1000, "max": 10000}
        self.imageQuality.sharpness_thresholdMinMax = value
        self.assertEqual(self.imageQuality.sharpness_thresholdMinMax, value)
        with self.assertRaises(ValueError):
            value = {"min": -1, "max": 10000}
            self.imageQuality.sharpness_thresholdMinMax = value
        with self.assertRaises(ValueError):
            value = {"min": 0, "max": 1228801}
            self.imageQuality.sharpness_thresholdMinMax = value
        with self.assertRaises(ValueError):
            value = {"min": 10000, "max": 200}
            self.imageQuality.sharpness_thresholdMinMax = value

    def test_meanBrightness_thresholdMinMax(self):
        value = {"min": 10, "max": 220}
        self.imageQuality.meanBrightness_thresholdMinMax = value
        self.assertEqual(self.imageQuality.meanBrightness_thresholdMinMax, value)
        with self.assertRaises(ValueError):
            value = {"min": -1, "max": 255}
            self.imageQuality.meanBrightness_thresholdMinMax = value
        with self.assertRaises(ValueError):
            value = {"min": 0, "max": 256}
            self.imageQuality.meanBrightness_thresholdMinMax = value
        with self.assertRaises(ValueError):
            value = {"min": 220, "max": 10}
            self.imageQuality.meanBrightness_thresholdMinMax = value

    def test_underexposedArea_thresholdMinMax(self):
        value = {"min": 10, "max": 90}
        self.imageQuality.underexposedArea_thresholdMinMax = value
        self.assertEqual(self.imageQuality.underexposedArea_thresholdMinMax, value)
        with self.assertRaises(ValueError):
            value = {"min": -1, "max": 100}
            self.imageQuality.underexposedArea_thresholdMinMax = value
        with self.assertRaises(ValueError):
            value = {"min": 0, "max": 101}
            self.imageQuality.underexposedArea_thresholdMinMax = value
        with self.assertRaises(ValueError):
            value = {"min": 110, "max": 10}
            self.imageQuality.underexposedArea_thresholdMinMax = value

    def overexposedArea_thresholdMinMax(self):
        value = {"min": 10, "max": 90}
        self.imageQuality.overexposedArea_thresholdMinMax = value
        self.assertEqual(self.imageQuality.overexposedArea_thresholdMinMax, value)
        with self.assertRaises(ValueError):
            value = {"min": -1, "max": 100}
            self.imageQuality.overexposedArea_thresholdMinMax = value
        with self.assertRaises(ValueError):
            value = {"min": 0, "max": 101}
            self.imageQuality.overexposedArea_thresholdMinMax = value
        with self.assertRaises(ValueError):
            value = {"min": 110, "max": 10}
            self.imageQuality.overexposedArea_thresholdMinMax = value


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
