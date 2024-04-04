import ast
import socket
import time
from unittest import TestCase
from source import O2x5xxPCICDevice
from source import O2x5xxRPCDevice
from source.static.configs import images_config
from tests.utils import *
from .config import *


class TestPCIC(TestCase):
    pcic = None
    rpc = None
    session = None
    config_file = None
    config_backup = None
    active_application_backup = None
    pin_layout = None

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

    def setUp(self):
        with O2x5xxPCICDevice(deviceAddress, pcicTcpPort) as pcic:
            result = pcic.activate_application(1)
            self.assertEqual(result, "*")

    def tearDown(self):
        pass

    def test_PCIC_client_timeout_property_and_autoconnect_true(self):
        timeout_values = [2, 6, 3, 9, 5, 7]
        with O2x5xxPCICDevice(deviceAddress, pcicTcpPort, autoconnect=True) as pcic:
            for _, x in enumerate(timeout_values):
                pcic.timeout = x
                self.assertEqual(pcic.timeout, x)

    def test_PCIC_client_timeout_property_and_autoconnect_false(self):
        timeout_values = [2, 6, 3, 9, 5, 7]
        with O2x5xxPCICDevice(deviceAddress, pcicTcpPort, autoconnect=False) as pcic:
            pcic.connect()
            for _, x in enumerate(timeout_values):
                pcic.timeout = x
                self.assertEqual(pcic.timeout, x)

    def test_PCIC_client_connect_timeout_with_wrong_ip_and_autoconnect_false(self):
        TIMEOUT_VALUE = 2
        start_time = time.time()
        with O2x5xxPCICDevice("192.168.0.5", pcicTcpPort, autoconnect=False, timeout=TIMEOUT_VALUE) as pcic:
            self.assertEqual(pcic.timeout, TIMEOUT_VALUE)
            with self.assertRaises(socket.timeout):
                pcic.connect()
        end_time = time.time()
        duration_secs = end_time - start_time
        self.assertLess(duration_secs, TIMEOUT_VALUE+1)

    def test_PCIC_client_connect_timeout_with_wrong_ip_and_autoconnect_true(self):
        TIMEOUT_VALUE = 2
        start_time = time.time()
        with self.assertRaises(socket.timeout):
            with O2x5xxPCICDevice("192.168.0.5", pcicTcpPort, autoconnect=True, timeout=TIMEOUT_VALUE) as pcic:
                pcic.occupancy_of_application_list()
        end_time = time.time()
        duration_secs = end_time - start_time
        self.assertLess(duration_secs, TIMEOUT_VALUE+1)

    def test_PCIC_client_with_multiple_connects(self):
        iterations = 100
        for i in range(iterations):
            with O2x5xxPCICDevice(deviceAddress, pcicTcpPort, autoconnect=False) as pcic:
                pcic.connect()
                result = pcic.occupancy_of_application_list()
                self.assertNotEqual(result, "!")
                self.assertNotEqual(result, "?")
                self.assertTrue(result.count('\t') >= 6)
                self.assertEqual(result, '006\t01\t01\t02\t03\t04\t05\t06')

    def test_PCIC_client_without_context_manager_with_autoconnect_False(self):
        device = O2x5xxPCICDevice(deviceAddress, pcicTcpPort, autoconnect=False)
        device.connect()
        result = device.occupancy_of_application_list()
        self.assertNotEqual(result, "!")
        self.assertNotEqual(result, "?")
        self.assertTrue(result.count('\t') >= 6)
        self.assertEqual(result, '006\t01\t01\t02\t03\t04\t05\t06')
        device.close()

    def test_PCIC_client_without_context_manager_with_autoconnect_True(self):
        device = O2x5xxPCICDevice(deviceAddress, pcicTcpPort, autoconnect=True)
        result = device.occupancy_of_application_list()
        self.assertNotEqual(result, "!")
        self.assertNotEqual(result, "?")
        self.assertTrue(result.count('\t') >= 6)
        self.assertEqual(result, '006\t01\t01\t02\t03\t04\t05\t06')
        device.close()

    def test_autoconnect_False(self):
        with O2x5xxPCICDevice(deviceAddress, pcicTcpPort, autoconnect=False) as pcic:
            with self.assertRaises(AttributeError):
                pcic.activate_application(1)
            with self.assertRaises(AttributeError):
                pcic.occupancy_of_application_list()
            with self.assertRaises(AttributeError):
                pcic.upload_process_interface_output_configuration(config=images_config)
            with self.assertRaises(AttributeError):
                pcic.retrieve_current_process_interface_configuration()
            with self.assertRaises(AttributeError):
                pcic.request_current_error_state()
            with self.assertRaises(AttributeError):
                pcic.request_current_error_state_decoded()
            with self.assertRaises(AttributeError):
                pcic.gated_software_trigger_on_or_off(state=1)
            with self.assertRaises(AttributeError):
                pcic.request_device_information()
            with self.assertRaises(AttributeError):
                pcic.return_a_list_of_available_commands()
            with self.assertRaises(AttributeError):
                pcic.request_last_image_taken()
            with self.assertRaises(AttributeError):
                pcic.request_last_image_taken_deserialized()
            with self.assertRaises(AttributeError):
                pcic.overwrite_data_of_a_string(container_id=1, data="Test")
            with self.assertRaises(AttributeError):
                pcic.read_string_from_defined_container(container_id=1)
            with self.assertRaises(AttributeError):
                pcic.return_the_current_session_id()
            with self.assertRaises(AttributeError):
                pcic.set_logic_state_of_an_id(io_id="01", state="1")
            with self.assertRaises(AttributeError):
                pcic.request_state_of_an_id(io_id="01")
            with self.assertRaises(AttributeError):
                pcic.turn_process_interface_output_on_or_off(state=0)
            with self.assertRaises(AttributeError):
                pcic.request_current_decoding_statistics()
            with self.assertRaises(AttributeError):
                pcic.execute_asynchronous_trigger()
            with self.assertRaises(AttributeError):
                pcic.execute_synchronous_trigger()
            with self.assertRaises(AttributeError):
                pcic.set_current_protocol_version(version=1)
            with self.assertRaises(AttributeError):
                pcic.request_current_protocol_version()
            with self.assertRaises(AttributeError):
                pcic.turn_state_of_view_indicator_on_or_off(state=1)
            with self.assertRaises(AttributeError):
                pcic.execute_currently_configured_button_functionality()

    def test_occupancy_of_application_list(self):
        with O2x5xxPCICDevice(deviceAddress, pcicTcpPort) as pcic:
            result = pcic.occupancy_of_application_list()
            self.assertNotEqual(result, "!")
            self.assertNotEqual(result, "?")
            self.assertTrue(result.count('\t') >= 6)
            self.assertEqual(result, '006\t01\t01\t02\t03\t04\t05\t06')

    def test_activate_application(self):
        with O2x5xxPCICDevice(deviceAddress, pcicTcpPort) as pcic:
            application_list = pcic.occupancy_of_application_list()
            initial_active_application = application_list.split("\t")[1]
            available_applications = application_list.split("\t")[2:]
            result = pcic.activate_application(available_applications[0])
            self.assertEqual(result, "*")
            active_application = pcic.occupancy_of_application_list().split("\t")[1]
            self.assertEqual(active_application, available_applications[0])
            result = pcic.activate_application(initial_active_application)
            self.assertEqual(result, "*")
            active_application = pcic.occupancy_of_application_list().split("\t")[1]
            self.assertEqual(active_application, initial_active_application)

    def test_retrieve_current_process_interface_configuration(self):
        with O2x5xxPCICDevice(deviceAddress, pcicTcpPort) as pcic:
            result = pcic.activate_application(5)
            self.assertEqual(result, "*")
            result = pcic.retrieve_current_process_interface_configuration()
            self.assertIsInstance(ast.literal_eval(result[9:]), dict)

    def test_upload_process_interface_output_configuration(self):
        with O2x5xxPCICDevice(deviceAddress, pcicTcpPort) as pcic:
            result = pcic.upload_process_interface_output_configuration(config=images_config)
            self.assertEqual(result, "*")
            result = pcic.retrieve_current_process_interface_configuration()
            self.assertEqual(ast.literal_eval(result[9:]), images_config)

    def test_request_current_error_state(self):
        with O2x5xxPCICDevice(deviceAddress, pcicTcpPort) as pcic:
            result = pcic.request_current_error_state()
            self.assertIsInstance(ast.literal_eval(result), int)

    def test_request_current_error_state_decoded(self):
        with O2x5xxPCICDevice(deviceAddress, pcicTcpPort) as pcic:
            error_code, error_msg = pcic.request_current_error_state_decoded()
            self.assertIsInstance(ast.literal_eval(error_code), int)
            self.assertEqual(error_code, '000000000')
            self.assertEqual(error_msg, 'No error detected')

    def test_gated_software_trigger_on_or_off(self):
        with O2x5xxPCICDevice(deviceAddress, pcicTcpPort) as pcic:
            result = pcic.activate_application(3)
            self.assertEqual(result, "*")
            result = pcic.gated_software_trigger_on_or_off(1)
            self.assertEqual(result, "*")
            result = pcic.gated_software_trigger_on_or_off(0)
            self.assertEqual(result, "*")

    def test_request_device_information(self):
        with O2x5xxPCICDevice(deviceAddress, pcicTcpPort) as pcic:
            result = pcic.request_device_information()
            self.assertEqual(result[:14], "IFM ELECTRONIC")

    def test_return_a_list_of_available_commands(self):
        with O2x5xxPCICDevice(deviceAddress, pcicTcpPort) as pcic:
            result = pcic.return_a_list_of_available_commands()
            self.assertTrue(len(result) > 800)

    def test_request_last_image_taken(self):
        with O2x5xxPCICDevice(deviceAddress, pcicTcpPort) as pcic:
            result = pcic.request_last_image_taken(1)
            self.assertIsInstance(result, bytes)
            self.assertTrue(len(result) > 1000)

    def test_request_multiple_images_taken(self):
        with O2x5xxPCICDevice(deviceAddress, pcicTcpPort) as pcic:
            result = pcic.activate_application(4)
            self.assertEqual(result, "*")
            result = pcic.execute_asynchronous_trigger()
            self.assertEqual(result, "*")
            result = pcic.request_last_image_taken(1)
            self.assertIsInstance(result, bytes)
            self.assertTrue(len(result) > 10000)

    def test_request_multiple_images_taken_deserialized(self):
        with O2x5xxPCICDevice(deviceAddress, pcicTcpPort) as pcic:
            result = pcic.activate_application(4)
            self.assertEqual(result, "*")
            time.sleep(2)
            result = pcic.execute_synchronous_trigger()
            # time.sleep(2)
            self.assertNotEqual(result, "!")
            # time.sleep(2)
            result = pcic.request_last_image_taken_deserialized(datatype='bytes')
            # time.sleep(2)
            self.assertEqual(len(result), 5)
            for i in range(len(result)):
                self.assertIsInstance(result[i][0], dict)
                self.assertIsInstance(result[i][1], bytes)
            for i in range(len(result)):
                result = pcic.request_last_image_taken_deserialized(image_id=1, datatype='ndarray')
                self.assertIsInstance(result[i][0], dict)
                self.assertEqual(type(result[i][1]).__name__, 'ndarray')

    def test_overwrite_data_of_a_string(self):
        with O2x5xxPCICDevice(deviceAddress, pcicTcpPort) as pcic:
            for i in range(maxNumberContainers + 1):
                # Test for data with leading number
                container_string = "1234567890 Hello container number {id}!".format(id=i)
                result = pcic.overwrite_data_of_a_string(container_id=i, data=container_string)
                self.assertEqual(result, "*")

                # Test for data with leading letter
                container_string = "Hello container number {id}!".format(id=i)
                result = pcic.overwrite_data_of_a_string(container_id=i, data=container_string)
                self.assertEqual(result, "*")

    def test_read_string_from_defined_container(self):
        with O2x5xxPCICDevice(deviceAddress, pcicTcpPort) as pcic:
            # Test for data with leading number
            for i in range(maxNumberContainers + 1):
                container_string = "1234567890 container number {id}".format(id=i)
                result = pcic.overwrite_data_of_a_string(container_id=i, data=container_string)
                self.assertEqual(result, "*")
            for i in range(maxNumberContainers + 1):
                container_string = "1234567890 container number {id}".format(id=i)
                result = pcic.read_string_from_defined_container(container_id=i)
                self.assertEqual(result[9:], container_string)

            # Test for data with leading letter
            for i in range(maxNumberContainers + 1):
                container_string = "Hello container number {id}!".format(id=i)
                result = pcic.overwrite_data_of_a_string(container_id=i, data=container_string)
                self.assertEqual(result, "*")
            for i in range(maxNumberContainers + 1):
                container_string = "Hello container number {id}!".format(id=i)
                result = pcic.read_string_from_defined_container(container_id=i)
                self.assertEqual(result[9:], container_string)

    def test_return_the_current_session_id(self):
        with O2x5xxPCICDevice(deviceAddress, pcicTcpPort) as pcic:
            result = pcic.return_the_current_session_id()
            self.assertIsInstance(int(result), int)

    def test_set_logic_state_of_an_id(self):
        with O2x5xxPCICDevice(deviceAddress, pcicTcpPort) as pcic, O2x5xxRPCDevice(deviceAddress) as rpc:
            pin_layout = int(rpc.getParameter(value="PinLayout"))
            if pin_layout == 2 or pin_layout == 0:
                sensor_digital_ios = [1, 2]
            else:
                sensor_digital_ios = [1, 2, 3, 4]
            for io_id in sensor_digital_ios:
                result = pcic.set_logic_state_of_an_id(io_id=io_id, state=1)
                self.assertEqual(result, "*")
                result = pcic.set_logic_state_of_an_id(io_id=io_id, state=0)
                self.assertEqual(result, "*")

    def test_request_state_of_an_id(self):
        with O2x5xxPCICDevice(deviceAddress, pcicTcpPort) as pcic:
            result = pcic.request_state_of_an_id(io_id=1)
            self.assertEqual(result, "010")

    def test_turn_process_interface_output_on_or_off(self):
        with O2x5xxPCICDevice(deviceAddress, pcicTcpPort) as pcic:
            result = pcic.activate_application(6)
            self.assertEqual(result, "*")
            time.sleep(1)
            result = pcic.turn_process_interface_output_on_or_off(7)
            self.assertEqual(result, "*")
            ticket, answer = pcic.read_next_answer()
            self.assertIsInstance(answer, bytes)
            result = pcic.turn_process_interface_output_on_or_off(0)
            self.assertEqual(result, "*")

    def test_request_current_decoding_statistics(self):
        with O2x5xxPCICDevice(deviceAddress, pcicTcpPort) as pcic:
            result = pcic.request_current_decoding_statistics()
            self.assertTrue(len(result) == 32)

    def test_execute_asynchronous_trigger(self):
        with O2x5xxPCICDevice(deviceAddress, pcicTcpPort) as pcic:
            result = pcic.execute_asynchronous_trigger()
            self.assertEqual(result, "*")

    def test_execute_synchronous_trigger(self):
        with O2x5xxPCICDevice(deviceAddress, pcicTcpPort) as pcic:
            time.sleep(2)
            result = pcic.execute_synchronous_trigger()
            self.assertNotEqual(result, "!")
            self.assertIsInstance(result, str)

    def test_set_current_protocol_version(self):
        with O2x5xxPCICDevice(deviceAddress, pcicTcpPort) as pcic, O2x5xxRPCDevice(deviceAddress) as rpc:
            initialPCICVersion = int(rpc.getParameter(value="PcicProtocolVersion"))
            # V3 only!
            if initialPCICVersion == 3:
                result = pcic.set_current_protocol_version(3)
                self.assertEqual(result, "*")

    def test_request_current_protocol_version(self):
        with O2x5xxPCICDevice(deviceAddress, pcicTcpPort) as pcic, O2x5xxRPCDevice(deviceAddress) as rpc:
            initialPCICVersion = int(rpc.getParameter(value="PcicProtocolVersion"))
            # V3 only!
            if initialPCICVersion == 3:
                result = pcic.set_current_protocol_version(3)
                self.assertEqual(result, "*")
                result = pcic.request_current_protocol_version()
                self.assertEqual(result, "03 01 02 03")
                # Set back to initial version
                result = pcic.set_current_protocol_version(initialPCICVersion)
                self.assertEqual(result, "*")
                result = pcic.request_current_protocol_version()
                self.assertEqual(result, "0{} 01 02 03".format(str(initialPCICVersion)))

    def test_timeout(self):
        TIMEOUT_VALUES = range(1, 5)

        # Passing timeout value to constructor
        for timeout_value in TIMEOUT_VALUES:
            with O2x5xxPCICDevice(deviceAddress, pcicTcpPort, timeout=timeout_value) as pcic:
                self.assertEqual(pcic.timeout, timeout_value)

        # Passing timeout value to constructor with autoconnect = False
        for timeout_value in TIMEOUT_VALUES:
            with O2x5xxPCICDevice(deviceAddress, pcicTcpPort, timeout=timeout_value, autoconnect=False) as pcic:
                self.assertEqual(pcic.timeout, timeout_value)

        # Passing timeout value to property
        for timeout_value in TIMEOUT_VALUES:
            with O2x5xxPCICDevice(deviceAddress, pcicTcpPort) as pcic:
                pcic.timeout = timeout_value
                self.assertEqual(pcic.timeout, timeout_value)

        # Passing timeout value to property with autoconnect = False
        for timeout_value in TIMEOUT_VALUES:
            with O2x5xxPCICDevice(deviceAddress, pcicTcpPort, autoconnect=False) as pcic:
                pcic.timeout = timeout_value
                self.assertEqual(pcic.timeout, timeout_value)
