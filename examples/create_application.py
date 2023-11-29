try:
    from o2x5xx import O2x5xxRPCDevice
except ModuleNotFoundError:
    from source.rpc.client import O2x5xxRPCDevice
import sys
from source.rpc.client import O2x5xxRPCDevice

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
                newApplicationIndex = device.edit.createApplication()
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
                        device.imager.FilterType = 1
                        print("Changed filter type: " + str(device.imager.FilterType))
                        device.imager.FilterStrength = 1
                        print("Changed filter strength: " + str(device.imager.FilterStrength))

                    # Setup of image002
                    newImagerIndex = device.application.createImagerConfig()
                    print("Created new imager (image00{}) for application.".format(newImagerIndex))
                    with device.applicationProxy.editImager(imager_index=newImagerIndex):
                        device.imager.Name = "My new image002"
                        print("Changed name of image002: " + device.imager.Name)
                        print("Start calculating auto exposure time...")
                        device.imager.startCalculateExposureTime()
                        device.imager.FilterType = 1
                        device.imager.FilterStrength = 5
                        device.imager.FilterInvert = True
                        imageQuality = device.imager.imageQualityCheck
                        imageQuality.enabled = True
                        print("image002: Quality check enabled: " + str(imageQuality.enabled))
                        imageQuality.sharpness_thresholdMinMax = {"min": 1000, "max": 10000}
                        imageQuality.meanBrightness_thresholdMinMax = {"min": 10, "max": 233}
                        imageQuality.underexposedArea_thresholdMinMax = {"min": 10, "max": 88}
                        imageQuality.overexposedArea_thresholdMinMax = {"min": 33, "max": 55}

                    # Setup of image003
                    newImagerIndex = device.application.createImagerConfig()
                    print("Created new imager (image00{}) for application.".format(newImagerIndex))
                    with device.applicationProxy.editImager(imager_index=newImagerIndex):
                        device.imager.Name = "My new image003"
                        print("Changed name of image003: " + device.imager.Name)
                        print("Start calculating auto exposure time...")
                        device.imager.startCalculateExposureTime()
                        device.imager.FilterType = 3
                        device.imager.FilterStrength = 1

                    # Setup of image004
                    newImagerIndex = device.application.createImagerConfig()
                    print("Created new imager (image00{}) for application.".format(newImagerIndex))
                    with device.applicationProxy.editImager(imager_index=newImagerIndex):
                        device.imager.Name = "My new image004"
                        print("Changed name of image004: " + device.imager.Name)
                        device.imager.AnalogGainFactor = 1
                        device.imager.ExposureTime = 15000
                        device.imager.FilterInvert = True

                    # Setup of image005
                    newImagerIndex = device.application.createImagerConfig()
                    print("Created new imager (image00{}) for application.".format(newImagerIndex))
                    with device.applicationProxy.editImager(imager_index=newImagerIndex):
                        device.imager.Name = "My new image005"
                        print("Changed name of image005: " + device.imager.Name)
                        device.imager.AnalogGainFactor = 2
                        device.imager.ExposureTime = 7500

                    device.application.save()
                    print("Saving parameter consistent to memory for application: " + device.application.Name)
        device.switchApplication(applicationIndex=newApplicationIndex)
        print("Application with new index {} now active".format(newApplicationIndex))
