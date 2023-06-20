from urllib.parse import urlparse
from urllib.request import urlopen
import json
import time
import ast


class ImageQualityCheckConfig(object):
    def __init__(self, imageURL, imageRPC, applicationAPI):
        self._imageURL = imageURL
        self._imageRPC = imageRPC
        self._applicationAPI = applicationAPI

    @property
    def enabled(self) -> bool:
        if self._imageRPC.getAllParameters()["QualityCheckConfig"]:
            return True
        return False

    @enabled.setter
    def enabled(self, value: bool) -> None:
        if value:
            self._imageRPC.setParameter("QualityCheckConfig", True)
            # self._imageRPC.setParameter("QualityCheckConfig", self._QualityCheckConfigSchema)
        else:
            self._imageRPC.setParameter("QualityCheckConfig", "")
        while self._applicationAPI.isConfigurationDone() < 1.0:
            time.sleep(1)

    @property
    def _QualityCheckConfig(self) -> [dict, None]:
        if not self.enabled:
            return None
        result = self._imageRPC.getAllParameters()["QualityCheckConfig"]
        result = ast.literal_eval(result)
        return result

    @_QualityCheckConfig.setter
    def _QualityCheckConfig(self, inputDict):
        if not self.enabled:
            self.enabled = True
        self._imageRPC.setParameter("QualityCheckConfig", json.dumps(inputDict))

    @property
    def _QualityCheckConfigSchema(self) -> [dict]:
        ip = urlparse(self._imageURL).netloc
        with urlopen("http://{}/schema/ParamImageFeatures.json".format(ip)) as url:
            data = json.load(url)
            return data

    @property
    def sharpness_thresholdMinMax(self) -> [int, None]:
        if not self.enabled:
            return None
        return {"min": self._QualityCheckConfig["threshold_min_sharpness"],
                "max": self._QualityCheckConfig["threshold_max_sharpness"]}

    @property
    def meanBrightness_thresholdMinMax(self) -> [dict, None]:
        if not self.enabled:
            return None
        return {"min": self._QualityCheckConfig["threshold_min_brightness"],
                "max": self._QualityCheckConfig["threshold_max_brightness"]}

    @property
    def underexposedArea_thresholdMinMax(self) -> [dict, None]:
        if not self.enabled:
            return None
        return {"min": self._QualityCheckConfig["threshold_min_area_low_exposure"],
                "max": self._QualityCheckConfig["threshold_max_area_low_exposure"]}

    @property
    def overexposedArea_thresholdMinMax(self) -> [dict, None]:
        if not self.enabled:
            return None
        return {"min": self._QualityCheckConfig["threshold_min_area_high_exposure"],
                "max": self._QualityCheckConfig["threshold_max_area_high_exposure"]}

    @sharpness_thresholdMinMax.setter
    def sharpness_thresholdMinMax(self, inputDict: dict) -> None:
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
        while self._applicationAPI.isConfigurationDone() < 1.0:
            time.sleep(1)

    @meanBrightness_thresholdMinMax.setter
    def meanBrightness_thresholdMinMax(self, inputDict: dict) -> None:
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
        while self._applicationAPI.isConfigurationDone() < 1.0:
            time.sleep(1)

    @underexposedArea_thresholdMinMax.setter
    def underexposedArea_thresholdMinMax(self, inputDict: dict) -> None:
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
        while self._applicationAPI.isConfigurationDone() < 1.0:
            time.sleep(1)

    @overexposedArea_thresholdMinMax.setter
    def overexposedArea_thresholdMinMax(self, inputDict: dict) -> None:
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
        while self._applicationAPI.isConfigurationDone() < 1.0:
            time.sleep(1)
