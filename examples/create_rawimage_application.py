try:
    from o2x5xx import O2x5xxRPCDevice, O2x5xxDeviceV2
except ModuleNotFoundError:
    from source.rpc.client import O2x5xxRPCDevice
    from source.device.client import O2x5xxDeviceV2
import sys
import matplotlib.pyplot as plt
import matplotlib.image

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
                    device.application.Name = "Application Uncompressed Image"
                    print("Changed name of application: " + device.application.Name)
                    device.application.Description = "Application for retrieving an uncompressed image"
                    print("Changed description of application: " + device.application.Description)
                    device.application.TriggerMode = 2  # process interface trigger mode
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
                        device.imager.Name = "Uncompressed Image"
                        print("Changed name of image001: " + device.imager.Name)

                    # Switch to uncompressed images
                    device.application.UncompressedImages = True
                    print("Enabled output of uncompressed images")

                    device.application.save()
                    print("Saving parameter consistent to memory for application: " + device.application.Name)
        device.switchApplication(applicationIndex=newApplicationIndex)
        print("Application with new index {} now active".format(newApplicationIndex))

    # create device
    print("Create O2x5xx V2 device.")
    with O2x5xxDeviceV2(address) as device:
        # Save 10 uncompressed images
        for i in range(10):
            print("Executing trigger.")
            # device.pcic.execute_asynchronous_trigger()
            trigger_result = device.pcic.execute_asynchronous_trigger()
            if trigger_result != '*':
                print(trigger_result)
                sys.exit("Trigger failed!")
            else:
                _ = device.pcic.read_next_answer()

            print("Requesting last image...")
            result = device.pcic.request_last_image_taken_deserialized(image_id=2, datatype="ndarray")
            if result == "!":
                print(result)
                sys.exit("Request for last image failed!")
            image_uncompressed = result[0][1]

            # Uncomment if you want to see the image
            # plt.imshow(image_uncompressed, cmap='gray')
            # plt.show()
            # matplotlib.image.imsave(fname='image_uncompressed_{}.png'.format(str(i)),
            #                         arr=image_uncompressed, cmap='gray')
