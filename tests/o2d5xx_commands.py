from o2x5xx.pcic.client import O2i5xxDevice
import sys

if __name__ == '__main__':
    if len(sys.argv) > 1:
        address = sys.argv[1]
    else:
        address = '192.168.0.69'

    # create device
    device = O2i5xxDevice(address, 50010)

    # # Activate application by number
    # device.activate_application(3)

    # # Get application list
    # application_list = device.occupancy_of_application_list()
    # print(application_list)

    # # Get pcic configuration as dict
    # pcic_configuration = device.retrieve_current_process_interface_configuration()
    # print(pcic_configuration)

    # # Upload new PCIC configuration
    # upload_config = {'elements': [{'id': 'start_string', 'type': 'string', 'value': 'star'},
    #                               {'id': 'delimiter', 'type': 'string', 'value': ';'},
    #                               {'id': 'ApplicationDecodingResult', 'type': 'int16'},
    #                               {'id': 'delimiter', 'type': 'string', 'value': ';'},
    #                               {'format': {'numericfill': True, 'width': 2}, 'id': 'ModelsSize', 'type': 'uint32'},
    #                               {'id': 'delimiter', 'type': 'string', 'value': ';'}, {'elements': [
    #         {'format': {'numericfill': True, 'width': 3}, 'id': 'ID', 'type': 'uint32'},
    #         {'id': 'delimiter', 'type': 'string', 'value': ';'},
    #         {'format': {'numericfill': True, 'width': 2}, 'id': 'type_numeric', 'type': 'uint32'},
    #         {'id': 'delimiter', 'type': 'string', 'value': ';'}, {'id': 'ModelDecodingResult', 'type': 'uint32'},
    #         {'id': 'delimiter', 'type': 'string', 'value': ';'},
    #         {'format': {'numericfill': True, 'width': 2}, 'id': 'GroupResultsSize', 'type': 'uint32'},
    #         {'id': 'delimiter', 'type': 'string', 'value': ';'}, {
    #             'elements': [{'format': {'numericfill': True, 'width': 2}, 'id': 'group_id', 'type': 'uint32'},
    #                          {'id': 'delimiter', 'type': 'string', 'value': ';'},
    #                          {'id': 'group_passed', 'type': 'uint8'},
    #                          {'id': 'delimiter', 'type': 'string', 'value': ';'},
    #                          {'id': 'number_of_matches', 'type': 'uint32'},
    #                          {'id': 'delimiter', 'type': 'string', 'value': ';'}, {
    #                              'elements': [{'id': 'match_id', 'type': 'int32'},
    #                                           {'id': 'delimiter', 'type': 'string', 'value': ';'}, {
    #                                               'format': {'numericfill': False, 'precision': 3, 'scale': 100,
    #                                                          'width': 3}, 'id': 'score', 'type': 'uint32'},
    #                                           {'id': 'delimiter', 'type': 'string', 'value': ';'}],
    #                              'id': 'matches_list_pass', 'type': 'records'},
    #                          {'id': 'object_list_passSize', 'type': 'uint32'},
    #                          {'id': 'delimiter', 'type': 'string', 'value': ';'}, {
    #                              'elements': [{'id': 'object_id', 'type': 'int32'},
    #                                           {'id': 'delimiter', 'type': 'string', 'value': ';'}, {
    #                                               'elements': [{'id': 'value', 'type': 'int32'},
    #                                                            {'id': 'delimiter', 'type': 'string', 'value': ';'}],
    #                                               'fixed_size': 1, 'id': 'object_area', 'type': 'records'}],
    #                              'id': 'object_list_pass', 'type': 'records'}], 'id': 'GroupResults',
    #             'type': 'records'}], 'id': 'Models', 'type': 'records'},
    #                               {'id': 'end_string', 'type': 'string', 'value': 'stop'}],
    #                  'format': {'dataencoding': 'ascii'}, 'layouter': 'flexible'}
    # result = o2x5xx_sensor.upload_pcic_output_configuration(config=upload_config)
    # print(result)

    # # Request current error state
    # print(o2x5xx_sensor.error_state)

    # # Request device information
    # print(o2x5xx_sensor.requests_device_information)

    # # Gated software trigger
    # print(o2x5xx_sensor.gated_software_trigger_on_or_off(1))
    # time.sleep(2)
    # print(o2x5xx_sensor.gated_software_trigger_on_or_off(0))

    # # Get a list of available commands
    # result = o2x5xx_sensor.return_a_list_of_available_commands()
    # print(result)

    # # Get last image taken as bytearray
    # o2d5xx_sensor.execute_asynchronous_trigger()
    # last_image = o2d5xx_sensor.request_last_image_taken(1)
    # result2 = o2d5xx_sensor.request_last_image_taken(2)

    # from PIL import Image
    # image_stream = o2d5xx_sensor.request_last_image_taken_decoded(1)
    # # Create image object
    # image = Image.open(image_stream)
    # # display image
    # image.show()
    # # print whether JPEG, PNG, etc.
    # print(image.format)
    # print('x')

    # # Overwrite data of a string
    # result = o2x5xx_sensor.overwrite_data_of_a_string(0, "Hello World!")
    # print(result)
    # # Read string from defined container
    # result = o2x5xx_sensor.read_string_from_defined_container(0)
    # print(result)
    # # Return current session ID
    # result = o2x5xx_sensor.return_the_current_session_id()
    # print(result)

    # Set IO state
    # TODO Test this with 8 pol sensor
    # result = o2x5xx_sensor.set_logic_state_of_a_id(1, 0)
    # print(result)
    # result = o2x5xx_sensor.set_logic_state_of_a_id(2, 0)
    # print(result)

    # # Request IO state
    # TODO Test this with 8 pol sensor
    # result = o2x5xx_sensor.request_state_of_a_id(1)
    # print(result)
    # result = o2x5xx_sensor.request_state_of_a_id(2)
    # print(result)

    # Set PCIC state
    # print(o2x5xx_sensor.turn_process_interface_output_on_or_off(0))  # TODO Not working
    # print(o2x5xx_sensor.turn_process_interface_output_on_or_off(1))  # TODO Not testable

    # # Request current decoding statistics
    # print(o2x5xx_sensor.request_current_decoding_statistics())

    # # Execute asynchronous trigger
    # o2x5xx_sensor.execute_asynchronous_trigger()

    # # Execute synchronous trigger
    # o2x5xx_sensor.execute_synchronous_trigger()

    # # Set protocol version
    # print(o2x5xx_sensor.set_current_protocol_version(2))
    # print(o2x5xx_sensor.set_current_protocol_version(3))

    # # Request current protocol version
    # print(o2x5xx_sensor.request_current_protocol_version())

    # device_address = "192.168.0.44"
    # o2i5xx_sensor = O2I5XXSensor(device_address, 50010)

    # # Turn on or of viewindicator
    # # TODO Test on O2I5xx sensor
    # print(o2i5xx_sensor.turn_state_of_viewindicator_on_or_off(100))
