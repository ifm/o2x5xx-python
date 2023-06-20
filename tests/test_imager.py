from unittest import TestCase
from o2x5xx import O2x5xxRPCDevice
from tests.utils import *
import unittest
import time
import sys
import os

SENSOR_ADDRESS = '192.168.0.69'


class TestRPC_ImagerObject(TestCase):
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
        ping = self.rpc.doPing()
        self.assertEqual(ping, "up")

    def tearDown(self):
        self.edit.stopEditingApplication()
        self.edit.deleteApplication(applicationIndex=self.newAppIndex)
        # cancelSession() will implicitly set operation mode = 0
        self.session.cancelSession()

    def test_getAllParameters(self):
        result = self.image001.getAllParameters()
        self.assertIsInstance(result, dict)

    def test_getParameter(self):
        result = self.image001.getParameter(value="Name")
        self.assertIsInstance(result, str)

    def test_getAllParameterLimits(self):
        result = self.image001.getAllParameterLimits()
        self.assertIsInstance(result, dict)

    def test_Type(self):
        result = self.image001.Type
        self.assertIsInstance(result, str)

    def test_Name(self):
        self.assertEqual(self.image001.Name, "New imager config")
        self.image001.Name = "New Image Name"
        self.assertEqual(self.image001.Name, "New Image Name")
        # max 64 chars allowed
        self.image001.Name = 64 * "X"
        self.assertEqual(self.image001.Name, 64 * "X")
        with self.assertRaises(ValueError):
            self.image001.Name = 65 * "X"

    def test_Illumination(self):
        # default Illumination for newly created application
        self.assertEqual(self.image001.Illumination, 1)
        self.assertIsInstance(self.image001.Illumination, int)
        self.image001.Illumination = 0
        self.assertEqual(self.image001.Illumination, 0)
        with self.assertRaises(ValueError):
            self.image001.Illumination = 4

    def test_IlluInternalSegments(self):
        # default IlluInternalSegments for newly created application
        self.assertEqual(self.image001.IlluInternalSegments, {"upper-left": True, "upper-right": True,
                                                              "lower-left": True, "lower-right": True})
        newIlluInternalSegmentsDict = {"upper-left": False, "upper-right": False,
                                       "lower-left": False, "lower-right": False}
        self.image001.IlluInternalSegments = newIlluInternalSegmentsDict
        self.assertEqual(self.image001.IlluInternalSegments, newIlluInternalSegmentsDict)
        newIlluInternalSegmentsDict = {"upper-left": True, "upper-right": False,
                                       "lower-left": False, "lower-right": True}
        self.image001.IlluInternalSegments = newIlluInternalSegmentsDict
        self.assertEqual(self.image001.IlluInternalSegments, newIlluInternalSegmentsDict)

    def test_Color(self):
        # in case of rgb-w sensor used for tests
        if "Color" in self.image001.getAllParameters().keys():
            # default Color for newly created application
            self.assertEqual(self.image001.Color, 0)
            self.image001.Color = 1
            self.assertEqual(self.image001.Color, 1)
            self.image001.Color = 2
            self.assertEqual(self.image001.Color, 2)
            self.image001.Color = 3
            self.assertEqual(self.image001.Color, 3)
            # allowed range = 0-3
            with self.assertRaises(ValueError):
                self.image001.Color = 4
        # in case of infrared sensor used for tests
        else:
            with self.assertRaises(TypeError):
                self.image001.Color = 0

    def test_ExposureTime(self):
        # default ExposureTime for newly created application
        self.assertEqual(self.image001.ExposureTime, 1000)
        self.image001.ExposureTime = 5000
        self.assertEqual(self.image001.ExposureTime, 5000)
        with self.assertRaises(ValueError):
            self.image001.ExposureTime = 15001
        with self.assertRaises(ValueError):
            self.image001.ExposureTime = 66

    def test_AnalogGainFactor(self):
        # default AnalogGainFactor for newly created application
        self.assertEqual(self.image001.AnalogGainFactor, 8)
        self.image001.AnalogGainFactor = 1
        self.assertEqual(self.image001.AnalogGainFactor, 1)
        self.image001.AnalogGainFactor = 2
        self.assertEqual(self.image001.AnalogGainFactor, 2)
        self.image001.AnalogGainFactor = 4
        self.assertEqual(self.image001.AnalogGainFactor, 4)
        with self.assertRaises(ValueError):
            self.image001.AnalogGainFactor = 0
        with self.assertRaises(ValueError):
            self.image001.AnalogGainFactor = 16

    def test_FilterType(self):
        # default FilterType for newly created application
        self.assertEqual(self.image001.FilterType, 0)
        self.image001.FilterType = 1
        self.assertEqual(self.image001.FilterType, 1)
        self.image001.FilterType = 2
        self.assertEqual(self.image001.FilterType, 2)
        self.image001.FilterType = 3
        self.assertEqual(self.image001.FilterType, 3)
        self.image001.FilterType = 4
        self.assertEqual(self.image001.FilterType, 4)
        with self.assertRaises(ValueError):
            self.image001.FilterType = 5

    def test_FilterStrength(self):
        # default FilterStrength for newly created application without using filter
        self.assertEqual(self.image001.FilterStrength, 1)
        # setup a filter type
        self.image001.FilterType = 1
        # default FilterStrength for newly created application with using filter
        self.assertEqual(self.image001.FilterStrength, 1)
        self.image001.FilterStrength = 2
        self.assertEqual(self.image001.FilterStrength, 2)
        self.image001.FilterStrength = 3
        self.assertEqual(self.image001.FilterStrength, 3)
        self.image001.FilterStrength = 4
        self.assertEqual(self.image001.FilterStrength, 4)
        self.image001.FilterStrength = 5
        self.assertEqual(self.image001.FilterStrength, 5)
        with self.assertRaises(ValueError):
            self.image001.FilterStrength = 0
        with self.assertRaises(ValueError):
            self.image001.FilterStrength = 6

    def test_FilterInvert(self):
        # default FilterInvert for newly created application
        self.assertEqual(self.image001.FilterInvert, False)
        self.image001.FilterInvert = True
        self.assertEqual(self.image001.FilterInvert, True)


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
