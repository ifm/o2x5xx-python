from unittest import TestCase
from source import O2x5xxRPCDevice
from tests.utils import *
from .config import *
import warnings


class TestRPC_EditObject(TestCase):
    config_backup = None
    config_file = None
    app_import_file = None
    active_application_backup = None
    pin_layout = None

    @classmethod
    def setUpClass(cls):
        setUpRPC = O2x5xxRPCDevice(deviceAddress)
        setUpSession = setUpRPC.requestSession()
        cls.config_backup = setUpSession.exportConfig()
        cls.active_application_backup = setUpRPC.getParameter("ActiveApplication")
        cls.config_file = getImportSetupByPinLayout(rpc=setUpRPC)['config_file']
        cls.app_import_file = getImportSetupByPinLayout(rpc=setUpRPC)['app_import_file']
        _config_file_data = setUpSession.readConfigFile(configFile=cls.config_file)
        setUpSession.importConfig(_config_file_data, global_settings=True, network_settings=False, applications=True)
        setUpRPC.switchApplication(1)
        setUpSession.cancelSession()

    @classmethod
    def tearDownClass(cls):
        tearDownRPC = O2x5xxRPCDevice(deviceAddress)
        tearDownSession = tearDownRPC.requestSession()
        tearDownSession.importConfig(cls.config_backup, global_settings=True, network_settings=False, applications=True)
        if cls.active_application_backup != "0":
            tearDownRPC.switchApplication(cls.active_application_backup)
        tearDownSession.cancelSession()

    def setUp(self):
        warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed.*<ssl.SSLSocket.*>")
        warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed <socket.socket.*>")
        warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed running multiprocessing pool.*>")
        self.rpc = O2x5xxRPCDevice(deviceAddress)
        self.rpc.switchApplication(1)
        self.session = self.rpc.requestSession()
        self.edit = self.session.setOperatingMode(mode=1)
        ping = self.rpc.doPing()
        self.assertEqual(ping, "up")

    def tearDown(self):
        # cancelSession() will implicitly set operation mode = 0
        self.session.cancelSession()

    def test_editApplication(self):
        application = self.edit.editApplication(applicationIndex=1)
        self.assertTrue(application)
        self.assertTrue(self.edit.application)
        # only one Edit-Mode for application allowed
        with self.assertRaises(PermissionError):
            self.edit.editApplication(applicationIndex=2)
        self.edit.stopEditingApplication()

    def test_stopEditingApplication(self):
        _ = self.edit.editApplication(applicationIndex=1)
        self.edit.stopEditingApplication()
        self.assertFalse(self.edit._application)

    def test_createApplication(self):
        newAppIndex = self.edit.createApplication()
        app_idx = [x["Index"] for x in self.rpc.getApplicationList()]
        self.assertTrue(newAppIndex in app_idx)
        self.edit.deleteApplication(applicationIndex=newAppIndex)

    def test_copyApplication(self):
        newAppIndex = self.edit.copyApplication(applicationIndex=1)
        app_idx = [x["Index"] for x in self.rpc.getApplicationList()]
        self.assertTrue(newAppIndex in app_idx)
        self.edit.deleteApplication(applicationIndex=newAppIndex)

    def test_deleteApplication(self):
        app = self.session.readApplicationConfigFile(self.app_import_file)
        app_idx_list = []
        for i in range(2):
            app_index = self.session.importApplication(application=app)
            app_idx_list.append(app_index)
        for x in app_idx_list:
            self.edit.deleteApplication(applicationIndex=x)
        app_idx = [x["Index"] for x in self.rpc.getApplicationList()]
        for x in app_idx_list:
            self.assertFalse(x in app_idx)

    def test_changeNameAndDescription(self):
        app = self.session.readApplicationConfigFile(self.app_import_file)
        appIndex = self.session.importApplication(application=app)
        newName = "TestName"
        newDescription = "TestDescription"
        self.edit.changeNameAndDescription(applicationIndex=appIndex,
                                           name=newName,
                                           description=newDescription)
        newAppDetails = self.session.getApplicationDetails(applicationIndex=appIndex)
        self.assertEqual(newName, newAppDetails["Name"])
        self.assertEqual(newDescription, newAppDetails["Description"])
        self.edit.deleteApplication(applicationIndex=appIndex)
        app_idx = [x["Index"] for x in self.rpc.getApplicationList()]
        self.assertTrue(appIndex not in app_idx)

    def test_moveApplications(self):
        app = self.session.readApplicationConfigFile(self.app_import_file)
        appIndex = self.session.importApplication(application=app)
        # Move app from app_index to position 30
        self.edit.moveApplications(applicationIndexFrom=appIndex,
                                   applicationIndexTo=30)
        app_idx = [x["Index"] for x in self.rpc.getApplicationList()]
        self.assertTrue(appIndex not in app_idx)
        self.assertTrue(30 in app_idx)
        # Move app from index 30 to 20
        self.edit.moveApplications(applicationIndexFrom=30,
                                   applicationIndexTo=20)
        app_idx = [x["Index"] for x in self.rpc.getApplicationList()]
        self.assertTrue(30 not in app_idx)
        self.assertTrue(20 in app_idx)
        self.edit.deleteApplication(applicationIndex=20)
        app_idx = [x["Index"] for x in self.rpc.getApplicationList()]
        self.assertTrue(20 not in app_idx)
