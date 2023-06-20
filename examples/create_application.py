from o2x5xx.rpc.client import O2x5xxRPCDevice
import sys
import time

if len(sys.argv) > 1:
    address = sys.argv[1]
else:
    address = '192.168.0.69'

# create device
device = O2x5xxRPCDevice(address)

print("Requesting new session...")
session = device.requestSession()
edit = session.setOperatingMode(mode=1)
print("Operation Mode 1 (Edit) set")
newApplicationIndex = edit.createApplication()
print("Created new application with index: " + str(newApplicationIndex))
application = edit.editApplication(applicationIndex=newApplicationIndex)
print("Starting editing application with index: " + str(newApplicationIndex))
application.Name = "My new application"
print("Changed name of application: My new application")
application.Description = "My new description"
print("Changed name of application: My new description")
application.TriggerMode = 2  # continuous trigger mode
print("Trigger Mode 2 (continuous mode) set")

# Setup of image001
image001 = application.editImage(imageIndex=1)
image001.startCalculateExposureTime()
image001.startCalculateAutofocus()
image001.Name = "My new image001"
image001.FilterType = 1
image001.FilterStrength = 1

# Setup of image002
print("Creating new imager (image002) for application.")
newImagerIndex = application.createImagerConfig()
image002 = application.editImage(imageIndex=newImagerIndex)
image002.Name = "My new image002"
image002.startCalculateExposureTime()
image002.startCalculateAutofocus()
image002.FilterType = 1
image002.FilterStrength = 5
image002.FilterInvert = True
imageQuality = image002.ImageQualityCheckConfig
imageQuality.enabled = True
print("Quality check enabled: " + str(imageQuality.enabled))
imageQuality.sharpness_thresholdMinMax = {"min": 1000, "max": 10000}
imageQuality.meanBrightness_thresholdMinMax = {"min": 10, "max": 233}
imageQuality.underexposedArea_thresholdMinMax = {"min": 10, "max": 88}
imageQuality.overexposedArea_thresholdMinMax = {"min": 33, "max": 55}

# Setup of image003
print("Creating new imager (image003) for application.")
newImagerIndex = application.createImagerConfig()
image003 = application.editImage(imageIndex=newImagerIndex)
image003.Name = "My new image003"
image003.startCalculateExposureTime()
image003.startCalculateAutofocus()
image003.FilterType = 3
image003.FilterStrength = 2

# Setup of image004
print("Creating new imager (image004) for application.")
newImagerIndex = application.createImagerConfig()
image004 = application.editImage(imageIndex=newImagerIndex)
image004.Name = "My new image004"
image004.startCalculateExposureTime()
image004.startCalculateAutofocus()
image004.AnalogGainFactor = 1
image004.ExposureTime = 15000
image004.FilterInvert = True

# Setup of image005
print("Creating new imager (image005) for application.")
newImagerIndex = application.createImagerConfig()
image005 = application.editImage(imageIndex=newImagerIndex)
image005.Name = "My new image005"
image005.startCalculateExposureTime()
image005.startCalculateAutofocus()
image005.AnalogGainFactor = 1
image005.ExposureTime = 15000

application.save()
session.setOperatingMode(mode=0)
session.cancelSession()
device.switchApplication(applicationIndex=newApplicationIndex)
