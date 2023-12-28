import os
import platform
import shutil
import subprocess
from ctypes import create_string_buffer, sizeof, byref, c_wchar_p, windll
from ctypes.wintypes import HWND, UINT, POINT, RECT
from typing import Union, Optional

from utils.deprecated import deprecated
from .calls import JAB
from .packages import *

SW_HIDE = 0
SW_SHOWNORMAL = 1
SW_NORMAL = 1
SW_SHOWMINIMIZED = 2
SW_SHOWMAXIMIZED = 3
SW_MAXIMIZE = 3
SW_SHOWNOACTIVATE = 4
SW_SHOW = 5
SW_MINIMIZE = 6
SW_SHOWMINNOACTIVE = 7
SW_SHOWNA = 8
SW_RESTORE = 9
SW_SHOWDEFAULT = 10
SW_FORCEMINIMIZE = 11
SW_MAX = 11


class JABElement:
    def __init__(self, jab: JAB, handle: Union[int, HWND], vmid: c_long, ctx: AccessibleContext, is_root, root: 'JABElement' = None):
        self._jab: JAB = jab
        self._handle: Union[int, HWND] = handle
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
            self._parent = JABElement.create_element(root=self._root, ctx=parent_ctx)
        return self._parent

    @property
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
            res.append(JABElement.create_element(root=self._root, ctx=ctx))
        return res

    @property
    def children_count(self) -> int:
        return self._jab.getVisibleChildrenCount(self._vmid, self._ctx)

    def child(self, index: int) -> Optional['JABElement']:
        count = self._jab.getVisibleChildrenCount(self._vmid, self._ctx)
        if count <= 0 or count <= index:
            return None
        vci = VisibleChildrenInfo()
        res = self._jab.getVisibleChildren(self._vmid, self._ctx, 0, vci)
        if not res or vci.returnedChildrenCount <= 0 or vci.returnedChildrenCount <= index:
            return None
        ctx = AccessibleContext(vci.children[index])
        return JABElement.create_element(root=self._root, ctx=ctx)

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
        return aci if res else None

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
        states = self.info.states_en_US
        if not states:
            return []
        return states.split(",")

    @property
    def enabled(self) -> bool:
        return "enabled" in self.states

    @property
    def focusable(self) -> bool:
        return "focusable" in self.states

    @property
    def visible(self) -> bool:
        return "visible" in self.states

    @property
    def editable(self) -> bool:
        return "editable" in self.states

    @property
    def checked(self) -> bool:
        return "checked" in self.states

    @property
    def showing(self) -> bool:
        return "showing" in self.states

    @property
    def opaque(self) -> bool:
        return "opaque" in self.states

    @property
    def index_in_parent(self) -> int:
        return self.info.indexInParent

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
        return x, y, x + w, y + h

    @property
    def depth(self) -> int:
        return self._jab.getObjectDepth(self._vmid, self._ctx)

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

    @deprecated
    @property
    def value(self) -> Optional[str]:
        raise NotImplemented

    @deprecated
    @property
    def interfaces(self) -> Optional[str]:
        raise NotImplemented

    def screenshot(self, filename: str) -> str:
        # TODO
        pass

    def click(self) -> bool:
        # TODO I don't know why 'click' does not work
        return self._do_action(action_names=['单击', 'click'])

    def input(self, text: str) -> bool:
        res = self._jab.setTextContents(self._vmid, self._ctx, c_wchar_p(text))
        return bool(res)

    def set_focus(self) -> bool:
        res = self._jab.requestFocus(self._vmid, self._ctx)
        return bool(res)

    def set_foreground(self) -> bool:
        self.show()
        res = windll.user32.SetForegroundWindow(self._handle)
        return bool(res)

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
        res = windll.user32.MoveWindow(self._handle, x, y, width, height, repaint)
        if not res:
            return False
        else:
            return True

    def hide(self):
        windll.user32.ShowWindow(self._handle, SW_HIDE)

    def show(self):
        windll.user32.ShowWindow(self._handle, SW_SHOW)

    def maximize(self):
        windll.user32.ShowWindow(self._handle, SW_MAXIMIZE)

    def minimize(self):
        windll.user32.ShowWindow(self._handle, SW_MINIMIZE)

    def restore(self):
        windll.user32.ShowWindow(self._handle, SW_RESTORE)

    def is_minimized(self):
        return self.get_window_state() == SW_SHOWMINIMIZED

    def is_maximized(self):
        return self.get_window_state() == SW_SHOWMAXIMIZED

    def is_normal(self):
        return self.get_window_state() == SW_SHOWNORMAL

    def get_window_state(self):
        # https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getwindowplacement
        class WINDOWPLACEMENT(Structure):
            _fields_ = [
                ('length', UINT),
                ('flags', UINT),
                ('showCmd', UINT),
                ('ptMinPosition', POINT),
                ('ptMaxPosition', POINT),
                ('rcNormalPosition', RECT),
            ]

        wp = WINDOWPLACEMENT()
        wp.length = sizeof(wp)
        windll.user32.GetWindowPlacement(self._handle, byref(wp))
        return wp.showCmd

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

    def matches(self, role: str = None, name: str = None, states: list[str] = None, description: str = None, text: str = None, value: str = None) -> bool:
        info = self.info
        if not info:
            return False
        # TODO value
        return (role is not None and role == info.role) \
            or (name is not None and name == info.name) \
            or (states is not None and set(states).issubset(set(info.states))) \
            or (description is not None and description == info.description) \
            or (text is not None and text == self.text)

    def find_elements(self, role: str = None, name: str = None, states: str = None, description: str = None, text: str = None, value: str = None) -> list['JABElement']:
        found = []
        closed = []
        children = self.children
        for child in children:
            matched = child.matches(role=role, name=name, states=states, description=description, text=text, value=value)
            if matched:
                found.append(child)
            else:
                closed.append(child)
            # looking for deep elements anyway
            found.extend(child.find_elements(role=role, name=name, states=states, description=description, text=text, value=value))
        # close all mismatched elements
        for child in closed:
            child.release()
        return found

    def find_element(self, role: str = None, name: str = None, states: str = None, description: str = None, text: str = None, value: str = None) -> Optional['JABElement']:
        found = None
        closed = []
        children = self.children
        for child in children:
            matched = child.matches(role=role, name=name, states=states, description=description, text=text, value=value)
            if matched:
                found = matched
                break
            else:
                closed.append(child)
        # looking for deep elements if not found
        if not found:
            for child in children:
                found = child.find_element(role=role, name=name, states=states, description=description, text=text, value=value)
                if found:
                    break
        # close all mismatched elements
        for child in closed:
            child.release()
        return found

    def release(self):
        self._jab.releaseJavaObject(self._vmid, self._ctx)

    @staticmethod
    def create_root(jab: JAB, handle: Union[int, HWND]) -> Optional['JABElement']:
        if jab.isJavaWindow(handle):
            vmid = c_long()
            ctx = AccessibleContext()
            if jab.getAccessibleContextFromHWND(handle, vmid, ctx):
                return JABElement(jab=jab, handle=handle, vmid=vmid, ctx=ctx, is_root=True)
        return None

    @staticmethod
    def create_element(root: 'JABElement', ctx: AccessibleContext) -> 'JABElement':
        return JABElement(jab=root._jab, handle=root._handle, vmid=root._vmid, ctx=ctx, is_root=False, root=root)


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

    def find_window(self, handle: Union[int, HWND]) -> Optional[JABElement]:
        return JABElement.create_root(jab=self._jab, handle=handle)


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
