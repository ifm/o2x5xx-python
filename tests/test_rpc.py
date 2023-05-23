from unittest import TestCase
from o2x5xx import O2x5xxRPCDevice
import numpy as np
import unittest
import time
import sys
import os

SENSOR_ADDRESS = '192.168.0.69'


class TestRPC(TestCase):
    _sensor = None
    _config_backup = None
    _active_application_backup = None

    @classmethod
    def get_import_setup_for_sensor_pin_layout(cls):
        pin_layout = int(cls._sensor.get_parameter("PinLayout"))
        if pin_layout == 3:
            result = {'config_file': "./deviceConfig/Unittest8PolDeviceConfig.o2d5xxcfg",
                      'app_import_file': "./deviceConfig/UnittestApplicationImport.o2d5xxapp"}
        elif pin_layout == 0 or pin_layout == 2:
            result = {'config_file': "./deviceConfig/Unittest5PolDeviceConfig.o2d5xxcfg",
                      'app_import_file': "./deviceConfig/UnittestApplicationImport.o2d5xxapp"}
        else:
            raise NotImplementedError(
                "Testcase for PIN layout {} not implemented yet!\nSee PIN layout overview here:\n"
                "0: M12 - 5 pins A Coded connector (compatible to O3D3xx camera, Trigger and 2Outs)\n"
                "1: reserved for O3D3xx 8pin (trigger, 3 OUTs, 2 INs ... analog OUT1)\n"
                "2: M12 - 5 pins L Coded connector\n"
                "3: M12 - 8 pins A Coded connector (different OUT-numbering then O3D3xx and with IN/OUT switching)\n"
                "4: reserved for CAN-5pin connector (like O3DPxx, O3M or O3R)")
        return result

    @classmethod
    def setUpClass(cls):
        cls._sensor = O2x5xxRPCDevice(SENSOR_ADDRESS)
        cls._config_backup = cls._sensor._export_config_bytes()
        cls._active_application_backup = cls._sensor.get_parameter("ActiveApplication")
        config_file = cls.get_import_setup_for_sensor_pin_layout()['config_file']
        cls._sensor.import_config(config_file, global_settings=True, network_settings=False, applications=True)
        cls._sensor.switch_application(1)

    @classmethod
    def tearDownClass(cls):
        cls._sensor.import_config(cls._config_backup, global_settings=True, network_settings=False, applications=True)
        if cls._active_application_backup != "0":
            cls._sensor.switch_application(cls._active_application_backup)

    def setUp(self):
        self.sensor = O2x5xxRPCDevice(SENSOR_ADDRESS)
        ping = self.sensor.doPing()
        self.assertEqual(ping, "up")

    def test_get_parameter(self):
        result = self.sensor.get_parameter(parameter_name="DeviceType")
        self.assertIsInstance(result, str)
        self.assertEqual(len(result), 5)

    def test_get_all_parameters(self):
        result = self.sensor.get_all_parameters()
        self.assertIsInstance(result, dict)

    def test_get_sw_version(self):
        result = self.sensor.get_sw_version()
        self.assertIsInstance(result, dict)

    def test_get_hw_info(self):
        result = self.sensor.get_hw_info()
        self.assertIsInstance(result, dict)

    def test_get_application_list(self):
        result = self.sensor.get_application_list()
        self.assertIsInstance(result, list)
        self.assertIsInstance(result[0], dict)
        self.assertIsInstance(result[1], dict)
        self.assertIsInstance(result[2], dict)
        self.assertIsInstance(result[3], dict)
        self.assertIsInstance(result[4], dict)
        self.assertIsInstance(result[5], dict)

    def test_switch_application(self):
        initial_application = int(self.sensor.get_parameter("ActiveApplication"))
        if initial_application > 1:
            self.sensor.switch_application(application_index=1)
            while self.sensor.get_parameter("OperatingMode") != "0":
                time.sleep(1)
            self.assertEqual(int(self.sensor.get_parameter("ActiveApplication")), 1)
        else:
            self.sensor.switch_application(application_index=2)
            while self.sensor.get_parameter("OperatingMode") != "0":
                time.sleep(1)
            self.assertEqual(int(self.sensor.get_parameter("ActiveApplication")), 2)
            time.sleep(5)
        # Switch back to initial application
        self.sensor.switch_application(application_index=initial_application)
        while self.sensor.get_parameter("OperatingMode") != "0":
            time.sleep(1)
        self.assertEqual(int(self.sensor.get_parameter("ActiveApplication")), initial_application)

    def test_get_application_statistic_data(self):
        application_active = self.sensor.get_parameter(parameter_name="ActiveApplication")
        result = self.sensor.get_application_statistic_data(application_id=int(application_active))
        self.assertIsInstance(result, dict)

    def test_reset_statistics(self):
        self.sensor.switch_application(application_index=2)
        for i in range(10):
            self.sensor.trigger()
        result = self.sensor.get_application_statistic_data(application_id=2)
        self.assertTrue(result['number_of_frames'] > 0)
        self.sensor.reset_statistics()
        time.sleep(0.5)
        result = self.sensor.get_application_statistic_data(application_id=2)
        self.assertTrue(result['number_of_frames'] == 0)

    def test_get_reference_image(self):
        result = self.sensor.get_reference_image()
        self.assertIsInstance(result, np.ndarray)

    def test_measure(self):
        input_measure_line = {
            "geometry": "line",
            "pixel_positions": [
                {
                    "column": 980,
                    "row": 374
                },
                {
                    "column": 603,
                    "row": 455
                }
            ]
        }

        input_measure_rect = {
            "geometry": "rect",
            "pixel_positions": [
                {
                    "column": 376,
                    "row": 426
                },
                {
                    "column": 710,
                    "row": 651
                }
            ]
        }

        input_measure_circle = {
            "geometry": "circle",
            "pixel_positions": [
                {
                    "column": 647,
                    "row": 452
                },
                {
                    "column": 775,
                    "row": 533
                }
            ]
        }

        result = self.sensor.measure(input_parameter=input_measure_line)
        self.assertIsInstance(result, dict)
        self.assertTrue(result)
        result = self.sensor.measure(input_parameter=input_measure_rect)
        self.assertIsInstance(result, dict)
        self.assertTrue(result)
        result = self.sensor.measure(input_parameter=input_measure_circle)
        self.assertIsInstance(result, dict)
        self.assertTrue(result)

    def test_trigger(self):
        application_active = self.sensor.get_parameter(parameter_name="ActiveApplication")
        initial_application_stats = self.sensor.get_application_statistic_data(application_id=int(application_active))
        initial_number_of_frames = initial_application_stats['number_of_frames']
        self.sensor.trigger()
        time.sleep(1)
        application_stats = self.sensor.get_application_statistic_data(application_id=int(application_active))
        number_of_frames = application_stats['number_of_frames']
        self.assertEqual(number_of_frames, initial_number_of_frames + 1)

    def test_doPing(self):
        result = self.sensor.doPing()
        self.assertEqual(result, "up")

    def test_export_application(self):
        tmp = "./DELETE_THIS.o2d5xxapp"
        # Check if file already exists
        self.assertFalse(os.path.exists(tmp))
        self.sensor.export_application(application_file=tmp, application_id=1)
        self.assertTrue(os.path.exists(tmp))
        os.remove(tmp)
        self.assertFalse(os.path.exists(tmp))

    def test_import_application(self):
        tmp = self.get_import_setup_for_sensor_pin_layout()['app_import_file']
        app_index = self.sensor.import_application(application=tmp)
        app_idx = [x["Index"] for x in self.sensor.get_application_list()]
        self.assertTrue(app_index in app_idx)
        self.sensor.delete_application(application_id=app_index)

    def test_delete_application(self):
        tmp = self.get_import_setup_for_sensor_pin_layout()['app_import_file']
        app_idx_list = []
        for i in range(2):
            app_index = self.sensor.import_application(application=tmp)
            app_idx_list.append(app_index)
        for x in app_idx_list:
            self.sensor.delete_application(application_id=x)
        app_idx = [x["Index"] for x in self.sensor.get_application_list()]
        for x in app_idx_list:
            self.assertFalse(x in app_idx)

    def test_move_applications(self):
        tmp = self.get_import_setup_for_sensor_pin_layout()['app_import_file']
        app_index = self.sensor.import_application(application=tmp)
        # Move app from app_index to position 30
        self.sensor.move_applications(id_from=app_index, id_into=30)
        app_idx = [x["Index"] for x in self.sensor.get_application_list()]
        self.assertTrue(app_index not in app_idx)
        self.assertTrue(30 in app_idx)
        # Move app from index 30 to 20
        self.sensor.move_applications(id_from=30, id_into=20)
        app_idx = [x["Index"] for x in self.sensor.get_application_list()]
        self.assertTrue(30 not in app_idx)
        self.assertTrue(20 in app_idx)
        self.sensor.delete_application(application_id=20)
        app_idx = [x["Index"] for x in self.sensor.get_application_list()]
        self.assertTrue(20 not in app_idx)

    def test_export_config(self):
        tmp = "./DELETE_THIS.o2d5xxapp"
        # Check if file already exists
        self.assertFalse(os.path.exists(tmp))
        self.sensor.export_application(application_file=tmp, application_id=1)
        self.assertTrue(os.path.exists(tmp))
        os.remove(tmp)
        self.assertFalse(os.path.exists(tmp))

    def test_import_config(self):
        tmp = self.get_import_setup_for_sensor_pin_layout()['config_file']
        self._sensor.import_config(tmp, global_settings=True, network_settings=False, applications=True)
        self._sensor.switch_application(1)
        app_idx = [x["Index"] for x in self.sensor.get_application_list()]
        self.assertTrue(len(app_idx) == 6)


if __name__ == '__main__':
    try:
        SENSOR_ADDRESS = sys.argv[1]
        LOGFILE = sys.argv[2]
    except IndexError:
        raise ValueError("Argument(s) are missing. Here is an example for running the unittests with logfile:\n"
                         "python test_rpc.py 192.168.0.69 True\n"
                         "Here is an example for running the unittests without an logfile:\n"
                         "python test_rpc.py 192.168.0.69")

    device_rpc = O2x5xxRPCDevice(address=SENSOR_ADDRESS)
    PCIC_TCP_PORT = device_rpc.get_parameter(parameter_name="PcicTcpPort")

    if LOGFILE:
        FIRMWARE_VERSION = device_rpc.get_sw_version()["IFM_Software"]
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        logfile = os.path.join('./logs', '{timestamp}_{firmware}_rpc_unittests_o2x5xx.log'
                               .format(timestamp=timestamp, firmware=FIRMWARE_VERSION))

        logfile = open(logfile, 'w')
        sys.stdout = logfile

        suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
        unittest.TextTestRunner(sys.stdout, verbosity=2).run(suite)

        logfile.close()

    else:
        suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
        unittest.TextTestRunner(verbosity=2).run(suite)
