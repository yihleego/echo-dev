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
from ctypes import create_string_buffer
from enum import Enum
from functools import cached_property

from echo.driver import Driver, Element
from echo.utils import to_string, matches, STR_EXPRS, INT_EXPRS, BOOL_EXPRS
from .jab import *


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
        return JABElement.create_root(lib=self._lib, driver=self)

    def find_elements(self, *filters: Callable[['JABElement'], bool], ignore_case: bool = False, **criteria) -> list['JABElement']:
        root = self.root()
        if root is None:
            return []
        return root.find_elements(*filters, ignore_case=ignore_case, include_self=True, **criteria)

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
        return to_string(self, 'role', 'name', 'description', 'index_in_parent',
                         'rectangle', 'states', 'text', 'children_count', 'depth')


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

    @staticmethod
    def create_root(lib: JABLib, driver: JABDriver) -> Optional['JABElement']:
        handle = driver.handle
        if lib.isJavaWindow(HWND(handle)):
            vmid = c_long()
            ctx = AccessibleContext()
            if lib.getAccessibleContextFromHWND(HWND(handle), vmid, ctx):
                return JABElement(lib=lib, vmid=vmid, ctx=ctx, driver=driver)
        return None

    @staticmethod
    def create_element(ctx: AccessibleContext, root: 'JABElement', parent: 'JABElement' = None) -> 'JABElement':
        return JABElement(lib=root._lib, vmid=root._vmid, ctx=ctx, driver=root._driver, root=root, parent=parent)

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
        chars_start = c_int(0)
        chars_end = ati.charCount - 1
        chars_len = ati.charCount
        buffer = create_string_buffer((chars_len + 1) * 2)
        res = self._lib.getAccessibleTextRange(self._vmid, self._ctx, chars_start, chars_end, buffer, chars_len)
        if not res:
            return None
        return buffer[:chars_len * 2].decode("utf_16", errors="replace")

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
        self._parent = JABElement.create_element(ctx=parent_ctx, root=self._root)
        return self._parent

    def child(self, index: int) -> Optional['JABElement']:
        ctx = self._lib.getAccessibleChildFromContext(self._vmid, self._ctx, c_int(index))
        if ctx == 0:
            return None
        ctx = AccessibleContext(ctx)
        return JABElement.create_element(ctx=ctx, root=self._root, parent=self)

    def children(self, *filters: Callable[[JABElementSnapshot], bool], ignore_case: bool = False, **criteria) -> list['JABElement']:
        res = []
        count = self.children_count
        for index in range(count):
            ctx = self._lib.getAccessibleChildFromContext(self._vmid, self._ctx, c_int(index))
            ctx = AccessibleContext(ctx)
            child = JABElement.create_element(ctx=ctx, root=self._root, parent=self)
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

    def click(self, button="left", simulate=False) -> bool:
        # TODO I don't know why 'click' does not work
        return self._do_action(action_names=['单击', 'click'])

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
        :key index_in_parent: index in parent equals
        :key text: text equals
        :key text_like: text contains
        :key text_in: text in list
        :key text_in_like: text contains in list
        :key text_regex: text regex
        :key editable: state editable
        :key focusable: state focusable
        :key resizable: state resizable
        :key visible: state visible
        :key selectable: state selectable
        :key multiselectable: state multiselectable
        :key collapsed: state collapsed
        :key checked: state checked
        :key enabled: state enabled
        :key focused: state focused
        :key selected: state selected
        :key showing: state showing
        :key children_count: children count equals
        :key depth: depth equals
        :return: True if matched
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
            "index_in_parent": INT_EXPRS,
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
            if res and failure:
                return True
        return False
