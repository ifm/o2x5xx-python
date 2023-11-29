import zipfile
import json
import warnings
import multiprocessing.pool
import functools


def timeout(max_timeout):
    """Timeout decorator, parameter in seconds."""
    def timeout_decorator(item):
        """Wrap the original function."""
        @functools.wraps(item)
        def func_wrapper(*args, **kwargs):
            """Closure for function."""
            pool = multiprocessing.pool.ThreadPool(processes=1)
            async_result = pool.apply_async(item, args, kwargs)
            pool.close()
            # raises a TimeoutError if execution exceeds max_timeout
            return async_result.get(max_timeout)
        return func_wrapper
    return timeout_decorator


def firmwareWarning(function):
    """Formware warning decorator."""

    def wrapper(self, *args, **kwargs):
        keyArgName = list(kwargs.keys())[0]
        zipOpen = zipfile.ZipFile(kwargs[keyArgName], "r")
        zipFiles = zipOpen.namelist()
        if "device.json" in zipFiles:
            tmp = "device.json"
        elif "application.json" in zipFiles:
            tmp = "application.json"
        else:
            raise ImportError("Unknown config file in zip: {}".format(str(zipFiles)))
        jsonData = json.loads(zipOpen.open(tmp).read())
        minConfigFileFirmware = jsonData["Firmware"]
        sensorFirmware = self._device.mainProxy.getSWVersion()["IFM_Software"]
        if int(sensorFirmware.replace(".", "")) < int(minConfigFileFirmware.replace(".", "")):
            message = "Missmatch in firmware versions: Sensor firmware {} is lower than {} firmware {}. " \
                      "Import of may will fail!".format(sensorFirmware, tmp, minConfigFileFirmware)
            warnings.warn(message, UserWarning)
        return function(self, *args, **kwargs)
    return wrapper


def rpc_exception_handler(max_timeout):
    """Timeout decorator, parameter in seconds."""

    def exception_decorator(item):
        """Wrap the original function."""

        @functools.wraps(item)
        def func_wrapper(*args, **kwargs):
            """Closure for function."""
            try:
                pool = multiprocessing.pool.ThreadPool(processes=1)
                async_result = pool.apply_async(item, args, kwargs)
                # raises a TimeoutError if execution exceeds max_timeout
                pool.close()
                return async_result.get(max_timeout)

            except multiprocessing.context.TimeoutError as e:
                raise TimeoutError(
                    "Unable to establish XML-RPC connection to device with IP {}. "
                    "Execution time exceeded max timeout of {} seconds."
                    .format(args[0].address, max_timeout))

        return func_wrapper

    return exception_decorator
