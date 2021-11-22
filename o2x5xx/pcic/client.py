from o2x5xx.static.formats import error_codes
import binascii
import socket
import struct
import json
import re


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
        Send a command to the device with 1000 as ticket number. The length and syntax
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


class O2x5xxDevice(PCICV3Client):
    def __init__(self, address, port):
        self.address = address
        self.port = port

        super(O2x5xxDevice, self).__init__(address, port)

    def activate_application(self, number):
        """
        Activates the selected application.

        :param number: (int) 2 digits for the application number as decimal value
        :return: - * Command was successful <br />
                 - ! Application not available
                   | &lt;application number> contains wrong value
                   | External application switching activated
                   | Device is in an invalid state for the command, e.g. configuration mode
                 - ? Invalid command length
        """
        command = 'a' + str(number).zfill(2)
        result = self.send_command(command)
        return result

    def occupancy_of_application_list(self):
        """
        Requests the occupancy of the application list.

        :return: Syntax: &lt;amount>&lt;t>&lt;number active application>&lt;t> ... &lt;number>&lt;t>&lt;number> <br />
                 e.g. 015    15  01  02	03	04	05	06	07	08	09	10	11	12	13	14	15 <br />
                 - &lt;amount> char string with 3 digits for the amount of applications
                   saved on the device as decimal number <br />
                 - &lt;t> tabulator (0x09) <br />
                 - &lt;number active application> 2 digits for the active application <br />
                 - &lt;number> 2 digits for the application number <br />
                 - ! Application not available
                   | &lt;application number> contains wrong value
                   | External application switching activated
                   | Device is in an invalid state for the command, e.g. configuration mode <br />
                 - ? Invalid command length
        """
        result = self.send_command('A?')
        result = result.decode()
        return result

    def upload_process_interface_output_configuration(self, config):
        """
        Uploads a Process interface output configuration lasting this session.

        :param config: (dict) configuration data
        :return: - * Command was successful <br />
                 - ! Error in configuration <br />
                   | Wrong data length <br />
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

        :return: Syntax: &lt;length>&lt;configuration> <br />
                 - &lt;length> 9 digits as decimal value for the data length <br />
                 - &lt;configuration> configuration data <br />
                 - ? Invalid command length
        """
        result = self.send_command('C?')
        result = result.decode()
        return result

    def request_current_error_state(self):
        """
        Requests the current error state.

        :return: Syntax: &lt;code> <br />
                 - &lt;code> Error code with 8 digits as a decimal value. It contains leading zeros. <br />
                 - ! Invalid state (e.g. configuration mode) <br />
                 - ? Invalid command length <br />
                 - $ Error code unknown
        """
        result = self.send_command('E?')
        result = result.decode()
        return result

    def request_current_error_state_decoded(self):
        """
        Requests the current error state and error message as a tuple.

        :return: Syntax: [&lt;code>,&lt;error_message>] <br />
                 - &lt;code> Error code with 8 digits as a decimal value. It contains leading zeros. <br />
                 - &lt;error_message> The corresponding error message to the error code. <br />
                 - ! Invalid state (e.g. configuration mode) <br />
                 - ? Invalid command length <br />
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

        :param state: (int) 1 digit <br />
                      "0": turn gated software trigger off <br />
                      "1": turn gated software trigger on
        :return: - * Trigger could be executed <br />
                 - ! Invalid argument, invalid state, trigger already executed <br />
                 - ? Something else went wrong
        """
        result = self.send_command('g{state}'.format(state=state))
        result = result.decode()
        return result

    def request_device_information(self):
        """
        Requests device information.

        :return: Syntax: <br />
                 &lt;vendor>&lt;t>&lt;article number>&lt;t>&lt;name>&lt;t>&lt;location>&lt;t>
                 &lt;description>&lt;t>&lt;ip>&lt;subnet mask>&lt;t>&lt;gateway>&lt;t>&lt;MAC>&lt;t>
                 &lt;DHCP>&lt;t>&lt;port number> <br />
                 - &lt;vendor>            IFM ELECTRONIC <br />
                 - &lt;t>                 Tabulator (0x09) <br />
                 - &lt;article number>    e.g. O2D500 <br />
                 - &lt;name>              UTF8 Unicode string <br />
                 - &lt;location>          UTF8 Unicode string <br />
                 - &lt;description>       UTF8 Unicode string <br />
                 - &lt;ip>                IP address of the device as ASCII character sting e.g. 192.168.0.69 <br />
                 - &lt;port number>       port number of the XML-RPC <br />
                 - &lt;subnet mask>       subnet mask of the device as ASCIIe.g. 192.168.0.69 <br />
                 - &lt;gateway>           gateway of the device as ASCIIe.g 192.168.0.69 <br />
                 - &lt;MAC>               MAC address of the device as ASCIIe.g. AA:AA:AA:AA:AA:AA <br />
                 - &lt;DHCP>              ASCII string "0" for off and "1" for on
        """
        result = self.send_command('G?')
        result = result.decode()
        return result

    def return_a_list_of_available_commands(self):
        """
        Returns a list of available commands.

        :return: - H?                        show this list <br />
                 - t                         execute Trigger <br />
                 - T?                        execute Trigger and wait for data <br />
                 - g&lt;state>               turn gated software trigger on or off <br />
                 - o&lt;io-id><io-state>     set IO state <br />
                 - O&lt;io-id>?              get IO state <br />
                 - I&lt;image-id>?           get last image of defined type <br />
                 - A?                        get application list <br />
                 - p&lt;state>               activate / deactivate data output <br />
                 - a&lt;application number>  set active application <br />
                 - E?                        get last Error <br />
                 - V?                        get current protocol version <br />
                 - v&lt;version>             get protocol version <br />
                 - c&lt;length of configuration file><configuration file>
                                             configure process data formatting <br />
                 - C?                        show current configuration <br />
                 - G?                        show device information <br />
                 - S?                        show statistics <br />
                 - L?                        retrieves the connection id <br />
                 - j&lt;id>&lt;length><data> sets string data under specific ID <br />
                 - J&lt;id>?                 reads string defined under specific ID <br />
                 - d&lt;on-off state of view indicator>&lt;duration> turn the view indicators on
                                             (permanently or for a defined time) or off
        """
        result = self.send_command('H?')
        result = result.decode()
        return result

    def request_last_image_taken(self, image_id):
        """
        Request last image taken.

        :param image_id: (int) 2 digits for the image type <br />
                         1: all JPEG images <br />
                         2: all uncompressed images
        :return: Syntax: &lt;length>&lt;image data> <br />
                 - &lt;length> (int) char string with exactly 9 digits as decimal number for the image data size in bytes. <br />
                 - &lt;image data> (bytearray) image data / result data. The data is encapsulated in an image chunk. <br />
                 - ! No image available
                   | Wrong ID <br />
                 - ? Invalid command length
        """
        if str(image_id).isnumeric():
            image_id = str(image_id).zfill(2)
        result = self.send_command('I{image_id}?'.format(image_id=image_id))
        return result

    def request_last_image_taken_deserialized(self, image_id=1):
        """
        Request last image taken deserialized in image header and image data.

        :param image_id: (int) 2 digits for the image type <br />
                         1: all JPEG images <br />
                         2: all uncompressed images
        :return: Syntax: [&lt;header>,&lt;image data>] <br />
                 - &lt;header> (dict) header of the image deserialized as dict object <br />
                 - &lt;image data> (bytearray) image data / result data. The data is encapsulated in an image chunk. <br />
                 - ! No image available
                   | Wrong ID <br />
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
            results[counter].append(image_hex)

            length -= header['CHUNK_SIZE']
            data = data[header['CHUNK_SIZE']:]
            counter += 1

        return results

    def overwrite_data_of_a_string(self, container_id, data):
        """
        Overwrites the string data of a specific (ID) string container used in the logic layer.

        :param container_id: (int) number from 00 to 09
        :param data: (string) string of a maximum size of 256 Bytes
        :return: - * Command was successful <br />
                 - ! Invalid argument or invalid state (other than run mode)
                   | Not existing string with input-container-ID <br />
                 - ? Syntax error
        """
        if str(container_id).isnumeric():
            container_id = str(container_id).zfill(2)
        cmd = 'j' + container_id + str(len(data)) + data
        result = self.send_command(cmd)
        result = result.decode()
        return result

    def read_string_from_defined_container(self, container_id):
        """
        Read the current defined string from the defined input string container.
        The string is represented as byte array.

        :param container_id: (int) number from 00 to 09
        :return: Syntax: &lt;length>&lt;data> <br />
                 - &lt;length>: 9 digits as decimal value for the data length <br />
                 - &lt;data>: content of byte array <br />
                 - ! Invalid argument or invalid state (other than run mode)
                   | Not existing string with input-container-ID <br />
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

        :param io_id: (int) 2 digits for digital output <br />
                      1: IO1 <br />
                      "02": IO2
        :param state: (int) 1 digit for the state <br />
                      "0": logic state low <br />
                      "1": logic state high
        :return: Syntax: &lt;IO-ID>&lt;IO-state> <br />
                 - &lt;IO-ID> 2 digits for digital output <br />
                 "01": IO1 <br />
                 "02": IO2 <br />
                 - &lt;IO-state> 1 digit for the state <br />
                 "0": logic state low <br />
                 "1": logic state high <br />
                 - ! Invalid state (e.g. configuration mode)
                   | Wrong ID
                   | Element PCIC Output not connected to DIGITAL_OUT element in logic layer <br />
                 - ? Invalid command length
        """
        if str(io_id).isnumeric():
            io_id = str(io_id).zfill(2)
        result = self.send_command('o{io_id}{state}'.format(io_id=io_id, state=str(state)))
        result = result.decode()
        return result

    def request_state_of_an_id(self, io_id):
        """
        Requests the state of a specific ID.

        :param io_id: 2 digits for digital output <br />
                      "01": IO1 <br />
                      "02": IO2
        :return: Syntax: &lt;IO-ID>&lt;IO-state> <br />
                 - &lt;IO-ID> 2 digits for digital output <br />
                 "01": IO1 <br />
                 "02": IO2 <br />
                 - &lt;IO-state> 1 digit for the state <br />
                 "0": logic state low <br />
                 "1": logic state high <br />
                 - ! Invalid state (e.g. configuration mode)
                   | Wrong ID
                   | Element PCIC Output not connected to DIGITAL_OUT element in logic layer <br />
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

        :param state: (int) 1 digit <br />
                      0: deactivates all asynchronous output <br />
                      1: activates asynchronous result output <br />
                      2: activates asynchronous error output <br />
                      3: activates asynchronous error and data output <br />
                      4: activates asynchronous notifications <br />
                      5: activates asynchronous notifications and asynchronous result <br />
                      6: activates asynchronous notifications and asynchronous error output <br />
                      7: activates all outputs
        :return: - * Command was successful <br />
                 - ! &lt;state>: contains wrong value <br />
                 - ? Invalid command length
        """
        result = self.send_command('p{state}'.format(state=state))
        result = result.decode()
        return result

    def request_current_decoding_statistics(self):
        """
        Requests current decoding statistics.

        :return: Syntax: &lt;number of results>&lt;t>&lt;number of positive decodings>&lt;t>&lt;number of false
                         decodings> <br />
                 - &lt;t> tabulator (0x09) <br />
                 - &lt;number of results> Images taken since application start. 10 digits decimal value with
                   leading "0" <br />
                 - &lt;number of positive decodings> Number of decodings leading to a positive result. 10 digits
                   decimal value with leading "0" <br />
                 - &lt;number of false decodings> Number of decodings leading to a negative result. 10 digits
                   decimal value with leading "0" <br />
                 - ! No application active
        """
        result = self.send_command('S?')
        result = result.decode()
        return result

    def execute_asynchronous_trigger(self):
        """
        Executes trigger. The result data is send asynchronously.

        :return: - * Trigger was executed, the device captures an image and evaluates the result. <br />
                 - ! Device is busy with an evaluation
                   | Device is in an invalid state for the command, e.g. configuration mode
                   | Device is set to a different trigger source
                   | No active application
        """
        result = self.send_command('t')
        result = result.decode()
        return result

    def execute_synchronous_trigger(self):
        """
        Executes trigger. The result data is send synchronously.

        :return: - * Trigger was executed, the device captures an image,
                     evaluates the result and sends the process data. <br />
                 - ! Device is busy with an evaluation
                   | Device is in an invalid state for the command, e.g. configuration mode
                   | Device is set to a different trigger source
                   | No active application
        """
        result = self.send_command('T?')
        result = result.decode()
        return result

    def set_current_protocol_version(self, version=3):
        """
        Sets the current protocol version. The device configuration is not affected.

        :param version: 2 digits for the protocol version. Only protocol version V3 is supported.
        :return: - * Command was successful <br />
                 - ! Invalid version <br />
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

        :return: Syntax: &lt;current version>&lt;empty>&lt;min version>&lt;empty>&lt;max version> <br />
                 - &lt;current version> 2 digits for the currently set version <br />
                 - &lt;empty> space sign 0x20 <br />
                 - &lt;min/max version> 2 digits for the available min and max version that can be set
        """
        result = self.send_command('V?')
        result = result.decode()
        return result

    def turn_state_of_view_indicator_on_or_off(self, state, duration=000):
        """
        Turn the view indicators on (permanently or for a defined time) or off.

        Syntax: d<on-off state of view indicator><duration>

        :param state: (int) duration time in seconds <br />
                      0: turn the view indicators off <br />
                      1: turn the view indicators on
        :param duration: (int) duration time in seconds (parameter has no impact if you turn indicators off)
        :return: - * Command was successful <br />
                 - ! Invalid state (e.g. configuration mode)
                   | Wrong state
                   | Wrong duration <br />
                 - ? Invalid command length
        """
        if str(duration).isnumeric():
            duration = str(duration).zfill(3)
        result = self.send_command('d{state}{duration}'.format(state=state, duration=duration))
        result = result.decode()
        return result
