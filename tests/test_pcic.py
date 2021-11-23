from unittest import TestCase
from o2x5xx import O2x5xxDevice
from o2x5xx.static.configs import images_config
import time
import ast


class TestPCIC(TestCase):
	def setUp(self):
		time.sleep(1)
		self.sensor = O2x5xxDevice('169.254.2.42', 50010)

	def tearDown(self):
		self.sensor.close()
		time.sleep(1)

	def test_occupancy_of_application_list(self):
		result = self.sensor.occupancy_of_application_list()
		self.assertNotEqual(result, "!")
		self.assertNotEqual(result, "?")
		self.assertTrue(result.count('\t') >= 3)

	def test_activate_application(self):
		application_list = self.sensor.occupancy_of_application_list()
		initial_active_application = application_list.split("\t")[1]
		available_applications = application_list.split("\t")[2:]
		result = self.sensor.activate_application(available_applications[0])
		time.sleep(10)
		self.assertEqual(result, "*")
		active_application = self.sensor.occupancy_of_application_list().split("\t")[1]
		self.assertEqual(active_application, available_applications[0])
		result = self.sensor.activate_application(initial_active_application)
		time.sleep(10)
		self.assertEqual(result, "*")
		active_application = self.sensor.occupancy_of_application_list().split("\t")[1]
		self.assertEqual(active_application, initial_active_application)

	def test_retrieve_current_process_interface_configuration(self):
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
		result = self.sensor.gated_software_trigger_on_or_off(1)
		self.assertEqual(result, "*")
		time.sleep(1)
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

	def test_request_last_image_taken_deserialized(self):
		result = self.sensor.request_last_image_taken_deserialized(image_id=1, datatype='bytes')
		self.assertIsInstance(result[0][0], dict)
		self.assertIsInstance(result[0][1], bytes)
		result = self.sensor.request_last_image_taken_deserialized(image_id=1, datatype='ndarray')
		self.assertIsInstance(result[0][0], dict)
		self.assertEqual(type(result[0][1]).__name__, 'ndarray')

	def test_overwrite_data_of_a_string(self):
		result = self.sensor.overwrite_data_of_a_string(container_id=0, data="Hello World!")
		self.assertEqual(result, "*")

	def test_read_string_from_defined_container(self):
		result = self.sensor.overwrite_data_of_a_string(container_id=0, data="Hello World!")
		self.assertEqual(result, "*")
		result = self.sensor.read_string_from_defined_container(container_id=0)
		self.assertEqual(result[9:], "Hello World!")

	def test_return_the_current_session_id(self):
		result = self.sensor.return_the_current_session_id()
		# Depends on the state in iVA. 1 and 2 are valid session IDs
		self.assertTrue(int(result) == 1 or int(result) == 2)

	def test_set_logic_state_of_an_id(self):
		result = self.sensor.set_logic_state_of_an_id(io_id=1, state=1)
		self.assertEqual(result, "*")
		result = self.sensor.set_logic_state_of_an_id(io_id=1, state=0)
		self.assertEqual(result, "*")

	def test_request_state_of_an_id(self):
		result = self.sensor.request_state_of_an_id(io_id=1)
		self.assertEqual(result, "010")

	def test_turn_process_interface_output_on_or_off(self):
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
		# Only v3 supported at the moment.
		result = self.sensor.set_current_protocol_version(3)
		self.assertEqual(result, "*")

	def test_request_current_protocol_version(self):
		result = self.sensor.request_current_protocol_version()
		self.assertEqual(result, "03 03 03")
