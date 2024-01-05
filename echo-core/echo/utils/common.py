# -*- coding: utf-8 -*-
# Copyright (C) 2024  Echo Authors. All Rights Reserved.
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

import re
from enum import Enum
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


class Expr(str, Enum):
    EQ = "eq"
    LIKE = "like"
    IN = "in"
    IN_LIKE = "in_like"
    REGEX = "regex"
    GT = "gt"
    GTE = "gte"
    LT = "lt"
    LTE = "lte"
    NULL = "null"


STR_EXPRS = [Expr.EQ, Expr.LIKE, Expr.IN, Expr.IN_LIKE, Expr.REGEX, Expr.NULL]
INT_EXPRS = [Expr.EQ, Expr.GT, Expr.GTE, Expr.LT, Expr.LTE, Expr.NULL]
BOOL_EXPRS = [Expr.EQ]


def matches(obj: any, rules: dict[str, Union[list[Expr], tuple[str, tuple[Expr]]]], ignore_case: bool = False, *filters: Callable[[any], bool], **criteria) -> bool:
    if len(filters) == 0 and len(criteria) == 0:
        return False

    def _do_expr(expr, fixed, value):
        if ignore_case:
            fixed = deep_to_lower(fixed)
            value = deep_to_lower(value)
        if expr == Expr.EQ:
            return fixed == value
        elif expr == Expr.LIKE:
            return fixed.find(value) >= 0
        elif expr == Expr.IN:
            return fixed in value
        elif expr == Expr.IN_LIKE:
            for v in value:
                if fixed.find(v) >= 0:
                    return True
            return False
        elif expr == Expr.REGEX:
            return re.match(value, fixed) is not None
        elif expr == Expr.GT:
            return fixed > value
        elif expr == Expr.GTE:
            return fixed >= value
        elif expr == Expr.LT:
            return fixed < value
        elif expr == Expr.LTE:
            return fixed <= value
        elif expr == Expr.NULL:
            return fixed is None
        raise ValueError(f"unknown expression: {expr}")

    def _do_prop(obj, prop):
        if "." not in prop:
            return getattr(obj, prop)
        val = obj
        levels = prop.split(".")
        for level in levels:
            if not val:
                return None
            val = getattr(val, level)
        return val

    if filters:
        for f in filters:
            if not f(obj):
                return False
    if criteria:
        data = {}
        for key, item in rules.items():
            if isinstance(item, list):
                prop, exprs = key, item
            elif isinstance(item, tuple) and len(tuple) == 2:
                prop, exprs = item
            else:
                raise ValueError(f"invalid rules, must be 'dict[str, list]' or 'dict[str, tuple[str, list]]', but given {rules}")
            for expr in exprs:
                key = key if expr == Expr.EQ else key + "_" + expr
                if key in criteria:
                    data[key] = (prop, expr)
                    break
        if len(criteria) != len(data):
            diff = criteria.keys() - data.keys()
            if len(diff) > 0:
                raise ValueError(f"unsupported key(s): {', '.join(diff)}")
        for key, (prop, expr) in data.items():
            cri_val = criteria.get(key)
            if cri_val is None:
                continue
            prop_val = _do_prop(obj, prop)
            if prop_val is None:
                return False
            if not _do_expr(expr, prop_val, cri_val):
                return False
    return True
