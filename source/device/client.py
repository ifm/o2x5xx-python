from ..pcic import (O2x5xxPCICDevice, SOCKET_TIMEOUT)
from ..rpc import O2x5xxRPCDevice


class O2x5xxDevice(O2x5xxPCICDevice):
    def __init__(self, address="192.168.0.69", port=50010, autoconnect=True, timeout=SOCKET_TIMEOUT):
        self._address = address
        self._port = port
        self._autoconnect = autoconnect
        self._rpc = None
        if autoconnect:
            self._rpc = O2x5xxRPCDevice(address=self._address)
        super(O2x5xxPCICDevice, self).__init__(address, port, autoconnect, timeout)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._rpc:
            self._rpc.mainProxy.close()
        self.close()
        self._rpc = None

    @property
    def rpc(self):
        return self._rpc


class O2x5xxDeviceV2(object):
    def __init__(self, address="192.168.0.69", port=50010, autoconnect=True, timeout=SOCKET_TIMEOUT):
        self._address = address
        self._port = port
        self._timeout = timeout
        self._autoconnect = autoconnect
        self._pcic = None
        self._rpc = None

    def __enter__(self):
        self._pcic = O2x5xxPCICDevice(address=self._address, port=self._port, autoconnect=self._autoconnect,
                                      timeout=self._timeout)
        self._rpc = O2x5xxRPCDevice(address=self._address)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._pcic.close()
        self._rpc.mainProxy.close()
        self._pcic = None
        self._rpc = None

    @property
    def rpc(self) -> O2x5xxRPCDevice:
        return self._rpc

    @property
    def pcic(self) -> O2x5xxPCICDevice:
        return self._pcic
