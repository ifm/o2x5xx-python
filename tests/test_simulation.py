from unittest import TestCase
from source import O2x5xxRPCDevice
from tests.utils import *
from .config import *
import xmlrpc


class TestRPC_SimulationObject(TestCase):
    config_backup = None
    config_file = None
    app_import_file = None
    active_application_backup = None
    image_paths = [r"tests\resources\simulation\image_01.jpg", 
                   r"tests\resources\simulation\image_02.jpg",
                   r"tests\resources\simulation\image_03.jpg",
                   r"tests\resources\simulation\image_04.jpg",
                   r"tests\resources\simulation\image_05.jpg",]

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
            self.rpc.switchApplication(4)

    def tearDown(self) -> None:
        pass

    def test_createPayloadList(self):
        with O2x5xxRPCDevice(deviceAddress) as self.rpc, self.rpc.mainProxy.requestSession():
            with self.rpc.sessionProxy.setOperatingMode(mode=2):
                simulation = self.rpc.simulation
                payloadList = simulation.createPayloadList(image_paths=self.image_paths)
                self.assertEqual(len(payloadList), len(self.image_paths))
                for payload in payloadList:
                    self.assertIsInstance(payload, xmlrpc.client.Binary)

    def test_processImageSequence(self):
        with O2x5xxRPCDevice(deviceAddress) as self.rpc, self.rpc.mainProxy.requestSession():
            with self.rpc.sessionProxy.setOperatingMode(mode=2):
                simulation = self.rpc.simulation
                payloadList = simulation.createPayloadList(image_paths=self.image_paths)
                try:
                    simulation.processImageSequence(image_sequence=payloadList, force_trigger=True)
                except Exception as e:
                    self.fail(f"processImageSequence raised an exception: {e}")