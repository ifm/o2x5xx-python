import xmlrpc.client
import json
from .imager import ImagerConfig


class ApplicationConfig(object):
    def __init__(self, applicationURL, mainAPI):
        self.url = applicationURL
        self.mainAPI = mainAPI
        self.rpc = xmlrpc.client.ServerProxy(self.url)
        self.imagerConfigURL = self.url + 'imager_{0:03d}/'

    def editImage(self, imageIndex: int):
        imageIDs = [int(x["Id"]) for x in self.getImagerConfigList()]
        if imageIndex not in imageIDs:
            raise ValueError("Image index {} not available. Choose one imageIndex from following"
                             "ImagerConfigList or create a new one with method createImagerConfig():\n{}"
                             .format(imageIndex, self.getImagerConfigList()))
        return ImagerConfig(self.imagerConfigURL.format(imageIndex), mainAPI=self.mainAPI, applicationAPI=self.rpc)

    def getAllParameters(self):
        """
        Returns all parameters of the object in one data-structure.

        :return:
        """
        result = self.rpc.getAllParameters()
        return result

    def getParameter(self, value):
        """
        Returns the current value of the parameter.

        :param value: (str) parameter name
        :return: (str)
        """
        result = self.rpc.getParameter(value)
        return result

    def getAllParameterLimits(self):
        result = self.rpc.getAllParameterLimits()
        return result

    @property
    def Type(self) -> str:
        result = self.getParameter("Type")
        return result

    @property
    def Name(self) -> str:
        result = self.getParameter("Name")
        return result

    @Name.setter
    def Name(self, value: str) -> None:
        max_chars = 64
        if value.__len__() > max_chars:
            raise ValueError("Max. {} characters".format(max_chars))
        self.rpc.setParameter("Name", value)
        self.waitForConfigurationDone()

    @property
    def Description(self) -> str:
        result = self.getParameter("Description")
        return result

    @Description.setter
    def Description(self, value: str) -> None:
        max_chars = 500
        if value.__len__() > 500:
            raise ValueError("Max. {} characters".format(max_chars))
        self.rpc.setParameter("Description", value)
        self.waitForConfigurationDone()

    @property
    def TriggerMode(self) -> int:
        result = int(self.getParameter("TriggerMode"))
        return result

    @TriggerMode.setter
    def TriggerMode(self, value: int) -> None:
        """
        Selects the trigger mode for the application.

        :param value: (int) 1 digit <br />
                      1: free run (continuous mode) <br />
                      2: process interface <br />
                      3: positive edge <br />
                      4: negative edge  <br />
                      5: positive and negative edge <br />
                      6: gated HW <br />
                      7: gated process interface <br />
                      8: time controlled gated HW
        :return: None
        """
        limits = self.getAllParameterLimits()["TriggerMode"]
        if value not in range(int(limits["min"]), int(limits["max"]), 1):
            raise ValueError("RPC Trigger value not available. Available range: {}\n"
                             "For more help take a look on the docstring documentation.".format(limits))
        self.rpc.setParameter("TriggerMode", value)
        self.waitForConfigurationDone()

    @property
    def FrameRate(self) -> float:
        """
        Currently set frame rate (in frames per second). This effects only free-run and gated trigger modes.

        :return: (float) frame rate
        """
        result = float(self.getParameter("FrameRate"))
        return result

    @FrameRate.setter
    def FrameRate(self, value: float) -> None:
        """
        Set desired frame rate (in frames per second). This effects only free-run and gated trigger modes.

        :param value: (float) allowed range [0.0167, 80.0]
        :return: None
        """
        limits = self.getAllParameterLimits()["FrameRate"]
        if not float(limits["min"]) <= float(value) <= float(limits["max"]):
            raise ValueError("FrameRate value not available. Available range: {}"
                             .format(self.getAllParameterLimits()["FrameRate"]))
        self.rpc.setParameter("FrameRate", value)
        self.waitForConfigurationDone()

    @property
    def HWROI(self) -> dict:
        """
        Get the area of the imager which is used for capturing images.

        :return:
        """
        result = eval(self.getParameter("HWROI"))
        return result

    @HWROI.setter
    def HWROI(self, value: dict) -> None:
        """
        Defines the area of the imager which is used for capturing images.
        Must be a JSON with the properties x, y, width, height, representing a valid rect inside 1280 x 960.
        "width" must be at least 640 (because of image-header/-footer) and a multiple of 16 (hw-JPEG-encoding).

        :param value: (dict) properties x, y, width, height
        :return: None
        """
        self.rpc.setParameter("HWROI", json.dumps(value))
        self.waitForConfigurationDone()

    @property
    def Rotate180Degree(self) -> bool:
        """
        Get rotation of the image by 180° (mirror horizontal+vertical).

        :return: (bool) True / False
        """
        result = self.rpc.getParameter("Rotate180Degree")
        if result == "false":
            return False
        return True

    @Rotate180Degree.setter
    def Rotate180Degree(self, value: bool) -> None:
        """
        Allows to rotate the image by 180° (mirror horizontal+vertical).

        :param value: (bool) True / False
        :return: None
        """
        self.rpc.setParameter("Rotate180Degree", value)
        self.waitForConfigurationDone()

    @property
    def FocusDistance(self) -> float:
        result = float(self.rpc.getParameter("FocusDistance"))
        return result

    @FocusDistance.setter
    def FocusDistance(self, value: float) -> None:
        """
        Allows to rotate the image by 180° (mirror horizontal+vertical).

        :param value: (float) focus distance in meter
        :return: None
        """
        limits = self.getAllParameterLimits()["FocusDistance"]
        if not float(limits["min"]) <= float(value) <= float(limits["max"]):
            raise ValueError("FocusDistance value not available. Available range: {}"
                             .format(self.getAllParameterLimits()["FocusDistance"]))
        self.rpc.setParameter("FocusDistance", value)
        self.waitForConfigurationDone()

    @property
    def ImageEvaluationOrder(self) -> str:
        """
        A whitespace separated list of ImagerConfig ids,
        denoting which images and in which order they should be evaluated.

        :return: (str)
        """
        result = self.rpc.getParameter("ImageEvaluationOrder")
        return result

    @ImageEvaluationOrder.setter
    def ImageEvaluationOrder(self, value: list) -> None:
        """
        A whitespace separated list of ImagerConfig ids,
        denoting which images and in which order they should be evaluated.

        :param value: (list) a whitespace separated list of ImagerConfig ids
        :return: None
        """
        self.rpc.setParameter("ImageEvaluationOrder", value)
        self.waitForConfigurationDone()

    def save(self) -> None:
        """
        Stores current configuration in persistent memory.

        :return: None
        """
        self.rpc.save()
        self.waitForConfigurationDone()

    def validate(self) -> list:
        """
        Validates the application, this means it checks if the application can be activated.

        :return: Array of fault-structs (Id: int, Text: string)
        """
        result = self.rpc.validate()
        return result

    def getImagerConfigList(self) -> list:
        """
        Returns a list representing the imager-configurations defined in this application.

        :return: (list) Array of strings
        """
        result = self.rpc.getImagerConfigList()
        return result

    def availableImagerConfigTypes(self) -> list:
        """
        List of types that could be used with createImagerConfig method.

        :return: (list) Array of strings
        """
        result = self.rpc.availableImagerConfigTypes()
        return result

    def createImagerConfig(self, imagerType='normal', addToEval=True):
        """
        Create an additional image-capturing-/exposure-config.

        :param imagerType: (str) default value is 'normal'
        :param addToEval: (bool) default value is 'True'. If you select False, the image will
                                 not be activated for the image acquisition/evaluation run
        :return: (int) ID of new image-config
        """
        imagerIndex = self.rpc.createImagerConfig(imagerType)
        if addToEval:
            imageEvalOrder = self.ImageEvaluationOrder
            imageEvalOrder += "{} ".format(imagerIndex)
            self.ImageEvaluationOrder = imageEvalOrder
        self.waitForConfigurationDone()
        return imagerIndex

    def copyImagerConfig(self, imagerIndex: int) -> int:
        """
        Create an additional image-capturing-/exposure-config.

        :param imagerIndex: (int) ID of other Imager config
        :return: (int) ID of new image-config
        """
        imagerIndex = self.rpc.copyImagerConfig(imagerIndex)
        self.waitForConfigurationDone()
        return imagerIndex

    def deleteImagerConfig(self, imagerIndex: int) -> None:
        """
        Remove an image-config from application This will only be possible,
        if no model is using this image.

        :param imagerIndex: (int) ID of image-config that should be removed
        :return: None
        """
        self.rpc.deleteImagerConfig(imagerIndex)
        self.waitForConfigurationDone()

    def isConfigurationDone(self) -> bool:
        """
        After an application (or imager configuration or model) parameter has been changed,
        this method can be used to check when the new configuration has been applied within the imager process.

        :return: (bool) True or False
        """
        result = self.rpc.isConfigurationDone()
        return result

    def waitForConfigurationDone(self):
        """
        After an application (or imager configuration or model) parameter has been changed,
        this method can be used to check when the new configuration has been applied within the imager process.
        This call blocks until configuration has been finished.

        :return: None
        """
        self.rpc.waitForConfigurationDone()

