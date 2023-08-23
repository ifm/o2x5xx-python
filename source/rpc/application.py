import xmlrpc.client
import json
from .imager import Imager


class Application(object):
    """
    Application object
    """

    def __init__(self, applicationURL, sessionAPI, mainAPI):
        self.url = applicationURL
        self.sessionAPI = sessionAPI
        self.mainAPI = mainAPI
        self.rpc = xmlrpc.client.ServerProxy(self.url)
        self.imagerConfigURL = self.url + 'imager_{0:03d}/'

    def getAllParameters(self):
        """
        Returns all parameters of the object in one data-structure. For an overview which parameters can be request use
        the method get_all_parameters().

        :return: (dict) name contains parameter-name, value the stringified parameter-value
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

    def getAllParameterLimits(self) -> dict:
        """
        Returns limits and default values of all
            1. numeric parameters that have limits in terms of minimum and maximum value
            2. parameters whose values are limited by a set of values (enum-like)

        :return: (dict)
        """
        result = self.rpc.getAllParameterLimits()
        return result

    @property
    def Type(self) -> str:
        """
        Type of the device

        :return: (str)
        """
        result = self.getParameter("Type")
        return result

    @property
    def Name(self) -> str:
        """
        User defined name of the application.

        :return: (str)
        """
        result = self.getParameter("Name")
        return result

    @Name.setter
    def Name(self, value: str) -> None:
        """
        User defined name of the application.

        :param value: (str) Max. 64 characters
        :return: None
        """
        max_chars = 64
        if value.__len__() > max_chars:
            raise ValueError("Max. {} characters".format(max_chars))
        self.rpc.setParameter("Name", value)
        self.waitForConfigurationDone()

    @property
    def Description(self) -> str:
        """
        User defined description of the application.

        :return: (str)
        """
        result = self.getParameter("Description")
        return result

    @Description.setter
    def Description(self, value: str) -> None:
        """
        User defined description of the application.

        :param value: (str) Max. 500 characters
        :return: None
        """
        max_chars = 500
        if value.__len__() > 500:
            raise ValueError("Max. {} characters".format(max_chars))
        self.rpc.setParameter("Description", value)
        self.waitForConfigurationDone()

    @property
    def TriggerMode(self) -> int:
        """
        Current set trigger mode for the application.

        :return: (int) 1 digit
                 1: free run (continuous mode)
                 2: process interface
                 3: positive edge
                 4: negative edge
                 5: positive and negative edge
                 6: gated HW
                 7: gated process interface
                 8: time controlled gated HW
        """
        result = int(self.getParameter("TriggerMode"))
        return result

    @TriggerMode.setter
    def TriggerMode(self, value: int) -> None:
        """
        Selects the trigger mode for the application.

        :param value: (int) 1 digit
                      1: free run (continuous mode)
                      2: process interface
                      3: positive edge
                      4: negative edge
                      5: positive and negative edge
                      6: gated HW
                      7: gated process interface
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
        "width" must be at least 640 (because of image-header/-footer) and a multiple of 16 (hw-JPEG-encoding)
        and "height" must be at least 128 (because of image-header/-footer) and a multiple of 16 (hw-JPEG-encoding).

        :param value: (dict) properties x, y, width, height
                      e.g.: {"x": 300, "y": 400, "width": 640, "height": 400}
        :return: None
        """
        valueErrorList = []

        def getValueErrorListNumber():
            return str(valueErrorList.__len__() + 1)

        # Checking if height is in valid image range
        if value["y"] + value["height"] > 960:
            valueErrorList.append("\n{idx}. Y coordinate {y} with a height {value} is out if a valid range of 960!"
                                  .format(idx=getValueErrorListNumber(), y=value["y"], value=value["height"]))
        # Checking if height is min. 128 pixel
        if value["height"] < 128:
            valueErrorList.append("\n{idx}. Height {value} must be at least 128!"
                                  .format(idx=getValueErrorListNumber(), value=value["height"]))
        # Check if height is multiple of 16
        if value["height"] % 16 != 0:
            height_remainder = value["height"] % 16
            height_lower = value["height"] - height_remainder
            height_upper = value["height"] + 16 - height_remainder
            valueErrorList.append("\n{idx}. Height {value} is not a multiple of 16! Did you mean {lower} or {upper}?"
                                  .format(idx=getValueErrorListNumber(), value=value["height"],
                                          lower=height_lower, upper=height_upper))
        # Checking if width is in valid image range
        if value["x"] + value["width"] > 1280:
            valueErrorList.append("\n{idx}. X coordinate {x} with a width {value} is out if a valid range of 1280!"
                                  .format(idx=getValueErrorListNumber(), x=value["x"], value=value["width"]))
        # Check if width is min. 640 pxl
        if value["width"] < 640:
            valueErrorList.append("\n{idx}. Width {value} must be at least 640!"
                                  .format(idx=getValueErrorListNumber(), value=value["width"]))
        # Check if width is multiple of 16
        if value["width"] % 16 != 0:
            width_remainder = value["width"] % 16
            width_lower = value["width"] - width_remainder
            width_upper = value["width"] + 16 - width_remainder
            valueErrorList.append("\n{idx}. Width {value} is not a multiple of 16! Did you mean {lower} or {upper}?"
                                  .format(idx=getValueErrorListNumber(), value=value["width"],
                                          lower=width_lower, upper=width_upper))
        if valueErrorList:
            raise ValueError("".join(valueErrorList))
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

    def editImage(self, imageIndex: int):
        """
        Requests an Imager object specified by the image index.
        
        :param imageIndex: (int) index of image from ImagerConfigList
        :return: Imager (object)
        """
        imageIDs = [int(x["Id"]) for x in self.getImagerConfigList()]
        if imageIndex not in imageIDs:
            raise ValueError("Image index {} not available. Choose one imageIndex from following"
                             "ImagerConfigList or create a new one with method createImagerConfig():\n{}"
                             .format(imageIndex, self.getImagerConfigList()))
        return Imager(self.imagerConfigURL.format(imageIndex), mainAPI=self.mainAPI,
                      sessionAPI=self.sessionAPI, applicationAPI=self.rpc)

    def __getattr__(self, name):
        # Forward otherwise undefined method calls to XMLRPC proxy
        return getattr(self.rpc, name)
