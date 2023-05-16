from unittest import TestCase
from o2x5xx import O2x5xxDevice, O2x5xxRPCDevice
from o2x5xx.static.configs import images_config
import unittest
import time
import sys
import ast
import os

SENSOR_ADDRESS = '192.168.0.69'
PCIC_TCP_PORT = 50010
MAX_NUMBER_CONTAINERS = 9


class TestPCIC(TestCase):
    _sensor = None
    _config_backup = None
    _active_application_backup = None
    _pin_layout = None

    @classmethod
    def setUpClass(cls):
        cls._sensor = O2x5xxRPCDevice(SENSOR_ADDRESS)
        cls._config_backup = cls._sensor._export_config_bytes()
        cls._active_application_backup = cls._sensor.get_parameter("ActiveApplication")
        cls._pin_layout = int(cls._sensor.get_parameter("PinLayout"))
        if cls._pin_layout == 3:
            config_file = "../tests/deviceConfig/Unittest8PolDeviceConfig.o2d5xxcfg"
        elif cls._pin_layout == 0:
            config_file = "../tests/deviceConfig/Unittest5PolDeviceConfig.o2d5xxcfg"
        else:
            raise NotImplementedError(
                "Testcase for PIN layout {} not implemented yet!\nSee PIN layout overview here:\n"
                "0: M12 - 5 pins A Coded connector (compatible to O3D3xx camera, Trigger and 2Outs)\n"
                "1: reserved for O3D3xx 8pin (trigger, 3 OUTs, 2 INs ... analog OUT1)\n"
                "2: M12 - 5 pins L Coded connector\n"
                "3: M12 - 8 pins A Coded connector (different OUT-numbering then O3D3xx and with IN/OUT switching)\n"
                "4: reserved for CAN-5pin connector (like O3DPxx, O3M or O3R)")
        cls._sensor.import_config(config_file, global_settings=True, network_settings=False, applications=True)
        cls._sensor.switch_application(1)

    @classmethod
    def tearDownClass(cls):
        cls._sensor.import_config(cls._config_backup, global_settings=True, network_settings=False, applications=True)
        if cls._active_application_backup != "0":
            cls._sensor.switch_application(cls._active_application_backup)

    def setUp(self):
        time.sleep(1)
        self.sensor = O2x5xxDevice(SENSOR_ADDRESS, PCIC_TCP_PORT)
        result = self.sensor.activate_application(1)
        self.assertEqual(result, "*")

    def tearDown(self):
        self.sensor.close()
        time.sleep(1)

    def test_occupancy_of_application_list(self):
        result = self.sensor.occupancy_of_application_list()
        self.assertNotEqual(result, "!")
        self.assertNotEqual(result, "?")
        self.assertTrue(result.count('\t') >= 6)
        self.assertEqual(result, '006\t01\t01\t02\t03\t04\t05\t06')

    def test_activate_application(self):
        application_list = self.sensor.occupancy_of_application_list()
        initial_active_application = application_list.split("\t")[1]
        available_applications = application_list.split("\t")[2:]
        result = self.sensor.activate_application(available_applications[0])
        self.assertEqual(result, "*")
        active_application = self.sensor.occupancy_of_application_list().split("\t")[1]
        self.assertEqual(active_application, available_applications[0])
        result = self.sensor.activate_application(initial_active_application)
        self.assertEqual(result, "*")
        active_application = self.sensor.occupancy_of_application_list().split("\t")[1]
        self.assertEqual(active_application, initial_active_application)

    def test_retrieve_current_process_interface_configuration(self):
        result = self.sensor.activate_application(5)
        self.assertEqual(result, "*")
        result = self.sensor.retrieve_current_process_interface_configuration()
        self.assertIsInstance(ast.literal_eval(result[9:]), dict)

    def test_upload_process_interface_output_configuration(self):
        result = self.sensor.upload_process_interface_output_configuration(config=images_config)
        self.assertEqual(result, "*")
        result = self.sensor.retrieve_current_process_interface_configuration()
        self.assertEqual(ast.literal_eval(result[9:]), images_config)

    def test_request_current_error_state(self):
        result = self.sensor.request_current_error_state()
        self.assertIsInstance(ast.literal_eval(result), int)

    def test_request_current_error_state_decoded(self):
        error_code, error_msg = self.sensor.request_current_error_state_decoded()
        self.assertIsInstance(ast.literal_eval(error_code), int)
        self.assertEqual(error_code, '000000000')
        self.assertEqual(error_msg, 'No error detected')

    def test_gated_software_trigger_on_or_off(self):
        result = self.sensor.activate_application(3)
        self.assertEqual(result, "*")
        result = self.sensor.gated_software_trigger_on_or_off(1)
        self.assertEqual(result, "*")
        result = self.sensor.gated_software_trigger_on_or_off(0)
        self.assertEqual(result, "*")

    def test_request_device_information(self):
        result = self.sensor.request_device_information()
        self.assertEqual(result[:14], "IFM ELECTRONIC")

    def test_return_a_list_of_available_commands(self):
        result = self.sensor.return_a_list_of_available_commands()
        self.assertTrue(len(result) > 800)

    def test_request_last_image_taken(self):
        result = self.sensor.request_last_image_taken(1)
        self.assertIsInstance(result, bytearray)
        self.assertTrue(len(result) > 1000)

    def test_request_multiple_images_taken(self):
        result = self.sensor.activate_application(4)
        self.assertEqual(result, "*")
        result = self.sensor.execute_asynchronous_trigger()
        self.assertEqual(result, "*")
        result = self.sensor.request_last_image_taken(1)
        self.assertIsInstance(result, bytearray)
        self.assertTrue(len(result) > 10000)

    def test_request_multiple_images_taken_deserialized(self):
        result = self.sensor.activate_application(4)
        self.assertEqual(result, "*")
        result = self.sensor.execute_asynchronous_trigger()
        self.assertEqual(result, "*")
        result = self.sensor.request_last_image_taken_deserialized(image_id=1, datatype='bytes')
        self.assertEqual(len(result), 5)
        for i in range(len(result)):
            self.assertIsInstance(result[i][0], dict)
            self.assertIsInstance(result[i][1], bytes)
        for i in range(len(result)):
            result = self.sensor.request_last_image_taken_deserialized(image_id=1, datatype='ndarray')
            self.assertIsInstance(result[i][0], dict)
            self.assertEqual(type(result[i][1]).__name__, 'ndarray')

    def test_overwrite_data_of_a_string(self):
        for i in range(MAX_NUMBER_CONTAINERS + 1):
            # Test for data with leading number
            container_string = "1234567890 Hello container number {id}!".format(id=i)
            result = self.sensor.overwrite_data_of_a_string(container_id=i, data=container_string)
            self.assertEqual(result, "*")

            # Test for data with leading letter
            container_string = "Hello container number {id}!".format(id=i)
            result = self.sensor.overwrite_data_of_a_string(container_id=i, data=container_string)
            self.assertEqual(result, "*")

    def test_read_string_from_defined_container(self):
        # Test for data with leading number
        for i in range(MAX_NUMBER_CONTAINERS + 1):
            container_string = "1234567890 container number {id}".format(id=i)
            result = self.sensor.overwrite_data_of_a_string(container_id=i, data=container_string)
            self.assertEqual(result, "*")
        for i in range(MAX_NUMBER_CONTAINERS + 1):
            container_string = "1234567890 container number {id}".format(id=i)
            result = self.sensor.read_string_from_defined_container(container_id=i)
            self.assertEqual(result[9:], container_string)

        # Test for data with leading letter
        for i in range(MAX_NUMBER_CONTAINERS + 1):
            container_string = "Hello container number {id}!".format(id=i)
            result = self.sensor.overwrite_data_of_a_string(container_id=i, data=container_string)
            self.assertEqual(result, "*")
        for i in range(MAX_NUMBER_CONTAINERS + 1):
            container_string = "Hello container number {id}!".format(id=i)
            result = self.sensor.read_string_from_defined_container(container_id=i)
            self.assertEqual(result[9:], container_string)

    def test_return_the_current_session_id(self):
        result = self.sensor.return_the_current_session_id()
        self.assertIsInstance(int(result), int)

    def test_set_logic_state_of_an_id(self):
        if self._pin_layout == 2:
            sensor_digital_ios = [1, 2]
        else:
            sensor_digital_ios = [1, 2, 3, 4]
        for io_id in sensor_digital_ios:
            result = self.sensor.set_logic_state_of_an_id(io_id=io_id, state=1)
            self.assertEqual(result, "*")
            result = self.sensor.set_logic_state_of_an_id(io_id=io_id, state=0)
            self.assertEqual(result, "*")

    def test_request_state_of_an_id(self):
        result = self.sensor.request_state_of_an_id(io_id=1)
        self.assertEqual(result, "010")

    def test_turn_process_interface_output_on_or_off(self):
        result = self.sensor.activate_application(6)
        self.assertEqual(result, "*")
        time.sleep(1)
        result = self.sensor.turn_process_interface_output_on_or_off(7)
        self.assertEqual(result, "*")
        ticket, answer = self.sensor.read_next_answer()
        self.assertIsInstance(answer, bytearray)
        result = self.sensor.turn_process_interface_output_on_or_off(0)
        self.assertEqual(result, "*")

    def test_request_current_decoding_statistics(self):
        result = self.sensor.request_current_decoding_statistics()
        self.assertTrue(len(result) == 32)

    def test_execute_asynchronous_trigger(self):
        result = self.sensor.execute_asynchronous_trigger()
        self.assertEqual(result, "*")

    def test_execute_synchronous_trigger(self):
        result = self.sensor.execute_synchronous_trigger()
        self.assertNotEqual(result, "!")
        self.assertIsInstance(result, str)

    def test_set_current_protocol_version(self):
        # V3
        result = self.sensor.set_current_protocol_version(3)
        self.assertEqual(result, "*")
        # V1 TODO
        # result = self.sensor.set_current_protocol_version(1)
        # self.assertEqual(result, "*")

    def test_request_current_protocol_version(self):
        initial_pcic_version = int(self.sensor.rpc.get_parameter(parameter_name="PcicProtocolVersion"))
        # # V1
        # result = self.sensor.set_current_protocol_version(1)
        # self.assertEqual(result, "*")
        # result = self.sensor.request_current_protocol_version()
        # self.assertEqual(result, "01 01 02 03")
        # # V2
        # result = self.sensor.set_current_protocol_version(2)
        # self.assertEqual(result, "*")
        # result = self.sensor.request_current_protocol_version()
        # self.assertEqual(result, "02 01 02 03")
        # V3
        result = self.sensor.set_current_protocol_version(3)
        self.assertEqual(result, "*")
        result = self.sensor.request_current_protocol_version()
        self.assertEqual(result, "03 01 02 03")
        # Set back to initial version
        result = self.sensor.set_current_protocol_version(initial_pcic_version)
        self.assertEqual(result, "*")
        result = self.sensor.request_current_protocol_version()
        self.assertEqual(result, "0{} 01 02 03".format(str(initial_pcic_version)))


if __name__ == '__main__':
    try:
        SENSOR_ADDRESS = sys.argv[1]
        LOGFILE = sys.argv[2]
    except IndexError:
        raise ValueError("Argument(s) are missing. Here is an example for running the unittests with logfile:\n"
                         "python test_pcic.py 192.168.0.69 True\n"
                         "Here is an example for running the unittests without an logfile:\n"
                         "python test_pcic.py 192.168.0.69 False")

    device_rpc = O2x5xxRPCDevice(address=SENSOR_ADDRESS)
    PCIC_TCP_PORT = int(device_rpc.get_parameter(parameter_name="PcicTcpPort"))

    if LOGFILE:
        FIRMWARE_VERSION = device_rpc.get_sw_version()["IFM_Software"]
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        logfile = os.path.join('./logs', '{timestamp}_{firmware}_pcic_unittests_o2x5xx.log'
                               .format(timestamp=timestamp, firmware=FIRMWARE_VERSION))

        logfile = open(logfile, 'w')
        sys.stdout = logfile

        suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
        unittest.TextTestRunner(sys.stdout, verbosity=2).run(suite)

        logfile.close()

    else:
        suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
        unittest.TextTestRunner(verbosity=2).run(suite)
