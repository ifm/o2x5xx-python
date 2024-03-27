import time
import json
from .imageQualityCheck import ImageQualityCheck


class Imager(object):
    """
    Imager object
    """

    def __init__(self, imagerProxy, device):
        self._imagerProxy = imagerProxy
        self._device = device
        self._imageQualityCheck = None

    @property
    def imageQualityCheck(self) -> ImageQualityCheck:
        """
        Request an Image Quality Check object for parametrizing the thresholds
        of the Image Quality check KPIs (key performance indicator).

        :return: ImageQualityCheck object
        """
        self._imageQualityCheck = ImageQualityCheck(self._imagerProxy, self._device)
        return self._imageQualityCheck

    def getAllParameters(self):
        """
        Returns all parameters of the object in one data-structure. For an overview which parameters can be request use
        the method get_all_parameters().

        :return: (dict) name contains parameter-name, value the stringified parameter-value
        """
        result = self._imagerProxy.getAllParameters()
        return result

    def getParameter(self, value):
        """
        Returns the current value of the parameter.

        :param value: (str) parameter name
        :return: (str)
        """
        result = self._imagerProxy.getParameter(value)
        return result

    def getAllParameterLimits(self):
        """
        Returns limits and default values of all
            1. numeric parameters that have limits in terms of minimum and maximum value
            2. parameters whose values are limited by a set of values (enum-like)

        :return: (dict)
        """
        result = self._imagerProxy.getAllParameterLimits()
        return result

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
        self._imagerProxy.setParameter("Name", value)
        self._device.waitForConfigurationDone()

    @property
    def Illumination(self) -> int:
        """
        Returns the kind of illumination used while capturing images.

        :return: (int) 1 digit 
                       0: no illumination active 
                       1: internal illumination shall be used 
                       2: external illumination shall be used 
                       3: internal and external illumination shall be used together
        """
        result = int(self.getParameter("Illumination"))
        return result

    @Illumination.setter
    def Illumination(self, value: int) -> None:
        """
        Defines which kind of illumination shall be used while capturing images.

        :param value: (int) 1 digit 
                            0: no illumination active 
                            1: internal illumination shall be used 
                            2: external illumination shall be used 
                            3: internal and external illumination shall be used together
        :return: None
        """
        limits = self.getAllParameterLimits()["Illumination"]
        if value not in range(int(limits["min"]), int(limits["max"]), 1):
            raise ValueError("Illumination value not available. Available range: {}"
                             .format(self.getAllParameterLimits()["Illumination"]))
        self._imagerProxy.setParameter("Illumination", value)
        self._device.waitForConfigurationDone()

    @property
    def IlluInternalSegments(self) -> dict:
        """
        Defines which segments of the internal illumination is used while capturing images.
        All directions are meant in view direction on top of the imager/device (not FOV!).

        :return: (dict) (dict) dict with LED segments enabled/disabled 
                          upper-left: (bool) enable/disable upper-left LED 
                          upper-Right: (bool) enable/disable upper-right LED 
                          lower-Left: (bool) enable/disable lower-left LED 
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

        :param inputDict: (dict) dict with LED segments 
                          syntax example: 
                          {"upper-left": True, "upper-right": True,
                          "lower-left": True, "lower-right": True}  
                          upper-left: (bool) enable/disable upper-left LED 
                          upper-Right: (bool) enable/disable upper-right LED 
                          lower-Left: (bool) enable/disable lower-left LED 
                          lower-Right: (bool) enable/disable lower-Right LED
        :return: None
        """
        value = 0
        value += inputDict["upper-left"] * 0x01
        value += inputDict["upper-right"] * 0x02
        value += inputDict["lower-left"] * 0x04
        value += inputDict["lower-right"] * 0x08
        self._imagerProxy.setParameter("IlluInternalSegments", value)
        self._device.waitForConfigurationDone()

    @property
    def Color(self) -> [int, None]:
        """
        RGB-W illumination selection for this image.

        :return: (int / None) 1 digit 
                              0: white 
                              1: green 
                              2: blue 
                              3: red 
                              None: infrared
        """
        if "Color" in self.getAllParameters().keys():
            result = int(self.getParameter("Color"))
            return result
        return None

    @Color.setter
    def Color(self, value: int) -> None:
        """
        RGB-W illumination selection for the image.

        :param value: (int) 1 digit 
                            0: white 
                            1: green 
                            2: blue 
                            3: red
        :return: None
        """
        if "Color" in self.getAllParameters().keys():
            limits = self.getAllParameterLimits()["Color"]
            if not int(limits["min"]) <= value <= int(limits["max"]):
                raise ValueError("Color value not available. Available range: {}"
                                 .format(self.getAllParameterLimits()["Color"]))
            self._imagerProxy.setParameter("Color", value)
        else:
            articleNumber = self._device.getParameter(value="ArticleNumber")
            raise TypeError("Color attribute not available for sensor {}.".format(articleNumber))
        self._device.waitForConfigurationDone()

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
        self._imagerProxy.setParameter("ExposureTime", value)
        self._device.waitForConfigurationDone()

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
        self._imagerProxy.setParameter("AnalogGainFactor", value)
        self._device.waitForConfigurationDone()

    @property
    def FilterType(self) -> int:
        """
        Selected Filter Type for acquired image.

        :return (int) Filter selection 
                0: no filter 
                1: erosion 
                2: dilatation 
                3: median 
                4: mean
        """
        result = int(self.getParameter("FilterType"))
        return result

    @FilterType.setter
    def FilterType(self, value: int) -> None:
        """
        Set Filter Type for acquired image.

        :param value: (int) Possible filter selection 
               0: no filter 
               1: erosion 
               2: dilatation 
               3: median 
               4: mean
        :return: None
        """
        limits = self.getAllParameterLimits()["FilterType"]
        if not int(limits["min"]) <= int(value) <= int(limits["max"]):
            raise ValueError("FilterType value not available. Available range: {}"
                             .format(self.getAllParameterLimits()["FilterType"]))
        self._imagerProxy.setParameter("FilterType", value)
        self._device.waitForConfigurationDone()

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
        self._imagerProxy.setParameter("FilterStrength", value)
        self._device.waitForConfigurationDone()

    @property
    def FilterInvert(self) -> bool:
        """
        Inversion of the image independent on the selected filter.

        :return: (bool) True or False
        """
        result = self._imagerProxy.getParameter("FilterInvert")
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
        self._imagerProxy.setParameter("FilterInvert", value)
        self._device.waitForConfigurationDone()

    def startCalculateExposureTime(self, minAnalogGainFactor: int = None, maxAnalogGainFactor: int = None,
                                   saturatedRatio: float = None, ROIs: list = None, RODs: list = None) -> None:
        """
        Starting calculation "auto exposure time" with analog gain factor, saturation ratio and ROI/ROD-definition.

        :param minAnalogGainFactor: Min. Analog Gain Factor upper limit. Possible values: 1, 2, 4 or 8
        :param maxAnalogGainFactor: Max. Analog Gain Factor upper limit. Possible values: 1, 2, 4 or 8
        :param saturatedRatio: (float/array) maximum acceptable ratio of saturated pixels. Possible range: [0.0, 1.0]
        :param ROIs: Auto-Exposure is calculated on these set of ROIs
        :param RODs: RODs are subtracted from the ROI union set
        :return: None
        """
        inputAutoExposure = {}
        if minAnalogGainFactor:
            inputAutoExposure.update({"minAnalogGainFactor": minAnalogGainFactor})
        if maxAnalogGainFactor:
            inputAutoExposure.update({"maxAnalogGainFactor": maxAnalogGainFactor})
        if saturatedRatio:
            inputAutoExposure.update({"saturatedRatio": saturatedRatio})
        if ROIs:
            inputAutoExposure.update({"ROIs": ROIs})
        if RODs and not ROIs:
            defaultROIsZone = [{"id": 0, "group": 0, "type": "Rect", "width": 1280,
                               "height": 960, "angle": 0, "center_x": 640, "center_y": 480}]
            inputAutoExposure.update({"ROIs": defaultROIsZone})
        if RODs:
            inputAutoExposure.update({"RODs": RODs})
        self._imagerProxy.startCalculateExposureTime(json.dumps(inputAutoExposure))
        while self.getProgressCalculateExposureTime() < 1.0:
            time.sleep(1)

    def getProgressCalculateExposureTime(self) -> float:
        """
        Will return 1.0 if teach is finished (or no teach is running).
        Returns something between 0 and 1 while teach is in progress.

        :return: (float) progress (0.0 to 1.0)
        """
        result = self._imagerProxy.getProgressCalculateExposureTime()
        return result

    def startCalculateAutofocus(self, ROIs: list = None, RODs: list = None) -> None:
        """
        Starting "autofocus" calculation with ROI-definition.
        The autofocus will be optimized for the center of the image (HWROI).

        :return: None
        """
        inputAutoFocus = {}
        if ROIs:
            inputAutoFocus.update({"ROIs": ROIs})
        if RODs and not ROIs:
            defaultROIsZone = [{"id": 0, "group": 0, "type": "Rect", "width": 1280,
                               "height": 960, "angle": 0, "center_x": 640, "center_y": 480}]
            inputAutoFocus.update({"ROIs": defaultROIsZone})
        if RODs:
            inputAutoFocus.update({"RODs": RODs})
        self._imagerProxy.startCalculateAutofocus(json.dumps(inputAutoFocus))
        while self.getProgressCalculateAutofocus() < 1.0:
            time.sleep(1)

    def stopCalculateAutofocus(self) -> None:
        """
        Interrupts the autofocus process initiated by startCalculateAutofocus().
        Initiates a soft stop. The focus process termination is signalled by the same progress signal
        reaching 1.0 as in startCalculateAutofocus()

        :return: None
        """
        self._imagerProxy.stopCalculateAutofocus()

    def getProgressCalculateAutofocus(self) -> float:
        """
        Will return 1.0 if teach is finished (or no teach is running).
        Returns something between 0 and 1 while teach is in progress.

        :return: (float) progress (0.0 to 1.0)
        """
        result = self._imagerProxy.getProgressCalculateAutofocus()
        return result

    def getAutofocusDistances(self) -> list:
        """
        Request a list of focus positions of the previous reference run.

        :return: a list of floating point values, separated by comma
        """
        result = self._imagerProxy.getAutofocusDistances()
        if result:
            if "," not in result:
                return [float(result)]
            tmp = result.split(",")
            result = [float(v) for v in tmp]
            return result

    def getAutoExposureResult(self) -> [dict, None]:
        """
        Request a result of auto exposure algo run.

        :return: (dict) json with algo run result as a string
        """
        result = self._imagerProxy.getAutoExposureResult()
        if result:
            data = json.loads(result)
            return data

    def __getattr__(self, name):
        """Pass given name to the actual xmlrpc.client.ServerProxy.

        Args:
            name (str): name of attribute
        Returns:
            Attribute of xmlrpc.client.ServerProxy
        """
        return self._editProxy.__getattr__(name)
