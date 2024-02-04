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
from typing import Callable


class InterruptException(Exception):
    """
    Interrupt retry
    """
    pass


_keys = ["max_retries", "delay", "use_logging", "exception_type", "error_message"]


def retry(func: Callable, max_retries: int = 1, delay: float = 0.0, use_logging: bool = False, exception_type=Exception, error_message=None, args=(), kwargs=None) -> any:
    """
    Retry if any error has occurred.
    Default to retry once without delay.
    :param func: the function to be wrapped
    :param max_retries: the maximum number of retries, i.e. 1 means running at most 2 times
    :param delay: the delay between retries (seconds)
    :param use_logging: whether to log the error
    :param exception_type: the exception type to be caught
    :param error_message: the custom error message will replace the caught error message if it is present
    :param args: the arguments to be passed to the function
    :param kwargs: the keyword arguments to be passed to the function
    :return: the result of the function
    """
    if max_retries <= 0:
        raise ValueError("max_retries must be greater than zero")

    if kwargs is None:
        kwargs = {}

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


def retryable(*args, **kwargs):
    """
    A decorator for retrying if any error has occurred.
    Default to retry once without delay.
    :key max_retries: the maximum number of retries, i.e. 1 means running at most 2 times
    :key delay: the delay between retries (seconds)
    :key use_logging: whether to log the error
    :key exception_type: the exception type to be caught
    :key error_message: the custom error message will replace the caught error message if it is present
    :return: the wrapped function
    """
    if not args:
        return partial(retryable, **kwargs)

    if callable(args[0]):
        wrapped = args[0]
        args = args[1:]
        return _retryable_adapter(wrapped=wrapped, *args, **kwargs)
    elif isinstance(args[0], (int, float)):
        for i in range(min(len(args), len(_keys))):
            kwargs[_keys[i]] = args[i]
        return partial(retryable, **kwargs)

    raise TypeError(repr(type(args[0])))


def _retryable_adapter(wrapped=None, max_retries: int = 1, delay: float = 0.0, use_logging: bool = False, exception_type=Exception, error_message=None) -> any:
    @wraps(wrapped)
    def wrapper(*args, **kwargs):
        return retry(func=wrapped, max_retries=max_retries, delay=delay, use_logging=use_logging, exception_type=exception_type, error_message=error_message, args=args, kwargs=kwargs)

    return wrapper
