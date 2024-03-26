import json
import os
import warnings
from .proxy import ImagerProxy


class Application(object):
    """
    Application object
    """

    def __init__(self, applicationProxy, device):
        self._applicationProxy = applicationProxy
        self._device = device

    def editImage(self, imager_index: int):
        """
        Requests an Imager object specified by the image index.

        :param imager_index: (int) index of image from ImagerConfigList
        :return: Imager (object)
        """
        imageIDs = [int(x["Id"]) for x in self.getImagerConfigList()]
        if imager_index not in imageIDs:
            raise ValueError("Image index {} not available. Choose one imageIndex from following"
                             "ImagerConfigList or create a new one with method createImagerConfig():\n{}"
                             .format(imager_index, self.getImagerConfigList()))

        _imagerURL = self._applicationProxy.baseURL + 'imager_{0:03d}/'.format(imager_index)
        setattr(self._device, "_imagerURL", _imagerURL)
        _imagerProxy = ImagerProxy(url=_imagerURL, device=self._device)
        setattr(self._device, "_imagerProxy", _imagerProxy)
        return self._device.imager

    def getAllParameters(self):
        """
        Returns all parameters of the object in one data-structure. For an overview which parameters can be request use
        the method get_all_parameters().

        :return: (dict) name contains parameter-name, value the stringified parameter-value
        """
        result = self._applicationProxy.getAllParameters()
        return result

    def getParameter(self, value):
        """
        Returns the current value of the parameter.

        :param value: (str) parameter name
        :return: (str)
        """
        result = self._applicationProxy.getParameter(value)
        return result

    def getAllParameterLimits(self) -> dict:
        """
        Returns limits and default values of all
            1. numeric parameters that have limits in terms of minimum and maximum value
            2. parameters whose values are limited by a set of values (enum-like)

        :return: (dict)
        """
        result = self._applicationProxy.getAllParameterLimits()
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
        self._applicationProxy.setParameter("Name", value)
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
        self._applicationProxy.setParameter("Description", value)
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
        self._applicationProxy.setParameter("TriggerMode", value)
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
        self._applicationProxy.setParameter("FrameRate", value)
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
        self._applicationProxy.setParameter("HWROI", json.dumps(value))
        self.waitForConfigurationDone()

    @property
    def Rotate180Degree(self) -> bool:
        """
        Get rotation of the image by 180° (mirror horizontal+vertical).

        :return: (bool) True / False
        """
        result = self._applicationProxy.getParameter("Rotate180Degree")
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
        self._applicationProxy.setParameter("Rotate180Degree", value)
        self.waitForConfigurationDone()

    @property
    def FocusDistance(self) -> float:
        """
        Represents current Focus position and allows to directly change to a specific position.

        :return: (float) current focus distance in meter
        """
        result = float(self._applicationProxy.getParameter("FocusDistance"))
        return result

    @FocusDistance.setter
    def FocusDistance(self, value: float) -> None:
        """
        Represents current Focus position and allows to directly change to a specific position.

        :param value: (float) focus distance in meter
        :return: None
        """
        limits = self.getAllParameterLimits()["FocusDistance"]
        if not float(limits["min"]) <= float(value) <= float(limits["max"]):
            raise ValueError("FocusDistance value not available. Available range: {}"
                             .format(self.getAllParameterLimits()["FocusDistance"]))
        self._applicationProxy.setParameter("FocusDistance", value)
        # TODO: Wird hier geblockt? Wird der Focus Distance direkt nach dem setzen angefahren?
        # Edit: Kein Error, jedoch sind die Bilder unscharf wenn direkt danach das Bild angefordert wird: Fokus wird während requestImage im PCIC noch angefahren!
        self.waitForConfigurationDone()

    @property
    def ImageEvaluationOrder(self) -> str:
        """
        A whitespace separated list of ImagerConfig ids,
        denoting which images and in which order they should be evaluated.

        :return: (str)
        """
        result = self._applicationProxy.getParameter("ImageEvaluationOrder")
        return result

    @ImageEvaluationOrder.setter
    def ImageEvaluationOrder(self, value: list) -> None:
        """
        A whitespace separated list of ImagerConfig ids,
        denoting which images and in which order they should be evaluated.

        :param value: (list) a whitespace separated list of ImagerConfig ids
        :return: None
        """
        self._applicationProxy.setParameter("ImageEvaluationOrder", value)
        self.waitForConfigurationDone()

    @property
    def PcicTcpResultSchema(self) -> str:
        """
        The PCIC TCP/IP Schema defines which result-data will be sent via TCP/IP.
        :return: (str) pcic tcp/ip schema config
        """
        return self._applicationProxy.getParameter("PcicTcpResultSchema")

    @PcicTcpResultSchema.setter
    def PcicTcpResultSchema(self, schema: str) -> None:
        """
        The PCIC TCP/IP Schema defines which result-data will be sent via TCP/IP.
        :param schema: (str) pcic tcp/ip schema config
        :return: None
        """
        self._applicationProxy.setParameter("PcicTcpResultSchema", schema)
        validation = self.validate()
        if validation:
            warnings.warn(str(validation), UserWarning)
            warnings.warn("PCIC TCP/IP data output may not work properly!")
        self.waitForConfigurationDone()

    @property
    def LogicGraph(self) -> str:
        """
        JSON string describing a flow-graph which allows to program the logic between model-results and output-pins.
        :return: (str) JSON string flow-graph of Logic Layer
        """
        return self._applicationProxy.getParameter("LogicGraph")

    @LogicGraph.setter
    def LogicGraph(self, schema: str) -> None:
        """
        JSON string describing a flow-graph which allows to program the logic between model-results and output-pins.
        :param schema: (str) JSON string flow-graph of Logic Layer
        :return: None
        """
        self._applicationProxy.setParameter("LogicGraph", schema)
        validation = self.validate()
        if validation:
            warnings.warn(str(validation), UserWarning)
            warnings.warn("Logic Graph process output may not work properly!")
        self.waitForConfigurationDone()

    def writeLogicGraphSchemaFile(self, configName: str, data: str) -> None:
        """
        Write a logic graph (Logic Layer) config file.

        :param configName: (str) schema file path as str
        :param data: (str) schema data as str
        :return: None
        """
        extension = self._device.deviceMeta.value["LogicGraphConfigExtension"]
        filename, file_extension = os.path.splitext(configName)
        if not file_extension == extension:
            configName = filename + extension
        with open(configName, "w") as f:
            f.write(data)

    def readLogicGraphSchemaFile(self, schemaFile: str) -> str:
        """
        Read a Logic Graph (Logic Layer) config file.

        :param schemaFile: (str) logic graph schema file path
        :return: (str) schema config data as a str
        """
        extension = self._device.deviceMeta.value["LogicGraphConfigExtension"]
        if not schemaFile.endswith(extension):
            raise ValueError("File {} does not fit required extension {}".format(schemaFile, extension))
        if isinstance(schemaFile, str):
            if os.path.exists(os.path.dirname(schemaFile)):
                with open(schemaFile, "r") as f:
                    schema = f.read()
                    return schema
            else:
                raise FileExistsError("File {} does not exist!".format(schemaFile))

    def writePcicTcpSchemaFile(self, configName: str, data: str) -> None:
        """
        Write a PCIC TCP/IP config file.

        :param configName: (str) schema file path as str
        :param data: (str) schema data as str
        :return: None
        """
        extension = self._device.deviceMeta.value["PCICConfigExtension"]
        filename, file_extension = os.path.splitext(configName)
        if not file_extension == extension:
            configName = filename + extension
        with open(configName, "w") as f:
            f.write(data)

    def readPcicTcpSchemaFile(self, schemaFile: str) -> str:
        """
        Read a PCIC TCP/IP config file.

        :param schemaFile: (str) pcic tcp schema file path
        :return: (str) schema config data as a str
        """
        extension = self._device.deviceMeta.value["PCICConfigExtension"]
        if not schemaFile.endswith(extension):
            raise ValueError("File {} does not fit required extension {}".format(schemaFile, extension))
        if isinstance(schemaFile, str):
            if os.path.exists(os.path.dirname(schemaFile)):
                with open(schemaFile, "r") as f:
                    schema = f.read()
                    return schema
            else:
                raise FileExistsError("File {} does not exist!".format(schemaFile))

    def save(self) -> None:
        """
        Stores current configuration in persistent memory.

        :return: None
        """
        self._applicationProxy.save()
        self.waitForConfigurationDone()

    def validate(self) -> list:
        """
        Validates the application, this means it checks if the application can be activated.

        :return: Array of fault-structs (Id: int, Text: string)
        """
        result = self._applicationProxy.validate()
        return result

    def getImagerConfigList(self) -> list:
        """
        Returns a list representing the imager-configurations defined in this application.

        :return: (list) Array of strings
        """
        result = self._applicationProxy.getImagerConfigList()
        return result

    def availableImagerConfigTypes(self) -> list:
        """
        List of types that could be used with createImagerConfig method.

        :return: (list) Array of strings
        """
        result = self._applicationProxy.availableImagerConfigTypes()
        return result

    def createImagerConfig(self, imagerType='normal', addToEval=True):
        """
        Create an additional image-capturing-/exposure-config.

        :param imagerType: (str) default value is 'normal'
        :param addToEval: (bool) default value is 'True'. If you select False, the image will
                                 not be activated for the image acquisition/evaluation run
        :return: (int) ID of new image-config
        """
        imagerIndex = self._applicationProxy.createImagerConfig(imagerType)
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
        imagerIndex = self._applicationProxy.copyImagerConfig(imagerIndex)
        self.waitForConfigurationDone()
        return imagerIndex

    def deleteImagerConfig(self, imagerIndex: int) -> None:
        """
        Remove an image-config from application This will only be possible,
        if no model is using this image.

        :param imagerIndex: (int) ID of image-config that should be removed
        :return: None
        """
        self._applicationProxy.deleteImagerConfig(imagerIndex)
        self.waitForConfigurationDone()

    def isConfigurationDone(self) -> bool:
        """
        After an application (or imager configuration or model) parameter has been changed,
        this method can be used to check when the new configuration has been applied within the imager process.

        :return: (bool) True or False
        """
        result = self._applicationProxy.isConfigurationDone()
        return result

    def waitForConfigurationDone(self):
        """
        After an application (or imager configuration or model) parameter has been changed,
        this method can be used to check when the new configuration has been applied within the imager process.
        This call blocks until configuration has been finished.

        :return: None
        """
        self._applicationProxy.waitForConfigurationDone()

    def __getattr__(self, name):
        """Pass given name to the actual xmlrpc.client.ServerProxy.

        Args:
            name (str): name of attribute
        Returns:
            Attribute of xmlrpc.client.ServerProxy
        """
        return self._editProxy.__getattr__(name)
