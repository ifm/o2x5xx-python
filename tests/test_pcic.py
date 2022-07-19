from unittest import TestCase
from o2x5xx import O2x5xxDevice
from o2x5xx.static.configs import images_config
import unittest
import time
import sys
import ast
import os

SENSOR_ADDRESS = '192.168.0.69'
MAX_NUMBER_CONTAINERS = 9
DIGITAL_OUT_IDs = [1, 2, 3, 4]

O2X5xxDigitalIOs = {
    "O2D500": [1, 2, 3, 4],
    "O2D502": [1, 2, 3, 4],
    "O2D504": [1, 2, 3, 4],
    "O2D520": [1, 2, 3, 4],
    "O2D522": [1, 2, 3, 4],
    "O2D524": [1, 2, 3, 4],
    "O2D510": [1, 2],
    "O2D512": [1, 2],
    "O2D514": [1, 2],
    "O2D530": [1, 2],
    "O2D532": [1, 2],
    "O2D534": [1, 2],
    "O2D550": [1, 2],
    "O2D552": [1, 2],
    "O2D554": [1, 2],
    "M03896": [1, 2]
}


class TestPCIC(TestCase):

    def setUp(self):
        time.sleep(1)
        self.sensor = O2x5xxDevice(SENSOR_ADDRESS, 50010)
        result = self.sensor.activate_application(1)
        self.assertEqual(result, "*")

    def tearDown(self):
        self.sensor.close()
        time.sleep(1)

    def get_sensor_type_digital_ios(self):
        device_information = self.sensor.request_device_information()
        sensor_type = device_information.split('\t')[1]
        return O2X5xxDigitalIOs[sensor_type]

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
            container_string = "Hello container number {id}!".format(id=i)
            result = self.sensor.overwrite_data_of_a_string(container_id=i, data=container_string)
            self.assertEqual(result, "*")

    def test_read_string_from_defined_container(self):
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
        # Depends on the state in iVA. 1 and 2 are valid session IDs
        self.assertTrue(int(result) == 1 or int(result) == 2)

    def test_set_logic_state_of_an_id(self):
        sensor_digital_ios = self.get_sensor_type_digital_ios()
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
        # V3
        result = self.sensor.set_current_protocol_version(3)
        self.assertEqual(result, "*")
        result = self.sensor.request_current_protocol_version()
        self.assertEqual(result, "03 01 03")
        # V1 TODO
        # result = self.sensor.set_current_protocol_version(1)
        # self.assertEqual(result, "*")


if __name__ == '__main__':
    try:
        SENSOR_ADDRESS = sys.argv[1]
        FIRMWARE_VERSION = sys.argv[2]
        LOGFILE = sys.argv[3]
    except IndexError:
        raise ValueError("Argument(s) are missing. Here is an example for running the unittests: "
                         "python test_pcic.py 192.168.0.69 1.27.4991 True")

    if LOGFILE:
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        logfile = os.path.join('./logs', '{timestamp}_{firmware}_unittests_o2x5xx.log'
                               .format(timestamp=timestamp, firmware=FIRMWARE_VERSION))

        logfile = open(logfile, 'w')
        sys.stdout = logfile

        suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
        unittest.TextTestRunner(sys.stdout, verbosity=2).run(suite)

        logfile.close()

    else:
        suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
        unittest.TextTestRunner(verbosity=2).run(suite)
