import socket
from unittest import TestCase
from source import O2x5xxDevice
from source import O2x5xxDeviceV2
from tests.utils import *
from .config import *
import time


class TestDeviceV1(TestCase):
    device = None
    config_file = None
    config_backup = None
    active_application_backup = None

    @classmethod
    def setUpClass(cls) -> None:
        with O2x5xxDevice(deviceAddress) as cls.device:
            cls.config_file = getImportSetupByPinLayout(rpc=cls.device.rpc)['config_file']
            cls.app_import_file = getImportSetupByPinLayout(rpc=cls.device.rpc)['app_import_file']
            if importDeviceConfigUnittests:
                cls.active_application_backup = cls.device.rpc.getParameter("ActiveApplication")
                with cls.device.rpc.mainProxy.requestSession():
                    cls.config_backup = cls.device.rpc.session.exportConfig()
                    _configFile = cls.device.rpc.session.readDeviceConfigFile(configFile=cls.config_file)
                    cls.device.rpc.session.importConfig(_configFile, global_settings=True, network_settings=False,
                                                        applications=True)

    @classmethod
    def tearDownClass(cls) -> None:
        if importDeviceConfigUnittests:
            with O2x5xxDevice(deviceAddress) as cls.device:
                with cls.device.rpc.mainProxy.requestSession():
                    cls.device.rpc.session.importConfig(cls.config_backup, global_settings=True, network_settings=False,
                                                        applications=True)
                    if cls.active_application_backup != "0":
                        cls.device.rpc.switchApplication(cls.active_application_backup)

    def setUp(self):
        with O2x5xxDevice(deviceAddress, pcicTcpPort) as device:
            result = device.activate_application(1)
            self.assertEqual(result, "*")

    def tearDown(self):
        pass

    def test_device_v1_client_with_multiple_connects(self):
        iterations = 100
        for i in range(iterations):
            with O2x5xxDevice(deviceAddress, pcicTcpPort, autoconnect=False) as device:
                device.connect()
                result = device.occupancy_of_application_list()
                self.assertNotEqual(result, "!")
                self.assertNotEqual(result, "?")
                self.assertTrue(result.count('\t') >= 6)
                self.assertEqual(result, '006\t01\t01\t02\t03\t04\t05\t06')

    def test_device_v1_client_without_context_manager_with_autoconnect_False(self):
        device = O2x5xxDevice(deviceAddress, pcicTcpPort, autoconnect=False)
        device.connect()
        result = device.occupancy_of_application_list()
        self.assertNotEqual(result, "!")
        self.assertNotEqual(result, "?")
        device.disconnect()

    def test_device_v1_client_without_context_manager_with_autoconnect_True(self):
        device = O2x5xxDevice(deviceAddress, pcicTcpPort, autoconnect=True)
        result = device.occupancy_of_application_list()
        self.assertNotEqual(result, "!")
        self.assertNotEqual(result, "?")
        device.close()

    def test_RPC_client_device_v1_client_with_wrong_ip_and_autoconnect_true(self):
        with self.assertRaises(socket.timeout):
            with O2x5xxDevice("192.168.0.5", pcicTcpPort, autoconnect=True) as device:
                device.rpc.getParameter("ActiveApplication")

    def test_PCIC_client_device_v1_client_with_wrong_ip_and_autoconnect_true(self):
        with self.assertRaises(socket.timeout):
            with O2x5xxDevice("192.168.0.5", pcicTcpPort, autoconnect=True) as device:
                device.occupancy_of_application_list()

    def test_RPC_client_device_v1_client_with_wrong_ip_and_autoconnect_false(self):
        with self.assertRaises(socket.timeout):
            with O2x5xxDevice("192.168.0.5", pcicTcpPort, autoconnect=False) as device:
                device.rpc.getParameter("ActiveApplication")

    def test_PCIC_client_device_v1_client_with_wrong_ip_and_autoconnect_false(self):
        with self.assertRaises(socket.timeout):
            with O2x5xxDevice("192.168.0.5", pcicTcpPort, autoconnect=False) as device:
                device.connect()

    def test_PCIC_client_device_v1_client_with_wrong_ip_and_autoconnect_false_and_timeout(self):
        TIMEOUT_VALUE = 2
        start_time = time.time()
        with self.assertRaises(socket.timeout):
            with O2x5xxDevice("192.168.0.5", pcicTcpPort, autoconnect=False, timeout=2) as device:
                device.connect()
        end_time = time.time()
        duration_secs = end_time - start_time
        self.assertLess(duration_secs, TIMEOUT_VALUE+1)

    def test_RPC_client_device_v1_client_with_wrong_ip_and_autoconnect_false_and_timeout(self):
        TIMEOUT_VALUE = 2
        start_time = time.time()
        with self.assertRaises(socket.timeout):
            with O2x5xxDevice("192.168.0.5", pcicTcpPort, autoconnect=False, timeout=2) as device:
                device.rpc.getParameter("ActiveApplication")
        end_time = time.time()
        duration_secs = end_time - start_time
        self.assertLess(duration_secs, TIMEOUT_VALUE+1)


