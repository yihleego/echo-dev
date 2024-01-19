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


from abc import ABC, abstractmethod
from ctypes import create_unicode_buffer
from enum import Enum
from functools import cached_property

from echo.core.driver import Driver, Element, matches, STR_EXPRS, INT_EXPRS, BOOL_EXPRS
from .jablib import *


class Role(str, Enum):
    ALERT = "alert"
    CANVAS = "canvas"
    CHECK_BOX = "check box"
    COLOR_CHOOSER = "color chooser"
    COLUMN_HEADER = "column header"
    COMBO_BOX = "combo box"
    DATE_EDITOR = "date editor"
    DESKTOP_ICON = "desktop icon"
    DESKTOP_PANE = "desktop pane"
    DIALOG = "dialog"
    DIRECTORY_PANE = "directory pane"
    EDIT_BAR = "edit bar"
    FILE_CHOOSER = "file chooser"
    FILLER = "filler"
    FONT_CHOOSER = "font chooser"
    FOOTER = "footer"
    FRAME = "frame"
    GLASS_PANE = "glass pane"
    GROUP_BOX = "group box"
    HEADER = "header"
    HYPERLINK = "hyperlink"
    ICON = "icon"
    INTERNAL_FRAME = "internal frame"
    LABEL = "label"
    LAYERED_PANE = "layered pane"
    LIST = "list"
    LIST_ITEM = "list item"
    MENU = "menu"
    MENU_BAR = "menu bar"
    MENU_ITEM = "menu item"
    OPTION_PANE = "option pane"
    PAGE_TAB = "page tab"
    PAGE_TAB_LIST = "page tab list"
    PANEL = "panel"
    PARAGRAPH = "paragraph"
    PASSWORD_TEXT = "password text"
    POPUP_MENU = "popup menu"
    PROGRESS_BAR = "progress bar"
    PUSH_BUTTON = "push button"
    RADIO_BUTTON = "radio button"
    ROOT_PANE = "root pane"
    ROW_HEADER = "row header"
    RULER = "ruler"
    SCROLL_BAR = "scroll bar"
    SCROLL_PANE = "scroll pane"
    SEPARATOR = "separator"
    SLIDER = "slider"
    SPIN_BOX = "spinbox"
    SPLIT_PANE = "split pane"
    STATUS_BAR = "status bar"
    TABLE = "table"
    TEXT = "text"
    TOGGLE_BUTTON = "toggle button"
    TOOL_BAR = "tool bar"
    TOOL_TIP = "tool tip"
    TREE = "tree"
    UNKNOWN = "unknown"
    VIEW_PORT = "viewport"
    WINDOW = "window"


class State(str, Enum):
    ACTIVE = "active"
    CHECKED = "checked"
    COLLAPSED = "collapsed"
    EDITABLE = "editable"
    ENABLED = "enabled"
    FOCUSABLE = "focusable"
    FOCUSED = "focused"
    HORIZONTAL = "horizontal"
    MODAL = "modal"
    MULTIPLELINE = "multiple line"
    MULTISELECTABLE = "multiselectable"
    OPAQUE = "opaque"
    RESIZABLE = "resizable"
    SELECTABLE = "selectable"
    SELECTED = "selected"
    SHOWING = "showing"
    SINGLELINE = "single line"
    VERTICAL = "vertical"
    VISIBLE = "visible"


class JABDriver(Driver):
    def __init__(self, handle: int, process_id: int = None, process_name: str = None):
        super().__init__(handle, process_id, process_name)
        self._lib = JABLib()

    def root(self) -> Optional['JABElement']:
        if self._lib.isJavaWindow(HWND(self.handle)):
            vmid = c_long()
            ctx = AccessibleContext()
            if self._lib.getAccessibleContextFromHWND(HWND(self.handle), vmid, ctx) != 0:
                return JABElement(lib=self._lib, vmid=vmid, ctx=ctx, driver=self)
        return None

    def find_elements(self, *filters: Callable[['JABElement'], bool], ignore_case: bool = False, **criteria) -> list['JABElement']:
        root = self.root()
        if root is None:
            return []
        return root.find_elements(*filters, ignore_case=ignore_case, include_self=True, **criteria)

    def find_element(self, *filters: Callable[['JABElement'], bool], ignore_case: bool = False, **criteria) -> Optional['JABElement']:
        root = self.root()
        if root is None:
            return None
        return root.find_element(*filters, ignore_case=ignore_case, include_self=True, **criteria)

    def close(self):
        # if self._lib:
        #     self._lib.stop()
        pass


