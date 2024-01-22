import time
from unittest import TestCase
import numpy as np
from source import O2x5xxRPCDevice
from tests.utils import *
from .config import *


class TestRPC_MainAPI(TestCase):
    config_backup = None
    active_application_backup = None

    @classmethod
    def setUpClass(cls) -> None:
        with O2x5xxRPCDevice(deviceAddress) as rpc:
            with rpc.mainProxy.requestSession():
                cls.config_backup = rpc.session.exportConfig()
                cls.active_application_backup = rpc.getParameter("ActiveApplication")
                configFile = getImportSetupByPinLayout(rpc=rpc)['config_file']
                configFile = rpc.session.readDeviceConfigFile(configFile=configFile)
                rpc.session.importConfig(configFile, global_settings=True, network_settings=False,
                                         applications=True)
                rpc.switchApplication(1)

    @classmethod
    def tearDownClass(cls) -> None:
        with O2x5xxRPCDevice(deviceAddress) as rpc:
            with rpc.mainProxy.requestSession():
                rpc.session.importConfig(cls.config_backup, global_settings=True, network_settings=False,
                                         applications=True)
                if cls.active_application_backup != "0":
                    rpc.switchApplication(cls.active_application_backup)

    def setUp(self) -> None:
        with O2x5xxRPCDevice(deviceAddress) as rpc:
            rpc.switchApplication(1)

    def tearDown(self) -> None:
        pass

    def test_getParameter(self):
        with O2x5xxRPCDevice(deviceAddress) as rpc:
            result = rpc.getParameter(value="DeviceType")
            self.assertIsInstance(result, str)
            self.assertEqual(len(result), 5)

    def test_getAllParameters(self):
        with O2x5xxRPCDevice(deviceAddress) as rpc:
            result = rpc.getAllParameters()
            self.assertIsInstance(result, dict)

    def test_getSWVersion(self):
        with O2x5xxRPCDevice(deviceAddress) as rpc:
            result = rpc.getSWVersion()
            self.assertIsInstance(result, dict)

    def test_getHWInfo(self):
        with O2x5xxRPCDevice(deviceAddress) as rpc:
            result = rpc.getHWInfo()
            self.assertIsInstance(result, dict)

    def test_getDmesgData(self):
        with O2x5xxRPCDevice(deviceAddress) as rpc:
            result = rpc.getDmesgData()
            self.assertIsInstance(result, str)

    def test_getClientCompatibilityList(self):
        with O2x5xxRPCDevice(deviceAddress) as rpc:
            result = rpc.getClientCompatibilityList()
            self.assertIsInstance(result, list)

    def test_getApplicationList(self):
        with O2x5xxRPCDevice(deviceAddress) as rpc:
            result = rpc.getApplicationList()
            self.assertIsInstance(result, list)
            self.assertIsInstance(result[0], dict)
            self.assertIsInstance(result[1], dict)
            self.assertIsInstance(result[2], dict)
            self.assertIsInstance(result[3], dict)
            self.assertIsInstance(result[4], dict)
            self.assertIsInstance(result[5], dict)

    def test_switchApplication(self):
        with O2x5xxRPCDevice(deviceAddress) as rpc:
            initial_application = int(rpc.getParameter("ActiveApplication"))
            if initial_application > 1:
                rpc.switchApplication(applicationIndex=1)
                while rpc.getParameter("OperatingMode") != "0":
                    time.sleep(1)
                self.assertEqual(int(rpc.getParameter("ActiveApplication")), 1)
            else:
                rpc.switchApplication(applicationIndex=2)
                while rpc.getParameter("OperatingMode") != "0":
                    time.sleep(1)
                self.assertEqual(int(rpc.getParameter("ActiveApplication")), 2)
                time.sleep(5)
            # Switch back to initial application
            rpc.switchApplication(applicationIndex=initial_application)
            while rpc.getParameter("OperatingMode") != "0":
                time.sleep(1)
            self.assertEqual(int(rpc.getParameter("ActiveApplication")), initial_application)

    def test_getTraceLogs(self):
        with O2x5xxRPCDevice(deviceAddress) as rpc:
            numberLogs = 10
            traces = rpc.getTraceLogs(nLogs=numberLogs)
            self.assertIsInstance(traces, list)
            self.assertEqual(len(traces), numberLogs)

    def test_getApplicationStatisticData(self):
        with O2x5xxRPCDevice(deviceAddress) as rpc:
            application_active = rpc.getParameter(value="ActiveApplication")
            result = rpc.getApplicationStatisticData(applicationIndex=int(application_active))
            self.assertIsInstance(result, dict)

    def test_getReferenceImage(self):
        with O2x5xxRPCDevice(deviceAddress) as rpc:
            result = rpc.getReferenceImage()
            self.assertIsInstance(result, np.ndarray)

    def test_isConfigurationDone(self):
        with O2x5xxRPCDevice(deviceAddress) as rpc:
            result = rpc.isConfigurationDone()
            self.assertTrue(result)

    def test_waitForConfigurationDone(self):
        with O2x5xxRPCDevice(deviceAddress) as rpc:
            rpc.waitForConfigurationDone()

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

        with O2x5xxRPCDevice(deviceAddress) as rpc:
            result = rpc.measure(measureInput=input_measure_line)
            self.assertIsInstance(result, dict)
            self.assertTrue(result)
            result = rpc.measure(measureInput=input_measure_rect)
            self.assertIsInstance(result, dict)
            self.assertTrue(result)
            result = rpc.measure(measureInput=input_measure_circle)
            self.assertIsInstance(result, dict)
            self.assertTrue(result)

    def test_trigger(self):
        with O2x5xxRPCDevice(deviceAddress) as rpc:
            number_trigger = 10
            application_active = rpc.getParameter(value="ActiveApplication")
            initial_application_stats = rpc.getApplicationStatisticData(applicationIndex=int(application_active))
            initial_number_of_frames = initial_application_stats['number_of_frames']
            for i in range(number_trigger):
                answer = rpc.trigger()
                self.assertTrue(answer)
            application_stats = rpc.getApplicationStatisticData(applicationIndex=int(application_active))
            number_of_frames = application_stats['number_of_frames']
            self.assertEqual(number_of_frames, initial_number_of_frames + number_trigger)

    def test_doPing(self):
        with O2x5xxRPCDevice(deviceAddress) as rpc:
            result = rpc.doPing()
            self.assertEqual(result, "up")
