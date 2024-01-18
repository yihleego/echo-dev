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
from enum import Enum
from typing import Optional, Callable

from pywinauto.application import Application
from pywinauto.controls.uia_controls import EditWrapper, ButtonWrapper, ListItemWrapper, TreeItemWrapper
from pywinauto.controls.uiawrapper import UIAWrapper
from pywinauto.uia_defines import NoPatternInterfaceError
from pywinauto.uia_element_info import UIAElementInfo

from echo.core.driver import Driver, Element, matches, STR_EXPRS, INT_EXPRS, BOOL_EXPRS


class Role(str, Enum):
    APP_BAR = "AppBar"
    BUTTON = "Button"
    CALENDAR = "Calendar"
    CHECK_BOX = "CheckBox"
    COMBO_BOX = "ComboBox"
    CUSTOM = "Custom"
    DATA_GRID = "DataGrid"
    DATA_ITEM = "DataItem"
    DOCUMENT = "Document"
    EDIT = "Edit"
    GROUP = "Group"
    HEADER = "Header"
    HEADER_ITEM = "HeaderItem"
    HYPERLINK = "Hyperlink"
    IMAGE = "Image"
    LIST = "List"
    LIST_ITEM = "ListItem"
    MENU_BAR = "MenuBar"
    MENU = "Menu"
    MENU_ITEM = "MenuItem"
    PANE = "Pane"
    PROGRESS_BAR = "ProgressBar"
    RADIO_BUTTON = "RadioButton"
    SCROLL_BAR = "ScrollBar"
    SEMANTIC_ZOOM = "SemanticZoom"
    SEPARATOR = "Separator"
    SLIDER = "Slider"
    SPINNER = "Spinner"
    SPLIT_BUTTON = "SplitButton"
    STATUS_BAR = "StatusBar"
    TAB = "Tab"
    TAB_ITEM = "TabItem"
    TABLE = "Table"
    TEXT = "Text"
    THUMB = "Thumb"
    TITLE_BAR = "TitleBar"
    TOOL_BAR = "ToolBar"
    TOOL_TIP = "ToolTip"
    TREE = "Tree"
    TREE_ITEM = "TreeItem"
    WINDOW = "Window"


class UIADriver(Driver):
    def root(self) -> Optional['UIAElement']:
        app = Application(backend='uia')
        app.connect(handle=self.handle)
        window = app.top_window().wrapper_object()
        return UIAElement(app=app, window=window, driver=self)

    def find_elements(self, *filters: Callable[['UIAElement'], bool], ignore_case: bool = False, **criteria) -> list['UIAElement']:
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
        self._handle: Optional[int] = None
        self._process_id: Optional[int] = None
        self._process_name: Optional[str] = None

    @property
    def handle(self) -> int:
        if not self._handle:
            self._handle = self.info.handle
        return self._handle

    @property
    def process_id(self) -> int:
        if not self._process_id:
            self._process_id = self.info.process_id
        return self._process_id

    @property
    def process_name(self) -> str:
        if not self._process_name:
            from echo import win32
            self._process_name = win32.get_process_name_by_process_id(self.process_id)
        return self._process_name

    @property
    def driver(self) -> UIADriver:
        return self._driver

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
        self._parent = UIAElement(app=self._app, window=parent_window, driver=self._driver, root=self._root, parent=None)
        return self._parent

    def child(self, index: int) -> Optional['UIAElement']:
        children = self._window.children()
        count = len(children)
        if count <= 0 or count <= index:
            return None
        return UIAElement(app=self._app, window=children[index], driver=self._driver, root=self._root, parent=self)

    def children(self, *filters: Callable[['UIAElement'], bool], ignore_case: bool = False, **criteria) -> list['UIAElement']:
        res = []
        for child_window in self._window.children():
            child = UIAElement(app=self._app, window=child_window, driver=self._driver, root=self._root, parent=self)
            if filters or criteria:
                matched = child.matches(*filters, ignore_case=ignore_case, **criteria)
                if matched:
                    res.append(child)
            else:
                res.append(child)
        return res

    def previous(self) -> Optional['UIAElement']:
        parent = self.parent()
        children_in_children = parent.children()
        for i in range(len(children_in_children)):
            if children_in_children[i]._window == self._window:
                if i > 0:
                    return children_in_children[i - 1]
                else:
                    return None
        return None

    def next(self) -> Optional['UIAElement']:
        parent = self.parent()
        children_in_children = parent.children()
        size = len(children_in_children)
        for i in range(size):
            if children_in_children[i]._window == self._window:
                if i < size:
                    return children_in_children[i + 1]
                else:
                    return None
        return None

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
            "automation_id": STR_EXPRS,
            "class_name": STR_EXPRS,
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
        return f"role: {self.role}, " \
               f"name: {self.name}, " \
               f"description: {self.description}, " \
               f"automation_id: {self.automation_id}, " \
               f"class_name: {self.class_name}, " \
               f"rectangle: {self.rectangle}, " \
               f"text: {self.text}, " \
               f"visible: {self.visible}, " \
               f"checked: {self.checked}, " \
               f"enabled: {self.enabled}, " \
               f"selected: {self.selected}, " \
               f"depth: {self.depth}"
