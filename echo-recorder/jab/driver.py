import os
import platform
import shutil
import subprocess
from ctypes import create_string_buffer
from ctypes.wintypes import HWND, HANDLE
from enum import Enum
from typing import Union, Optional

import pyperclip

from .calls import JAB
from .packages import *


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


class JABElement:
    def __init__(self, jab: JAB, handle: Union[int, HWND, HANDLE], vmid: c_long, ctx: AccessibleContext, is_root, root: 'JABElement' = None):
        self._jab: JAB = jab
        self._handle: Union[int, HWND, HANDLE] = handle
        self._vmid: c_long = vmid
        self._ctx: AccessibleContext = ctx
        if is_root or root == self:
            self._root: JABElement = self
            self._is_root: bool = True
        else:
            self._root: JABElement = root
            self._is_root: bool = False
        self._parent: Optional[JABElement] = None

    @property
    def root(self) -> 'JABElement':
        return self._root

    @property
    def parent(self) -> Optional['JABElement']:
        # the root does not have a parent
        if self._is_root:
            return None
        # return if parent exists
        if self._parent is not None:
            return self._parent
        # get parent from context
        parent_ctx = self._jab.getAccessibleParentFromContext(self._vmid, self._ctx)
        if parent_ctx != 0:
            self._parent = JABElement(jab=self._jab, handle=self._handle, vmid=self._vmid, ctx=parent_ctx, is_root=False, root=self._root)
        return self._parent

    @property
    def vmid(self) -> c_long:
        return self._vmid

    @property
    def accessible_context(self) -> AccessibleContext:
        return self._ctx

    @property
    def info(self) -> AccessibleContextInfo:
        aci = AccessibleContextInfo()
        res = self._jab.getAccessibleContextInfo(self._vmid, self._ctx, aci)
        return aci

    @property
    def name(self) -> str:
        return self.info.name

    @property
    def description(self) -> str:
        return self.info.description

    @property
    def role(self) -> str:
        return self.info.role_en_US

    @property
    def states(self) -> list[str]:
        return self.info.states_en_US

    @property
    def index_in_parent(self) -> int:
        return self.info.indexInParent

    @property
    def children_count(self) -> int:
        return self.info.childrenCount

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
    def rect(self) -> tuple[int, int, int, int]:
        x, y, w, h = self.x, self.y, self.width, self.height
        return x, y, x + w, y + h

    @property
    def text(self) -> Optional[str]:
        if not self.info.accessibleText:
            return None
        ati = AccessibleTextInfo()
        res = self._jab.getAccessibleTextInfo(self._vmid, self._ctx, ati)
        if not res:
            return None
        chars_start = c_int(0)
        chars_end = ati.charCount - 1
        chars_len = ati.charCount
        if chars_len == 0:
            return ""
        buffer = create_string_buffer((chars_len + 1) * 2)
        res = self._jab.getAccessibleTextRange(self._vmid, self._ctx, chars_start, chars_end, buffer, chars_len)
        if not res:
            return None
        return buffer[:chars_len * 2].decode("utf_16", errors="replace")

    @property
    def value(self) -> Optional[str]:
        if not self.info.accessibleValue:
            return None

    def click(self):
        return self._do_action(action_names=['单击', 'click'])

    def input(self, text: str, set_foreground=True) -> bool:
        pyperclip.copy(text)
        pyperclip.paste()
        pyperclip.copy("")
        return True

    def _do_action(self, action_names: list[str]) -> bool:
        if not self.info.accessibleAction:
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

    def child(self, index: int) -> Optional['JABElement']:
        count = self._jab.getVisibleChildrenCount(self._vmid, self._ctx)
        if count <= 0 or count <= index:
            return None
        vci = VisibleChildrenInfo()
        res = self._jab.getVisibleChildren(self._vmid, self._ctx, 0, vci)
        if not res or vci.returnedChildrenCount <= 0 or vci.returnedChildrenCount <= index:
            return None
        ctx = AccessibleContext(vci.children[index])
        return JABElement(jab=self._jab, handle=self._handle, vmid=self._vmid, ctx=ctx, is_root=False, root=self._root)

    def children(self) -> list['JABElement']:
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
            res.append(JABElement(jab=self._jab, handle=self._handle, vmid=self._vmid, ctx=ctx, is_root=False, root=self._root))
        return res

    def matches(self, role: str = None, name: str = None, states: list[str] = None, description: str = None, text: str = None, value: str = None) -> bool:
        return (role is not None and role == self.role) \
            or (name is not None and name == self.name) \
            or (states is not None and set(states).issubset(set(self.states))) \
            or (description is not None and description == self.description) \
            or (text is not None and text == self.text) \
            or (value is not None and value == self.value)

    def find_elements(self, role: str = None, name: str = None, states: str = None, description: str = None, text: str = None, value: str = None) -> list['JABElement']:
        res = []
        if self.matches(role=role, name=name, states=states, description=description, text=text, value=value):
            res.append(self)
        children = self.children()
        for child in children:
            res.extend(child.find_elements(role=role, name=name, states=states, description=description, text=text, value=value))
        return res

    def find_element(self, role: str = None, name: str = None, states: str = None, description: str = None, text: str = None, value: str = None) -> Optional['JABElement']:
        if self.matches(role=role, name=name, states=states, description=description, text=text, value=value):
            return self
        children = self.children()
        for child in children:
            found = child.find_element(role=role, name=name, states=states, description=description, text=text, value=value)
            if found:
                return found
        return None

    @staticmethod
    def build(jab: JAB, handle: Union[int, HWND, HANDLE]) -> Optional['JABElement']:
        if jab.isJavaWindow(handle):
            vmid = c_long()
            ctx = AccessibleContext()
            if jab.getAccessibleContextFromHWND(handle, vmid, ctx):
                return JABElement(jab=jab, handle=handle, vmid=vmid, ctx=ctx, is_root=True)
        return None


