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


from functools import wraps
from threading import RLock


def singleton(cls):
    instances = {}

    @wraps(cls)
    def wrapper(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return wrapper


class Singleton(type):
    """Metaclass for classes that wish to implement Singleton
    functionality.  If an instance of the class exists, it's returned,
    otherwise a single instance is instantiated and returned.
    """

    def __init__(cls, name, bases, dct):
        super(Singleton, cls).__init__(name, bases, dct)
        cls.__instance = None
        cls.__rlock = RLock()

    def __call__(cls, *args, **kw):
        if cls.__instance is not None:
            return cls.__instance

        with cls.__rlock:
            if cls.__instance is None:
                cls.__instance = super(Singleton, cls).__call__(*args, **kw)

        return cls.__instance
