from unittest import TestCase
from source.device import O2x5xxDevice, O2x5xxDeviceV2, O2x5xxRPCDevice
from tests.utils import *
from .config import *


class TestDevice(TestCase):
    config_backup = None
    active_application_backup = None

    # @classmethod
    # def setUpClass(cls) -> None:
    #     with O2x5xxRPCDevice(deviceAddress) as rpc:
    #         with rpc.mainProxy.requestSession():
    #             cls.config_backup = rpc.session.exportConfig()
    #             cls.active_application_backup = rpc.getParameter("ActiveApplication")
    #             configFile = getImportSetupByPinLayout(rpc=rpc)['config_file']
    #             configFile = rpc.session.readConfigFile(configFile=configFile)
    #             rpc.session.importConfig(configFile, global_settings=True, network_settings=False,
    #                                      applications=True)
    #             rpc.switchApplication(1)
    #
    # @classmethod
    # def tearDownClass(cls) -> None:
    #     with O2x5xxRPCDevice(deviceAddress) as rpc:
    #         with rpc.mainProxy.requestSession():
    #             rpc.session.importConfig(cls.config_backup, global_settings=True, network_settings=False,
    #                                      applications=True)
    #             if cls.active_application_backup != "0":
    #                 rpc.switchApplication(cls.active_application_backup)

    def setUp(self) -> None:
        with O2x5xxRPCDevice(deviceAddress) as rpc:
            rpc.switchApplication(1)

    def tearDown(self) -> None:
        pass

    def test_O2x5xxDevice(self):
        with O2x5xxDevice(deviceAddress, pcicTcpPort) as device:
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
        with O2x5xxDeviceV2(deviceAddress, pcicTcpPort) as device:
            # PCIC
            result = device.pcic.occupancy_of_application_list()
            self.assertNotEqual(result, "!")
            self.assertNotEqual(result, "?")
            self.assertTrue(result.count('\t') >= 6)
            self.assertEqual(result, '006\t01\t01\t02\t03\t04\t05\t06')
            # RPC
            result = device.rpc.getAllParameters()
            self.assertIsInstance(result, dict)
