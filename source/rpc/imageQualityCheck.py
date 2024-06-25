from urllib.request import urlopen
import json
import time
import ast


class ImageQualityCheck(object):
    """
    ImageQualityCheck object
    """

    def __init__(self, imagerProxy, device):
        self._imagerProxy = imagerProxy
        self._device = device

    @property
    def enabled(self) -> bool:
        """
        Get current state (enabled or disabled) of Image Quality Check for this image.

        :return: (bool) True / False
        """
        if self._imagerProxy.proxy.getAllParameters()["QualityCheckConfig"]:
            return True
        return False

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """
        Enable or disable Image Quality Check for this image.

        :param value: (bool) True / False
        :return: None
        """
        if value:
            self._imagerProxy.proxy.setParameter("QualityCheckConfig", True)
        else:
            self._imagerProxy.proxy.setParameter("QualityCheckConfig", "")
        while self._device.isConfigurationDone() < 1.0:
            time.sleep(1)

    @property
    def _QualityCheckConfig(self) -> [dict, None]:
        """
        The configuration of the quality check currently performed on the image.

        :return: (dict or None) The configuration as an empty string or a JSON object
        """
        if not self.enabled:
            return None
        result = self._imagerProxy.proxy.getAllParameters()["QualityCheckConfig"]
        result = ast.literal_eval(result)
        return result

    @_QualityCheckConfig.setter
    def _QualityCheckConfig(self, inputDict):
        """
        The configuration of the quality check that should be performed on the image.

        :param inputDict: (dict) configuration for Image Quality Check
        :return:
        """
        if not self.enabled:
            self.enabled = True
        self._imagerProxy.proxy.setParameter("QualityCheckConfig", json.dumps(inputDict))

    @property
    def _QualityCheckConfigSchema(self) -> dict:
        """
        Get the schema mit default values, limits and keys for Image Quality Check.

        :return: (dict) schema of Image Quality Check
        """
        with urlopen("http://{}/schema/ParamImageFeatures.json".format(self._device.address)) as url:
            data = json.load(url)
            return data

    @property
    def sharpness_thresholdMinMax(self) -> [dict, None]:
        """
        Get the current set min. and max. sharpness threshold values for this image.

        :return: (dict or None) if Image Quality Check is disabled return value is None
        """
        if not self.enabled:
            return None
        return {"min": self._QualityCheckConfig["threshold_min_sharpness"],
                "max": self._QualityCheckConfig["threshold_max_sharpness"]}

    @sharpness_thresholdMinMax.setter
    def sharpness_thresholdMinMax(self, inputDict: dict) -> None:
        """
        Set the min. and max. sharpness threshold values for this image.

        :param inputDict: (dict) input dict with keys "min" and "max"
            example: inputDict = {"min": 1000, "max": 10000}
        :return: None
        """
        if not self.enabled:
            raise SystemError("Image Quality Check not enabled!")
        limits = self._QualityCheckConfigSchema
        minThreshold_MinLimit = int(limits["threshold_min_sharpness"]["min"])
        minThreshold_MaxLimit = int(limits["threshold_min_sharpness"]["max"])
        maxThreshold_MinLimit = int(limits["threshold_max_sharpness"]["min"])
        maxThreshold_MaxLimit = int(limits["threshold_max_sharpness"]["max"])
        if not minThreshold_MinLimit <= inputDict["min"] <= minThreshold_MaxLimit:
            raise ValueError("Min. sharpness threshold value {} not in range [{}, {}]"
                             .format(inputDict["min"], minThreshold_MinLimit, minThreshold_MaxLimit))
        if not maxThreshold_MinLimit <= inputDict["max"] <= maxThreshold_MaxLimit:
            raise ValueError("Max. sharpness threshold value {} not in range [{}, {}]"
                             .format(inputDict["max"], maxThreshold_MinLimit, maxThreshold_MaxLimit))
        if not inputDict["min"] < inputDict["max"]:
            raise ValueError("Max. sharpness threshold value {} is smaller than Min. sharpness threshold value {}!"
                             .format(inputDict["max"], inputDict["min"]))
        tmp = self._QualityCheckConfig
        tmp["threshold_min_sharpness"] = inputDict["min"]
        tmp["threshold_max_sharpness"] = inputDict["max"]
        self._QualityCheckConfig = tmp
        self._device.waitForConfigurationDone()

    @property
    def meanBrightness_thresholdMinMax(self) -> [dict, None]:
        """
        Get the current set min. and max. mean brightness threshold values for this image.

        :return: (dict or None) if Image Quality Check is disabled return value is None
        """
        if not self.enabled:
            return None
        return {"min": self._QualityCheckConfig["threshold_min_brightness"],
                "max": self._QualityCheckConfig["threshold_max_brightness"]}

    @meanBrightness_thresholdMinMax.setter
    def meanBrightness_thresholdMinMax(self, inputDict: dict) -> None:
        """
        Set the min. and max. mean brightness threshold values for this image.

        :param inputDict: (dict) input dict with keys "min" and "max"
            example: inputDict = {"min": 10, "max": 220}
        :return: None
        """
        if not self.enabled:
            raise SystemError("Image Quality Check not enabled!")
        limits = self._QualityCheckConfigSchema
        minThreshold_MinLimit = int(limits["threshold_min_brightness"]["min"])
        minThreshold_MaxLimit = int(limits["threshold_min_brightness"]["max"])
        maxThreshold_MinLimit = int(limits["threshold_max_brightness"]["min"])
        maxThreshold_MaxLimit = int(limits["threshold_max_brightness"]["max"])
        if not minThreshold_MinLimit <= inputDict["min"] <= minThreshold_MaxLimit:
            raise ValueError("Min. brightness threshold value {} not in range [{}, {}]"
                             .format(inputDict["min"], minThreshold_MinLimit, minThreshold_MaxLimit))
        if not maxThreshold_MinLimit <= inputDict["max"] <= maxThreshold_MaxLimit:
            raise ValueError("Max. brightness threshold value {} not in range [{}, {}]"
                             .format(inputDict["max"], maxThreshold_MinLimit, maxThreshold_MaxLimit))
        if not inputDict["min"] < inputDict["max"]:
            raise ValueError("Max. brightness threshold value {} is smaller than Min. brightness threshold value {}!"
                             .format(inputDict["max"], inputDict["min"]))
        tmp = self._QualityCheckConfig
        tmp["threshold_min_brightness"] = inputDict["min"]
        tmp["threshold_max_brightness"] = inputDict["max"]
        self._QualityCheckConfig = tmp
        self._device.waitForConfigurationDone()

    @property
    def underexposedArea_thresholdMinMax(self) -> [dict, None]:
        """
        Get the current set min. and max. underexposed area threshold values for this image.

        :return: (dict or None) if Image Quality Check is disabled return value is None
        """
        if not self.enabled:
            return None
        return {"min": self._QualityCheckConfig["threshold_min_area_low_exposure"],
                "max": self._QualityCheckConfig["threshold_max_area_low_exposure"]}

    @underexposedArea_thresholdMinMax.setter
    def underexposedArea_thresholdMinMax(self, inputDict: dict) -> None:
        """
        Set the min. and max. underexposed area threshold values for this image.

        :param inputDict: (dict) input dict with keys "min" and "max"
            example: inputDict = {"min": 10, "max": 90}
        :return: None
        """
        if not self.enabled:
            raise SystemError("Image Quality Check not enabled!")
        limits = self._QualityCheckConfigSchema
        minThreshold_MinLimit = int(limits["threshold_min_area_low_exposure"]["min"])
        minThreshold_MaxLimit = int(limits["threshold_min_area_low_exposure"]["max"])
        maxThreshold_MinLimit = int(limits["threshold_max_area_low_exposure"]["min"])
        maxThreshold_MaxLimit = int(limits["threshold_max_area_low_exposure"]["max"])
        if not minThreshold_MinLimit <= inputDict["min"] <= minThreshold_MaxLimit:
            raise ValueError("Min. underexposedArea threshold value {} not in range [{}, {}]"
                             .format(inputDict["min"], minThreshold_MinLimit, minThreshold_MaxLimit))
        if not maxThreshold_MinLimit <= inputDict["max"] <= maxThreshold_MaxLimit:
            raise ValueError("Max. underexposedArea threshold value {} not in range [{}, {}]"
                             .format(inputDict["max"], maxThreshold_MinLimit, maxThreshold_MaxLimit))
        if not inputDict["min"] < inputDict["max"]:
            raise ValueError("Max. underexposedArea threshold value {} is smaller "
                             "than Min. underexposedArea threshold value {}!"
                             .format(inputDict["max"], inputDict["min"]))
        tmp = self._QualityCheckConfig
        tmp["threshold_min_area_low_exposure"] = inputDict["min"]
        tmp["threshold_max_area_low_exposure"] = inputDict["max"]
        self._QualityCheckConfig = tmp
        self._device.waitForConfigurationDone()

    @property
    def overexposedArea_thresholdMinMax(self) -> [dict, None]:
        """
        Get the current set min. and max. overexposed area threshold values for this image.

        :return: (dict or None) if Image Quality Check is disabled return value is None
        """
        if not self.enabled:
            return None
        return {"min": self._QualityCheckConfig["threshold_min_area_high_exposure"],
                "max": self._QualityCheckConfig["threshold_max_area_high_exposure"]}

    @overexposedArea_thresholdMinMax.setter
    def overexposedArea_thresholdMinMax(self, inputDict: dict) -> None:
        """
        Set the min. and max. overexposed area threshold values for this image.

        :param inputDict: (dict) input dict with keys "min" and "max"
            example: inputDict = {"min": 10, "max": 90}
        :return: None
        """
        if not self.enabled:
            raise SystemError("Image Quality Check not enabled!")
        limits = self._QualityCheckConfigSchema
        minThreshold_MinLimit = int(limits["threshold_min_area_high_exposure"]["min"])
        minThreshold_MaxLimit = int(limits["threshold_min_area_high_exposure"]["max"])
        maxThreshold_MinLimit = int(limits["threshold_max_area_high_exposure"]["min"])
        maxThreshold_MaxLimit = int(limits["threshold_max_area_high_exposure"]["max"])
        if not minThreshold_MinLimit <= inputDict["min"] <= minThreshold_MaxLimit:
            raise ValueError("Min. overexposedArea threshold value {} not in range [{}, {}]"
                             .format(inputDict["min"], minThreshold_MinLimit, minThreshold_MaxLimit))
        if not maxThreshold_MinLimit <= inputDict["max"] <= maxThreshold_MaxLimit:
            raise ValueError("Max. overexposedArea threshold value {} not in range [{}, {}]"
                             .format(inputDict["max"], maxThreshold_MinLimit, maxThreshold_MaxLimit))
        if not inputDict["min"] < inputDict["max"]:
            raise ValueError("Max. overexposedArea threshold value {} is smaller "
                             "than Min. overexposedArea threshold value {}!"
                             .format(inputDict["max"], inputDict["min"]))
        tmp = self._QualityCheckConfig
        tmp["threshold_min_area_high_exposure"] = inputDict["min"]
        tmp["threshold_max_area_high_exposure"] = inputDict["max"]
        self._QualityCheckConfig = tmp
        while self._device.isConfigurationDone() < 1.0:
            time.sleep(1)
