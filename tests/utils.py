import os


def getImportSetupByPinLayout(rpc):
    pin_layout = int(rpc.getParameter("PinLayout"))
    if os.path.exists(os.path.join(os.getcwd(), "deviceConfig")):
        config_file_path = os.path.join(os.getcwd(), "deviceConfig")
        app_import_file_path = os.path.join(os.getcwd(), "deviceConfig", "UnittestApplicationImport.o2d5xxapp")
    else:
        config_file_path = os.path.join(os.getcwd(), "tests", "deviceConfig")
        app_import_file_path = os.path.join(os.getcwd(), "tests", "deviceConfig", "UnittestApplicationImport.o2d5xxapp")
    if pin_layout == 3:
        result = {'config_file': os.path.join(config_file_path, "Unittest8PolDeviceConfig.o2d5xxcfg"),
                  'app_import_file': app_import_file_path}
    elif pin_layout == 0 or pin_layout == 2:
        result = {'config_file': os.path.join(config_file_path, "Unittest5PolDeviceConfig.o2d5xxcfg"),
                  'app_import_file': app_import_file_path}
    else:
        raise NotImplementedError(
            "Testcase for PIN layout {} not implemented yet!\nSee PIN layout overview here:\n"
            "0: M12 - 5 pins A Coded connector (compatible to O3D3xx camera, Trigger and 2Outs)\n"
            "1: reserved for O3D3xx 8pin (trigger, 3 OUTs, 2 INs ... analog OUT1)\n"
            "2: M12 - 5 pins L Coded connector\n"
            "3: M12 - 8 pins A Coded connector (different OUT-numbering then O3D3xx and with IN/OUT switching)\n"
            "4: reserved for CAN-5pin connector (like O3DPxx, O3M or O3R)")
    return result
