from unittest import TestCase
from source.device import O2x5xxDevice, O2x5xxDeviceV2, O2x5xxPCICDevice, O2x5xxRPCDevice
from tests.utils import *
from .config import *
import warnings


class TestDevice(TestCase):
    pcic = None
    rpc = None
    session = None
    config_backup = None
    active_application_backup = None
    pin_layout = None

    @classmethod
    def setUpClass(cls):
        with O2x5xxRPCDevice(deviceAddress) as cls.rpc:
            cls.session = cls.rpc.requestSession()
            cls.config_backup = cls.session.exportConfig()
            cls.active_application_backup = cls.rpc.getParameter("ActiveApplication")
            configFile = getImportSetupByPinLayout(rpc=cls.rpc)['config_file']
            configFile = cls.session.readConfigFile(configFile=configFile)
            cls.session.importConfig(configFile, global_settings=True, network_settings=False, applications=True)
            cls.session.cancelSession()
            cls.rpc.switchApplication(1)

    @classmethod
    def tearDownClass(cls):
        with O2x5xxRPCDevice(deviceAddress) as cls.rpc:
            cls.session = cls.rpc.requestSession()
            cls.session.importConfig(cls.config_backup, global_settings=True, network_settings=False, applications=True)
            if cls.active_application_backup != "0":
                cls.rpc.switchApplication(cls.active_application_backup)

    def setUp(self):
        with O2x5xxRPCDevice(deviceAddress) as self.rpc:
            self.rpc.switchApplication(1)
        warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed.*<ssl.SSLSocket.*>")
        warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed <socket.socket.*>")
        warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed running multiprocessing pool.*>")

    def test_O2x5xxDevice(self):
        device = O2x5xxDevice(deviceAddress, pcicTcpPort)
        # PCIC
        result = device.occupancy_of_application_list()
        self.assertNotEqual(result, "!")
        self.assertNotEqual(result, "?")
        self.assertTrue(result.count('\t') >= 6)
        self.assertEqual(result, '006\t01\t01\t02\t03\t04\t05\t06')
        # RPC
        result = device.rpc.getAllParameters()
        self.assertIsInstance(result, dict)

    def test_O2x5xxDeviceV2(self):
        device = O2x5xxDeviceV2(deviceAddress, pcicTcpPort)
        # PCIC
        result = device.pcic.occupancy_of_application_list()
        self.assertNotEqual(result, "!")
        self.assertNotEqual(result, "?")
        self.assertTrue(result.count('\t') >= 6)
        self.assertEqual(result, '006\t01\t01\t02\t03\t04\t05\t06')
        # RPC
        result = device.rpc.getAllParameters()
        self.assertIsInstance(result, dict)

    def test_O2x5xxRPCDevice_with_context_manager(self):
        with O2x5xxRPCDevice(address=deviceAddress) as device:
            result = device.rpc.getAllParameters()
            self.assertIsInstance(result, dict)

    def test_O2x5xxPCICDevice_with_context_manager(self):
        with O2x5xxPCICDevice(address=deviceAddress, port=pcicTcpPort) as device:
            result = device.occupancy_of_application_list()
            self.assertNotEqual(result, "!")
            self.assertNotEqual(result, "?")
            self.assertTrue(result.count('\t') >= 6)
            self.assertEqual(result, '006\t01\t01\t02\t03\t04\t05\t06')

    def test_O2x5xxRPCDevice_with_context_manager_with_autoconnect_False(self):
        with O2x5xxRPCDevice(address=deviceAddress, autoconnect=False) as device:
            # without connecting
            with self.assertRaises(TypeError):
                device.rpc.getTraceLogs(nLogs=10)
            # with connecting
            device.connect()
            numberLogs = 10
            traces = self.rpc.getTraceLogs(nLogs=numberLogs)
            self.assertIsInstance(traces, list)
            self.assertEqual(len(traces), numberLogs)

    def test_O2x5xxPCICDevice_with_context_manager_with_autoconnect_False(self):
        with O2x5xxPCICDevice(address=deviceAddress, port=pcicTcpPort, autoconnect=False) as device:
            # without connecting
            with self.assertRaises(AttributeError):
                _ = device.occupancy_of_application_list()
            # with connecting
            device.connect()
            result = device.occupancy_of_application_list()
            self.assertNotEqual(result, "!")
            self.assertNotEqual(result, "?")
            self.assertTrue(result.count('\t') >= 6)
            self.assertEqual(result, '006\t01\t01\t02\t03\t04\t05\t06')
