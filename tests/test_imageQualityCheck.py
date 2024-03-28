from unittest import TestCase
from source import O2x5xxRPCDevice
from tests.utils import *
from .config import *


class TestRPC_ImageQualityObject(TestCase):
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

    def test_enabled(self):
        with O2x5xxRPCDevice(deviceAddress) as self.rpc, self.rpc.mainProxy.requestSession():
            with self.rpc.sessionProxy.setOperatingMode(mode=1), self.rpc.editProxy.editApplication(
                    app_index=self.newApplicationIndex):
                with self.rpc.applicationProxy.editImager(imager_index=1):
                    self.rpc.imager.imageQualityCheck.enabled = True
                    self.assertTrue(self.rpc.imager.imageQualityCheck.enabled)
                    self.rpc.imager.imageQualityCheck.enabled = False
                    self.assertFalse(self.rpc.imager.imageQualityCheck.enabled)
                    self.rpc.imager.imageQualityCheck.enabled = True
                    self.assertTrue(self.rpc.imager.imageQualityCheck.enabled)

    def test_sharpness_thresholdMinMax(self):
        with O2x5xxRPCDevice(deviceAddress) as self.rpc, self.rpc.mainProxy.requestSession():
            with self.rpc.sessionProxy.setOperatingMode(mode=1), self.rpc.editProxy.editApplication(
                    app_index=self.newApplicationIndex):
                with self.rpc.applicationProxy.editImager(imager_index=1):
                    self.rpc.imager.imageQualityCheck.enabled = True
                    value = {"min": 1000, "max": 10000}
                    self.rpc.imager.imageQualityCheck.sharpness_thresholdMinMax = value
                    self.assertEqual(self.rpc.imager.imageQualityCheck.sharpness_thresholdMinMax, value)
                    with self.assertRaises(ValueError):
                        value = {"min": -1, "max": 10000}
                        self.rpc.imager.imageQualityCheck.sharpness_thresholdMinMax = value
                    with self.assertRaises(ValueError):
                        value = {"min": 0, "max": 1228801}
                        self.rpc.imager.imageQualityCheck.sharpness_thresholdMinMax = value
                    with self.assertRaises(ValueError):
                        value = {"min": 10000, "max": 200}
                        self.rpc.imager.imageQualityCheck.sharpness_thresholdMinMax = value

    def test_meanBrightness_thresholdMinMax(self):
        with O2x5xxRPCDevice(deviceAddress) as self.rpc, self.rpc.mainProxy.requestSession():
            with self.rpc.sessionProxy.setOperatingMode(mode=1), self.rpc.editProxy.editApplication(
                    app_index=self.newApplicationIndex):
                with self.rpc.applicationProxy.editImager(imager_index=1):
                    self.rpc.imager.imageQualityCheck.enabled = True
                    value = {"min": 10, "max": 220}
                    self.rpc.imager.imageQualityCheck.meanBrightness_thresholdMinMax = value
                    self.assertEqual(self.rpc.imager.imageQualityCheck.meanBrightness_thresholdMinMax, value)
                    with self.assertRaises(ValueError):
                        value = {"min": -1, "max": 255}
                        self.rpc.imager.imageQualityCheck.meanBrightness_thresholdMinMax = value
                    with self.assertRaises(ValueError):
                        value = {"min": 0, "max": 256}
                        self.rpc.imager.imageQualityCheck.meanBrightness_thresholdMinMax = value
                    with self.assertRaises(ValueError):
                        value = {"min": 220, "max": 10}
                        self.rpc.imager.imageQualityCheck.meanBrightness_thresholdMinMax = value

    def test_underexposedArea_thresholdMinMax(self):
        with O2x5xxRPCDevice(deviceAddress) as self.rpc, self.rpc.mainProxy.requestSession():
            with self.rpc.sessionProxy.setOperatingMode(mode=1), self.rpc.editProxy.editApplication(
                    app_index=self.newApplicationIndex):
                with self.rpc.applicationProxy.editImager(imager_index=1):
                    self.rpc.imager.imageQualityCheck.enabled = True
                    value = {"min": 10, "max": 90}
                    self.rpc.imager.imageQualityCheck.underexposedArea_thresholdMinMax = value
                    self.assertEqual(self.rpc.imager.imageQualityCheck.underexposedArea_thresholdMinMax, value)
                    with self.assertRaises(ValueError):
                        value = {"min": -1, "max": 100}
                        self.rpc.imager.imageQualityCheck.underexposedArea_thresholdMinMax = value
                    with self.assertRaises(ValueError):
                        value = {"min": 0, "max": 101}
                        self.rpc.imager.imageQualityCheck.underexposedArea_thresholdMinMax = value
                    with self.assertRaises(ValueError):
                        value = {"min": 110, "max": 10}
                        self.rpc.imager.imageQualityCheck.underexposedArea_thresholdMinMax = value

    def overexposedArea_thresholdMinMax(self):
        with O2x5xxRPCDevice(deviceAddress) as self.rpc, self.rpc.mainProxy.requestSession():
            with self.rpc.sessionProxy.setOperatingMode(mode=1), self.rpc.editProxy.editApplication(
                    app_index=self.newApplicationIndex):
                with self.rpc.applicationProxy.editImager(imager_index=1):
                    self.rpc.imager.imageQualityCheck.enabled = True
                    value = {"min": 10, "max": 90}
                    self.rpc.imager.imageQualityCheck.overexposedArea_thresholdMinMax = value
                    self.assertEqual(self.rpc.imager.imageQualityCheck.overexposedArea_thresholdMinMax, value)
                    with self.assertRaises(ValueError):
                        value = {"min": -1, "max": 100}
                        self.rpc.imager.imageQualityCheck.overexposedArea_thresholdMinMax = value
                    with self.assertRaises(ValueError):
                        value = {"min": 0, "max": 101}
                        self.rpc.imager.imageQualityCheck.overexposedArea_thresholdMinMax = value
                    with self.assertRaises(ValueError):
                        value = {"min": 110, "max": 10}
                        self.rpc.imager.imageQualityCheck.overexposedArea_thresholdMinMax = value
