from unittest import TestCase
try:
    from source import O2x5xxRPCDevice
    from tests.utils import *
    from .config import *
except ModuleNotFoundError:
    import os
    import sys
    sys.path.insert(0, '../source')
    from utils import *
    from config import *
import numpy as np
import warnings
import time


class TestRPC_MainAPI(TestCase):
    rpc = None
    session = None
    config_backup = None
    active_application_backup = None
    pin_layout = None

    @classmethod
    def setUpClass(cls):
        cls.rpc = O2x5xxRPCDevice(deviceAddress)
        cls.session = cls.rpc.requestSession()
        cls.config_backup = cls.session.exportConfig()
        cls.active_application_backup = cls.rpc.getParameter("ActiveApplication")
        configFile = getImportSetupByPinLayout(rpc=cls.rpc)['config_file']
        configFile = cls.session.readConfigFile(configFile=configFile)
        cls.session.importConfig(configFile, global_settings=True, network_settings=False, applications=True)
        cls.rpc.switchApplication(1)

    @classmethod
    def tearDownClass(cls):
        cls.session.importConfig(cls.config_backup, global_settings=True, network_settings=False, applications=True)
        if cls.active_application_backup != "0":
            cls.rpc.switchApplication(cls.active_application_backup)
        cls.session.cancelSession()

    def setUp(self):
        warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed.*<ssl.SSLSocket.*>")
        warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed <socket.socket.*>")
        warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed running multiprocessing pool.*>")
        self.rpc.switchApplication(1)

    def test_getParameter(self):
        result = self.rpc.getParameter(value="DeviceType")
        self.assertIsInstance(result, str)
        self.assertEqual(len(result), 5)

    def test_getAllParameters(self):
        result = self.rpc.getAllParameters()
        self.assertIsInstance(result, dict)

    def test_getSWVersion(self):
        result = self.rpc.getSWVersion()
        self.assertIsInstance(result, dict)

    def test_getHWInfo(self):
        result = self.rpc.getHWInfo()
        self.assertIsInstance(result, dict)

    def test_getDmesgData(self):
        result = self.rpc.getDmesgData()
        self.assertIsInstance(result, str)

    def test_getClientCompatibilityList(self):
        result = self.rpc.getClientCompatibilityList()
        self.assertIsInstance(result, list)

    def test_getApplicationList(self):
        result = self.rpc.getApplicationList()
        self.assertIsInstance(result, list)
        self.assertIsInstance(result[0], dict)
        self.assertIsInstance(result[1], dict)
        self.assertIsInstance(result[2], dict)
        self.assertIsInstance(result[3], dict)
        self.assertIsInstance(result[4], dict)
        self.assertIsInstance(result[5], dict)

    def test_switchApplication(self):
        initial_application = int(self.rpc.getParameter("ActiveApplication"))
        if initial_application > 1:
            self.rpc.switchApplication(applicationIndex=1)
            while self.rpc.getParameter("OperatingMode") != "0":
                time.sleep(1)
            self.assertEqual(int(self.rpc.getParameter("ActiveApplication")), 1)
        else:
            self.rpc.switchApplication(applicationIndex=2)
            while self.rpc.getParameter("OperatingMode") != "0":
                time.sleep(1)
            self.assertEqual(int(self.rpc.getParameter("ActiveApplication")), 2)
            time.sleep(5)
        # Switch back to initial application
        self.rpc.switchApplication(applicationIndex=initial_application)
        while self.rpc.getParameter("OperatingMode") != "0":
            time.sleep(1)
        self.assertEqual(int(self.rpc.getParameter("ActiveApplication")), initial_application)

    def test_getTraceLogs(self):
        numberLogs = 10
        traces = self.rpc.getTraceLogs(nLogs=numberLogs)
        self.assertIsInstance(traces, list)
        self.assertEqual(len(traces), numberLogs)

    def test_getApplicationStatisticData(self):
        application_active = self.rpc.getParameter(value="ActiveApplication")
        result = self.rpc.getApplicationStatisticData(applicationIndex=int(application_active))
        self.assertIsInstance(result, dict)

    def test_getReferenceImage(self):
        result = self.rpc.getReferenceImage()
        self.assertIsInstance(result, np.ndarray)

    def test_isConfigurationDone(self):
        result = self.rpc.isConfigurationDone()
        self.assertTrue(result)

    def test_waitForConfigurationDone(self):
        self.rpc.waitForConfigurationDone()

    def test_measure(self):
        input_measure_line = {
            "geometry": "line",
            "pixel_positions": [
                {
                    "column": 980,
                    "row": 374
                },
                {
                    "column": 603,
                    "row": 455
                }
            ]
        }

        input_measure_rect = {
            "geometry": "rect",
            "pixel_positions": [
                {
                    "column": 376,
                    "row": 426
                },
                {
                    "column": 710,
                    "row": 651
                }
            ]
        }

        input_measure_circle = {
            "geometry": "circle",
            "pixel_positions": [
                {
                    "column": 647,
                    "row": 452
                },
                {
                    "column": 775,
                    "row": 533
                }
            ]
        }

        result = self.rpc.measure(measureInput=input_measure_line)
        self.assertIsInstance(result, dict)
        self.assertTrue(result)
        result = self.rpc.measure(measureInput=input_measure_rect)
        self.assertIsInstance(result, dict)
        self.assertTrue(result)
        result = self.rpc.measure(measureInput=input_measure_circle)
        self.assertIsInstance(result, dict)
        self.assertTrue(result)

    def test_trigger(self):
        number_trigger = 100
        application_active = self.rpc.getParameter(value="ActiveApplication")
        initial_application_stats = self.rpc.getApplicationStatisticData(applicationIndex=int(application_active))
        initial_number_of_frames = initial_application_stats['number_of_frames']
        for i in range(number_trigger):
            answer = self.rpc.trigger()
            self.assertTrue(answer)
        application_stats = self.rpc.getApplicationStatisticData(applicationIndex=int(application_active))
        number_of_frames = application_stats['number_of_frames']
        self.assertEqual(number_of_frames, initial_number_of_frames + number_trigger)

    def test_doPing(self):
        result = self.rpc.doPing()
        self.assertEqual(result, "up")
