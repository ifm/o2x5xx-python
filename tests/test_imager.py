from unittest import TestCase
from tests.utils import *
from source import O2x5xxRPCDevice
from .config import *


class TestRPC_ImagerObject(TestCase):
    config_backup = None
    config_file = None
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
            with self.rpc.mainProxy.requestSession(), self.rpc.sessionProxy.setOperatingMode(mode=1):
                self.newApplicationIndex = self.rpc.edit.createApplication()

    def tearDown(self) -> None:
        with O2x5xxRPCDevice(deviceAddress) as self.rpc, self.rpc.mainProxy.requestSession():
            with self.rpc.sessionProxy.setOperatingMode(mode=1):
                self.rpc.edit.deleteApplication(applicationIndex=self.newApplicationIndex)

    def test_getAllParameters(self):
        with O2x5xxRPCDevice(deviceAddress) as self.rpc, self.rpc.mainProxy.requestSession():
            with self.rpc.sessionProxy.setOperatingMode(mode=1), self.rpc.editProxy.editApplication(
                    app_index=self.newApplicationIndex):
                with self.rpc.applicationProxy.editImager(imager_index=1):
                    result = self.rpc.imager.getAllParameters()
                    self.assertIsInstance(result, dict)

    def test_getParameter(self):
        with O2x5xxRPCDevice(deviceAddress) as self.rpc, self.rpc.mainProxy.requestSession():
            with self.rpc.sessionProxy.setOperatingMode(mode=1), self.rpc.editProxy.editApplication(
                    app_index=self.newApplicationIndex):
                with self.rpc.applicationProxy.editImager(imager_index=1):
                    result = self.rpc.imager.getParameter(value="Name")
                    self.assertIsInstance(result, str)

    def test_getAllParameterLimits(self):
        with O2x5xxRPCDevice(deviceAddress) as self.rpc, self.rpc.mainProxy.requestSession():
            with self.rpc.sessionProxy.setOperatingMode(mode=1), self.rpc.editProxy.editApplication(
                    app_index=self.newApplicationIndex):
                with self.rpc.applicationProxy.editImager(imager_index=1):
                    result = self.rpc.imager.getAllParameterLimits()
                    self.assertIsInstance(result, dict)

    def test_Type(self):
        with O2x5xxRPCDevice(deviceAddress) as self.rpc, self.rpc.mainProxy.requestSession():
            with self.rpc.sessionProxy.setOperatingMode(mode=1), self.rpc.editProxy.editApplication(
                    app_index=self.newApplicationIndex):
                with self.rpc.applicationProxy.editImager(imager_index=1):
                    result = self.rpc.imager.Type
                    self.assertIsInstance(result, str)

    def test_Name(self):
        with O2x5xxRPCDevice(deviceAddress) as self.rpc, self.rpc.mainProxy.requestSession():
            with self.rpc.sessionProxy.setOperatingMode(mode=1), self.rpc.editProxy.editApplication(
                    app_index=self.newApplicationIndex):
                with self.rpc.applicationProxy.editImager(imager_index=1):
                    self.assertEqual(self.rpc.imager.Name, "New imager config")
                    self.rpc.imager.Name = "New Image Name"
                    self.assertEqual(self.rpc.imager.Name, "New Image Name")
                    # max 64 chars allowed
                    self.rpc.imager.Name = 64 * "X"
                    self.assertEqual(self.rpc.imager.Name, 64 * "X")
                    with self.assertRaises(ValueError):
                        self.rpc.imager.Name = 65 * "X"

    def test_Illumination(self):
        with O2x5xxRPCDevice(deviceAddress) as self.rpc, self.rpc.mainProxy.requestSession():
            with self.rpc.sessionProxy.setOperatingMode(mode=1), self.rpc.editProxy.editApplication(
                    app_index=self.newApplicationIndex):
                with self.rpc.applicationProxy.editImager(imager_index=1):
                    # default Illumination for newly created application
                    self.assertEqual(self.rpc.imager.Illumination, 1)
                    self.assertIsInstance(self.rpc.imager.Illumination, int)
                    self.rpc.imager.Illumination = 0
                    self.assertEqual(self.rpc.imager.Illumination, 0)
                    with self.assertRaises(ValueError):
                        self.rpc.imager.Illumination = 4

    def test_IlluInternalSegments(self):
        with O2x5xxRPCDevice(deviceAddress) as self.rpc, self.rpc.mainProxy.requestSession():
            with self.rpc.sessionProxy.setOperatingMode(mode=1), self.rpc.editProxy.editApplication(
                    app_index=self.newApplicationIndex):
                with self.rpc.applicationProxy.editImager(imager_index=1):
                    # default IlluInternalSegments for newly created application
                    self.assertEqual(self.rpc.imager.IlluInternalSegments, {"upper-left": True, "upper-right": True,
                                                                            "lower-left": True, "lower-right": True})
                    newIlluInternalSegmentsDict = {"upper-left": False, "upper-right": False,
                                                   "lower-left": False, "lower-right": False}
                    self.rpc.imager.IlluInternalSegments = newIlluInternalSegmentsDict
                    self.assertEqual(self.rpc.imager.IlluInternalSegments, newIlluInternalSegmentsDict)
                    newIlluInternalSegmentsDict = {"upper-left": True, "upper-right": False,
                                                   "lower-left": False, "lower-right": True}
                    self.rpc.imager.IlluInternalSegments = newIlluInternalSegmentsDict
                    self.assertEqual(self.rpc.imager.IlluInternalSegments, newIlluInternalSegmentsDict)

    def test_Color(self):
        with O2x5xxRPCDevice(deviceAddress) as self.rpc, self.rpc.mainProxy.requestSession():
            with self.rpc.sessionProxy.setOperatingMode(mode=1), self.rpc.editProxy.editApplication(
                    app_index=self.newApplicationIndex):
                with self.rpc.applicationProxy.editImager(imager_index=1):
                    # in case of rgb-w sensor used for tests
                    if "Color" in self.rpc.imager.getAllParameters().keys():
                        # default Color for newly created application
                        self.assertEqual(self.rpc.imager.Color, 0)
                        self.rpc.imager.Color = 1
                        self.assertEqual(self.rpc.imager.Color, 1)
                        self.rpc.imager.Color = 2
                        self.assertEqual(self.rpc.imager.Color, 2)
                        self.rpc.imager.Color = 3
                        self.assertEqual(self.rpc.imager.Color, 3)
                        # allowed range = 0-3
                        with self.assertRaises(ValueError):
                            self.rpc.imager.Color = 4
                    # in case of infrared sensor used for tests
                    else:
                        with self.assertRaises(TypeError):
                            self.rpc.imager.Color = 0

    def test_ExposureTime(self):
        with O2x5xxRPCDevice(deviceAddress) as self.rpc, self.rpc.mainProxy.requestSession():
            with self.rpc.sessionProxy.setOperatingMode(mode=1), self.rpc.editProxy.editApplication(
                    app_index=self.newApplicationIndex):
                with self.rpc.applicationProxy.editImager(imager_index=1):
                    # default ExposureTime for newly created application
                    self.assertEqual(self.rpc.imager.ExposureTime, 1000)
                    self.rpc.imager.ExposureTime = 5000
                    self.assertEqual(self.rpc.imager.ExposureTime, 5000)
                    with self.assertRaises(ValueError):
                        self.rpc.imager.ExposureTime = 15001
                    with self.assertRaises(ValueError):
                        self.rpc.imager.ExposureTime = 66

    def test_AnalogGainFactor(self):
        with O2x5xxRPCDevice(deviceAddress) as self.rpc, self.rpc.mainProxy.requestSession():
            with self.rpc.sessionProxy.setOperatingMode(mode=1), self.rpc.editProxy.editApplication(
                    app_index=self.newApplicationIndex):
                with self.rpc.applicationProxy.editImager(imager_index=1):
                    # default AnalogGainFactor for newly created application
                    self.assertEqual(self.rpc.imager.AnalogGainFactor, 8)
                    self.rpc.imager.AnalogGainFactor = 1
                    self.assertEqual(self.rpc.imager.AnalogGainFactor, 1)
                    self.rpc.imager.AnalogGainFactor = 2
                    self.assertEqual(self.rpc.imager.AnalogGainFactor, 2)
                    self.rpc.imager.AnalogGainFactor = 4
                    self.assertEqual(self.rpc.imager.AnalogGainFactor, 4)
                    with self.assertRaises(ValueError):
                        self.rpc.imager.AnalogGainFactor = 0
                    with self.assertRaises(ValueError):
                        self.rpc.imager.AnalogGainFactor = 16

    def test_FilterType(self):
        with O2x5xxRPCDevice(deviceAddress) as self.rpc, self.rpc.mainProxy.requestSession():
            with self.rpc.sessionProxy.setOperatingMode(mode=1), self.rpc.editProxy.editApplication(
                    app_index=self.newApplicationIndex):
                with self.rpc.applicationProxy.editImager(imager_index=1):
                    # default FilterType for newly created application
                    self.assertEqual(self.rpc.imager.FilterType, 0)
                    self.rpc.imager.FilterType = 1
                    self.assertEqual(self.rpc.imager.FilterType, 1)
                    self.rpc.imager.FilterType = 2
                    self.assertEqual(self.rpc.imager.FilterType, 2)
                    self.rpc.imager.FilterType = 3
                    self.assertEqual(self.rpc.imager.FilterType, 3)
                    self.rpc.imager.FilterType = 4
                    self.assertEqual(self.rpc.imager.FilterType, 4)
                    with self.assertRaises(ValueError):
                        self.rpc.imager.FilterType = 5

    def test_FilterStrength(self):
        with O2x5xxRPCDevice(deviceAddress) as self.rpc, self.rpc.mainProxy.requestSession():
            with self.rpc.sessionProxy.setOperatingMode(mode=1), self.rpc.editProxy.editApplication(
                    app_index=self.newApplicationIndex):
                with self.rpc.applicationProxy.editImager(imager_index=1):
                    # default FilterStrength for newly created application without using filter
                    self.assertEqual(self.rpc.imager.FilterStrength, 1)
                    # setup a filter type
                    self.rpc.imager.FilterType = 1
                    # default FilterStrength for newly created application with using filter
                    self.assertEqual(self.rpc.imager.FilterStrength, 1)
                    self.rpc.imager.FilterStrength = 2
                    self.assertEqual(self.rpc.imager.FilterStrength, 2)
                    self.rpc.imager.FilterStrength = 3
                    self.assertEqual(self.rpc.imager.FilterStrength, 3)
                    self.rpc.imager.FilterStrength = 4
                    self.assertEqual(self.rpc.imager.FilterStrength, 4)
                    self.rpc.imager.FilterStrength = 5
                    self.assertEqual(self.rpc.imager.FilterStrength, 5)
                    with self.assertRaises(ValueError):
                        self.rpc.imager.FilterStrength = 0
                    with self.assertRaises(ValueError):
                        self.rpc.imager.FilterStrength = 6

    def test_FilterInvert(self):
        with O2x5xxRPCDevice(deviceAddress) as self.rpc, self.rpc.mainProxy.requestSession():
            with self.rpc.sessionProxy.setOperatingMode(mode=1), self.rpc.editProxy.editApplication(
                    app_index=self.newApplicationIndex):
                with self.rpc.applicationProxy.editImager(imager_index=1):
                    # default FilterInvert for newly created application
                    self.assertEqual(self.rpc.imager.FilterInvert, False)
                    self.rpc.imager.FilterInvert = True
                    self.assertEqual(self.rpc.imager.FilterInvert, True)

    def test_startCalculateExposureTime(self):
        with O2x5xxRPCDevice(deviceAddress) as self.rpc, self.rpc.mainProxy.requestSession():
            with self.rpc.sessionProxy.setOperatingMode(mode=1), self.rpc.editProxy.editApplication(
                    app_index=self.newApplicationIndex):
                with self.rpc.applicationProxy.editImager(imager_index=1):
                    self.rpc.imager.startCalculateExposureTime()
                    self.assertEqual(self.rpc.imager.getProgressCalculateExposureTime(), 1.0)

    def test_startCalculateExposureTimeWithArguments(self):
        with O2x5xxRPCDevice(deviceAddress) as self.rpc, self.rpc.mainProxy.requestSession():
            with self.rpc.sessionProxy.setOperatingMode(mode=1), self.rpc.editProxy.editApplication(
                    app_index=self.newApplicationIndex):
                with self.rpc.applicationProxy.editImager(imager_index=1):
                    exposureROIsZone = [{"id": 0, "group": 0, "type": "Rect", "width": 100,
                                         "height": 50, "angle": 45, "center_x": 123, "center_y": 42},
                                        {"id": 0, "group": 0, "type": "Ellipse", "width": 50,
                                         "height": 100, "angle": 45, "center_x": 42, "center_y": 123},
                                        {"id": 0, "group": 0, "type": "Poly", "points": [
                                            {"x": 100, "y": 100}, {"x": 234, "y": 100}, {"x": 150, "y": 300}]}]
                    exposureRODsZone = [{"id": 0, "group": 0, "type": "Rect", "width": 30,
                                         "height": 40, "angle": 45, "center_x": 123, "center_y": 42},
                                        {"id": 0, "group": 0, "type": "Ellipse", "width": 20,
                                         "height": 100, "angle": 90, "center_x": 42, "center_y": 153},
                                        {"id": 0, "group": 0, "type": "Poly", "points": [
                                            {"x": 100, "y": 100}, {"x": 334, "y": 300}, {"x": 250, "y": 400}]}]
                    self.rpc.imager.startCalculateExposureTime(minAnalogGainFactor=2,
                                                               maxAnalogGainFactor=8,
                                                               saturatedRatio=0.25,
                                                               ROIs=exposureROIsZone,
                                                               RODs=exposureRODsZone)
                    self.assertEqual(self.rpc.imager.getProgressCalculateExposureTime(), 1.0)

    def test_startCalculateAutofocus(self):
        with O2x5xxRPCDevice(deviceAddress) as self.rpc, self.rpc.mainProxy.requestSession():
            with self.rpc.sessionProxy.setOperatingMode(mode=1), self.rpc.editProxy.editApplication(
                    app_index=self.newApplicationIndex):
                with self.rpc.applicationProxy.editImager(imager_index=1):
                    self.rpc.imager.startCalculateAutofocus()
                    self.assertEqual(self.rpc.imager.getProgressCalculateAutofocus(), 1.0)

    def test_startCalculateAutofocusWithArguments(self):
        with O2x5xxRPCDevice(deviceAddress) as self.rpc, self.rpc.mainProxy.requestSession():
            with self.rpc.sessionProxy.setOperatingMode(mode=1), self.rpc.editProxy.editApplication(
                    app_index=self.newApplicationIndex):
                with self.rpc.applicationProxy.editImager(imager_index=1):
                    focusROIsZone = [{"id": 0, "group": 0, "type": "Rect", "width": 100,
                                      "height": 50, "angle": 45, "center_x": 123, "center_y": 42},
                                     {"id": 0, "group": 0, "type": "Ellipse", "width": 50,
                                      "height": 100, "angle": 45, "center_x": 42, "center_y": 123},
                                     {"id": 0, "group": 0, "type": "Poly", "points": [
                                         {"x": 100, "y": 100}, {"x": 234, "y": 100}, {"x": 150, "y": 300}]}]
                    focusRODsZone = [{"id": 0, "group": 0, "type": "Rect", "width": 30,
                                      "height": 40, "angle": 45, "center_x": 123, "center_y": 42},
                                     {"id": 0, "group": 0, "type": "Ellipse", "width": 20,
                                      "height": 100, "angle": 90, "center_x": 42, "center_y": 153},
                                     {"id": 0, "group": 0, "type": "Poly", "points": [
                                         {"x": 100, "y": 100}, {"x": 334, "y": 300}, {"x": 250, "y": 400}]}]
                    self.rpc.imager.startCalculateAutofocus(ROIs=focusROIsZone,
                                                            RODs=focusRODsZone)
                    self.assertEqual(self.rpc.imager.getProgressCalculateAutofocus(), 1.0)

    def test_getAutofocusDistances(self):
        with O2x5xxRPCDevice(deviceAddress) as self.rpc, self.rpc.mainProxy.requestSession():
            with self.rpc.sessionProxy.setOperatingMode(mode=1), self.rpc.editProxy.editApplication(
                    app_index=self.newApplicationIndex):
                with self.rpc.applicationProxy.editImager(imager_index=1):
                    self.rpc.imager.startCalculateAutofocus()
                    self.assertEqual(self.rpc.imager.getProgressCalculateAutofocus(), 1.0)
                    result = self.rpc.imager.getAutofocusDistances()
                    self.assertIsInstance(result, list)
                    self.assertIsInstance(result[0], float)

    def test_getAutoExposureResult(self):
        with O2x5xxRPCDevice(deviceAddress) as self.rpc, self.rpc.mainProxy.requestSession():
            with self.rpc.sessionProxy.setOperatingMode(mode=1), self.rpc.editProxy.editApplication(
                    app_index=self.newApplicationIndex):
                with self.rpc.applicationProxy.editImager(imager_index=1):
                    self.rpc.imager.startCalculateExposureTime()
                    result = self.rpc.imager.getAutoExposureResult()
                    self.assertIsInstance(result, dict)
