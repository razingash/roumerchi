from tests.management.commands.bot import send_message
import logging
"""
Ex levels  - logging, notification -
green -  1 - uncritical, predictable, possible error
yellow - 2 - +, + an error that most likely occurred due to bugs on the server or information transfer
red -    3 - +, +, an error that most likely occurred due to incorrect data transfer
black -  4 - +, -, an error that occurred due to an attempt to transmit unauthorized information | a little suspicious
dark -   5 - +, + - an error that shouldn't be possible without special tools | extremely suspicious
"""

class CustomException(Exception):
    def __init__(self, message, error_type=None):
        super().__init__(message)
        self.error_type = error_type

# logger conf...
custom_logger = logging.getLogger('custom_logger')
custom_logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('logger.log', encoding='utf-8')
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)s (%(asctime)s): %(message)s [%(filename)s]', datefmt='%d/%m/%Y %H:%M:%S')
handler.setFormatter(formatter)
custom_logger.addHandler(handler)


def log_and_notify_decorator(expected_return=None, *return_args, **return_kwargs): # overwhelming | 2, 3, 5, 1
    def decorator(func: callable):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except CustomException as e:
                print(f"Error: {e}")
                if e.error_type == 2:
                    custom_logger.error(e)
                    send_message(error_message=e)
                elif e.error_type == 3:
                    custom_logger.critical(e)
                    send_message(error_message=e)
                elif e.error_type == 5:
                    custom_logger.warning(e)
                    send_message(error_message=e)
                if callable(expected_return):
                    return expected_return(*args, **kwargs)
                if return_args or return_kwargs:
                    return return_args, return_kwargs
                return expected_return
        return wrapper
    return decorator

def log_decorator(expected_return=None, *return_args, **return_kwargs): # 4, 1
    def decorator(func: callable):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except CustomException as e:
                print(f"Error: {e}")
                if e.error_type == 2:
                    custom_logger.exception(e)
                if callable(expected_return):
                    return expected_return(*args, **kwargs)
                if return_args or return_kwargs:
                    return return_args, return_kwargs
                return expected_return
        return wrapper
    return decorator
