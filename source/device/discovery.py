import socket
import struct
import platform
import sys
import os


class DiscoveryClient(object):

    def __init__(self, interface):
        self.interface = interface
        self.broadcast = bytearray([0x10, 0x20, 0xef, 0xcf, 0x0c, 0xf9, 0x00, 0x00])
        self.response_magic = 0x19111981
        # The port number for communication. It is recommended to use
        # the same port for incoming and outgoing communication this
        # help to pierce a hole through a firewall like the default firewall
        # under Windows 7. This technique is called
        # UDP hole punching (https://en.wikipedia.org/wiki/UDP_hole_punching)
        self.port = 3321
        self.udp_response = []
        self.result_dict = {"interface": self.interface, "devices": {}}
        self.my_os = platform.system()

    def response_to_dict(self, dict_id, response):

        response_dict = {"device_ip": socket.inet_ntoa(response[4:8]), "gateway_ip": socket.inet_ntoa(response[8:12]),
                         "subnet_mask": socket.inet_ntoa(response[12:16]),
                         "port_xml_rpc": struct.unpack('>H', response[16:18])[0],
                         "vendor_id": struct.unpack('>H', response[18:20])[0],
                         "device_id": struct.unpack('>H', response[20:22])[0],
                         "device_mac": ":".join(
                             "{:02x}".format(ord(v)) for v in struct.unpack("<%dc" % 6, response[32:38])),
                         "device_flags": struct.unpack('>H', response[38:40])[0],
                         "device_article_number": response[40:46].decode("utf-8"),
                         "device_name": response[104:].decode("utf-8").replace('\x00', '')}

        self.result_dict["devices"].update({dict_id: response_dict})

    def detect_devices(self):
        if self.my_os == "Linux":
            # Check for sudo privileges
            if os.getuid() != 0:
                print(sys.stderr,
                      "Check your privileges. Root permissions are required for platform ".format(self.my_os))
                sys.exit(-1)
        print('{ip}: Sending UDP broadcast ...'.format(ip=self.interface))
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, True)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)

        if self.my_os == "Linux":
            try:
                # here we use a hardcoded interface as an example
                # 25 is the magic number to use a specific interface 'SO_BINDTODEVICE'
                sock.setsockopt(socket.SOL_SOCKET, 25, self.interface)
                sock.bind(('', self.port))
            except IOError:
                print(sys.stderr, "Socket setup failed. Does the specified interface exist? Check using: ")
                print(sys.stderr, "ifconfig")
                sys.exit(1)
        elif self.my_os == "Windows":
            sock.bind((self.interface, self.port))
        else:
            raise RuntimeError("Operation system {} not supported yet!".format(self.my_os))
        # reducing socket timeout to 5 seconds
        sock.settimeout(5)
        sock.sendto(self.broadcast, ("<broadcast>", self.port))

        response, server = sock.recvfrom(8)  # we typically receive our own broadcast
        print("Receiving own broadcast msg: {msg} from: {server}".format(msg=response, server=server))

        # First collect all UDP responses from ifm devices
        while True:
            try:
                response, server = sock.recvfrom(360)  # receive the reply from the device
                if self.response_magic == struct.unpack('>I', response[0:4])[0]:
                    self.udp_response.append(response)
                    print("{inf}: IFM device ({name}) found with IP {ip}"
                          .format(inf=self.interface, name=response[40:46].decode("utf-8"),
                                  ip=socket.inet_ntoa(response[4:8])))
            except socket.timeout:
                sock.close()
                break

        sock.close()

        # Process the response data for each ifm device and write to result_dict
        for idx, res in enumerate(self.udp_response):
            self.response_to_dict(dict_id=idx, response=res)

        return self.result_dict
