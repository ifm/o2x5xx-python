from source.static.formats import error_codes, serialization_format
import matplotlib.image as mpimg
import binascii
import socket
import struct
import json
import re
import io


class Client(object):
    def __init__(self, address, port):
        # open raw socket
        self.pcicSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.pcicSocket.connect((address, port))
        self.recv_counter = 0
        self.debug = False
        self.debugFull = False

    def __del__(self):
        self.close()

    def recv(self, number_bytes):
        """
        Read the next bytes of the answer with a defined length.

        :param number_bytes: (int) length of bytes
        :return: the data as bytearray
        """
        data = bytearray()
        while len(data) < number_bytes:
            data_part = self.pcicSocket.recv(number_bytes - len(data))
            if len(data_part) == 0:
                raise RuntimeError("Connection to server closed")
            data = data + data_part
        self.recv_counter += number_bytes
        return data

    def close(self):
        """
        Close the socket session with the device.

        :return: None
        """
        self.pcicSocket.close()


class PCICV3Client(Client):
    def read_next_answer(self):
        """
        Read next available answer.

        :return: None
        """
        # read PCIC ticket + ticket length
        answer = self.recv(16)
        ticket = answer[0:4]
        answer_length = int(re.findall(r'\d+', str(answer))[1])
        answer = self.recv(answer_length)
        return ticket, answer[4:-2]

    def read_answer(self, ticket):
        """
        Read the next available answer with a defined ticket number.

        :param ticket: (string) ticket number
        :return: answer of the device as a string
        """
        recv_ticket = ""
        answer = ""
        while recv_ticket != ticket.encode():
            recv_ticket, answer = self.read_next_answer()
        return answer

    def send_command(self, cmd):
        """
        Send a command to the device with 1000 as default ticket number. The length and syntax
        of the command is calculated and generated automatically.

        :param cmd: (string) Command which you want to send to the device.
        :return: answer of the device as a string
        """
        cmd_length = len(cmd) + 6
        length_header = str.encode("1000L%09d\r\n" % cmd_length)
        self.pcicSocket.sendall(length_header)
        self.pcicSocket.sendall(b"1000")
        self.pcicSocket.sendall(cmd.encode())
        newline = "\r\n"
        self.pcicSocket.sendall(newline.encode())
        answer = self.read_answer("1000")
        return answer


