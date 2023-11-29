from unittest import TestCase
from source import O2x5xxRPCDevice
from tests.utils import *
from .config import *


class TestRPC_ApplicationObject(TestCase):
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
                _configFile = rpc.session.readConfigFile(configFile=cls.config_file)
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
                allParams = self.rpc.application.getAllParameters()
                self.assertIsInstance(allParams, dict)

    def test_getParameter(self):
        with O2x5xxRPCDevice(deviceAddress) as self.rpc, self.rpc.mainProxy.requestSession():
            with self.rpc.sessionProxy.setOperatingMode(mode=1), self.rpc.editProxy.editApplication(
                    app_index=self.newApplicationIndex):
                result = self.rpc.application.getParameter(value="Name")
                self.assertIsInstance(result, str)

    def test_getAllParameterLimits(self):
        with O2x5xxRPCDevice(deviceAddress) as self.rpc, self.rpc.mainProxy.requestSession():
            with self.rpc.sessionProxy.setOperatingMode(mode=1), self.rpc.editProxy.editApplication(
                    app_index=self.newApplicationIndex):
                result = self.rpc.application.getAllParameterLimits()
                self.assertIsInstance(result, dict)

    def test_Type(self):
        with O2x5xxRPCDevice(deviceAddress) as self.rpc, self.rpc.mainProxy.requestSession():
            with self.rpc.sessionProxy.setOperatingMode(mode=1), self.rpc.editProxy.editApplication(
                    app_index=self.newApplicationIndex):
                result = self.rpc.application.Type
                self.assertIsInstance(result, str)

    def test_Name(self):
        with O2x5xxRPCDevice(deviceAddress) as self.rpc, self.rpc.mainProxy.requestSession():
            with self.rpc.sessionProxy.setOperatingMode(mode=1), self.rpc.editProxy.editApplication(
                    app_index=self.newApplicationIndex):
                self.assertEqual(self.rpc.application.Name, "New Application")
                self.rpc.application.Name = "New Application Name"
                self.assertEqual(self.rpc.application.Name, "New Application Name")
                # max 64 chars allowed
                self.rpc.application.Name = 64 * "X"
                self.assertEqual(self.rpc.application.Name, 64 * "X")
                with self.assertRaises(ValueError):
                    self.rpc.application.Name = 65 * "X"

    def test_Description(self):
        with O2x5xxRPCDevice(deviceAddress) as self.rpc, self.rpc.mainProxy.requestSession():
            with self.rpc.sessionProxy.setOperatingMode(mode=1), self.rpc.editProxy.editApplication(
                    app_index=self.newApplicationIndex):
                self.assertEqual(self.rpc.application.Description, "")
                self.rpc.application.Description = "New Application Description"
                self.assertEqual(self.rpc.application.Description, "New Application Description")
                # max 500 chars allowed
                self.rpc.application.Description = 500 * "X"
                self.assertEqual(self.rpc.application.Description, 500 * "X")
                with self.assertRaises(ValueError):
                    self.rpc.application.Description = 501 * "X"

    def test_TriggerMode(self):
        with O2x5xxRPCDevice(deviceAddress) as self.rpc, self.rpc.mainProxy.requestSession():
            with self.rpc.sessionProxy.setOperatingMode(mode=1), self.rpc.editProxy.editApplication(
                    app_index=self.newApplicationIndex):
                # default trigger mode for newly created application
                self.assertEqual(self.rpc.application.TriggerMode, 1)
                self.rpc.application.TriggerMode = 2
                self.assertEqual(self.rpc.application.TriggerMode, 2)
                # allowed values: 1-8
                with self.assertRaises(ValueError):
                    self.rpc.application.TriggerMode = 0
                with self.assertRaises(ValueError):
                    self.rpc.application.TriggerMode = 9
                self.assertFalse(self.rpc.application.validate())

    def test_FrameRate(self):
        with O2x5xxRPCDevice(deviceAddress) as self.rpc, self.rpc.mainProxy.requestSession():
            with self.rpc.sessionProxy.setOperatingMode(mode=1), self.rpc.editProxy.editApplication(
                    app_index=self.newApplicationIndex):
                # default frame rate for newly created application
                self.assertEqual(self.rpc.application.FrameRate, 35.0)
                self.rpc.application.FrameRate = 20.0
                self.assertEqual(self.rpc.application.FrameRate, 20.0)
                # allowed range = [0.0167, 80.0]
                with self.assertRaises(ValueError):
                    self.rpc.application.FrameRate = 0.0166
                with self.assertRaises(ValueError):
                    self.rpc.application.FrameRate = 80.1
                self.assertFalse(self.rpc.application.validate())

    def test_HWROI(self):
        with O2x5xxRPCDevice(deviceAddress) as self.rpc, self.rpc.mainProxy.requestSession():
            with self.rpc.sessionProxy.setOperatingMode(mode=1), self.rpc.editProxy.editApplication(
                    app_index=self.newApplicationIndex):
                # default HWROI for newly created application
                self.assertEqual(self.rpc.application.HWROI, {"x": 0, "y": 0, "width": 1280, "height": 960})
                self.rpc.application.HWROI = {"x": 100, "y": 100, "width": 640, "height": 640}
                self.assertEqual(self.rpc.application.HWROI, {"x": 100, "y": 100, "width": 640, "height": 640})
                self.rpc.application.HWROI = {"x": 100, "y": 100, "width": 640, "height": 128}
                self.assertEqual(self.rpc.application.HWROI, {"x": 100, "y": 100, "width": 640, "height": 128})
                # Check width < 640 but multiple of 16
                with self.assertRaises(ValueError):
                    self.rpc.application.HWROI = {"x": 100, "y": 100, "width": 624, "height": 128}
                # Check height < 128 but multiple of 16
                with self.assertRaises(ValueError):
                    self.rpc.application.HWROI = {"x": 100, "y": 100, "width": 640, "height": 112}
                # Check width > 640 but not multiple of 16
                with self.assertRaises(ValueError):
                    self.rpc.application.HWROI = {"x": 100, "y": 100, "width": 641, "height": 128}
                # Check height > 128 but not multiple of 16
                with self.assertRaises(ValueError):
                    self.rpc.application.HWROI = {"x": 100, "y": 100, "width": 640, "height": 129}
                self.assertFalse(self.rpc.application.validate())

    def test_Rotate180Degree(self):
        with O2x5xxRPCDevice(deviceAddress) as self.rpc, self.rpc.mainProxy.requestSession():
            with self.rpc.sessionProxy.setOperatingMode(mode=1), self.rpc.editProxy.editApplication(
                    app_index=self.newApplicationIndex):
                # default test_Rotate180Degree value for newly created application
                self.assertFalse(self.rpc.application.Rotate180Degree)
                self.rpc.application.Rotate180Degree = True
                self.assertTrue(self.rpc.application.Rotate180Degree)
                self.assertFalse(self.rpc.application.validate())

    def test_FocusDistance(self):
        with O2x5xxRPCDevice(deviceAddress) as self.rpc, self.rpc.mainProxy.requestSession():
            with self.rpc.sessionProxy.setOperatingMode(mode=1), self.rpc.editProxy.editApplication(
                    app_index=self.newApplicationIndex):
                self.rpc.application.FocusDistance = 1.2
                self.assertEqual(self.rpc.application.FocusDistance, 1.2)
                # allowed range = [0.035, 5]
                with self.assertRaises(ValueError):
                    self.rpc.application.FocusDistance = 5.001
                with self.assertRaises(ValueError):
                    self.rpc.application.FocusDistance = 0.034
                self.assertFalse(self.rpc.application.validate())

    def test_ImageEvaluationOrder(self):
        with O2x5xxRPCDevice(deviceAddress) as self.rpc, self.rpc.mainProxy.requestSession():
            with self.rpc.sessionProxy.setOperatingMode(mode=1), self.rpc.editProxy.editApplication(
                    app_index=self.newApplicationIndex):
                result = self.rpc.application.ImageEvaluationOrder
                self.assertEqual(result, "1 ")
                newImagerIndex01 = self.rpc.application.createImagerConfig()
                result = self.rpc.application.ImageEvaluationOrder
                self.assertEqual(result, "1 {} ".format(newImagerIndex01))
                newImagerIndex02 = self.rpc.application.createImagerConfig()
                result = self.rpc.application.ImageEvaluationOrder
                self.assertEqual(result, "1 {} {} ".format(newImagerIndex01, newImagerIndex02))

    def test_save(self):
        with O2x5xxRPCDevice(deviceAddress) as self.rpc, self.rpc.mainProxy.requestSession():
            with self.rpc.sessionProxy.setOperatingMode(mode=1):
                with self.rpc.editProxy.editApplication(app_index=self.newApplicationIndex):
                    self.rpc.application.FrameRate = 20.0
                    self.rpc.application.TriggerMode = 1
                    self.rpc.application.FocusDistance = 1.2
                    self.rpc.application.Rotate180Degree = True
                    self.rpc.application.save()

            self.rpc.switchApplication(applicationIndex=1)
            self.rpc.switchApplication(applicationIndex=self.newApplicationIndex)

            with self.rpc.sessionProxy.setOperatingMode(mode=1):
                with self.rpc.editProxy.editApplication(app_index=self.newApplicationIndex):
                    self.assertEqual(self.rpc.application.FrameRate, 20.0)
                    self.assertEqual(self.rpc.application.TriggerMode, 1)
                    self.assertEqual(self.rpc.application.FocusDistance, 1.2)
                    self.assertEqual(self.rpc.application.Rotate180Degree, True)

    def test_getImagerConfigList(self):
        with O2x5xxRPCDevice(deviceAddress) as self.rpc, self.rpc.mainProxy.requestSession():
            with self.rpc.sessionProxy.setOperatingMode(mode=1), self.rpc.editProxy.editApplication(
                    app_index=self.newApplicationIndex):
                result = self.rpc.application.getImagerConfigList()
                self.assertTrue(result)
                self.assertIsInstance(result, list)

    def test_availableImagerConfigTypes(self):
        with O2x5xxRPCDevice(deviceAddress) as self.rpc, self.rpc.mainProxy.requestSession():
            with self.rpc.sessionProxy.setOperatingMode(mode=1), self.rpc.editProxy.editApplication(
                    app_index=self.newApplicationIndex):
                result = self.rpc.application.availableImagerConfigTypes()
                self.assertTrue(result)
                self.assertIsInstance(result, list)

    def test_createImagerConfig(self):
        with O2x5xxRPCDevice(deviceAddress) as self.rpc, self.rpc.mainProxy.requestSession():
            with self.rpc.sessionProxy.setOperatingMode(mode=1), self.rpc.editProxy.editApplication(
                    app_index=self.newApplicationIndex):
                oldImagerConfigList = self.rpc.application.getImagerConfigList()
                _ = self.rpc.application.createImagerConfig()
                newImagerConfigList = self.rpc.application.getImagerConfigList()
                self.assertNotEqual(oldImagerConfigList, newImagerConfigList)

    def test_copyImagerConfig(self):
        with O2x5xxRPCDevice(deviceAddress) as self.rpc, self.rpc.mainProxy.requestSession():
            with self.rpc.sessionProxy.setOperatingMode(mode=1), self.rpc.editProxy.editApplication(
                    app_index=self.newApplicationIndex):
                oldImagerConfigList = self.rpc.application.getImagerConfigList()
                _ = self.rpc.application.copyImagerConfig(imagerIndex=1)
                newImagerConfigList = self.rpc.application.getImagerConfigList()
                self.assertNotEqual(oldImagerConfigList, newImagerConfigList)

    def test_deleteImagerConfig(self):
        with O2x5xxRPCDevice(deviceAddress) as self.rpc, self.rpc.mainProxy.requestSession():
            with self.rpc.sessionProxy.setOperatingMode(mode=1), self.rpc.editProxy.editApplication(
                    app_index=self.newApplicationIndex):
                oldImagerConfigList = self.rpc.application.getImagerConfigList()
                newImagerIndex = self.rpc.application.createImagerConfig()
                self.rpc.application.deleteImagerConfig(imagerIndex=newImagerIndex)
                newImagerConfigList = self.rpc.application.getImagerConfigList()
                self.assertEqual(oldImagerConfigList, newImagerConfigList)
