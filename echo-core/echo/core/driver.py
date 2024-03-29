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


import re
import time
from abc import ABC, abstractmethod
from enum import Enum
from typing import Callable, Union, Tuple, List, Dict

from PIL import Image

from echo.utils import win32, screenshot, strings


class Expr(str, Enum):
    EQ = "eq"
    NOT = "not"
    LIKE = "like"
    IN = "in"
    IN_LIKE = "in_like"
    REGEX = "regex"
    GT = "gt"
    GTE = "gte"
    LT = "lt"
    LTE = "lte"
    NULL = "null"


STR_EXPRS = [Expr.EQ, Expr.NOT, Expr.LIKE, Expr.IN, Expr.IN_LIKE, Expr.REGEX, Expr.NULL]
NUM_EXPRS = [Expr.EQ, Expr.NOT, Expr.GT, Expr.GTE, Expr.LT, Expr.LTE, Expr.NULL]
BOOL_EXPRS = [Expr.EQ, Expr.NOT, Expr.NULL]


class _Common(ABC):
    @property
    @abstractmethod
    def rectangle(self) -> Tuple[int, int, int, int]:
        pass

    @abstractmethod
    def set_foreground(self) -> bool:
        pass

    def draw_outline(self, color=0x0000ff):
        win32.draw_outline(self.rectangle, color=color)

    def simulate_click(self, button="left", coords: Tuple[int, int] = None,
                       button_down=True, button_up=True, double=False,
                       wheel_dist=0, pressed="", key_down=True, key_up=True):
        from pywinauto import mouse

        if not coords:
            # click the center of the element
            rect = self.rectangle
            coords = (int((rect[2] + rect[0]) / 2), int((rect[3] + rect[1]) / 2))

        mouse._perform_click_input(
            button=button, coords=coords,
            button_down=button_down, button_up=button_up, double=double,
            wheel_dist=wheel_dist, pressed=pressed, key_down=key_down, key_up=key_up)

    def simulate_input(self, keys, pause=0.05, with_spaces=False, with_tabs=False, with_newlines=False,
                       turn_off_numlock=False, vk_packet=True, set_foreground=False):
        from pywinauto import keyboard
        import six
        import locale

        if isinstance(keys, six.text_type):
            aligned_keys = keys
        elif isinstance(keys, six.binary_type):
            aligned_keys = keys.decode(locale.getpreferredencoding())
        else:
            # convert a non-string input
            aligned_keys = six.text_type(keys)

        if set_foreground:
            self.set_foreground()

        keyboard.send_keys(
            keys=aligned_keys, pause=pause,
            with_spaces=with_spaces, with_tabs=with_tabs,
            with_newlines=with_newlines, turn_off_numlock=turn_off_numlock,
            vk_packet=vk_packet)


class Driver(_Common, ABC):
    def __init__(self, handle: int, process_id: int = None, process_name: str = None, window_name: str = None, class_name: str = None):
        self._handle = handle
        self._process_id = process_id or win32.get_process_id_from_handle(self.handle)
        self._process_name = process_name or win32.get_process_name_by_process_id(self.process_id)
        self._window_name = window_name or win32.get_window_text(self.handle)
        self._class_name = class_name or win32.get_class_name(self.handle)

    @property
    def handle(self) -> int:
        return self._handle

    @property
    def process_id(self) -> int:
        return self._process_id

    @property
    def process_name(self) -> str:
        return self._process_name

    @property
    def window_name(self) -> str:
        return self._window_name

    @property
    def class_name(self) -> str:
        return self._class_name

    @property
    def rectangle(self) -> Tuple[int, int, int, int]:
        return win32.get_window_rect(self.handle)

    def screenshot(self, filename: str = None) -> Image:
        self.set_foreground()
        time.sleep(0.06)
        return screenshot.screenshot(self.rectangle, filename)

    def set_foreground(self) -> bool:
        self.show()
        self.normal()
        return win32.set_foreground(self.handle, self.process_id)

    def move(self, x: int = None, y: int = None, width: int = None, height: int = None, repaint=True) -> bool:
        return win32.move_window(self.handle, self.process_id, x, y, width, height, repaint)

    def normal(self) -> bool:
        return win32.show_window(self.handle, win32.SW_NORMAL)

    def hide(self) -> bool:
        return win32.show_window(self.handle, win32.SW_HIDE)

    def show(self) -> bool:
        return win32.show_window(self.handle, win32.SW_SHOW)

    def maximize(self) -> bool:
        return win32.show_window(self.handle, win32.SW_MAXIMIZE)

    def minimize(self) -> bool:
        return win32.show_window(self.handle, win32.SW_MINIMIZE)

    def restore(self) -> bool:
        return win32.show_window(self.handle, win32.SW_RESTORE)

    def is_minimized(self) -> bool:
        return win32.get_window_placement(self.handle).showCmd == win32.SW_SHOWMINIMIZED

    def is_maximized(self) -> bool:
        return win32.get_window_placement(self.handle).showCmd == win32.SW_SHOWMAXIMIZED

    def is_normal(self) -> bool:
        return win32.get_window_placement(self.handle).showCmd == win32.SW_SHOWNORMAL

    def close(self):
        pass

    def __str__(self) -> str:
        return f"handle: {self.handle}, " \
               f"process_id: {self.process_id}, " \
               f"process_name: {self.process_name}, " \
               f"window_name: {self.window_name}, " \
               f"class_name: {self.class_name}," \
               f"rectangle: {self.rectangle}"


