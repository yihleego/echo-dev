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


from typing import Union, Callable


def to_string(obj, *keys) -> str:
    if not obj or isinstance(obj, str):
        return obj

    def _warp(v):
        return "'" + v + "'" if isinstance(v, str) else v

    return ", ".join([f"{k}={_warp(getattr(obj, k))}" for k in keys])


def deep_to_lower(obj: Union[str, list, set, tuple, dict, any]) -> Union[str, list, set, tuple, dict, any]:
    return _deep_str_func(obj, lambda x: x.lower())


def deep_to_upper(obj: Union[str, list, set, tuple, dict, any]) -> Union[str, list, set, tuple, dict, any]:
    return _deep_str_func(obj, lambda x: x.upper())


def deep_strip(obj: Union[str, list, set, tuple, dict, any]) -> Union[str, list, set, tuple, dict, any]:
    return _deep_str_func(obj, lambda x: x.strip())


def _deep_str_func(obj, func: Callable):
    if isinstance(obj, str):
        return func(obj)
    elif isinstance(obj, list):
        return [_deep_str_func(v, func) for v in obj]
    elif isinstance(obj, set):
        return {_deep_str_func(v, func) for v in obj}
    elif isinstance(obj, tuple):
        return tuple(_deep_str_func(v, func) for v in obj)
    elif isinstance(obj, dict):
        return {_deep_str_func(k, func): _deep_str_func(v, func) for k, v in obj.items()}
    return obj
