from ..pcic import O2x5xxPCICDevice
from ..rpc import O2x5xxRPCDevice


class O2x5xxDevice(O2x5xxPCICDevice):
    def __init__(self, address="192.168.0.69", port=50010):
        self.rpc = O2x5xxRPCDevice(address=address)

        super(O2x5xxPCICDevice, self).__init__(address, port)


class O2x5xxDeviceV2(object):
    def __init__(self, address="192.168.0.69", port=50010):
        self.pcic = O2x5xxPCICDevice(address=address, port=port)
        self.rpc = O2x5xxRPCDevice(address=address)
