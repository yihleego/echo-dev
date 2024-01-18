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


def retryable(func=None, max_retries: int = 2, delay: float = 1, use_logging: bool = True):
    if func is None:
        return partial(retryable, max_retries=max_retries, delay=delay, use_logging=use_logging)
    elif not callable(func) and isinstance(func, int):
        return partial(retryable, max_retries=func, delay=delay, use_logging=use_logging)

    @wraps(func)
    def wrapper(*args, **kwargs):
        count = 0
        err = None
        while count < max_retries:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                err = e
                count += 1
                if count < max_retries:
                    if use_logging:
                        logging.error(f"Attempt to execute {func.__name__} {count + 1} failed, retry in {delay} seconds", e)
                    time.sleep(delay)
        if err is not None:
            if use_logging:
                logging.error(f"Max retries({max_retries}) reached, failed to execute {func.__name__}", err)
            raise err
        else:
            raise Exception(f"Max retries reached. Failed to execute {func.__name__}")

    return wrapper