class TestDeviceV2(TestCase):
    device = None
    config_file = None
    config_backup = None
    active_application_backup = None

    @classmethod
    def setUpClass(cls) -> None:
        with O2x5xxDeviceV2(deviceAddress) as cls.device:
            cls.config_file = getImportSetupByPinLayout(rpc=cls.device.rpc)['config_file']
            cls.app_import_file = getImportSetupByPinLayout(rpc=cls.device.rpc)['app_import_file']
            if importDeviceConfigUnittests:
                cls.active_application_backup = cls.device.rpc.getParameter("ActiveApplication")
                with cls.device.rpc.mainProxy.requestSession():
                    cls.config_backup = cls.device.rpc.session.exportConfig()
                    _configFile = cls.device.rpc.session.readDeviceConfigFile(configFile=cls.config_file)
                    cls.device.rpc.session.importConfig(_configFile, global_settings=True, network_settings=False,
                                                        applications=True)

    @classmethod
    def tearDownClass(cls) -> None:
        if importDeviceConfigUnittests:
            with O2x5xxDeviceV2(deviceAddress) as cls.device:
                with cls.device.rpc.mainProxy.requestSession():
                    cls.device.rpc.session.importConfig(cls.config_backup, global_settings=True, network_settings=False,
                                                        applications=True)
                    if cls.active_application_backup != "0":
                        cls.device.rpc.switchApplication(cls.active_application_backup)

    def setUp(self):
        with O2x5xxDeviceV2(deviceAddress, pcicTcpPort) as device:
            result = device.pcic.activate_application(1)
            self.assertEqual(result, "*")

    def tearDown(self):
        pass

    def test_device_v2_client_with_multiple_connects_with_autoconnect_False(self):
        iterations = 100
        for i in range(iterations):
            with O2x5xxDeviceV2(deviceAddress, pcicTcpPort, autoconnect=False) as device:
                device.pcic.connect()
                result = device.pcic.occupancy_of_application_list()
                self.assertNotEqual(result, "!")
                self.assertNotEqual(result, "?")

    def test_device_v2_client_without_context_manager_with_autoconnect_False(self):
        device = O2x5xxDeviceV2(deviceAddress, pcicTcpPort, autoconnect=False)
        device.pcic.connect()
        result = device.pcic.occupancy_of_application_list()
        self.assertNotEqual(result, "!")
        self.assertNotEqual(result, "?")
        device.pcic.disconnect()
        device.rpc.mainProxy.close()

    def test_device_v2_client_without_context_manager_with_autoconnect_True(self):
        device = O2x5xxDeviceV2(deviceAddress, pcicTcpPort, autoconnect=True)
        result = device.pcic.occupancy_of_application_list()
        self.assertNotEqual(result, "!")
        self.assertNotEqual(result, "?")
        device.pcic.close()
        device.rpc.mainProxy.close()

    def test_RPC_client_device_v2_client_with_wrong_ip_and_autoconnect_true(self):
        with self.assertRaises(socket.timeout):
            with O2x5xxDeviceV2("192.168.0.5", pcicTcpPort, autoconnect=True) as device:
                device.rpc.getParameter("ActiveApplication")

    def test_PCIC_client_device_v2_client_with_wrong_ip_and_autoconnect_true(self):
        with self.assertRaises(socket.timeout):
            with O2x5xxDeviceV2("192.168.0.5", pcicTcpPort, autoconnect=True) as device:
                device.pcic.occupancy_of_application_list()

    def test_RPC_client_device_v2_client_with_wrong_ip_and_autoconnect_false(self):
        with self.assertRaises(socket.timeout):
            with O2x5xxDeviceV2("192.168.0.5", pcicTcpPort, autoconnect=False) as device:
                device.rpc.getParameter("ActiveApplication")

    def test_PCIC_client_device_v2_client_with_wrong_ip_and_autoconnect_false(self):
        with self.assertRaises(socket.timeout):
            with O2x5xxDeviceV2("192.168.0.5", pcicTcpPort, autoconnect=False) as device:
                device.pcic.connect()

    def test_PCIC_client_device_v2_client_with_wrong_ip_and_autoconnect_false_and_timeout(self):
        TIMEOUT_VALUE = 2
        start_time = time.time()
        with self.assertRaises(socket.timeout):
            with O2x5xxDeviceV2("192.168.0.5", pcicTcpPort, autoconnect=False, timeout=2) as device:
                device.pcic.connect()
        end_time = time.time()
        duration_secs = end_time - start_time
        self.assertLess(duration_secs, TIMEOUT_VALUE+1)

    def test_RPC_client_device_v2_client_with_wrong_ip_and_autoconnect_false_and_timeout(self):
        TIMEOUT_VALUE = 2
        start_time = time.time()
        with self.assertRaises(socket.timeout):
            with O2x5xxDeviceV2("192.168.0.5", pcicTcpPort, autoconnect=False, timeout=2) as device:
                device.rpc.getParameter("ActiveApplication")
        end_time = time.time()
        duration_secs = end_time - start_time
        self.assertLess(duration_secs, TIMEOUT_VALUE+1)