class JABElementProperties(ABC):
    @property
    @abstractmethod
    def info(self) -> AccessibleContextInfo:
        raise NotImplementedError

    @property
    @abstractmethod
    def text(self) -> Optional[str]:
        raise NotImplementedError

    @property
    @abstractmethod
    def children_count(self) -> int:
        raise NotImplementedError

    @property
    @abstractmethod
    def depth(self) -> int:
        raise NotImplementedError

    @property
    def role(self) -> str:
        return self.info.role_en_US

    @property
    def name(self) -> str:
        return self.info.name

    @property
    def description(self) -> str:
        return self.info.description

    @property
    def index_in_parent(self) -> int:
        return int(self.info.indexInParent)

    @property
    def x(self) -> int:
        return int(self.info.x)

    @property
    def y(self) -> int:
        return int(self.info.y)

    @property
    def width(self) -> int:
        return int(self.info.width)

    @property
    def height(self) -> int:
        return int(self.info.height)

    @property
    def position(self) -> tuple[int, int]:
        info = self.info
        return int(info.x), int(info.y)

    @property
    def size(self) -> tuple[int, int]:
        info = self.info
        return int(info.width), int(info.height)

    @property
    def rectangle(self) -> tuple[int, int, int, int]:
        info = self.info
        x, y, w, h = int(info.x), int(info.y), int(info.width), int(info.height)
        return x, y, x + w, y + h  # left, top, right, bottom

    @property
    def states(self) -> list[str]:
        states = self.info.states_en_US
        if not states:
            return []
        return states.split(",")

    @property
    def editable(self) -> bool:
        return State.EDITABLE in self.info.states_en_US

    @property
    def focusable(self) -> bool:
        return State.FOCUSABLE in self.info.states_en_US

    @property
    def resizable(self) -> bool:
        return State.RESIZABLE in self.info.states_en_US

    @property
    def visible(self) -> bool:
        return State.VISIBLE in self.info.states_en_US

    @property
    def selectable(self) -> bool:
        return State.SELECTABLE in self.info.states_en_US

    @property
    def multiselectable(self) -> bool:
        return State.MULTISELECTABLE in self.info.states_en_US

    @property
    def collapsed(self) -> bool:
        return State.COLLAPSED in self.info.states_en_US

    @property
    def checked(self) -> bool:
        # checkbox, radiobutton
        return State.CHECKED in self.info.states_en_US

    @property
    def enabled(self) -> bool:
        return State.ENABLED in self.info.states_en_US

    @property
    def focused(self) -> bool:
        return State.FOCUSED in self.info.states_en_US

    @property
    def selected(self) -> bool:
        return State.SELECTED in self.info.states_en_US

    @property
    def showing(self) -> bool:
        return State.SHOWING in self.info.states_en_US

    def __str__(self) -> str:
        return f"role: {self.role}, " \
               f"name: {self.name}, " \
               f"description: {self.description}, " \
               f"rectangle: {self.rectangle}, " \
               f"states: {self.states}, " \
               f"index_in_parent: {self.index_in_parent}, " \
               f"children_count: {self.children_count}, " \
               f"depth: {self.depth}"


class JABElementSnapshot(JABElementProperties):
    def __init__(self, elem):
        self._elem: JABElement = elem

    @cached_property
    def info(self) -> Optional[AccessibleContextInfo]:
        return self._elem.info

    @cached_property
    def text(self) -> Optional[str]:
        return self._elem.text

    @cached_property
    def children_count(self) -> int:
        return self._elem.children_count

    @cached_property
    def depth(self) -> int:
        return self._elem.depth

    def root(self) -> 'JABElementSnapshot':
        return self._elem.root().snapshot()

    def parent(self) -> Optional['JABElementSnapshot']:
        parent = self._elem.parent()
        return parent.snapshot() if parent else None

    def children(self) -> list['JABElementSnapshot']:
        children = self._elem.children()
        return [child.snapshot() for child in children]