class JABDriver:
    def __init__(self):
        self._dll_path = self._init()
        self._jab = JAB(self._dll_path)

    def _init(self):
        # https://docs.oracle.com/javase/accessbridge/2.0.2/setup.htm
        os_arch = platform.architecture()[0][:2]  # 32 or 64
        jab_version = "2.0.2"
        jab_lib_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), f"javaaccessbridge{jab_version}")
        system_root_dir = _get_system_root_dir()
        java_home_dir = _get_java_home_dir()
        paths = {
            f"WindowsAccessBridge-{os_arch}.dll": os.path.join(system_root_dir, "System32"),
            f"JavaAccessBridge-{os_arch}.dll": os.path.join(java_home_dir, "bin"),
            f"JAWTAccessBridge-{os_arch}.dll": os.path.join(java_home_dir, "bin"),
            f"accessibility.properties": os.path.join(java_home_dir, "lib"),
            f"access-bridge-{os_arch}.jar": os.path.join(java_home_dir, "lib", "ext"),
            f"jaccess.jar": os.path.join(java_home_dir, "lib", "ext"),
        }
        for fn, dst in paths.items():
            if not os.path.exists(os.path.join(dst, fn)):
                shutil.copy(os.path.join(jab_lib_dir, fn), os.path.join(dst, fn))
        return os.path.join(system_root_dir, "System32", f"WindowsAccessBridge-{os_arch}.dll")

    def find_window(self, handle: Union[int, HWND, HANDLE]) -> Optional[JABElement]:
        return JABElement.build(jab=self._jab, handle=handle)


def _get_system_root_dir():
    return os.environ.get("SYSTEMROOT")


def _get_java_home_dir() -> Optional[str]:
    java_home_dir = os.environ.get("JAVA_HOME")
    if java_home_dir:
        return java_home_dir
    process = subprocess.Popen(['java', '-XshowSettings:properties', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    decoded = (stdout or stderr).decode('utf-8')
    lines = decoded.splitlines()
    for line in lines:
        if line.strip().startswith("java.home"):
            return line.split("=")[1].strip()
    return None
