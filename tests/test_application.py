from unittest import TestCase
from o2x5xx import O2x5xxRPCDevice
from tests.utils import *
import xmlrpc.client
import unittest
import time
import sys
import os

SENSOR_ADDRESS = '192.168.0.69'


class TestRPC_ApplicationObject(TestCase):
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
        ping = self.rpc.doPing()
        self.assertEqual(ping, "up")

    def tearDown(self):
        self.edit.stopEditingApplication()
        self.edit.deleteApplication(applicationIndex=self.newAppIndex)
        # cancelSession() will implicitly set operation mode = 0
        self.session.cancelSession()

    def test_editImage(self):
        image001 = self.application.editImage(imageIndex=1)
        self.assertTrue(image001)
        with self.assertRaises(ValueError):
            self.application.editImage(imageIndex=2)

    def test_getAllParameters(self):
        allParams = self.application.getAllParameters()
        self.assertIsInstance(allParams, dict)

    def test_getParameter(self):
        result = self.application.getParameter(value="Name")
        self.assertIsInstance(result, str)

    def test_getAllParameterLimits(self):
        result = self.application.getAllParameterLimits()
        self.assertIsInstance(result, dict)

    def test_Type(self):
        result = self.application.Type
        self.assertIsInstance(result, str)

    def test_Name(self):
        self.assertEqual(self.application.Name, "New Application")
        self.application.Name = "New Application Name"
        self.assertEqual(self.application.Name, "New Application Name")
        # max 64 chars allowed
        self.application.Name = 64 * "X"
        self.assertEqual(self.application.Name, 64 * "X")
        with self.assertRaises(ValueError):
            self.application.Name = 65 * "X"

    def test_Description(self):
        self.assertEqual(self.application.Description, "")
        self.application.Description = "New Application Description"
        self.assertEqual(self.application.Description, "New Application Description")
        # max 500 chars allowed
        self.application.Description = 500 * "X"
        self.assertEqual(self.application.Description, 500 * "X")
        with self.assertRaises(ValueError):
            self.application.Description = 501 * "X"

    def test_TriggerMode(self):
        # default trigger mode for newly created application
        self.assertEqual(self.application.TriggerMode, 1)
        self.application.TriggerMode = 2
        self.assertEqual(self.application.TriggerMode, 2)
        # allowed values: 1-8
        with self.assertRaises(ValueError):
            self.application.TriggerMode = 0
        with self.assertRaises(ValueError):
            self.application.TriggerMode = 9
        self.assertFalse(self.application.validate())

    def test_FrameRate(self):
        # default frame rate for newly created application
        self.assertEqual(self.application.FrameRate, 35.0)
        self.application.FrameRate = 20.0
        self.assertEqual(self.application.FrameRate, 20.0)
        # allowed range = [0.0167, 80.0]
        with self.assertRaises(ValueError):
            self.application.FrameRate = 0.0166
        with self.assertRaises(ValueError):
            self.application.FrameRate = 80.1
        self.assertFalse(self.application.validate())

    def test_HWROI(self):
        # default HWROI for newly created application
        self.assertEqual(self.application.HWROI, {"x": 0, "y": 0, "width": 1280, "height": 960})
        self.application.HWROI = {"x": 100, "y": 100, "width": 640, "height": 640}
        self.assertEqual(self.application.HWROI, {"x": 100, "y": 100, "width": 640, "height": 640})
        with self.assertRaises(xmlrpc.client.Error):
            self.application.HWROI = {"x": 100, "y": 100, "width": 1280, "height": 960}
        with self.assertRaises(xmlrpc.client.Error):
            self.application.HWROI = {"x": 100, "y": 100, "width": 1, "height": 1}
        self.assertFalse(self.application.validate())

    def test_Rotate180Degree(self):
        # default test_Rotate180Degree value for newly created application
        self.assertFalse(self.application.Rotate180Degree)
        self.application.Rotate180Degree = True
        self.assertTrue(self.application.Rotate180Degree)
        self.assertFalse(self.application.validate())

    def test_FocusDistance(self):
        self.application.FocusDistance = 1.2
        self.assertEqual(self.application.FocusDistance, 1.2)
        # allowed range = [0.035, 5]
        with self.assertRaises(ValueError):
            self.application.FocusDistance = 5.001
        with self.assertRaises(ValueError):
            self.application.FocusDistance = 0.034
        self.assertFalse(self.application.validate())

    def test_ImageEvaluationOrder(self):
        result = self.application.ImageEvaluationOrder
        self.assertEqual(result, "1 ")
        newImagerIndex01 = self.application.createImagerConfig()
        result = self.application.ImageEvaluationOrder
        self.assertEqual(result, "1 {} ".format(newImagerIndex01))
        newImagerIndex02 = self.application.createImagerConfig()
        result = self.application.ImageEvaluationOrder
        self.assertEqual(result, "1 {} {} ".format(newImagerIndex01, newImagerIndex02))

    def test_save(self):
        self.application.FrameRate = 20.0
        self.application.TriggerMode = 1
        self.application.FocusDistance = 1.2
        self.application.Rotate180Degree = True
        self.application.save()
        self.session.edit.stopEditingApplication()
        self.session.cancelSession()
        self.rpc.switchApplication(applicationIndex=1)
        self.rpc.switchApplication(applicationIndex=self.newAppIndex)
        self.session = self.rpc.requestSession()
        self.edit = self.session.setOperatingMode(mode=1)
        self.application = self.edit.editApplication(applicationIndex=self.newAppIndex)
        self.assertEqual(self.application.FrameRate, 20.0)
        self.assertEqual(self.application.TriggerMode, 1)
        self.assertEqual(self.application.FocusDistance, 1.2)
        self.assertEqual(self.application.Rotate180Degree, True)

    def test_getImagerConfigList(self):
        result = self.application.getImagerConfigList()
        self.assertTrue(result)
        self.assertIsInstance(result, list)

    def test_availableImagerConfigTypes(self):
        result = self.application.availableImagerConfigTypes()
        self.assertTrue(result)
        self.assertIsInstance(result, list)

    def test_createImagerConfig(self):
        oldImagerConfigList = self.application.getImagerConfigList()
        _ = self.application.createImagerConfig()
        newImagerConfigList = self.application.getImagerConfigList()
        self.assertNotEqual(oldImagerConfigList, newImagerConfigList)

    def test_copyImagerConfig(self):
        oldImagerConfigList = self.application.getImagerConfigList()
        _ = self.application.copyImagerConfig(imagerIndex=1)
        newImagerConfigList = self.application.getImagerConfigList()
        self.assertNotEqual(oldImagerConfigList, newImagerConfigList)

    def test_deleteImagerConfig(self):
        oldImagerConfigList = self.application.getImagerConfigList()
        newImagerIndex = self.application.createImagerConfig()
        self.application.deleteImagerConfig(imagerIndex=newImagerIndex)
        newImagerConfigList = self.application.getImagerConfigList()
        self.assertEqual(oldImagerConfigList, newImagerConfigList)


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
