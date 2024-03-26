import functools
import multiprocessing.pool


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


def socket_exception_handler(max_timeout):
    """Timeout decorator, parameter in seconds."""

    def exception_decorator(item):
        """Wrap the original function."""

        def close_socket_on_exception(session):
            pcicSocket = getattr(session, "pcicSocket")
            if pcicSocket:
                pcicSocket.close()

        @functools.wraps(item)
        def func_wrapper(*args, **kwargs):
            """Closure for function."""
            # max_timeout = getattr(args[0], "timeout")
            # max_timeout = timeout
            try:
                pool = multiprocessing.pool.ThreadPool(processes=1)
                async_result = pool.apply_async(item, args, kwargs)
                pool.close()
                # raises a TimeoutError if execution exceeds max_timeout
                return async_result.get(max_timeout)

            except multiprocessing.context.TimeoutError:
                close_socket_on_exception(session=args[0])
                raise TimeoutError(
                    "Unable to establish socket connection to device with IP {}. "
                    "Execution time exceeded max timeout of {} seconds."
                    .format(args[0].address, max_timeout))

            except ConnectionRefusedError:
                close_socket_on_exception(session=args[0])
                raise ConnectionRefusedError(
                    "Device with IP {} refuses socket connection with defined port {}. "
                    "Is the port ok? Default port number is 50010."
                    .format(args[0].address, args[0].port))

        return func_wrapper

    return exception_decorator