class Element(_Common, ABC):
    @property
    @abstractmethod
    def driver(self) -> Driver:
        pass

    @property
    @abstractmethod
    def rectangle(self) -> Tuple[int, int, int, int]:
        pass

    def set_foreground(self) -> bool:
        return self.driver.set_foreground()

    def screenshot(self, filename: str = None) -> Image:
        self.driver.set_foreground()
        time.sleep(0.06)
        return screenshot.screenshot(self.rectangle, filename)

    @staticmethod
    def _match(
            obj: any,
            filters: Union[List[Callable[[any], bool]], Tuple[Callable[[any], bool], ...]] = None,
            rules: Dict[str, Union[List[Expr], Tuple[str, List[Expr]]]] = None,
            ignore_case: bool = False,
            **criteria) -> bool:
        if not filters and not criteria:
            return False

        def _do_expr(expr, fixed, value):
            if fixed is None:
                if expr == Expr.NULL:
                    return bool(value)
                else:
                    return False
            if ignore_case:
                fixed = strings.deep_to_lower(fixed)
                value = strings.deep_to_lower(value)
            if expr == Expr.EQ:
                return fixed == value
            if expr == Expr.NOT:
                return fixed != value
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
                    _key = key if expr == Expr.EQ else key + "_" + expr
                    if _key in criteria:
                        data[_key] = (prop, expr)
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
                if not _do_expr(expr, prop_val, cri_val):
                    return False
        return True

    @staticmethod
    def _gen_match_docs(rules: Dict[str, Union[List[Expr], Tuple[str, List[Expr]]]] = None) -> str:
        docs = []
        for name, exprs in rules.items():
            for expr in exprs:
                if expr == Expr.EQ:
                    docs.append(f":key {name}: {name} == value")
                elif expr == Expr.NOT:
                    docs.append(f":key {name}_{expr}: {name} != value")
                elif expr == Expr.LIKE:
                    docs.append(f":key {name}_{expr}: {name} like *value*")
                elif expr == Expr.IN:
                    docs.append(f":key {name}_{expr}: {name} in [value1, value2]")
                elif expr == Expr.IN_LIKE:
                    docs.append(f":key {name}_{expr}: {name} in like [*value1*, *value2*]")
                elif expr == Expr.REGEX:
                    docs.append(f":key {name}_{expr}: {name} regex pattern (str)")
                elif expr == Expr.GT:
                    docs.append(f":key {name}_{expr}: {name} > value")
                elif expr == Expr.GTE:
                    docs.append(f":key {name}_{expr}: {name} >= value")
                elif expr == Expr.LT:
                    docs.append(f":key {name}_{expr}: {name} < value")
                elif expr == Expr.LTE:
                    docs.append(f":key {name}_{expr}: {name} <= value")
                elif expr == Expr.NULL:
                    docs.append(f":key {name}_{expr}: {name} is None (bool)")
        return "\n".join(docs)

    def __str__(self) -> str:
        return f"rectangle: {self.rectangle}"
