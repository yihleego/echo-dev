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


def retryable(func=None, max_retries: int = 2, delay: float = 1):
    if func is None:
        return partial(retryable, max_retries=max_retries, delay=delay)
    elif not callable(func) and isinstance(func, int):
        return partial(retryable, max_retries=func, delay=delay)

    @wraps(func)
    def wrapper(*args, **kwargs):
        attempts = 0
        while attempts < max_retries:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logging.error(f"Attempt {attempts + 1} failed. Retrying in {delay} seconds...", e)
                time.sleep(delay)
                attempts += 1
        logging.error(f"Max retries reached. Failed to execute {func.__name__}.")

    return wrapper
