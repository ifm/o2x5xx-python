try:
    from o2x5xx import O2x5xxRPCDevice, O2x5xxPCICDevice
except ModuleNotFoundError:
    from source.rpc.client import O2x5xxRPCDevice
    from source.pcic.client import O2x5xxPCICDevice
import sys

if __name__ == '__main__':
    if len(sys.argv) > 1:
        address = sys.argv[1]
    else:
        address = '192.168.0.69'

    with O2x5xxRPCDevice(address) as rpc, rpc.mainProxy.requestSession():
        with rpc.sessionProxy.setOperatingMode(mode=1):
            newApplicationIndex = rpc.edit.createApplication(deviceType="Camera")
            print("Created new application with index: " + str(newApplicationIndex))

            with rpc.editProxy.editApplication(app_index=newApplicationIndex):

                # Setup application name and description
                rpc.application.Name = "DIGITAL_OUT Elements Handling"
                rpc.application.Description = "This is an example of how to\n" \
                                              "overwriting the Logic Graph schema config and\n" \
                                              "fully control the DIGITAL_OUT elements (GPIO)"

                # Setup new Logic Graph schema
                pin_layout = int(rpc.getParameter("PinLayout"))
                if pin_layout in [0, 2]:  # 5 pins A coded or 5 pins L coded
                    schemaFilename = "./LogicGraph_Templates/O_commands_to_DIGITAL_OUTx_5PIN.o2xlgc"
                elif pin_layout == 3:  # 8 pins A coded
                    schemaFilename = "./LogicGraph_Templates/O_commands_to_DIGITAL_OUTx_8PIN.o2xlgc"
                else:
                    raise ValueError("Device with Pin Layout {} not supported!".format(pin_layout))
                logicGraphConfig = rpc.application.readLogicGraphSchemaFile(schemaFile=schemaFilename)
                rpc.application.LogicGraph = logicGraphConfig
                print("Default Logic Graph schema replaced with schema from file: {}".format(schemaFilename))

                # Setup trigger mode process interface
                rpc.application.TriggerMode = 2
                print("Trigger Mode {} set".format(rpc.application.TriggerMode))

                print("Saving application...")
                rpc.application.save()

    with O2x5xxPCICDevice(address, port=50010) as pcic:

        # Switch into above created application
        pcic.activate_application(application_number=newApplicationIndex)
        print("Application switched into {}".format(newApplicationIndex))

        # Modify state of DIGITAL_OUT1
        print("DIGITAL_OUT1 state: {}".format(pcic.request_state_of_an_id(io_id=1)))
        pcic.set_logic_state_of_an_id(io_id=1, state=1)
        print("DIGITAL_OUT1 state: {}".format(pcic.request_state_of_an_id(io_id=1)))
        pcic.set_logic_state_of_an_id(io_id=1, state=0)
        print("DIGITAL_OUT1 state: {}".format(pcic.request_state_of_an_id(io_id=1)))

        # Modify state of DIGITAL_OUT2
        print("DIGITAL_OUT2 state: {}".format(pcic.request_state_of_an_id(io_id=2)))
        pcic.set_logic_state_of_an_id(io_id=2, state=1)
        print("DIGITAL_OUT2 state: {}".format(pcic.request_state_of_an_id(io_id=2)))
        pcic.set_logic_state_of_an_id(io_id=2, state=0)
        print("DIGITAL_OUT1 state: {}".format(pcic.request_state_of_an_id(io_id=2)))

        print("Finished!")
