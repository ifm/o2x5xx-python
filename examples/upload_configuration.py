from o2x5xx.pcic.client import O2x5xxDevice
import sys

if __name__ == '__main__':
    if len(sys.argv) > 1:
        address = sys.argv[1]
    else:
        address = '192.168.0.69'

    # create device
    device = O2x5xxDevice(address, 50010)

    # Upload a new process interface configuration
    upload_config = {'elements': [{'id': 'start_string', 'type': 'string', 'value': 'star'},
                                  {'id': 'delimiter', 'type': 'string', 'value': ';'},
                                  {'id': 'ApplicationDecodingResult', 'type': 'int16'},
                                  {'id': 'delimiter', 'type': 'string', 'value': ';'},
                                  {'format': {'numericfill': True, 'width': 2}, 'id': 'ModelsSize', 'type': 'uint32'},
                                  {'id': 'delimiter', 'type': 'string', 'value': ';'}, {'elements': [
            {'format': {'numericfill': True, 'width': 3}, 'id': 'ID', 'type': 'uint32'},
            {'id': 'delimiter', 'type': 'string', 'value': ';'},
            {'format': {'numericfill': True, 'width': 2}, 'id': 'type_numeric', 'type': 'uint32'},
            {'id': 'delimiter', 'type': 'string', 'value': ';'}, {'id': 'ModelDecodingResult', 'type': 'uint32'},
            {'id': 'delimiter', 'type': 'string', 'value': ';'},
            {'format': {'numericfill': True, 'width': 2}, 'id': 'GroupResultsSize', 'type': 'uint32'},
            {'id': 'delimiter', 'type': 'string', 'value': ';'}, {
                'elements': [{'format': {'numericfill': True, 'width': 2}, 'id': 'group_id', 'type': 'uint32'},
                             {'id': 'delimiter', 'type': 'string', 'value': ';'},
                             {'id': 'group_passed', 'type': 'uint8'},
                             {'id': 'delimiter', 'type': 'string', 'value': ';'},
                             {'id': 'number_of_matches', 'type': 'uint32'},
                             {'id': 'delimiter', 'type': 'string', 'value': ';'}, {
                                 'elements': [{'id': 'match_id', 'type': 'int32'},
                                              {'id': 'delimiter', 'type': 'string', 'value': ';'}, {
                                                  'format': {'numericfill': False, 'precision': 3, 'scale': 100,
                                                             'width': 3}, 'id': 'score', 'type': 'uint32'},
                                              {'id': 'delimiter', 'type': 'string', 'value': ';'}],
                                 'id': 'matches_list_pass', 'type': 'records'},
                             {'id': 'object_list_passSize', 'type': 'uint32'},
                             {'id': 'delimiter', 'type': 'string', 'value': ';'}, {
                                 'elements': [{'id': 'object_id', 'type': 'int32'},
                                              {'id': 'delimiter', 'type': 'string', 'value': ';'}, {
                                                  'elements': [{'id': 'value', 'type': 'int32'},
                                                               {'id': 'delimiter', 'type': 'string', 'value': ';'}],
                                                  'fixed_size': 1, 'id': 'object_area', 'type': 'records'}],
                                 'id': 'object_list_pass', 'type': 'records'}], 'id': 'GroupResults',
                'type': 'records'}], 'id': 'Models', 'type': 'records'},
                                  {'id': 'end_string', 'type': 'string', 'value': 'stop'}],
                     'format': {'dataencoding': 'ascii'}, 'layouter': 'flexible'}

    result = device.upload_process_interface_output_configuration(config=upload_config)
    print(result)
