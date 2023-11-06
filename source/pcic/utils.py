import functools
import multiprocessing.pool


def socket_exception_handler(max_timeout):
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
                return async_result.get(max_timeout)

            except multiprocessing.context.TimeoutError as e:
                print(e)
                raise TimeoutError(
                    "Unable to establish socket connection to device with IP {}. "
                    "Execution time exceeded max timeout of {} seconds."
                    .format(args[0].address, max_timeout))

            except ConnectionRefusedError as e:
                print(e)
                raise ConnectionRefusedError(
                    "Device with IP {} refuses socket connection with defined port {}. "
                    "Is the port ok? Default port number is 50010."
                    .format(args[0].address, args[0].port))

        return func_wrapper

    return exception_decorator
