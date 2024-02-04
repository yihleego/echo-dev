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


import inspect
import warnings
from functools import wraps, partial

_string_types = (type(b''), type(u''))
_keys = ["reason", "version", "action", "category", "stacklevel"]


def deprecated(*args, **kwargs):
    """
    A decorator which can be used to mark functions as deprecated.
    It will result in a warning being emitted when the function is used.
    :key reason: the reason which documents the deprecation in your library (can be omitted)
    :key version: the version of your project which deprecates this feature
    :key action: A warning filter used to activate or not the deprecation warning
    :key category: the warning category to use for the deprecation warning
    :key stacklevel: the number of additional stack levels to consider instrumentation rather than user code
    :return: the wrapped class, method or function
    """
    if not args:
        return partial(deprecated, **kwargs)

    if callable(args[0]):
        wrapped = args[0]
        args = args[1:]
        return _deprecated_adapter(wrapped=wrapped, *args, **kwargs)
    elif isinstance(args[0], _string_types):
        for i in range(min(len(args), len(_keys))):
            kwargs[_keys[i]] = args[i]
        return partial(deprecated, **kwargs)

    raise TypeError(repr(type(args[0])))


def _deprecated_adapter(wrapped=None, reason: str = None, version: str = None, action=None, category=DeprecationWarning, stacklevel=2):
    if inspect.isclass(wrapped):
        old_new1 = wrapped.__new__

        def wrapped_cls(cls, *args, **kwargs):
            msg = _get_msg(wrapped, reason, version)
            if action:
                with warnings.catch_warnings():
                    warnings.simplefilter(action, category)
                    warnings.warn(msg, category=category, stacklevel=stacklevel)
            else:
                warnings.warn(msg, category=category, stacklevel=stacklevel)
            if old_new1 is object.__new__:
                return old_new1(cls)
            return old_new1(cls, *args, **kwargs)

        wrapped.__new__ = staticmethod(wrapped_cls)
        return wrapped
    elif inspect.isroutine(wrapped):
        @wraps(wrapped)
        def wrapper(*args, **kwargs):
            msg = _get_msg(wrapped, reason, version)
            if action:
                with warnings.catch_warnings():
                    warnings.simplefilter(action, category)
                    warnings.warn(msg, category=category, stacklevel=stacklevel)
            else:
                warnings.warn(msg, category=category, stacklevel=stacklevel)
            return wrapped(*args, **kwargs)

        return wrapper
    else:
        raise TypeError(repr(type(wrapped)))


def _get_msg(wrapped, reason: str = None, version: str = None) -> str:
    if inspect.isclass(wrapped):
        msg = f"Class `{wrapped.__name__}` is deprecated"
    elif inspect.isfunction(wrapped):
        if wrapped.__name__ != wrapped.__qualname__:
            msg = f"Method `{wrapped.__qualname__}()` is deprecated"
        else:
            msg = f"Function `{wrapped.__qualname__}()` is deprecated"
    else:
        msg = f"`{wrapped.__name__}` is deprecated"
    if version:
        msg += f" since version {version}"
    if reason:
        msg += f", {reason}"
    return msg
