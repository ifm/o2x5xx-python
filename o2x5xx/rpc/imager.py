import time
import xmlrpc.client
from .imageQualityCheck import ImageQualityCheckConfig
import json


class ImagerConfig(object):
    def __init__(self, imageURL, mainAPI, applicationAPI):
        self.imageURL = imageURL
        self.applicationAPI = applicationAPI
        self.mainAPI = mainAPI
        self.rpc = xmlrpc.client.ServerProxy(self.imageURL)
        self._imageQualityCheckConfig = None

    def getAllParameters(self):
        result = self.rpc.getAllParameters()
        return result

    def getParameter(self, value):
        result = self.rpc.getParameter(value)
        return result

    def getAllParameterLimits(self):
        result = self.rpc.getAllParameterLimits()
        return result

    @property
    def ImageQualityCheckConfig(self):
        """
        # TODO

        :return:
        """
        self._imageQualityCheckConfig = ImageQualityCheckConfig(imageURL=self.imageURL,
                                                                imageRPC=self.rpc,
                                                                applicationAPI=self.applicationAPI)
        return self._imageQualityCheckConfig

    @property
    def Type(self) -> str:
        """
        The used exposure mode.

        :return: (str)
        """
        result = self.getParameter("Type")
        return result

    @property
    def Name(self) -> str:
        """
        User defined name of the imager config.

        :return: (str)
        """
        result = self.getParameter("Name")
        return result

    @Name.setter
    def Name(self, value: str) -> None:
        """
        User defined name of the imager config.

        :return: None
        """
        max_chars = 64
        if value.__len__() > max_chars:
            raise ValueError("Max. {} characters".format(max_chars))
        self.rpc.setParameter("Name", value)
        self.applicationAPI.waitForConfigurationDone()

    @property
    def Illumination(self) -> int:
        """
        Returns the kind of illumination used while capturing images.

        :return: (int) 1 digit <br />
                       0: no illumination active <br />
                       1: internal illumination shall be used <br />
                       2: external illumination shall be used <br />
                       3: internal and external illumination shall be used together
        """
        result = int(self.getParameter("Illumination"))
        return result

    @Illumination.setter
    def Illumination(self, value: int) -> None:
        """
        Defines which kind of illumination shall be used while capturing images.

        :param value: (int) 1 digit <br />
                            0: no illumination active <br />
                            1: internal illumination shall be used <br />
                            2: external illumination shall be used <br />
                            3: internal and external illumination shall be used together
        :return: None
        """
        limits = self.getAllParameterLimits()["Illumination"]
        if value not in range(int(limits["min"]), int(limits["max"]), 1):
            raise ValueError("Illumination value not available. Available range: {}"
                             .format(self.getAllParameterLimits()["Illumination"]))
        self.rpc.setParameter("Illumination", value)
        self.applicationAPI.waitForConfigurationDone()

    @property
    def IlluInternalSegments(self) -> dict:
        """
        Defines which segments of the internal illumination is used while capturing images.
        All directions are meant in view direction on top of the imager/device (not FOV!).

        :return: (dict) (dict) dict with LED segments enabled/disabled <br />
                          upper-left: (bool) enable/disable upper-left LED <br />
                          upper-Right: (bool) enable/disable upper-right LED <br />
                          lower-Left: (bool) enable/disable lower-left LED <br />
                          lower-Right: (bool) enable/disable lower-Right LED
        """
        result = self.getParameter("IlluInternalSegments")
        result = '{0:04b}'.format(int(result))
        return {"upper-left": bool(int(result[0])), "upper-right": bool(int(result[1])),
                "lower-left": bool(int(result[2])), "lower-right": bool(int(result[3]))}

    @IlluInternalSegments.setter
    def IlluInternalSegments(self, inputDict: dict) -> None:
        """
        Defines which segments of the internal illumination shall be used while capturing images.
        All directions are meant in view direction on top of the imager/device (not FOV!).

        :param inputDict: (dict) dict with LED segments <br />
                          syntax example: <br />
                          {"upper-left": True, "upper-right": True,
                          "lower-left": True, "lower-right": True}  <br />
                          upper-left: (bool) enable/disable upper-left LED <br />
                          upper-Right: (bool) enable/disable upper-right LED <br />
                          lower-Left: (bool) enable/disable lower-left LED <br />
                          lower-Right: (bool) enable/disable lower-Right LED
        :return: None
        """
        value = 0
        value += inputDict["upper-left"] * 0x01
        value += inputDict["upper-right"] * 0x02
        value += inputDict["lower-left"] * 0x04
        value += inputDict["lower-right"] * 0x08
        self.rpc.setParameter("IlluInternalSegments", value)
        self.applicationAPI.waitForConfigurationDone()

    @property
    def Color(self) -> [int, None]:
        """
        RGB-W illumination selection for this image.

        :return: (int / None) 1 digit <br />
                              0: white <br />
                              1: green <br />
                              2: blue <br />
                              3: red <br />
                              None: infrared
        """
        if "Color" in self.getAllParameters().keys():
            result = self.getParameter("Color")
            return result
        return None

    @Color.setter
    def Color(self, value: int) -> None:
        """
        RGB-W illumination selection for the image.

        :param value: (int) 1 digit <br />
                            0: white <br />
                            1: green <br />
                            2: blue <br />
                            3: red
        :return: None
        """
        if "Color" in self.getAllParameters().keys():
            limits = self.getAllParameterLimits()["Color"]
            if value not in range(int(limits["min"]), int(limits["max"]), 1):
                raise ValueError("Color value not available. Available range: {}"
                                 .format(self.getAllParameterLimits()["Color"]))
            self.rpc.setParameter("Color", value)
        else:
            articleNumber = self.mainAPI.getParameter("ArticleNumber")
            raise TypeError("Color attribute not available for sensor {}.".format(articleNumber))
        self.applicationAPI.waitForConfigurationDone()

    @property
    def ExposureTime(self) -> int:
        """
        Exposure time (in microseconds)

        :return: (int)
        """
        result = int(self.getParameter("ExposureTime"))
        return result

    @ExposureTime.setter
    def ExposureTime(self, value: int) -> None:
        """
        Exposure time (in microseconds)

        :param value: (int) Allowed range: 67 - 15000
        :return: None
        """
        limits = self.getAllParameterLimits()["ExposureTime"]
        if not int(limits["min"]) <= int(value) <= int(limits["max"]):
            raise ValueError("ExposureTime value not available. Available range: {}"
                             .format(self.getAllParameterLimits()["ExposureTime"]))
        self.rpc.setParameter("ExposureTime", value)
        self.applicationAPI.waitForConfigurationDone()

    @property
    def AnalogGainFactor(self) -> int:
        """
        Analog Gain Factor (increasing image brightness with a linear factor)

        :return:
        """
        result = int(self.getParameter("AnalogGainFactor"))
        return result

    @AnalogGainFactor.setter
    def AnalogGainFactor(self, value: int) -> None:
        """
        Analog Gain Factor (increasing image brightness with a linear factor)

        :param value: (int) Allowed values: 1, 2, 4, 8 for O2D / 1, 2, 4 for O2I
        :return: None
        """
        limits = self.getAllParameterLimits()["AnalogGainFactor"]
        if str(value) not in limits["values"]:
            raise ValueError("AnalogGainFactor value not available. Available values: {}"
                             .format(self.getAllParameterLimits()["AnalogGainFactor"]))
        self.rpc.setParameter("AnalogGainFactor", value)
        self.applicationAPI.waitForConfigurationDone()

    @property
    def FilterType(self) -> int:
        """
        Selected Filter Type for acquired image.

        :return (int) Filter selection <br />
                0: no filter <br />
                1: erosion <br />
                2: dilatation <br />
                3: median <br />
                4: mean
        """
        result = int(self.getParameter("FilterType"))
        return result

    @FilterType.setter
    def FilterType(self, value: int) -> None:
        """
        Set Filter Type for acquired image.

        :param value: (int) Possible filter selection <br />
               0: no filter <br />
               1: erosion <br />
               2: dilatation <br />
               3: median <br />
               4: mean
        :return: None
        """
        limits = self.getAllParameterLimits()["FilterType"]
        if not int(limits["min"]) <= int(value) <= int(limits["max"]):
            raise ValueError("FilterType value not available. Available range: {}"
                             .format(self.getAllParameterLimits()["FilterType"]))
        self.rpc.setParameter("FilterType", value)
        self.applicationAPI.waitForConfigurationDone()

    @property
    def FilterStrength(self) -> int:
        """
        Filter strength of selected filter type.
        Algo uses 2*Strength+1 as mask size for the filters.

        :return: (int) filter strength
        """
        result = int(self.getParameter("FilterStrength"))
        return result

    @FilterStrength.setter
    def FilterStrength(self, value: int):
        """
        Filter strength of selected filter type.
        Algo uses 2*Strength+1 as mask size for the filters.

        :param value: (int) Allowed values: 1, 2, 3, 4, 5
        :return:
        """
        limits = self.getAllParameterLimits()["FilterStrength"]
        if not int(limits["min"]) <= int(value) <= int(limits["max"]):
            raise ValueError("FilterStrength value not available. Available range: {}"
                             .format(self.getAllParameterLimits()["FilterStrength"]))
        self.rpc.setParameter("FilterStrength", value)
        self.applicationAPI.waitForConfigurationDone()

    @property
    def FilterInvert(self) -> bool:
        """
        Inversion of the image independent on the selected filter.

        :return: (bool) True or False
        """
        result = self.rpc.getParameter("FilterInvert")
        if result == "false":
            return False
        return True

    @FilterInvert.setter
    def FilterInvert(self, value: bool) -> None:
        """
        Set the inversion of the image independent on the selected filter.

        :param value: (bool) True or False
        :return: None
        """
        self.rpc.setParameter("FilterInvert", value)
        self.applicationAPI.waitForConfigurationDone()

    def startCalculateExposureTime(self) -> None:
        """
        Starting "auto exposuretime" with ROI-definition.

        :return: None
        """
        self.rpc.startCalculateExposureTime()
        while self.getProgressCalculateExposureTime() < 1.0:
            time.sleep(1)

    def getProgressCalculateExposureTime(self) -> float:
        """
        Will return 1.0 if teach is finished (or no teach is running).
        Returns something between 0 and 1 while teach is in progress.

        :return: (float) progress (0.0 to 1.0)
        """
        result = self.rpc.getProgressCalculateExposureTime()
        return result

    def startCalculateAutofocus(self) -> None:
        """
        Starting "autofocus" calculation with ROI-definition.

        :return: None
        """
        self.rpc.startCalculateAutofocus()
        while self.getProgressCalculateAutofocus() < 1.0:
            time.sleep(1)

    def stopCalculateAutofocus(self) -> None:
        """
        Interrupts the autofocus process initiated by startCalculateAutofocus().
        Initiates a soft stop. The focus process termination is signalled by the same progress signal
        reaching 1.0 as in startCalculateAutofocus()

        :return: None
        """
        self.rpc.stopCalculateAutofocus()

    def getProgressCalculateAutofocus(self) -> float:
        """
        Will return 1.0 if teach is finished (or no teach is running).
        Returns something between 0 and 1 while teach is in progress.

        :return: (float) progress (0.0 to 1.0)
        """
        result = self.rpc.getProgressCalculateAutofocus()
        return result

    def getAutofocusDistances(self) -> list:
        """
        Request a list of focus positions of the previous reference run.

        :return: (str) a list of floating point values, separated by comma
        """
        result = self.rpc.getAutofocusDistances()
        return result

    def getAutoExposureResult(self) -> dict:
        """
        Request a result of auto exposure algo run.

        :return: (dict) json with algo run result as a string
        """
        result = self.rpc.getAutoExposureResult()
        data = json.load(result)
        return data