class JABElement(JABElementProperties, Element):
    def __init__(self, lib: JABLib, vmid: c_long, ctx: AccessibleContext, driver: JABDriver, root: 'JABElement' = None, parent: 'JABElement' = None):
        self._lib: JABLib = lib
        self._vmid: c_long = vmid
        self._ctx: AccessibleContext = ctx
        self._driver: JABDriver = driver
        self._root: JABElement = root or self  # TODO root
        self._parent: Optional[JABElement] = parent
        self._released: bool = False

    @property
    def driver(self) -> JABDriver:
        return self._driver

    @property
    def vmid(self) -> c_long:
        return self._vmid

    @property
    def accessible_context(self) -> AccessibleContext:
        return self._ctx

    @property
    def info(self) -> Optional[AccessibleContextInfo]:
        aci = AccessibleContextInfo()
        res = self._lib.getAccessibleContextInfo(self._vmid, self._ctx, aci)
        if not res:
            raise Exception("failed to get info")
        return aci

    @property
    def text(self) -> Optional[str]:
        if not self.info.accessibleText:
            return None
        ati = AccessibleTextInfo()
        res = self._lib.getAccessibleTextInfo(self._vmid, self._ctx, ati, c_int(0), c_int(0))
        if not res:
            return None
        if ati.charCount <= 0:
            return ""
        chars_len = ati.charCount
        chars_start = c_int(0)
        chars_end = chars_len - 1
        buffer = create_unicode_buffer(ati.charCount)
        res = self._lib.getAccessibleTextRange(self._vmid, self._ctx, chars_start, chars_end, buffer, chars_len)
        if not res:
            return None
        return buffer.value

    @property
    def depth(self) -> int:
        return self._lib.getObjectDepth(self._vmid, self._ctx)

    def root(self) -> 'JABElement':
        return self._root

    def parent(self) -> Optional['JABElement']:
        # the root does not have a parent
        if self.depth == 0:
            return None
        # return if parent exists and is not released
        if self._parent is not None and not self._parent._released:
            return self._parent
        # get parent from context
        parent_ctx = self._lib.getAccessibleParentFromContext(self._vmid, self._ctx)
        if parent_ctx == 0:
            return None
        parent_ctx = AccessibleContext(parent_ctx)
        self._parent = JABElement(lib=self._lib, vmid=self._vmid, ctx=parent_ctx, driver=self._driver, root=self._root, parent=None)
        return self._parent

    def child(self, index: int) -> Optional['JABElement']:
        ctx = self._lib.getAccessibleChildFromContext(self._vmid, self._ctx, c_int(index))
        if ctx == 0:
            return None
        ctx = AccessibleContext(ctx)
        return JABElement(lib=self._lib, vmid=self._vmid, ctx=ctx, driver=self._driver, root=self._root, parent=self)

    def children(self, *filters: Callable[[JABElementSnapshot], bool], ignore_case: bool = False, **criteria) -> list['JABElement']:
        res = []
        count = self.children_count
        for index in range(count):
            ctx = self._lib.getAccessibleChildFromContext(self._vmid, self._ctx, c_int(index))
            if ctx == 0:
                continue
            ctx = AccessibleContext(ctx)
            child = JABElement(lib=self._lib, vmid=self._vmid, ctx=ctx, driver=self._driver, root=self._root, parent=self)
            if filters or criteria:
                matched = child.matches(*filters, ignore_case=ignore_case, **criteria)
                if matched:
                    res.append(child)
                else:
                    child.release()
            else:
                res.append(child)
        return res

    def previous(self) -> Optional['JABElement']:
        parent = self.parent()
        return parent.child(self.index_in_parent - 1) if parent is not None else None

    def next(self) -> Optional['JABElement']:
        parent = self.parent()
        return parent.child(self.index_in_parent + 1) if parent is not None else None

    @property
    def children_count(self) -> int:
        return self.info.childrenCount

    def click(self, button="left") -> bool:
        # TODO I don't know why 'click' does not work
        res = self._do_action(action_names=['单击', 'click'])
        if res:
            return res
        # fallback
        self.simulate_click(button)
        return True

    def input(self, text: str) -> bool:
        res = self._lib.setTextContents(self._vmid, self._ctx, c_wchar_p(text))
        return bool(res)

    def set_focus(self) -> bool:
        res = self._lib.requestFocus(self._vmid, self._ctx)
        return bool(res)

    def matches(self, *filters: Callable[[JABElementSnapshot], bool], ignore_case=False, **criteria) -> bool:
        """
        Match element by criteria.
        :param filters: filters
        :param ignore_case: two strings are considered equal ignoring case
        :key role: role == value
        :key role_not: role != value
        :key role_like: role like *value*
        :key role_in: role in [value1, value2]
        :key role_in_like: role in like [*value1*, *value2*]
        :key role_regex: role regex pattern (str)
        :key role_null: role is None (bool)
        :key name: name == value
        :key name_not: name != value
        :key name_like: name like *value*
        :key name_in: name in [value1, value2]
        :key name_in_like: name in like [*value1*, *value2*]
        :key name_regex: name regex pattern (str)
        :key name_null: name is None (bool)
        :key description: description == value
        :key description_not: description != value
        :key description_like: description like *value*
        :key description_in: description in [value1, value2]
        :key description_in_like: description in like [*value1*, *value2*]
        :key description_regex: description regex pattern (str)
        :key description_null: description is None (bool)
        :key text: text == value
        :key text_not: text != value
        :key text_like: text like *value*
        :key text_in: text in [value1, value2]
        :key text_in_like: text in like [*value1*, *value2*]
        :key text_regex: text regex pattern (str)
        :key text_null: text is None (bool)
        :key x: x == value
        :key x_not: x != value
        :key x_gt: x > value
        :key x_gte: x >= value
        :key x_lt: x < value
        :key x_lte: x <= value
        :key x_null: x is None (bool)
        :key y: y == value
        :key y_not: y != value
        :key y_gt: y > value
        :key y_gte: y >= value
        :key y_lt: y < value
        :key y_lte: y <= value
        :key y_null: y is None (bool)
        :key width: width == value
        :key width_not: width != value
        :key width_gt: width > value
        :key width_gte: width >= value
        :key width_lt: width < value
        :key width_lte: width <= value
        :key width_null: width is None (bool)
        :key height: height == value
        :key height_not: height != value
        :key height_gt: height > value
        :key height_gte: height >= value
        :key height_lt: height < value
        :key height_lte: height <= value
        :key height_null: height is None (bool)
        :key editable: editable == value
        :key editable_not: editable != value
        :key editable_null: editable is None (bool)
        :key focusable: focusable == value
        :key focusable_not: focusable != value
        :key focusable_null: focusable is None (bool)
        :key resizable: resizable == value
        :key resizable_not: resizable != value
        :key resizable_null: resizable is None (bool)
        :key visible: visible == value
        :key visible_not: visible != value
        :key visible_null: visible is None (bool)
        :key selectable: selectable == value
        :key selectable_not: selectable != value
        :key selectable_null: selectable is None (bool)
        :key multiselectable: multiselectable == value
        :key multiselectable_not: multiselectable != value
        :key multiselectable_null: multiselectable is None (bool)
        :key collapsed: collapsed == value
        :key collapsed_not: collapsed != value
        :key collapsed_null: collapsed is None (bool)
        :key checked: checked == value
        :key checked_not: checked != value
        :key checked_null: checked is None (bool)
        :key enabled: enabled == value
        :key enabled_not: enabled != value
        :key enabled_null: enabled is None (bool)
        :key focused: focused == value
        :key focused_not: focused != value
        :key focused_null: focused is None (bool)
        :key selected: selected == value
        :key selected_not: selected != value
        :key selected_null: selected is None (bool)
        :key showing: showing == value
        :key showing_not: showing != value
        :key showing_null: showing is None (bool)
        :key index_in_parent: index_in_parent == value
        :key index_in_parent_not: index_in_parent != value
        :key index_in_parent_gt: index_in_parent > value
        :key index_in_parent_gte: index_in_parent >= value
        :key index_in_parent_lt: index_in_parent < value
        :key index_in_parent_lte: index_in_parent <= value
        :key index_in_parent_null: index_in_parent is None (bool)
        :key children_count: children_count == value
        :key children_count_not: children_count != value
        :key children_count_gt: children_count > value
        :key children_count_gte: children_count >= value
        :key children_count_lt: children_count < value
        :key children_count_lte: children_count <= value
        :key children_count_null: children_count is None (bool)
        :key depth: depth == value
        :key depth_not: depth != value
        :key depth_gt: depth > value
        :key depth_gte: depth >= value
        :key depth_lt: depth < value
        :key depth_lte: depth <= value
        :key depth_null: depth is None (bool)
        """
        snapshot = self.snapshot()
        rules = {
            "role": STR_EXPRS,
            "name": STR_EXPRS,
            "description": STR_EXPRS,
            "text": STR_EXPRS,
            "x": INT_EXPRS,
            "y": INT_EXPRS,
            "width": INT_EXPRS,
            "height": INT_EXPRS,
            "editable": BOOL_EXPRS,
            "focusable": BOOL_EXPRS,
            "resizable": BOOL_EXPRS,
            "visible": BOOL_EXPRS,
            "selectable": BOOL_EXPRS,
            "multiselectable": BOOL_EXPRS,
            "collapsed": BOOL_EXPRS,
            "checked": BOOL_EXPRS,
            "enabled": BOOL_EXPRS,
            "focused": BOOL_EXPRS,
            "selected": BOOL_EXPRS,
            "showing": BOOL_EXPRS,
            "index_in_parent": INT_EXPRS,
            "children_count": INT_EXPRS,
            "depth": INT_EXPRS,
        }
        return matches(snapshot, filters, rules, ignore_case, **criteria)

    def find_all_elements(self) -> list['JABElement']:
        found = [self]
        children = self.children()
        for child in children:
            found.extend(child.find_all_elements())
        return found

    def find_elements(self, *filters: Callable[['JABElement'], bool], ignore_case: bool = False, include_self=False, **criteria) -> list['JABElement']:
        # return empty list if no filters or criteria
        if len(filters) == 0 and len(criteria) == 0:
            return []
        found = []
        releasing = []
        if include_self:
            if self.matches(*filters, ignore_case=ignore_case, **criteria):
                found.append(self)
        children = self.children()
        for child in children:
            matched = child.matches(*filters, ignore_case=ignore_case, **criteria)
            if matched:
                found.append(child)
            else:
                releasing.append(child)
            # looking for deep elements
            found.extend(child.find_elements(*filters, ignore_case=ignore_case, include_self=False, **criteria))
        # release all mismatched elements
        for child in releasing:
            child.release()
        return found

    def find_element(self, *filters: Callable[['JABElement'], bool], ignore_case: bool = False, include_self=False, **criteria) -> Optional['JABElement']:
        # return None if no filters or criteria
        if len(filters) == 0 and len(criteria) == 0:
            return None
        if include_self:
            if self.matches(*filters, ignore_case=ignore_case, **criteria):
                return self
        found = None
        releasing = []
        children = self.children()
        for child in children:
            matched = child.matches(*filters, ignore_case=ignore_case, **criteria)
            if matched:
                found = child
                break
            else:
                releasing.append(child)
        # looking for deep elements if not found
        if not found:
            for child in children:
                found = child.find_element(*filters, ignore_case=ignore_case, include_self=False, **criteria)
                if found:
                    break
        # release all mismatched elements
        for child in releasing:
            child.release()
        return found

    def snapshot(self) -> JABElementSnapshot:
        return JABElementSnapshot(self)

    def release(self):
        self._lib.releaseJavaObject(self._vmid, self._ctx)
        self._released = True

    def _do_action(self, action_names: list[str]) -> bool:
        aa = AccessibleActions()
        res = self._lib.getAccessibleActions(self._vmid, self._ctx, aa)
        if not res:
            return False
        for index in range(aa.actionsCount):
            name = aa.actionInfo[index].name
            if name not in action_names:
                continue
            aatd = AccessibleActionsToDo()
            aatd.actions[0].name = name
            aatd.actionsCount = 1
            failure = c_int(0)
            res = self._lib.doAccessibleActions(self._vmid, self._ctx, aatd, failure)
            if res and failure.value == -1:
                return True
        return False
