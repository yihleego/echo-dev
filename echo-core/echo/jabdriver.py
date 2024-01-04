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

from abc import ABC, abstractmethod
from ctypes import create_string_buffer, c_wchar_p, c_int, c_long
from ctypes.wintypes import HWND
from enum import Enum
from functools import cached_property
from typing import Optional, Callable

from .driver import Driver, Element
from .jab import *
from .utils import win32, to_string


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
        return JABElementSnapshot(self._elem.root())

    def parent(self) -> Optional['JABElementSnapshot']:
        parent = self._elem.parent()
        return JABElementSnapshot(parent) if parent else None

    def children(self) -> list['JABElementSnapshot']:
        children = self._elem.children()
        return [JABElementSnapshot(child) for child in children]


class JABElement(JABElementProperties, Element):
    def __init__(self, jab: JAB, vmid: c_long, ctx: AccessibleContext, handle: int, process_id: int, process_name: str, root: 'JABElement' = None, parent: 'JABElement' = None):
        self._jab: JAB = jab
        self._vmid: c_long = vmid
        self._ctx: AccessibleContext = ctx
        self._handle: int = handle
        self._process_id: int = process_id
        self._process_name: str = process_name
        self._root: JABElement = root or self  # TODO
        self._parent: Optional[JABElement] = parent
        self._released: bool = False

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
    def vmid(self) -> c_long:
        return self._vmid

    @property
    def accessible_context(self) -> AccessibleContext:
        return self._ctx

    @property
    def info(self) -> Optional[AccessibleContextInfo]:
        aci = AccessibleContextInfo()
        res = self._jab.getAccessibleContextInfo(self._vmid, self._ctx, aci)
        return aci

    @property
    def text(self) -> Optional[str]:
        if not self.info.accessibleText:
            return None
        ati = AccessibleTextInfo()
        res = self._jab.getAccessibleTextInfo(self._vmid, self._ctx, ati)
        if not res:
            return None
        if ati.charCount <= 0:
            return ""
        chars_start = c_int(0)
        chars_end = ati.charCount - 1
        chars_len = ati.charCount
        buffer = create_string_buffer((chars_len + 1) * 2)
        res = self._jab.getAccessibleTextRange(self._vmid, self._ctx, chars_start, chars_end, buffer, chars_len)
        if not res:
            return None
        return buffer[:chars_len * 2].decode("utf_16", errors="replace")

    @property
    def depth(self) -> int:
        return self._jab.getObjectDepth(self._vmid, self._ctx)

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
        parent_ctx = self._jab.getAccessibleParentFromContext(self._vmid, self._ctx)
        if parent_ctx == 0:
            return None
        self._parent = JABElement.create_element(ctx=parent_ctx, root=self._root)
        return self._parent

    def child(self, index: int) -> Optional['JABElement']:
        count = self.children_count
        if count <= 0 or count <= index:
            return None
        vci = VisibleChildrenInfo()
        res = self._jab.getVisibleChildren(self._vmid, self._ctx, 0, vci)
        if not res or vci.returnedChildrenCount <= 0 or vci.returnedChildrenCount <= index:
            return None
        ctx = AccessibleContext(vci.children[index])
        return JABElement.create_element(ctx=ctx, root=self._root, parent=self)

    def children(self, *filters: Callable[[JABElementSnapshot], bool], **criteria) -> list['JABElement']:
        count = self._jab.getVisibleChildrenCount(self._vmid, self._ctx)
        if count <= 0:
            return []
        vci = VisibleChildrenInfo()
        res = self._jab.getVisibleChildren(self._vmid, self._ctx, 0, vci)
        if not res or vci.returnedChildrenCount <= 0:
            return []
        res = []
        for idx in range(vci.returnedChildrenCount):
            ctx = AccessibleContext(vci.children[idx])
            child = JABElement.create_element(ctx=ctx, root=self._root, parent=self)
            if filters or criteria:
                matched = child.matches(*filters, **criteria)
                if matched:
                    res.append(child)
            else:
                res.append(child)
        return res

    @property
    def children_count(self) -> int:
        return self._jab.getVisibleChildrenCount(self._vmid, self._ctx)

    def click(self, button="left") -> bool:
        # TODO I don't know why 'click' does not work
        return self._do_action(action_names=['单击', 'click'])

    def input(self, text: str) -> bool:
        res = self._jab.setTextContents(self._vmid, self._ctx, c_wchar_p(text))
        return bool(res)

    def set_focus(self) -> bool:
        res = self._jab.requestFocus(self._vmid, self._ctx)
        return bool(res)

    def matches(self, *filters: Callable[[JABElementSnapshot], bool], **criteria) -> bool:
        """
        Match element by criteria.
        :param filters: filters
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
        snapshot = JABElementSnapshot(self)
        rules = {
            "role": ("role", ["eq", "like", "in", "in_like", "regex"]),
            "name": ("name", ["eq", "like", "in", "in_like", "regex"]),
            "description": ("description", ["eq", "like", "in", "in_like", "regex"]),
            "x": ("x", ["eq", "gt", "gte", "lt", "lte"]),
            "y": ("y", ["eq", "gt", "gte", "lt", "lte"]),
            "width": ("width", ["eq", "gt", "gte", "lt", "lte"]),
            "height": ("height", ["eq", "gt", "gte", "lt", "lte"]),
            "index_in_parent": ("index_in_parent", ["eq", "gt", "gte", "lt", "lte"]),
            "text": ("text", ["eq", "like", "in", "in_like", "regex"]),
            "editable": ("editable", ["eq"]),
            "focusable": ("focusable", ["eq"]),
            "resizable": ("resizable", ["eq"]),
            "visible": ("visible", ["eq"]),
            "selectable": ("selectable", ["eq"]),
            "multiselectable": ("multiselectable", ["eq"]),
            "collapsed": ("collapsed", ["eq"]),
            "checked": ("checked", ["eq"]),
            "enabled": ("enabled", ["eq"]),
            "focused": ("focused", ["eq"]),
            "selected": ("selected", ["eq"]),
            "showing": ("showing", ["eq"]),
            "children_count": ("children_count", ["eq", "gt", "gte", "lt", "lte"]),
            "depth": ("depth", ["eq", "gt", "gte", "lt", "lte"]),
        }
        return self._matches(snapshot, rules, *filters, **criteria)

    def find_all_elements(self) -> list['JABElement']:
        found = [self]
        children = self.children()
        for child in children:
            found.extend(child.find_all_elements())
        return found

    def find_elements(self, *filters: Callable[['JABElement'], bool], **criteria) -> list['JABElement']:
        # return empty list if no filters or criteria
        if len(filters) == 0 and len(criteria) == 0:
            return []
        found = []
        releasing = []
        children = self.children()
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

    def find_element(self, *filters: Callable[['JABElement'], bool], **criteria) -> Optional['JABElement']:
        # return None if no filters or criteria
        if len(filters) == 0 and len(criteria) == 0:
            return None
        found = None
        releasing = []
        children = self.children()
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

    def release(self):
        self._jab.releaseJavaObject(self._vmid, self._ctx)
        self._released = True

    def _do_action(self, action_names: list[str]) -> bool:
        if not action_names or not self.info.accessibleAction:
            return False
        aa = AccessibleActions()
        res = self._jab.getAccessibleActions(self._vmid, self._ctx, aa)
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
            res = self._jab.doAccessibleActions(self._vmid, self._ctx, aatd, failure)
            if res and failure:
                return True
        return False

    @staticmethod
    def create_root(jab: JAB, handle: int) -> Optional['JABElement']:
        process_id = win32.get_process_id_from_handle(handle)
        process_name = win32.get_process_name_by_process_id(process_id)
        if jab.isJavaWindow(HWND(handle)):
            vmid = c_long()
            ctx = AccessibleContext()
            if jab.getAccessibleContextFromHWND(HWND(handle), vmid, ctx):
                return JABElement(jab=jab, vmid=vmid, ctx=ctx, handle=handle, process_id=process_id, process_name=process_name)
        return None

    @staticmethod
    def create_element(ctx: AccessibleContext, root: 'JABElement', parent: 'JABElement' = None) -> 'JABElement':
        return JABElement(jab=root._jab, vmid=root._vmid, ctx=ctx, handle=root._handle, process_id=root._process_id, root=root, parent=parent)


class JABDriver(Driver):
    def __init__(self):
        self._jab = JAB()

    def find_window(self, handle: int) -> Optional[JABElement]:
        return JABElement.create_root(jab=self._jab, handle=handle)

    def close(self):
        if self._jab:
            self._jab.stop()