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


from _ctypes import COMError
from typing import Optional, Callable

from pywinauto.application import Application
from pywinauto.controls.uia_controls import EditWrapper, ButtonWrapper, ListItemWrapper, TreeItemWrapper
from pywinauto.controls.uiawrapper import UIAWrapper
from pywinauto.uia_defines import NoPatternInterfaceError
from pywinauto.uia_element_info import UIAElementInfo

from echo.driver import Driver, Element
from echo.utils import to_string, matches, STR_EXPRS, INT_EXPRS, BOOL_EXPRS
from . import Role


class UIADriver(Driver):
    def root(self) -> Optional['UIAElement']:
        app = Application(backend='uia')
        app.connect(handle=self.handle)
        window = app.top_window()
        return UIAElement.create_root(app=app, window=window.wrapper_object(), driver=self)

    def find_window(self, *filters: Callable[['UIAElement'], bool], ignore_case: bool = False, **criteria) -> list['UIAElement']:
        root = self.root()
        if root is None:
            return []
        return root.find_elements(*filters, ignore_case=ignore_case, include_self=True, **criteria)

    def close(self):
        pass


class UIAElement(Element):
    def __init__(self, app: Application, window: UIAWrapper, driver: UIADriver, root: 'UIAElement' = None, parent: 'UIAElement' = None):
        self._app: Application = app
        self._window: UIAWrapper = window
        self._driver: UIADriver = driver
        self._root: UIAElement = root or self  # TODO root
        self._parent: Optional[UIAElement] = parent
        self._virtual_depth: int = parent.depth + 1 if parent else 0

    @staticmethod
    def create_root(app: Application, window: UIAWrapper, driver: UIADriver) -> Optional['UIAElement']:
        return UIAElement(app=app, window=window, driver=driver)

    @staticmethod
    def create_element(window: UIAWrapper, root: 'UIAElement', parent: 'UIAElement' = None) -> 'UIAElement':
        return UIAElement(app=root._app, window=window, driver=root._driver, root=root, parent=parent)

    @property
    def driver(self) -> UIADriver:
        return self.driver

    @property
    def info(self) -> UIAElementInfo:
        return self._window.element_info

    @property
    def role(self) -> str:
        return self.info.control_type

    @property
    def name(self) -> str:
        return self.info.name

    @property
    def description(self) -> str:
        return self.info.rich_text

    @property
    def automation_id(self) -> int:
        return self.info.automation_id

    @property
    def class_name(self) -> int:
        return self.info.class_name

    @property
    def x(self) -> int:
        return self.info.rectangle.left

    @property
    def y(self) -> int:
        return self.info.rectangle.top

    @property
    def width(self) -> int:
        return self.info.rectangle.right - self.info.rectangle.left

    @property
    def height(self) -> int:
        return self.info.rectangle.bottom - self.info.rectangle.top

    @property
    def position(self) -> tuple[int, int]:
        info = self.info
        return info.rectangle.left, info.rectangle.top

    @property
    def size(self) -> tuple[int, int]:
        info = self.info
        return info.rectangle.right - info.rectangle.left, info.rectangle.bottom - info.rectangle.top

    @property
    def rectangle(self) -> tuple[int, int, int, int]:
        info = self.info
        return info.rectangle.left, info.rectangle.top, info.rectangle.right, info.rectangle.bottom

    @property
    def visible(self) -> bool:
        return self.info.visible

    @property
    def checked(self) -> bool:
        # checkbox
        role = self.role
        if role == Role.CHECK_BOX and isinstance(self._window, ButtonWrapper):
            return self._window.get_toggle_state() == 1
        elif role == Role.LIST_ITEM and isinstance(self._window, ListItemWrapper):
            return self._window.is_checked()
        elif role == Role.TREE_ITEM and isinstance(self._window, TreeItemWrapper):
            return self._window.is_checked()
        return False

    @property
    def enabled(self) -> bool:
        return self.info.enabled

    @property
    def selected(self) -> bool:
        # radiobutton
        try:
            return self._window.is_selected() == 1
        except NoPatternInterfaceError:
            return False
        except Exception as e:
            raise e

    @property
    def depth(self) -> int:
        return self._virtual_depth

    @property
    def text(self) -> Optional[str]:
        role = self.role
        if role == Role.EDIT and isinstance(self._window, EditWrapper):
            return self._window.get_value()
        return None

    def root(self) -> 'UIAElement':
        return self._root

    def parent(self) -> Optional['UIAElement']:
        # return if parent exists
        if self._parent is not None:
            return self._parent
        parent_window = self._window.parent()
        if parent_window is None:
            return None
        self._parent = UIAElement.create_element(window=parent_window, root=self._root)
        return self._parent

    def child(self, index: int) -> Optional['UIAElement']:
        children = self._window.children()
        count = len(children)
        if count <= 0 or count <= index:
            return None
        return UIAElement.create_element(window=children[index], root=self._root, parent=self)

    def children(self, *filters: Callable[['UIAElement'], bool], ignore_case: bool = False, **criteria) -> list['UIAElement']:
        res = []
        for child_window in self._window.children():
            child = UIAElement.create_element(window=child_window, root=self._root, parent=self)
            if filters or criteria:
                matched = child.matches(*filters, ignore_case=ignore_case, **criteria)
                if matched:
                    res.append(child)
            else:
                res.append(child)
        return res

    @property
    def children_count(self) -> int:
        return len(self._window.children())

    def click(self, button="left") -> bool:
        if isinstance(self._window, ButtonWrapper):
            try:
                role = self.role
                if role == Role.BUTTON:
                    self._window.click()
                elif role == Role.CHECK_BOX:
                    self._window.toggle()
                elif role == Role.RADIO_BUTTON:
                    self._window.select()
                else:
                    return False
                return True
            except NoPatternInterfaceError:
                # fallthrough
                pass
        # fallback
        self._window.set_focus()
        self._window.click_input(button)
        return True

    def input(self, text: str) -> bool:
        if isinstance(self._window, EditWrapper):
            try:
                self._window.set_edit_text(text)
                return True
            except COMError:
                return self._window.get_value() == text
            except NoPatternInterfaceError:
                return False
            except Exception as e:
                if not self._window.get_value() == text:
                    raise Exception("failed to input", e)
        return False

    def set_focus(self) -> bool:
        self._window.set_focus()
        return True

    def matches(self, *filters: Callable[['UIAElement'], bool], ignore_case=False, **criteria) -> bool:
        """
        Match element by criteria.
        :param filters: filters
        :param ignore_case: two strings are considered equal ignoring case
        :key role: role equals
        :key role_like: role name contains
        :key role_in: role name in list
        :key role_in_like: role name contains in list
        :key role_regex: role name regex
        :key name: name equals
        :key name_like: name contains
        :key name_in: name in list
        :key name_in_like: name contains in list
        :key name_regex: name regex
        :key description: description equals
        :key description_like: description contains
        :key description_in: description in list
        :key description_in_like: description contains in list
        :key description_regex: description regex
        :key x: x equals
        :key y: y equals
        :key width: width equals
        :key height: height equals
        :key text: text equals
        :key text_like: text contains
        :key text_in: text in list
        :key text_in_like: text contains in list
        :key text_regex: text regex
        :key visible: state visible
        :key checked: state checked
        :key selected: state selected
        :key enabled: state enabled
        :return: True if matched
        """
        snapshot = self
        rules = {
            "role": STR_EXPRS,
            "name": STR_EXPRS,
            "description": STR_EXPRS,
            "text": STR_EXPRS,
            "x": INT_EXPRS,
            "y": INT_EXPRS,
            "width": INT_EXPRS,
            "height": INT_EXPRS,
            "visible": BOOL_EXPRS,
            "checked": BOOL_EXPRS,
            "selected": BOOL_EXPRS,
            "enabled": BOOL_EXPRS,
        }
        return matches(snapshot, filters, rules, ignore_case, **criteria)

    def find_all_elements(self) -> list['UIAElement']:
        found = [self]
        children = self.children()
        for child in children:
            found.extend(child.find_all_elements())
        return found

    def find_elements(self, *filters: Callable[['UIAElement'], bool], ignore_case: bool = False, include_self=False, **criteria) -> list['UIAElement']:
        # return empty list if no filters or criteria
        if len(filters) == 0 and len(criteria) == 0:
            return []
        found = []
        if include_self:
            if self.matches(*filters, ignore_case=ignore_case, **criteria):
                found.append(self)
        children = self.children()
        for child in children:
            matched = child.matches(*filters, ignore_case=ignore_case, **criteria)
            if matched:
                found.append(child)
            # looking for deep elements
            found.extend(child.find_elements(*filters, ignore_case=ignore_case, include_self=False, **criteria))
        return found

    def find_element(self, *filters: Callable[['UIAElement'], bool], ignore_case: bool = False, include_self=False, **criteria) -> Optional['UIAElement']:
        # return None if no filters or criteria
        if len(filters) == 0 and len(criteria) == 0:
            return None
        if include_self:
            if self.matches(*filters, ignore_case=ignore_case, **criteria):
                return self
        children = self.children()
        for child in children:
            matched = child.matches(*filters, ignore_case=ignore_case, **criteria)
            if matched:
                return child
        # looking for deep elements if not found
        for child in children:
            found = child.find_element(*filters, ignore_case=ignore_case, include_self=False, **criteria)
            if found is not None:
                return found
        return None

    def __str__(self) -> str:
        return to_string(self, 'role', 'name', 'description', 'automation_id', 'class_name',
                         'rectangle', 'text', 'visible', 'checked', 'enabled', 'selected', 'depth')
