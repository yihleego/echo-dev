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


import time
from functools import wraps, partial


def wait_until(func=None, timeout: float = 5.0, delay: float = 1.0):
    """
    Wait until the function returns a truthy value, i.e. True, non-empty string, non-zero number, non-null object etc.
    Default to wait 5 seconds with 1 second delay.
    :param func: the function to be wrapped
    :param timeout: the maximum waiting time (seconds)
    :param delay: the delay between retries (seconds)
    :return: the wrapped function
    """
    if func is None:
        return partial(wait_until, timeout=timeout, delay=delay)
    elif not callable(func) and isinstance(func, float):
        return partial(wait_until, timeout=timeout, delay=delay)

    @wraps(func)
    def wrapper(*args, **kwargs):
        if timeout <= 0:
            raise ValueError("timeout must be greater than zero")

        st = time.perf_counter()
        ct = st
        while ct - st < timeout:
            res = func(*args, **kwargs)
            if res:
                return res
            if delay > 0:
                time.sleep(delay)
            ct = time.perf_counter()

    return wrapper
