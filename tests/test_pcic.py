from unittest import TestCase

from o2x5xx import O2x5xxDevice


class TestPcic(TestCase):
	def setUp(self):
		self.sensor = O2x5xxDevice('192.168.0.44', 50010)

	def test_sensor_answer_1(self):
		ticket, answer = self.sensor.read_next_answer()
		answer = answer.decode()
		self.assertEqual(answer, "star;1;4;5;6;7;stop")

	def test_sensor_answer_2(self):
		ticket, answer = self.sensor.read_next_answer()
		answer = answer.decode()
		self.assertEqual(answer, "star;11111;4;5;6;7;stop")
