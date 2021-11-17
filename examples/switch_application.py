from o2x5xx.pcic.client import O2x5xxDevice
import sys

if __name__ == '__main__':
    if len(sys.argv) > 2:
        address = sys.argv[1]
        app_number = sys.argv[2]
    else:
        address = '192.168.0.69'
        app_number = 0

    # create device
    device = O2x5xxDevice(address, 50010)

    # get application list
    application_list = device.occupancy_of_application_list

    if app_number in application_list:
        # activate application by number
        device.activate_application(1)
    else:
        raise ValueError('Application with number {i} does not exist.'.format(i=app_number))
