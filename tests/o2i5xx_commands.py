from o2x5xx.pcic.client import O2x5xxDevice
from PIL import Image
import sys

if __name__ == '__main__':
    if len(sys.argv) > 1:
        address = sys.argv[1]
    else:
        address = '192.168.0.69'

    # create device
    device = O2x5xxDevice(address, 50010)
    # device_o2d5xx = O2d5xxDevice('192.168.0.70', 50010)

    # # Activate application by number
    # device.activate_application(3)

    # # Get application list
    # application_list = device.occupancy_of_application_list()
    # print(application_list)

    # # Upload new PCIC configuration
    # upload_config = {
    #     "elements": [
    #         {
    #             "id": "start_string",
    #             "type": "string",
    #             "value": "star"
    #         },
    #         {
    #             "id": "delimiter",
    #             "type": "string",
    #             "value": ";"
    #         },
    #         {
    #             "id": "ApplicationDecodingResult",
    #             "type": "int16"
    #         },
    #         {
    #             "id": "delimiter",
    #             "type": "string",
    #             "value": ";"
    #         },
    #         {
    #             "elements": [
    #                 {
    #                     "elements": [
    #                         {
    #                             "elements": [
    #                                 {
    #                                     "id": "content",
    #                                     "type": "blob"
    #                                 },
    #                                 {
    #                                     "id": "delimiter",
    #                                     "type": "string",
    #                                     "value": ";"
    #                                 }
    #                             ],
    #                             "id": "codes",
    #                             "type": "records"
    #                         }
    #                     ],
    #                     "id": "GroupResults",
    #                     "type": "records"
    #                 }
    #             ],
    #             "id": "Models",
    #             "type": "records"
    #         },
    #         {
    #             "id": "end_string",
    #             "type": "string",
    #             "value": "stop"
    #         }
    #     ],
    #     "format": {
    #         "dataencoding": "ascii"
    #     },
    #     "layouter": "flexible"
    # }
    # result = device.upload_process_interface_output_configuration(config=upload_config)
    # print(result)

    # # Get pcic configuration as dict
    # pcic_configuration = device.retrieve_current_process_interface_configuration()
    # print(pcic_configuration)

    # # Request current error state
    # error_state = device.request_current_error_state()
    # print(error_state)
    #
    # # Request current error state decoded
    # error_state = device.request_current_error_state_decoded()
    # print(error_state)

    # # Gated software trigger
    # result_on = device.gated_software_trigger_on_or_off(1)
    # print(result_on)
    # time.sleep(2)
    # result_off = device.gated_software_trigger_on_or_off(0)
    # print(result_off)

    # # Request device information
    # device_information = device.request_device_information()
    # print(device_information)
    #
    # # Get a list of available commands
    # result = device.return_a_list_of_available_commands()
    # print(result)

    # # Get last image taken as bytearray
    # device.execute_asynchronous_trigger()
    # all_jpeg_images = device.request_last_image_taken(1)
    # print(all_jpeg_images)
    # all_uncompressed_images = device.request_last_image_taken(2)
    # print(all_uncompressed_images)

    # Request last image taken decoded
    image_stream = device.request_last_image_taken_decoded(1)
    # Create image object
    image = Image.open(image_stream)
    # display image
    image.show()
    # print whether JPEG, PNG, etc.
    print(image.format)

    # # Overwrite data of a string
    # result = device.overwrite_data_of_a_string(0, "Hello World!")
    # print(result)
    #
    # # Read string from defined container
    # result = device.read_string_from_defined_container(0)
    # print(result)
    #
    # # Return current session ID
    # result = device.return_the_current_session_id()
    # print(result)

    # # Set IO state
    # result = device.set_logic_state_of_a_id(1, 1)
    # print(result)
    # result = device.set_logic_state_of_a_id(2, 1)
    # print(result)
    #
    # # Request IO state
    # result = device.request_state_of_a_id(1)
    # print(result)
    # result = device.request_state_of_a_id(2)
    # print(result)

    # # Set PCIC state
    # result = device.turn_process_interface_output_on_or_off(0)
    # print(result)

    # # Request current decoding statistics
    # decoding_statistics = device.request_current_decoding_statistics()
    # print(decoding_statistics)

    # # Execute asynchronous trigger
    # result = device.execute_asynchronous_trigger()
    # print(result)
    #
    # # Execute synchronous trigger
    # result = device.execute_synchronous_trigger()
    # print(result)

    # # Set protocol version
    # result = device.set_current_protocol_version(2)
    # print(result)
    # result = device.set_current_protocol_version(3)
    # print(result)

    # # Request current protocol version
    # protocol_version = device.request_current_protocol_version()
    # print(protocol_version)

    # # Turn on or of view indicator
    # result = device.turn_state_of_view_indicator_on_or_off(1, 15)
    # print(result)
    # time.sleep(2)
    # result = device.turn_state_of_view_indicator_on_or_off(0)
    # print(result)
