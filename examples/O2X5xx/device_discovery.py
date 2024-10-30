try:
    from o2x5xx import DiscoveryClient
    from o2x5xx.device.utils import get_local_network_interfaces
except ModuleNotFoundError:
    from source.device.discovery import DiscoveryClient
    from source.device.utils import get_local_network_interfaces
except ImportError:
    from source.device.discovery import DiscoveryClient
    from source.device.utils import get_local_network_interfaces


if __name__ == '__main__':

    # detect local network adapters
    my_network_interfaces = get_local_network_interfaces()

    if my_network_interfaces:
        # iterate over all available network adapters and detect IFM devices
        interface_devices = {}
        for inf_id, my_inf in enumerate(my_network_interfaces):
            discovery_client = DiscoveryClient(interface=my_inf)
            devices = discovery_client.detect_devices()
            interface_devices[inf_id] = devices

        print(interface_devices)
    else:
        raise EnvironmentError("No network interfaces found. Please check your network adapter.")
