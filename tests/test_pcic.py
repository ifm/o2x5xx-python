from unittest import TestCase
from source import O2x5xxPCICDevice, O2x5xxRPCDevice
from source.static.configs import images_config
from tests.utils import *
from .config import *
import time
import ast


class TestPCIC(TestCase):
    pcic = None
    rpc = None
    session = None
    config_backup = None
    active_application_backup = None
    pin_layout = None

    @classmethod
    def setUpClass(cls):
        cls.pcic = O2x5xxPCICDevice(deviceAddress, pcicTcpPort)
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
        result = self.pcic.activate_application(1)
        self.assertEqual(result, "*")

    def test_occupancy_of_application_list(self):
        result = self.pcic.occupancy_of_application_list()
        self.assertNotEqual(result, "!")
        self.assertNotEqual(result, "?")
        self.assertTrue(result.count('\t') >= 6)
        self.assertEqual(result, '006\t01\t01\t02\t03\t04\t05\t06')

    def test_activate_application(self):
        application_list = self.pcic.occupancy_of_application_list()
        initial_active_application = application_list.split("\t")[1]
        available_applications = application_list.split("\t")[2:]
        result = self.pcic.activate_application(available_applications[0])
        self.assertEqual(result, "*")
        active_application = self.pcic.occupancy_of_application_list().split("\t")[1]
        self.assertEqual(active_application, available_applications[0])
        result = self.pcic.activate_application(initial_active_application)
        self.assertEqual(result, "*")
        active_application = self.pcic.occupancy_of_application_list().split("\t")[1]
        self.assertEqual(active_application, initial_active_application)

    def test_retrieve_current_process_interface_configuration(self):
        result = self.pcic.activate_application(5)
        self.assertEqual(result, "*")
        result = self.pcic.retrieve_current_process_interface_configuration()
        self.assertIsInstance(ast.literal_eval(result[9:]), dict)

    def test_upload_process_interface_output_configuration(self):
        result = self.pcic.upload_process_interface_output_configuration(config=images_config)
        self.assertEqual(result, "*")
        result = self.pcic.retrieve_current_process_interface_configuration()
        self.assertEqual(ast.literal_eval(result[9:]), images_config)

    def test_request_current_error_state(self):
        result = self.pcic.request_current_error_state()
        self.assertIsInstance(ast.literal_eval(result), int)

    def test_request_current_error_state_decoded(self):
        error_code, error_msg = self.pcic.request_current_error_state_decoded()
        self.assertIsInstance(ast.literal_eval(error_code), int)
        self.assertEqual(error_code, '000000000')
        self.assertEqual(error_msg, 'No error detected')

    def test_gated_software_trigger_on_or_off(self):
        result = self.pcic.activate_application(3)
        self.assertEqual(result, "*")
        result = self.pcic.gated_software_trigger_on_or_off(1)
        self.assertEqual(result, "*")
        result = self.pcic.gated_software_trigger_on_or_off(0)
        self.assertEqual(result, "*")

    def test_request_device_information(self):
        result = self.pcic.request_device_information()
        self.assertEqual(result[:14], "IFM ELECTRONIC")

    def test_return_a_list_of_available_commands(self):
        result = self.pcic.return_a_list_of_available_commands()
        self.assertTrue(len(result) > 800)

    def test_request_last_image_taken(self):
        result = self.pcic.request_last_image_taken(1)
        self.assertIsInstance(result, bytearray)
        self.assertTrue(len(result) > 1000)

    def test_request_multiple_images_taken(self):
        result = self.pcic.activate_application(4)
        self.assertEqual(result, "*")
        result = self.pcic.execute_asynchronous_trigger()
        self.assertEqual(result, "*")
        result = self.pcic.request_last_image_taken(1)
        self.assertIsInstance(result, bytearray)
        self.assertTrue(len(result) > 10000)

    def test_request_multiple_images_taken_deserialized(self):
        result = self.pcic.activate_application(4)
        self.assertEqual(result, "*")
        result = self.pcic.execute_asynchronous_trigger()
        self.assertEqual(result, "*")
        time.sleep(2)
        result = self.pcic.request_last_image_taken_deserialized(datatype='bytes')
        self.assertEqual(len(result), 5)
        for i in range(len(result)):
            self.assertIsInstance(result[i][0], dict)
            self.assertIsInstance(result[i][1], bytes)
        for i in range(len(result)):
            result = self.pcic.request_last_image_taken_deserialized(image_id=1, datatype='ndarray')
            self.assertIsInstance(result[i][0], dict)
            self.assertEqual(type(result[i][1]).__name__, 'ndarray')

    def test_overwrite_data_of_a_string(self):
        for i in range(maxNumberContainers + 1):
            # Test for data with leading number
            container_string = "1234567890 Hello container number {id}!".format(id=i)
            result = self.pcic.overwrite_data_of_a_string(container_id=i, data=container_string)
            self.assertEqual(result, "*")

            # Test for data with leading letter
            container_string = "Hello container number {id}!".format(id=i)
            result = self.pcic.overwrite_data_of_a_string(container_id=i, data=container_string)
            self.assertEqual(result, "*")

    def test_read_string_from_defined_container(self):
        # Test for data with leading number
        for i in range(maxNumberContainers + 1):
            container_string = "1234567890 container number {id}".format(id=i)
            result = self.pcic.overwrite_data_of_a_string(container_id=i, data=container_string)
            self.assertEqual(result, "*")
        for i in range(maxNumberContainers + 1):
            container_string = "1234567890 container number {id}".format(id=i)
            result = self.pcic.read_string_from_defined_container(container_id=i)
            self.assertEqual(result[9:], container_string)

        # Test for data with leading letter
        for i in range(maxNumberContainers + 1):
            container_string = "Hello container number {id}!".format(id=i)
            result = self.pcic.overwrite_data_of_a_string(container_id=i, data=container_string)
            self.assertEqual(result, "*")
        for i in range(maxNumberContainers + 1):
            container_string = "Hello container number {id}!".format(id=i)
            result = self.pcic.read_string_from_defined_container(container_id=i)
            self.assertEqual(result[9:], container_string)

    def test_return_the_current_session_id(self):
        result = self.pcic.return_the_current_session_id()
        self.assertIsInstance(int(result), int)

    def test_set_logic_state_of_an_id(self):
        pin_layout = int(self.rpc.getParameter(value="PinLayout"))
        if pin_layout == 2 or pin_layout == 0:
            sensor_digital_ios = [1, 2]
        else:
            sensor_digital_ios = [1, 2, 3, 4]
        for io_id in sensor_digital_ios:
            result = self.pcic.set_logic_state_of_an_id(io_id=io_id, state=1)
            self.assertEqual(result, "*")
            result = self.pcic.set_logic_state_of_an_id(io_id=io_id, state=0)
            self.assertEqual(result, "*")

    def test_request_state_of_an_id(self):
        result = self.pcic.request_state_of_an_id(io_id=1)
        self.assertEqual(result, "010")

    def test_turn_process_interface_output_on_or_off(self):
        result = self.pcic.activate_application(6)
        self.assertEqual(result, "*")
        time.sleep(1)
        result = self.pcic.turn_process_interface_output_on_or_off(7)
        self.assertEqual(result, "*")
        ticket, answer = self.pcic.read_next_answer()
        self.assertIsInstance(answer, bytearray)
        result = self.pcic.turn_process_interface_output_on_or_off(0)
        self.assertEqual(result, "*")

    def test_request_current_decoding_statistics(self):
        result = self.pcic.request_current_decoding_statistics()
        self.assertTrue(len(result) == 32)

    def test_execute_asynchronous_trigger(self):
        result = self.pcic.execute_asynchronous_trigger()
        self.assertEqual(result, "*")

    def test_execute_synchronous_trigger(self):
        result = self.pcic.execute_synchronous_trigger()
        self.assertNotEqual(result, "!")
        self.assertIsInstance(result, str)

    def test_set_current_protocol_version(self):
        initialPCICVersion = int(self.rpc.getParameter(value="PcicProtocolVersion"))
        # V3 only!
        if initialPCICVersion == 3:
            result = self.pcic.set_current_protocol_version(3)
            self.assertEqual(result, "*")

    def test_request_current_protocol_version(self):
        initialPCICVersion = int(self.rpc.getParameter(value="PcicProtocolVersion"))
        # V3 only!
        if initialPCICVersion == 3:
            result = self.pcic.set_current_protocol_version(3)
            self.assertEqual(result, "*")
            result = self.pcic.request_current_protocol_version()
            self.assertEqual(result, "03 01 02 03")
            # Set back to initial version
            result = self.pcic.set_current_protocol_version(initialPCICVersion)
            self.assertEqual(result, "*")
            result = self.pcic.request_current_protocol_version()
            self.assertEqual(result, "0{} 01 02 03".format(str(initialPCICVersion)))
