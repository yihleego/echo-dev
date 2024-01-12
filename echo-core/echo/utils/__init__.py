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


from .common import is_linux, is_mac, is_windows, \
    to_string, deep_to_lower, deep_to_upper, deep_strip, \
    matches, STR_EXPRS, INT_EXPRS, BOOL_EXPRS
from .deprecated import deprecated
from .screenshot import screenshot
from .singleton import singleton

__all__ = [
    "deprecated",
    "singleton",
    "screenshot",
    'is_linux', 'is_mac', 'is_windows',
    "to_string", "deep_to_lower", "deep_to_upper", "deep_strip",
    "matches", "STR_EXPRS", "INT_EXPRS", "BOOL_EXPRS"
]
