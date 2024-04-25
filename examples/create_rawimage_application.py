try:
    from o2x5xx import O2x5xxRPCDevice
except ModuleNotFoundError:
    from source.rpc.client import O2x5xxRPCDevice
import sys

if __name__ == '__main__':
    if len(sys.argv) > 1:
        address = sys.argv[1]
    else:
        address = '192.168.0.69'

    # create device
    print("Create RPC device, request session and setup edit mode.")
    with O2x5xxRPCDevice(address) as device:

        with device.mainProxy.requestSession():
            with device.sessionProxy.setOperatingMode(mode=1):
                print("Operation Mode {} set".format(device.getParameter(value="OperatingMode")))
                newApplicationIndex = device.edit.createApplication("Camera")
                print("Created new application with index: " + str(newApplicationIndex))

                with device.editProxy.editApplication(app_index=newApplicationIndex):
                    print("Starting editing application with index: " + str(newApplicationIndex))
                    device.application.Name = "My new application"
                    print("Changed name of application: " + device.application.Name)
                    device.application.Description = "My new description"
                    print("Changed description of application: " + device.application.Description)
                    device.application.TriggerMode = 2  # continuous trigger mode
                    print("Trigger Mode {} set".format(device.application.TriggerMode))

                    # Setup of image001
                    with device.applicationProxy.editImager(imager_index=1):
                        print("Start calculating auto exposure time...")
                        device.imager.startCalculateExposureTime()
                        print("End of calculating exposure time with recommended value: " + str(
                            device.imager.ExposureTime))
                        print("Start calculating autofocus...")
                        device.imager.startCalculateAutofocus()
                        print("End of calculating autofocus with recommended value(s): " + str(
                            device.imager.getAutofocusDistances()))
                        device.imager.Name = "My new image001"
                        print("Changed name of image001: " + device.imager.Name)

                    # Switch to uncompressed images
                    device.application.UncompressedImages = True
                    print("Enabled output of uncompressed images")

                    device.application.save()
                    print("Saving parameter consistent to memory for application: " + device.application.Name)
        device.switchApplication(applicationIndex=newApplicationIndex)
        print("Application with new index {} now active".format(newApplicationIndex))
