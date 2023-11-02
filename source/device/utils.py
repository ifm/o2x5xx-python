import platform
import os
import socket


def get_os() -> str:
    """
    Get the current operating system

    :return: (str) operating system
    """
    print("platform.system() = %s" % (platform.system()))
    return platform.system()


def get_local_network_interfaces() -> list:
    """
    Get all local network interfaces as a list

    :return: (list) local network interfaces
    """
    local_os = get_os()
    if local_os == "Linux":
        interfaces = os.listdir('/sys/class/net/')
        interfaces = [str.encode(inf) for inf in interfaces]
    elif local_os == "Windows":
        interfaces = socket.getaddrinfo(host=socket.gethostname(),
                                        port=None,
                                        family=socket.AF_INET)
        interfaces = [ip[-1][0] for ip in interfaces]
    else:
        raise EnvironmentError("IFM device discovery not implemented and tested yet for OS {}".format(local_os))

    print("Following interfaces found for OS {}:\n{}".format(local_os, interfaces))
    return interfaces
