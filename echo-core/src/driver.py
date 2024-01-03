import os
import re
import time
from abc import ABC, abstractmethod
from typing import Callable, Optional, TypeVar, Generic, Union

from PIL import Image, ImageGrab

from .utils import win32

T = TypeVar('T')


class Element(ABC, Generic[T]):

    @property
    @abstractmethod
    def handle(self) -> int:
        pass

    @property
    @abstractmethod
    def process_id(self) -> int:
        pass

    @property
    @abstractmethod
    def rectangle(self) -> tuple[int, int, int, int]:
        pass

    @property
    @abstractmethod
    def parent(self) -> Optional[T]:
        pass

    @property
    @abstractmethod
    def children(self) -> list[T]:
        pass

    @abstractmethod
    def child(self, index: int) -> Optional[T]:
        pass

    @abstractmethod
    def _snapshot(self) -> Union[T, any]:
        pass

    @abstractmethod
    def _rules(self) -> dict:
        pass

    def matches(self, *filters: Callable[[Union[T, any]], bool], **criteria) -> bool:
        def _do_expr(expr, fixed, value):
            if expr == "eq":
                return fixed == value
            if expr == "like":
                return fixed.find(value) >= 0
            if expr == "in":
                return fixed in value
            if expr == "in_like":
                for v in value:
                    if fixed.find(v) >= 0:
                        return True
                return False
            if expr == "regex":
                return re.match(value, fixed) is not None
            if expr == "gt":
                return fixed > value
            if expr == "gte":
                return fixed >= value
            if expr == "lt":
                return fixed < value
            if expr == "lte":
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

        if len(filters) == 0 and len(criteria) == 0:
            return False

        snapshot = self._snapshot()
        rules = self._rules()
        if filters:
            for filter in filters:
                if not filter(snapshot):
                    return False
        if criteria:
            data = {}
            for key, (prop, exprs) in rules.items():
                for expr in exprs:
                    fullkey = key if expr == "eq" else key + "_" + expr
                    if fullkey in criteria:
                        data[fullkey] = (prop, expr)
                        break
            if len(criteria) != len(data):
                diff = criteria.keys() - data.keys()
                if len(diff) > 0:
                    raise Exception(f"Unsupported key(s): {str(diff)}")
            for key, (prop, expr) in data.items():
                arg = criteria.get(key)
                if arg is None:
                    continue
                val = _do_prop(snapshot, prop)
                if val is None:
                    return False
                if not _do_expr(expr, val, arg):
                    return False
        return True

    def release(self):
        pass

    def find_all_elements(self) -> list[T]:
        found = [self]
        children = self.children
        for child in children:
            found.extend(child.find_all_elements())
        return found

    def find_elements(self, *filters: Callable[[T], bool], **criteria) -> list[T]:
        # return empty list if no criteria
        if len(filters) == 0 and len(criteria) == 0:
            return []
        found = []
        releasing = []
        children = self.children
        for child in children:
            matched = child.matches(*filters, **criteria)
            if matched:
                found.append(child)
            else:
                releasing.append(child)
            # looking for deep elements
            found.extend(child.find_elements(*filters, **criteria))
        # release all mismatched elements
        for child in releasing:
            child.release()
        return found

    def find_element(self, *filters: Callable[[T], bool], **criteria) -> Optional[T]:
        # return None if no criteria
        if len(filters) == 0 and len(criteria) == 0:
            return None
        found = None
        releasing = []
        children = self.children
        for child in children:
            matched = child.matches(*filters, **criteria)
            if matched:
                found = child
                break
            else:
                releasing.append(child)
        # looking for deep elements if not found
        if not found:
            for child in children:
                found = child.find_element(*filters, **criteria)
                if found:
                    break
        # release all mismatched elements
        for child in releasing:
            child.release()
        return found

    def exists_element(self, *filters: Callable[[T], bool], **criteria) -> bool:
        found = self.find_element(*filters, **criteria)
        if found:
            return True
        else:
            return False

    def set_foreground(self) -> bool:
        self.show()
        return win32.set_foreground(self.handle, self.process_id)

    def move(self, x: int = None, y: int = None, width: int = None, height: int = None, repaint=True) -> bool:
        if x is None or y is None or width is None or height is None:
            rect = self.root.rectangle
            if x is None:
                x = rect[0]
            if y is None:
                y = rect[1]
            if width is None:
                width = rect[2] - rect[0]
            if height is None:
                height = rect[3] - rect[1]
        return win32.move_window(self.handle, self.process_id, x, y, width, height, repaint)

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

    def screenshot(self, filename: str = None) -> Image:
        self.set_foreground()
        time.sleep(0.06)
        image = ImageGrab.grab(self.rectangle)
        dirname = os.path.dirname(filename)
        if filename:
            if not os.path.exists(dirname):
                os.makedirs(dirname, exist_ok=True)
            image.save(filename)
        return filename


class Driver(ABC):
    pass
