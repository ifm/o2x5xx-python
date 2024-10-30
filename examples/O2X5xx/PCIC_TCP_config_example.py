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
                rpc.application.Name = "Logic Graph and PCIC TCP config overwrite example"
                rpc.application.Description = "This is a Hello World example\n" \
                                              "for overwriting the PCIC TCP/IP config and\n" \
                                              "the Logic Graph schema config"

                # Setup new Logic Graph schema
                schemaFilename = "./LogicGraph_Templates/logic_export_Hello_World.o2xlgc"
                logicGraphConfig = rpc.application.readLogicGraphSchemaFile(schemaFile=schemaFilename)
                rpc.application.LogicGraph = logicGraphConfig
                print("Default Logic Graph schema replaced with schema from file: {}".format(schemaFilename))

                # Setup new PCIC TCP/IP schema
                schemaFilename = "./PCIC_TCP_templates/TCP_IP_interface_Hello_World.o2xpcic"
                pcicConfig = rpc.application.readPcicTcpSchemaFile(schemaFile=schemaFilename)
                rpc.application.PcicTcpResultSchema = pcicConfig
                print("Default PCIC TCP/IP schema replaced with schema from file: {}".format(schemaFilename))

                # Setup trigger mode process interface
                rpc.application.TriggerMode = 2
                print("Trigger Mode {} set".format(rpc.application.TriggerMode))

                print("Saving application...")
                rpc.application.save()

    with O2x5xxPCICDevice(address, port=50010) as pcic:

        # Switch into above created application
        pcic.activate_application(application_number=newApplicationIndex)
        print("Application switched into {}".format(newApplicationIndex))

        # Execute trigger
        print("Executing trigger...")
        trigger_result = pcic.execute_asynchronous_trigger()

        # Read next answer if trigger was successful
        if trigger_result == "*":
            answer = pcic.read_next_answer()
            print(answer[1].decode())

        print("Finished!")
