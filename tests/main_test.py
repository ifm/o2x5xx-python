from o2x5xx.pcic.client import O2x5xxDevice
import time
import sys
from datetime import datetime


if __name__ == '__main__':
    if len(sys.argv) > 1:
        address = sys.argv[1]
    else:
        address = '192.168.0.69'

    # create device
    device = O2x5xxDevice(address, 50010)

    answer = device.return_the_current_session_id()
    print(answer)
    # # &lt;IO-ID>&lt;IO-state><br />
