"""
Copyright (c) 2023 Michael Gann
Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:
    The above copyright notice and this permission notice shall be
    included in all copies or substantial portions of the Software.
    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
    MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
    IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
    CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
    TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
    SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import enum
import errno
import os
import shutil
import logging
import requests
import os.path
import base64
import threading
from threading import Timer
import sys
import json
import argparse
import time
from datetime import datetime
import xmlrpc.client


class DeviceMode(enum.Enum):
    PRODUCTIVE = "PRODUCTIVE-MODE"
    BOOTING = "BOOTING"
    RECOVERY = "RECOVERY-MODE"


class DevicesMeta(enum.Enum):
    O2D5xx = {"DeviceType": ["1:320", 0x140],
              "ApplicationExtension": ".o2d5xxapp",
              "ConfigExtension": ".o2d5xxcfg"}
    O2I5xx = {"DeviceType": ["1:256", 0x100],
              "ApplicationExtension": ".o2i5xxapp",
              "ConfigExtension": ".o2i5xxcfg"}

    @classmethod
    def getData(cls, key, value):
        for s in DevicesMeta:
            _data = s.value[key]
            if isinstance(_data, list):
                for v in _data:
                    if v == value:
                        return s
            else:
                if _data == value:
                    return s


class Session(object):

    def __init__(self, sessionURL, mainAPI, autoHeartbeat=True, autoHeartbeatInterval=10):
        self.url = sessionURL
        self.mainAPI = mainAPI
        self.defaultAutoHeartbeatInterval = autoHeartbeatInterval
        self.rpc = xmlrpc.client.ServerProxy(self.url)
        self.connected = True
        self.autoHeartbeatTimer = None
        if autoHeartbeat:
            self.rpc.heartbeat(autoHeartbeatInterval)
            self.autoHeartbeatInterval = autoHeartbeatInterval
            self.autoHeartbeatTimer = Timer(self.autoHeartbeatInterval - 1, self.doAutoHeartbeat)
            self.autoHeartbeatTimer.start()
        else:
            self.rpc.heartbeat(300)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def heartbeat(self, heartbeatInterval: int) -> int:
        result = self.rpc.heartbeat(heartbeatInterval)
        return result

    def doAutoHeartbeat(self) -> None:
        newHeartbeatInterval = self.rpc.heartbeat(self.autoHeartbeatInterval)
        self.autoHeartbeatInterval = newHeartbeatInterval
        # schedule event a little ahead of time
        self.autoHeartbeatTimer = Timer(self.autoHeartbeatInterval - 1, self.doAutoHeartbeat)
        self.autoHeartbeatTimer.start()

    def cancelSession(self) -> None:
        if self.autoHeartbeatTimer:
            self.autoHeartbeatTimer.cancel()
            self.autoHeartbeatTimer.join()
            self.autoHeartbeatTimer = None
        if self.connected:
            self.rpc.cancelSession()
            self.connected = False

    def cleanupExport(self) -> None:
        self.rpc.cleanupExport()

    def getImportProgress(self) -> float:
        try:
            result = self.rpc.getImportProgress()
            return result
        except xmlrpc.client.Fault as fault:
            if fault.faultCode == 101107:
                return 1.0

    def getExportProgress(self) -> float:
        try:
            result = self.rpc.getExportProgress()
            return result
        except xmlrpc.client.Fault as fault:
            if fault.faultCode == 101110:
                return 1.0
        finally:
            self.cleanupExport()

    def exportConfig(self) -> bytearray:
        # increase heartbeat interval which will prevent a closed session after the "long" export progress
        self.rpc.heartbeat(30)
        config = self.rpc.exportConfig()
        config_bytes = bytearray()
        config_bytes.extend(map(ord, str(config)))
        while self.getExportProgress() < 1.0:
            time.sleep(1)
        self.cleanupExport()
        self.mainAPI.waitForConfigurationDone()
        return config_bytes

    def importConfig(self, config: [str, bytearray], global_settings=True, network_settings=False,
                     applications=True) -> None:
        # This is required due to the long import progress which may take longer than 10 seconds (default)
        self.rpc.heartbeat(30)
        if global_settings:
            self.rpc.importConfig(config, 0x0001)
        if network_settings:
            self.rpc.importConfig(config, 0x0002)
        if applications:
            self.rpc.importConfig(config, 0x0010)
        while self.getImportProgress() < 1.0:
            time.sleep(1)
        self.mainAPI.waitForConfigurationDone()

    def writeConfigFile(self, configName: str, data: bytearray) -> str:
        device_type = self.mainAPI.getParameter(value="DeviceType")
        my_device = DevicesMeta.getData(key="DeviceType", value=device_type)
        meta_extension = my_device.value["ConfigExtension"]
        filename, input_extension = os.path.splitext(configName)
        if not input_extension == meta_extension:
            configName = filename + meta_extension
        with open(configName, "wb") as f:
            f.write(data)
        return configName

    @staticmethod
    def readConfigFile(configFile: str) -> str:
        if isinstance(configFile, str):
            if os.path.exists(os.path.dirname(configFile)):
                with open(configFile, "rb") as f:
                    encodedZip = base64.b64encode(f.read())
                    decoded = encodedZip.decode()
                    return decoded
            else:
                raise FileExistsError("File {} does not exist!".format(configFile))


class O2x5xxRPCDevice(object):

    def __init__(self, address="192.168.0.69", api_path="/api/rpc/v1/"):
        self.baseURL = "http://" + address + api_path
        self.mainURL = self.baseURL + "com.ifm.efector/"
        self.address = address
        self.rpc = xmlrpc.client.ServerProxy(self.mainURL)
        self.session = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def getAllParameters(self) -> dict:
        result = self.rpc.getAllParameters()
        return result

    def getParameter(self, value: str) -> str:
        try:
            result = self.rpc.getParameter(value)
            return result
        except xmlrpc.client.Fault as e:
            if e.faultCode == 101000:
                available_parameters = list(self.getAllParameters().keys())
                logging.info("Here is a list of available parameters:\n{}".format(available_parameters))
            raise e

    def requestSession(self, password="", sessionID="", heartbeatInterval=10) -> Session:
        sessionID = self.rpc.requestSession(password, sessionID)
        sessionURL = self.mainURL + 'session_' + sessionID + '/'
        # self.session = Session(sessionURL=sessionURL, autoHeartbeat=False, mainAPI=self)
        self.session = Session(sessionURL=sessionURL, autoHeartbeatInterval=heartbeatInterval, mainAPI=self)
        return self.session

    def waitForConfigurationDone(self):
        self.rpc.waitForConfigurationDone()

    def switchApplication(self, applicationIndex: int) -> None:
        self.rpc.switchApplication(applicationIndex)
        self.waitForConfigurationDone()

    def __getattr__(self, name):
        # Forward otherwise undefined method calls to XMLRPC proxy
        return getattr(self.rpc, name)


class FirmwareUpdater(object):

    def __init__(self, address='192.168.0.69', update_files=None):
        self.address = address
        self.update_files = update_files
        self.backup = None
        self.active_application = None
        self.cfg_name = None
        self.rpc_client = O2x5xxRPCDevice(address=self.address)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def upload_firmware(self, filename):
        payload = open(filename, 'rb').read()
        header = {'Content-Type': 'application/octet-stream', 'X_FILENAME': filename}
        upload_url = 'http://{}:8080/handle_post_request'.format(self.address)
        logging.info('{} : Uploading update file: {} to {}'.format(self.address, filename, upload_url))

        def post():
            requests.post(upload_url, headers=header, data=payload)

        upload_thread = threading.Thread(target=post)
        upload_thread.daemon = True
        upload_thread.start()

        finished = False

        while not finished:
            is_ok, res = self.get_update_status()
            if is_ok and res["Msg"] != "":
                logging.info("{} : {}".format(self.address, res["Msg"]))
            if not is_ok:
                raise requests.exceptions.HTTPError("{} Something went wrong during Uploading/Installation")
            if res["Error"] != "0":
                logging.info(json.dumps(res, indent=4))
                raise requests.exceptions.HTTPError("Error occurred during Installation")
            finished = res["Status"] == "3"
            time.sleep(0.5)
        logging.info("{} : Finished firmware update".format(self.address))
        return True

    def read_device_mode(self):
        # Check if device is already in recovery-mode
        try:
            recovery_url = 'http://{}:8080'.format(self.address)
            result_recovery = requests.get(recovery_url, timeout=1).status_code
            if result_recovery == requests.codes.ok:  # 200
                mode = DeviceMode.RECOVERY
                return mode
        except requests.exceptions.ConnectionError:
            pass

        # Check if device is already in productive-mode
        try:
            rpc_api_url = 'http://{}/api/rpc/v1/com.ifm.efector'.format(self.address)
            result_productive = requests.get(rpc_api_url, timeout=1).status_code
            if result_productive == requests.codes.ok:  # 200
                mode = DeviceMode.PRODUCTIVE
                return mode
        except requests.exceptions.ConnectionError:
            pass

        mode = DeviceMode.BOOTING
        return mode

    def boot_recovery_mode(self):
        if self.read_device_mode() != DeviceMode.RECOVERY:
            logging.info("{} : Booting into {} ...".format(self.address, DeviceMode.RECOVERY))
            requests.post("http://" + self.address + "/api/rpc/v1/com.ifm.efector?method=reboot&params=[1]")
        else:
            logging.info("{} : Already in {}".format(self.address, DeviceMode.RECOVERY))

    def boot_productive_mode(self):
        if self.read_device_mode() != DeviceMode.PRODUCTIVE:
            logging.info("{} : Booting into {} ...".format(self.address, DeviceMode.PRODUCTIVE))
            requests.post("http://" + self.address + ":8080/reboot_to_live")
        else:
            logging.info("{} : Already in {}".format(self.address, DeviceMode.PRODUCTIVE))

    def wait_for_recovery_mode_booted(self):
        device_mode_recovery = False
        while not device_mode_recovery:
            current_device_mode = self.read_device_mode()
            if current_device_mode == DeviceMode.RECOVERY:
                device_mode_recovery = True
                logging.info("{} : Current mode {} ... SUCCESS".format(self.address, str(current_device_mode)))
            else:
                wait_time = 5
                logging.info("{} : Current mode {} ... "
                             "NEXT CHECK IN {} SECONDS".format(self.address, str(current_device_mode), wait_time))
                time.sleep(wait_time)
                result = self.wait_for_recovery_mode_booted()
                return result
        return device_mode_recovery

    def wait_for_productive_mode_booted(self):
        device_mode_productive = False
        while not device_mode_productive:
            current_device_mode = self.read_device_mode()
            if current_device_mode == DeviceMode.PRODUCTIVE:
                device_mode_productive = True
                logging.info("{} : Current mode {} ... SUCCESS".format(self.address, str(current_device_mode)))
            else:
                wait_time = 5
                logging.info("{} : Current mode {} ... "
                             "NEXT CHECK IN {} SECONDS".format(self.address, str(current_device_mode), wait_time))
                time.sleep(wait_time)
                result = self.wait_for_productive_mode_booted()
                return result
        return device_mode_productive

    def get_update_status(self):
        update_status_url = 'http://{}:8080/getstatus.json'.format(self.address)
        try:
            update_status_response = requests.get(update_status_url, timeout=60)
        except requests.exceptions.ConnectionError as e:
            logging.info(e)
            logging.info(
                "{} : {} not reachable. Waiting 10 seconds and retrying ...".format(self.address, update_status_url))
            time.sleep(10)
            update_status_response = requests.get(update_status_url)
        if update_status_response.status_code == requests.codes.ok:
            return True, update_status_response.json()
        else:
            return False, {}

    def install_swu(self):
        # Booting to recovery-mode (this is necessary for the update process)
        self.boot_recovery_mode()
        # Waiting for booting into recovery-mode to be finished
        self.wait_for_recovery_mode_booted()

        for file in self.update_files:
            logging.info("{} : Uploading firmware {} ...".format(self.address, file))
            self.upload_firmware(os.path.expanduser(file))

        # Reboot to productive mode
        self.boot_productive_mode()
        # Wait till device is in productive mode
        self.wait_for_productive_mode_booted()

    def backup_device_config(self, backup_path):
        # Booting into recovery-mode (this is necessary for the update process)
        self.boot_productive_mode()
        # Waiting for booting into recovery-mode to be finished
        self.wait_for_productive_mode_booted()
        _session = self.rpc_client.requestSession(heartbeatInterval=30)
        logging.info("{} : Exporting device config ...".format(self.address))
        self.backup = _session.exportConfig()
        self.active_application = self.rpc_client.getParameter("ActiveApplication")
        _cfg_name = "{}/deviceConfig_{}".format(backup_path, self.address.replace(".", "_"))
        self.cfg_name = _session.writeConfigFile(configName=_cfg_name, data=self.backup)
        logging.info("{ip} : Exporting device config ... SUCCESS Path: {p}"
                     .format(ip=self.address, p=os.path.abspath(self.cfg_name)))
        _session.cancelSession()

    def import_device_config(self):
        logging.info("{} : Requesting session ...".format(self.address))
        _session = self.rpc_client.requestSession(heartbeatInterval=30)
        logging.info("{} : Requesting session ... SUCCESS".format(self.address))
        logging.info("{} : Importing device config ...".format(self.address))
        _session.importConfig(config=self.backup, global_settings=True, network_settings=False, applications=True)
        logging.info("{} : Importing device config ... SUCCESS".format(self.address))
        _session.cancelSession()
        if self.active_application != "0":
            self.rpc_client.switchApplication(self.active_application)


def trace_threads(_threads, start_datetime, thread_type):
    while True:
        alive_list = [t.is_alive() for t in _threads]
        if True not in alive_list:
            logging.info("None of the {} threads is alive any more ... SUCCESS".format(thread_type))
            logging.info("Total runtime for {} threads: {}".format(thread_type, datetime.now() - start_datetime))
            break
        else:
            wait_time = 30
            logging.info("Threads still alive: {}. Waiting {} secs.".format(str(_threads), wait_time))
            time.sleep(wait_time)


def threaded_backup_device_config(_updater, backup_path):
    _updater.backup_device_config(backup_path=backup_path)


def threaded_install_swu(_updater):
    _updater.install_swu()


def threaded_import_device_config(_updater):
    _updater.import_device_config()


def check_or_make_dir(path):
    if not os.path.exists(path):
        logging.info("Folder created : Path: {}".format(os.path.abspath(path)))
        os.makedirs(path)
    else:
        logging.info("Folder already exists. Path: {}".format(os.path.abspath(path)))


def is_path_creatable(path_name: str) -> bool:
    dir_name = os.path.dirname(path_name) or os.getcwd()
    return os.access(dir_name, os.W_OK)


def is_pathname_valid(path_name: str) -> bool:
    ERROR_INVALID_NAME = 123
    try:
        if not isinstance(path_name, str) or not path_name:
            return False
        _, path_name = os.path.splitdrive(path_name)
        root_dir_name = os.environ.get('HOMEDRIVE', 'C:') \
            if sys.platform == 'win32' else os.path.sep
        assert os.path.isdir(root_dir_name)
        root_dir_name = root_dir_name.rstrip(os.path.sep) + os.path.sep
        for pathname_part in path_name.split(os.path.sep):
            try:
                os.lstat(root_dir_name + pathname_part)
            except OSError as exc:
                if hasattr(exc, 'winerror'):
                    if exc.winerror == ERROR_INVALID_NAME:
                        return False
                elif exc.errno in {errno.ENAMETOOLONG, errno.ERANGE}:
                    return False
    except TypeError:
        return False
    else:
        return True


def is_path_exists_or_creatable(path_name: str) -> [str, bool]:
    try:
        if is_pathname_valid(path_name) and (os.path.exists(path_name) or is_path_creatable(path_name)):
            return path_name
    except OSError:
        return False


def validate_ifm_sensor(address):
    try:
        device_type_url = "http://{}/api/rpc/v1/com.ifm.efector".format(address)
        if requests.get(device_type_url, timeout=2).status_code == 200:
            device = O2x5xxRPCDevice(address=address)
            device_type = device.getParameter(value="DeviceType")
            my_device = DevicesMeta.getData(key="DeviceType", value=device_type)
            if my_device:
                logging.info("{} : Device is a valid ifm sensor.".format(address))
            else:
                raise TypeError("{} : Device is not a O2I5xx or O2D5xx.".format(address))
    except requests.exceptions.ConnectTimeout as e:
        _msg = "{} : Device is not a valid ifm sensor.".format(address)
        logging.info(_msg)
        raise e
    return address


def validate_swu_files(file):
    if not os.path.isfile(file):
        _msg = "File {} not found.".format(file)
        logging.info(_msg)
        raise FileNotFoundError(file)
    else:
        _extension = os.path.splitext(file)[1]  # file[-4:]
        if _extension.lower() != ".swu":
            _msg = "Invalid extension for file {}. Extension must be *.swu".format(file)
            logging.info(_msg)
            raise Exception(_msg)
        else:
            _msg = "SWU file {} is valid.".format(file)
            logging.info(_msg)
    return file


if __name__ == "__main__":
    start = datetime.now()

    p = argparse.ArgumentParser()
    p.add_argument("-i", "--input", nargs="+", default=[], type=validate_swu_files, required=True,
                   help="specify input SWU file(s)")
    p.add_argument("-H", "--host", nargs="+", default=["192.168.0.69"], type=validate_ifm_sensor, required=True,
                   help="specify host IPs")
    p.add_argument("-b", "--backup", type=is_path_exists_or_creatable, required=False,
                   help="path for config backup folder")
    p.add_argument("-l", "--log", type=is_path_exists_or_creatable, required=False,
                   help="path for log file folder")
    p.add_argument("-r", "--remove", action='store_true', required=False,
                   help="remove config backup folder after application finished")
    args = p.parse_args()

    if len(sys.argv) < 5:
        p.print_help()
        sys.exit(-1)

    # Instantiate the Firmware Updater for the sensor(s)
    firmware_updater = []
    for host in args.host:
        updater = FirmwareUpdater(address=host, update_files=args.input)
        firmware_updater.append(updater)

    # End program if no device is ready or reachable
    if not firmware_updater:
        msg = "No firmware updater detected. Check your device IPs. Stopping program here."
        logging.info(msg)
        raise RuntimeError(msg)

    # Logging
    logging.root.handlers = []
    handlers = [logging.StreamHandler(sys.stdout)]
    if args.log:
        check_or_make_dir(path=args.log)
        logfile = os.path.join(args.log, "{}_fw_updater_log".format(start.strftime("%Y_%m_%d_%H_%M_%S")))
        handlers.append(logging.FileHandler(logfile, mode="a"))

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=handlers
    )

    logging.info("Start of application ...")

    # BACKUP DEVICE CONFIG PROCESS ###
    if args.backup:
        backup_start_datetime = datetime.now()
        # Create the backup folder
        check_or_make_dir(path=args.backup)

        # Thread config backup process for each device
        for u in firmware_updater:
            logging.info("{} : Config backup thread started ...".format(u.address))
            thread = threading.Thread(target=threaded_backup_device_config, daemon=True,
                                      kwargs={"_updater": u, "backup_path": args.backup})
            thread.name = 'ifm_config_backup_IP_{}'.format(u.address)
            thread.start()

        backup_threads = [t for t in threading.enumerate() if "ifm_config_backup_IP_" in t.name]
        trace_threads(backup_threads, backup_start_datetime, thread_type="backup")

    # ## UPDATE PROCESS ###
    update_start_datetime = datetime.now()

    # Thread updater process for each device
    for u in firmware_updater:
        logging.info("{} : swu update started ...".format(u.address))
        thread = threading.Thread(target=threaded_install_swu, daemon=True, kwargs={"_updater": u})
        thread.name = 'ifm_FW_updater_IP_{}'.format(u.address)
        thread.start()

    updater_threads = [t for t in threading.enumerate() if "ifm_FW_updater_IP_" in t.name]
    trace_threads(updater_threads, update_start_datetime, thread_type="update")

    # Write backup device configs
    if args.backup:
        import_start_datetime = datetime.now()
        # Thread config import process for each device
        for u in firmware_updater:
            logging.info("{} : Config import thread started ...".format(u.address))
            thread = threading.Thread(target=threaded_import_device_config, daemon=True, kwargs={"_updater": u})
            thread.name = 'ifm_config_import_IP_{}'.format(u.address)
            thread.start()

        import_threads = [t for t in threading.enumerate() if "ifm_config_import_IP_" in t.name]
        trace_threads(import_threads, import_start_datetime, thread_type="import")

    # Remove the backup folder
    if args.remove:
        shutil.rmtree(args.backup)
        logging.info("Config backup folder {} removed".format(args.backup))

    logging.info("Total application runtime: {}".format(datetime.now() - start))
    logging.info("Thanks for using this application.")
