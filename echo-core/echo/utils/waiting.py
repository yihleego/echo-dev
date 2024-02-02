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


def wait_until(func=None, timeout: float = 5.0, delay: float = 1.0, use_logging: bool = False, validator: Callable = None):
    """
    Wait until the function returns a truthy value, i.e. True, non-empty string, non-zero number, non-null object etc.
    Default to wait 5 seconds and delay 1 second.
    :param func: the function to be wrapped
    :param timeout: the maximum waiting time (seconds)
    :param delay: the delay between retries (seconds)
    :param use_logging: whether to log the error
    :param validator: the function to validate the result
    :return: the wrapped function
    """
    if func is None:
        return partial(wait_until, timeout=timeout, delay=delay, use_logging=use_logging, validator=validator)
    elif not callable(func) and isinstance(func, (int, float)):
        return partial(wait_until, timeout=func, delay=delay, use_logging=use_logging, validator=validator)

    @wraps(func)
    def wrapper(*args, **kwargs):
        return wait(func=func, timeout=timeout, delay=delay, use_logging=use_logging, validator=validator, args=args, kwargs=kwargs)

    return wrapper


def wait(func: Callable, timeout: float = 5.0, delay: float = 1.0, use_logging: bool = False, validator: Callable = None, args=(), kwargs=None) -> any:
    """
    Wait until the function returns a truthy value, i.e. True, non-empty string, non-zero number, non-null object etc.
    Default to wait 5 seconds and delay 1 second.
    :param func: the function to be wrapped
    :param timeout: the maximum waiting time (seconds)
    :param delay: the delay between retries (seconds)
    :param use_logging: whether to log the error
    :param validator: the function to validate the result
    :param args: the arguments to be passed to the function
    :param kwargs: the keyword arguments to be passed to the function
    :return: the result of the function
    """
    if timeout <= 0:
        raise ValueError("timeout must be greater than zero")

    if kwargs is None:
        kwargs = {}

    elapsed = 0.0
    start = time.perf_counter()
    while elapsed <= timeout:
        res = func(*args, **kwargs)
        if validator is not None:
            if validator(res):
                return res
        else:
            if res:
                return res
        if use_logging:
            logging.debug("Unexpected result [%s] returned, %.3f seconds remaining", str(res), timeout - elapsed)
        time.sleep(max(delay, 0))
        elapsed = time.perf_counter() - start

    if use_logging:
        logging.error("Max timeout reached. Failed to waiting for the expected result")
