# -*- coding: utf-8 -*-
# Copyright (c) 2024 Echo Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import logging
import time
from functools import wraps, partial


class InterruptException(Exception):
    """
    Interrupt retry
    """
    pass


def retryable(func=None, max_retries: int = 1, delay: float = 0.0, use_logging: bool = False, exception_type=Exception, error_message=None):
    """
    Retry if the function raises an exception.
    Default to retry once without delay.
    :param func: the function to be wrapped
    :param max_retries: the maximum number of retries, i.e. 1 means running at most 2 times
    :param delay: the delay between retries (seconds)
    :param use_logging: whether to log the error
    :param exception_type: the exception type to be caught
    :param error_message: the custom error message will replace the caught error message if it is present
    :return: the wrapped function
    """
    if func is None:
        return partial(retryable, max_retries=max_retries, delay=delay, use_logging=use_logging, exception_type=exception_type)
    elif not callable(func) and isinstance(func, int):
        return partial(retryable, max_retries=func, delay=delay, use_logging=use_logging, exception_type=exception_type)

    @wraps(func)
    def wrapper(*args, **kwargs):
        if max_retries <= 0:
            raise ValueError("max_retries must be greater than zero")

        count = 0
        err = None
        while count <= max_retries:
            try:
                return func(*args, **kwargs)
            except InterruptException as ie:
                # interrupt
                raise ie
            except exception_type as e:
                err = e
                # skip if it's the last time
                if count < max_retries:
                    if use_logging:
                        logging.error(f"Attempt to execute {func.__name__} {count + 1} failed, retry in {delay} seconds", e)
                    if delay > 0:
                        time.sleep(delay)
            count += 1

        if err is not None and use_logging:
            logging.error(f"Max retries({max_retries}) reached, failed to execute {func.__name__}", err)

        if error_message is not None:
            raise Exception(error_message)
        elif err is not None:
            raise err
        else:
            raise Exception(f"Max retries reached. Failed to execute {func.__name__}")

    return wrapper