class O2x5xxPCICDevice(PCICV3Client):
    def __init__(self, address, port):
        self.address = address
        self.port = port

        super(O2x5xxPCICDevice, self).__init__(address, port)

    def activate_application(self, application_number: [str, int]) -> str:
        """
        Activates the selected application.

        Parameters
        ----------
        application_number :
            2 digits for the application number.

            - '01': IO1

            - '02': IO2

        Returns
        -------
        result :
            sensor feedback code

            - \* Command was successful

            - ! Application not available
              | <application number> contains wrong value
              | External application switching activated
              | Device is in an invalid state for the command, e.g. configuration mode

            - ? Invalid command length
        """
        command = 'a' + str(application_number).zfill(2)
        result = self.send_command(command)
        result = result.decode()
        return result

    def occupancy_of_application_list(self):
        """
        Requests the occupancy of the application list.

        Returns
        -------
        result :
                - Syntax: <amount><t><number active application><t> ... <number><t><number>
                  e.g. 015    15  01  02	03	04	05	06	07	08	09	10	11	12	13	14	15

                - <amount> char string with 3 digits for the amount of applications
                saved on the device as decimal number

                - <t> tabulator (0x09)

                - <number active application> 2 digits for the active application

                - <number> 2 digits for the application number

                - ! Application not available
                  | <application number> contains wrong value
                  | External application switching activated
                  | Device is in an invalid state for the command, e.g. configuration mode

                - ? Invalid command length
        """
        result = self.send_command('A?')
        result = result.decode()
        return result

    def upload_process_interface_output_configuration(self, config):
        """
        Uploads a Process interface output configuration lasting this session.

        :param config: (dict) configuration data
        :return: - * Command was successful
                 - ! Error in configuration
                   | Wrong data length
                 - ? Invalid command length
        """
        config = json.dumps(config)
        cmd = 'c' + str(len(config)).zfill(9) + config
        result = self.send_command(cmd)
        result = result.decode()
        return result

    def retrieve_current_process_interface_configuration(self):
        """
        Retrieves the current Process interface configuration.

        :return: Syntax: <length><configuration> 
                 - <length> 9 digits as decimal value for the data length 
                 - <configuration> configuration data 
                 - ? Invalid command length
        """
        result = self.send_command('C?')
        result = result.decode()
        return result

    def request_current_error_state(self):
        """
        Requests the current error state.

        :return: Syntax: <code> 
                 - <code> Error code with 8 digits as a decimal value. It contains leading zeros. 
                 - ! Invalid state (e.g. configuration mode) 
                 - ? Invalid command length 
                 - $ Error code unknown
        """
        result = self.send_command('E?')
        result = result.decode()
        return result

    def request_current_error_state_decoded(self):
        """
        Requests the current error state and error message as a tuple.

        :return: Syntax: [<code>,<error_message>] 
                 - <code> Error code with 8 digits as a decimal value. It contains leading zeros. 
                 - <error_message> The corresponding error message to the error code. 
                 - ! Invalid state (e.g. configuration mode) 
                 - ? Invalid command length 
                 - $ Error code unknown
        """
        result = self.request_current_error_state()
        if result.isnumeric():
            error_message = error_codes[int(result)]
            if error_message:
                return [result, error_message]
            return '$'
        return result

    def gated_software_trigger_on_or_off(self, state):
        """
        Turn gated software trigger on or off.

        :param state: (int) 1 digit 
                      "0": turn gated software trigger off 
                      "1": turn gated software trigger on
        :return: - * Trigger could be executed 
                 - ! Invalid argument, invalid state, trigger already executed 
                 - ? Something else went wrong
        """
        result = self.send_command('g{state}'.format(state=state))
        result = result.decode()
        return result

    def request_device_information(self):
        """
        Requests device information.

        :return: Syntax: 
                 <vendor><t><article number><t><name><t><location><t>
                 <description><t><ip><subnet mask><t><gateway><t><MAC><t>
                 <DHCP><t><port number> 
                 - <vendor>            IFM ELECTRONIC 
                 - <t>                 Tabulator (0x09) 
                 - <article number>    e.g. O2D500 
                 - <name>              UTF8 Unicode string 
                 - <location>          UTF8 Unicode string 
                 - <description>       UTF8 Unicode string 
                 - <ip>                IP address of the device as ASCII character sting e.g. 192.168.0.69 
                 - <port number>       port number of the XML-RPC 
                 - <subnet mask>       subnet mask of the device as ASCIIe.g. 192.168.0.69 
                 - <gateway>           gateway of the device as ASCIIe.g 192.168.0.69 
                 - <MAC>               MAC address of the device as ASCIIe.g. AA:AA:AA:AA:AA:AA 
                 - <DHCP>              ASCII string "0" for off and "1" for on
        """
        result = self.send_command('G?')
        result = result.decode()
        return result

    def return_a_list_of_available_commands(self):
        """
        Returns a list of available commands.

        :return: - H?                        show this list 
                 - t                         execute Trigger 
                 - T?                        execute Trigger and wait for data 
                 - g<state>               turn gated software trigger on or off 
                 - o<io-id><io-state>     set IO state 
                 - O<io-id>?              get IO state 
                 - I<image-id>?           get last image of defined type 
                 - A?                        get application list 
                 - p<state>               activate / deactivate data output 
                 - a<application number>  set active application 
                 - E?                        get last Error 
                 - V?                        get current protocol version 
                 - v<version>             get protocol version 
                 - c<length of configuration file><configuration file>
                                             configure process data formatting 
                 - C?                        show current configuration 
                 - G?                        show device information 
                 - S?                        show statistics 
                 - L?                        retrieves the connection id 
                 - j<id><length><data> sets string data under specific ID 
                 - J<id>?                 reads string defined under specific ID 
                 - d<on-off state of view indicator><duration> turn the view indicators on
                                             (permanently or for a defined time) or off
        """
        result = self.send_command('H?')
        result = result.decode()
        return result

    def request_last_image_taken(self, image_id):
        """
        Request last image taken.

        :param image_id: (int) 2 digits for the image type 
                         1: all JPEG images 
                         2: all uncompressed images
        :return: Syntax: <length><image data> 
                 - <length> (int) char string with exactly 9 digits as decimal number for the image data size in bytes. 
                 - <image data> (bytearray) image data / result data. The data is encapsulated in an image chunk. 
                 - ! No image available
                   | Wrong ID 
                 - ? Invalid command length
        """
        if str(image_id).isnumeric():
            image_id = str(image_id).zfill(2)
        result = self.send_command('I{image_id}?'.format(image_id=image_id))
        return result

    def request_last_image_taken_deserialized(self, image_id=1, datatype='ndarray'):
        """
        Request last image taken deserialized in image header and image data. Image data can be requested as bytes
        or decoded as ndarray datatype.

        :param image_id: (int) 2 digits for the image type 
                         1: all JPEG images 
                         2: all uncompressed images
        :param datatype: (str) image output as hex or ndarray datatype 
                         bytes: image(s) as bytes datatype 
                         ndarray: image(s) as ndarray datatype
        :return: Syntax: [<header>,<image data>] 
                 - <header> (dict) header of the image deserialized as dict object 
                 - <image data> image data / result data. The data is encapsulated
                 in an image chunk if bytes as datatype is selected. 
                 - ! No image available
                   | Wrong ID 
                 - ? Invalid command length
        """
        results = {}
        result = self.request_last_image_taken(image_id)
        length = int(result[:9].decode())
        data = binascii.unhexlify(result[9:].hex())
        counter = 0

        while length:
            # get header information
            header = {}
            for key, value in serialization_format.items():
                hex_val = data[key: key + value[2]]
                dec_val = struct.unpack('<i', hex_val)[0]
                header[value[0]] = dec_val

            # append header
            results.setdefault(counter, []).append(header)
            # append image
            image_hex = data[header['HEADER_SIZE']:header['CHUNK_SIZE']]
            if datatype == 'ndarray':
                image = mpimg.imread(io.BytesIO(image_hex), format='jpg')
                results[counter].append(image)
            elif datatype == 'bytes':
                results[counter].append(image_hex)
            else:
                raise ValueError("{} is not a valid datatype. "
                                 "Use either 'bytes' or 'ndarray' as datatype".format(datatype))

            length -= header['CHUNK_SIZE']
            data = data[header['CHUNK_SIZE']:]
            counter += 1

        return results

    def overwrite_data_of_a_string(self, container_id, data):
        """
        Overwrites the string data of a specific (ID) string container used in the logic layer.

        :param container_id: (int) number from 00 to 09
        :param data: (string) string of a maximum size of 256 bytes
        :return: - * Command was successful 
                 - ! Invalid argument or invalid state (other than run mode)
                   | Not existing element with input-container-ID in logic layer 
                 - ? Syntax error
        """
        if str(container_id).isnumeric():
            container_id = str(container_id).zfill(2)
        cmd = 'j' + container_id + str(len(data)).zfill(9) + data
        result = self.send_command(cmd)
        result = result.decode()
        return result

    def read_string_from_defined_container(self, container_id):
        """
        Read the current defined string from the defined input string container.
        The string is represented as byte array.

        :param container_id: (int) number from 00 to 09
        :return: Syntax: <length><data> 
                 - <length>: 9 digits as decimal value for the data length 
                 - <data>: content of byte array 
                 - ! Invalid argument or invalid state (other than run mode)
                   | Not existing element with input-container-ID in logic layer 
                 - ? Syntax error
        """
        if str(container_id).isnumeric():
            container_id = str(container_id).zfill(2)
        result = self.send_command('J{container_id}?'.format(container_id=container_id))
        result = result.decode()
        return result

    def return_the_current_session_id(self):
        """
        Returns the current session ID.

        :return: 3 digits with leading "0"
        """
        result = self.send_command('L?')
        result = result.decode()
        return result

    def set_logic_state_of_an_id(self, io_id, state):
        """
        Sets the logic state of a specific ID.

        :param io_id: (int) 2 digits for digital output
                      "01": IO1
                      "02": IO2
        :param state: (int) 1 digit for the state 
                      "0": logic state low 
                      "1": logic state high
        :return: Syntax: <IO-ID><IO-state> 
                 - <IO-ID> 2 digits for digital output 
                 "01": IO1 
                 "02": IO2 
                 - <IO-state> 1 digit for the state 
                 "0": logic state low 
                 "1": logic state high 
                 - ! Invalid state (e.g. configuration mode)
                   | Wrong ID
                   | Element PCIC Output not connected to DIGITAL_OUT element in logic layer 
                 - ? Invalid command length
        """
        if str(io_id).isnumeric():
            io_id = str(io_id).zfill(2)
        result = self.send_command('o{io_id}{state}'.format(io_id=io_id, state=str(state)))
        result = result.decode()
        return result

    def set_logic_state_of_an_id2(self, io_id, state):
        """
        This is a reST style.

        :param io_id : (int)
        2 digits for digital output
            * "01": IO1
            * "02": IO2
        :param state : (str)
        this is a second param
            * "01": IO1
            * "02": IO2
        :returns: this is a description of what is returned
        :raises keyError: raises an exception
        """
        if str(io_id).isnumeric():
            io_id = str(io_id).zfill(2)
        result = self.send_command('o{io_id}{state}'.format(io_id=io_id, state=str(state)))
        result = result.decode()
        return result

    def foo(self, array, pad_width, mode):
        """
        Activates the selected application.

        Parameters
        ----------
        array : array_like of rank N
            The array to pad.
        pad_width : {sequence, array_like, int}
            Number of values padded to the edges of each axis.
            ((before_1, after_1), ... (before_N, after_N)) unique pad widths
            for each axis.
            ((before, after),) yields same before and after pad for each axis.
            (pad,) or int is a shortcut for before = after = pad width for all
            axes.
        mode : str or function, optional
            One of the following string values or a user supplied function.

            'constant' (default)
                Pads with a constant value.
            'edge'
                Pads with the edge values of array.
            'linear_ramp'
                Pads with the linear ramp between end_value and the
                array edge value.
            'maximum'
                Pads with the maximum value of all or part of the
                vector along each axis.
            'mean'
                Pads with the mean value of all or part of the
                vector along each axis.
            'median'
                Pads with the median value of all or part of the
                vector along each axis.
            'minimum'
                Pads with the minimum value of all or part of the
                vector along each axis.
            'reflect'
                Pads with the reflection of the vector mirrored on
                the first and last values of the vector along each
                axis.
            'symmetric'
                Pads with the reflection of the vector mirrored
                along the edge of the array.
            'wrap'
                Pads with the wrap of the vector along the axis.
                The first values are used to pad the end and the
                end values are used to pad the beginning.
            'empty'
                Pads with undefined values.

                .. versionadded:: 1.17

            <function>
                Padding function, see Notes.

        Returns
        -------
        pad : ndarray
            Padded array of rank equal to `array` with shape increased
            according to `pad_width`.
        """
        pad = 2
        return pad

    def request_state_of_an_id(self, io_id):
        """
        Requests the state of a specific ID.

        :param io_id: 2 digits for digital output 
                      "01": IO1 
                      "02": IO2
        :return: Syntax: <IO-ID><IO-state> 
                 - <IO-ID> 2 digits for digital output 
                 "01": IO1 
                 "02": IO2 
                 - <IO-state> 1 digit for the state 
                 "0": logic state low 
                 "1": logic state high 
                 - ! Invalid state (e.g. configuration mode)
                   | Wrong ID
                   | Element PCIC Output not connected to DIGITAL_OUT element in logic layer
                   (only valid for FW lower 1.30.40100) 
                 - ? Invalid command length
        """
        if str(io_id).isnumeric():
            io_id = str(io_id).zfill(2)
        result = self.send_command('O{io_id}?'.format(io_id=io_id))
        result = result.decode()
        return result

    def turn_process_interface_output_on_or_off(self, state):
        """
        Turns the Process interface output on or off. Be aware that this modification only
        affects the own session and is not considered to be a global parameter.

        :param state: (int) 1 digit 
                      0: deactivates all asynchronous output 
                      1: activates asynchronous result output 
                      2: activates asynchronous error output 
                      3: activates asynchronous error and data output 
                      4: activates asynchronous notifications 
                      5: activates asynchronous notifications and asynchronous result 
                      6: activates asynchronous notifications and asynchronous error output 
                      7: activates all outputs
        :return: - * Command was successful 
                 - ! <state>: contains wrong value 
                 - ? Invalid command length
        """
        result = self.send_command('p{state}'.format(state=str(state)))
        result = result.decode()
        return result

    def request_current_decoding_statistics(self):
        """
        Requests current decoding statistics.

        :return: Syntax: <number of results><t><number of positive decodings><t><number of false
                         decodings> 
                 - <t> tabulator (0x09) 
                 - <number of results> Images taken since application start. 10 digits decimal value with
                   leading "0" 
                 - <number of positive decodings> Number of decodings leading to a positive result. 10 digits
                   decimal value with leading "0" 
                 - <number of false decodings> Number of decodings leading to a negative result. 10 digits
                   decimal value with leading "0" 
                 - ! No application active
        """
        result = self.send_command('S?')
        result = result.decode()
        return result

    def execute_asynchronous_trigger(self):
        """
        Executes trigger. The result data is send asynchronously.
        Only compatible with configured trigger "Process Interface" on the sensor.

        :return: - * Trigger was executed, the device captures an image and evaluates the result. 
                 - ! Device is busy with an evaluation
                   | Device is in an invalid state for the command, e.g. configuration mode
                   | Device is set to a different trigger
                   | No active application
        """
        result = self.send_command('t')
        result = result.decode()
        return result

    def execute_synchronous_trigger(self):
        """
        Executes trigger. The result data is send synchronously.
        Only compatible with configured trigger "Process Interface" on the sensor.

        :return: - (str) decoded data output of process interface  
                 - ! Device is busy with an evaluation
                   | Device is in an invalid state for the command, e.g. configuration mode
                   | Device is set to a different trigger 
                   | No active application
        """
        result = self.send_command('T?')
        result = result.decode()
        return result

    def set_current_protocol_version(self, version=3):
        """
        Sets the current protocol version. The device configuration is not affected.

        :param version: 2 digits for the protocol version. Only protocol version V3 is supported.
        :return: - * Command was successful 
                 - ! Invalid version 
                 - ? Invalid command length
        """
        if str(version).isnumeric():
            version = str(version).zfill(2)
        result = self.send_command('v{version}'.format(version=version))
        result = result.decode()
        return result

    def request_current_protocol_version(self):
        """
        Requests current protocol version.

        :return: Syntax: <current version><empty><min version><empty><max version> 
                 - <current version> 2 digits for the currently set version 
                 - <empty> space sign 0x20 
                 - <min/max version> 2 digits for the available min and max version that can be set
        """
        result = self.send_command('V?')
        result = result.decode()
        return result

    def turn_state_of_view_indicator_on_or_off(self, state, duration=000):
        """
        Turn the view indicators on (permanently or for a defined time) or off.

        Syntax: d<on-off state of view indicator><duration>

        :param state: (int) duration time in seconds 
                      0: turn the view indicators off 
                      1: turn the view indicators on
        :param duration: (int) duration time in seconds (parameter has no impact if you turn indicators off)
        :return: - * Command was successful 
                 - ! Invalid state (e.g. configuration mode)
                   | Wrong state
                   | Wrong duration 
                 - ? Invalid command length
        """
        if str(duration).isnumeric():
            duration = str(duration).zfill(3)
        result = self.send_command('d{state}{duration}'.format(state=state, duration=duration))
        result = result.decode()
        return result

    def execute_currently_configured_button_functionality(self):
        """
        Execute the currently configured button functionality.

        :return: - * Button functionality was executed without an error. 
                 - ! no button function configured
                   | button function already running
                   | button function caused an error
                   | device is in an invalid state for this command, e.g. configuration mode
        """
        result = self.send_command('b')
        result = result.decode()
        return result
