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


import os
import time
from ctypes import Structure, windll, sizeof, byref
from ctypes.wintypes import HWND, DWORD, UINT, RECT, POINT
from typing import Optional, Tuple

from PIL import Image

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

DELETE = 0x00010000
READ_CONTROL = 0x00020000
SYNCHRONIZE = 0x00100000
WRITE_DAC = 0x00040000
WRITE_OWNER = 0x00080000

STANDARD_RIGHTS_REQUIRED = 983040
STANDARD_RIGHTS_READ = READ_CONTROL
STANDARD_RIGHTS_WRITE = READ_CONTROL
STANDARD_RIGHTS_EXECUTE = READ_CONTROL
STANDARD_RIGHTS_ALL = 2031616
SPECIFIC_RIGHTS_ALL = 65535
ACCESS_SYSTEM_SECURITY = 16777216
MAXIMUM_ALLOWED = 33554432
GENERIC_READ = -2147483648
GENERIC_WRITE = 1073741824
GENERIC_EXECUTE = 536870912
GENERIC_ALL = 268435456

PROCESS_TERMINATE = 0x0001
PROCESS_CREATE_THREAD = 0x0002
PROCESS_VM_OPERATION = 0x0008
PROCESS_VM_READ = 0x0010
PROCESS_VM_WRITE = 0x0020
PROCESS_DUP_HANDLE = 0x0040
PROCESS_CREATE_PROCESS = 0x0080
PROCESS_SET_QUOTA = 0x0100
PROCESS_SET_INFORMATION = 0x0200
PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_SUSPEND_RESUME = 0x0800
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
PROCESS_SET_LIMITED_INFORMATION = 0x2000
PROCESS_ALL_ACCESS = STANDARD_RIGHTS_REQUIRED | SYNCHRONIZE | 0xFFFF


class WINDOWPLACEMENT(Structure):
    _fields_ = [
        ('length', UINT),
        ('flags', UINT),
        ('showCmd', UINT),
        ('ptMinPosition', POINT),
        ('ptMaxPosition', POINT),
        ('rcNormalPosition', RECT),
    ]


def find_window(class_name: str = None, window_name: str = None) -> HWND:
    return windll.user32.FindWindowW(class_name, window_name)


def find_window_ex(parent: int = None, child_after: int = None, class_name: str = None, window_name: str = None) -> HWND:
    return windll.user32.FindWindowExW(parent, child_after, class_name, window_name)


def set_foreground(handle: int, process_id: int = None) -> bool:
    # https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setforegroundwindow
    res = windll.user32.SetForegroundWindow(handle)
    if process_id:
        wait_thread_idle(process_id, handle)
    return bool(res)


def get_window_rect(handle: int) -> Tuple[int, int, int, int]:
    # https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getwindowrect
    rect = RECT()
    windll.user32.GetWindowRect(handle, byref(rect))
    return rect.left, rect.top, rect.right, rect.bottom


def move_window(handle: int, process_id: int = None, x: int = None, y: int = None, width: int = None, height: int = None, repaint=True):
    if x is None or y is None or width is None or height is None:
        rect = get_window_rect(handle)
        if x is None:
            x = rect[0]
        if y is None:
            y = rect[1]
        if width is None:
            width = rect[2] - rect[0]
        if height is None:
            height = rect[3] - rect[1]
    # https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-movewindow
    res = windll.user32.MoveWindow(handle, x, y, width, height, repaint)
    if process_id:
        wait_thread_idle(process_id, handle)
    time.sleep(0)
    if not res:
        return False
    else:
        return True


def show_window(handle: int, cmd: int) -> bool:
    # https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-showwindow
    res = windll.user32.ShowWindow(handle, cmd)
    return bool(res)


def get_window_placement(handle: int) -> WINDOWPLACEMENT:
    # https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getwindowplacement
    wp = WINDOWPLACEMENT()
    wp.length = sizeof(wp)
    windll.user32.GetWindowPlacement(handle, byref(wp))
    return wp


def get_process_id_from_handle(handle: int) -> int:
    # https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getwindowthreadprocessid
    process_id = DWORD(0)
    handle = HWND(handle) if isinstance(handle, int) else handle
    windll.user32.GetWindowThreadProcessId(handle, byref(process_id))
    return process_id.value


def get_window_text(handle: int) -> str:
    import win32gui
    return win32gui.GetWindowText(handle)


def get_class_name(handle: int) -> str:
    import win32gui
    return win32gui.GetClassName(handle)


def get_process_name_by_process_id(process_id):
    import psutil
    try:
        process = psutil.Process(process_id)
        return process.name()
    except psutil.NoSuchProcess:
        return f"Process with PID {process_id} not found"
    except psutil.AccessDenied:
        return f"Access denied to process with PID {process_id}"


def get_cursor_pos() -> Optional[Tuple[int, int]]:
    # https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getcursorpos
    point = POINT()
    res = windll.user32.GetCursorPos(byref(point))
    if res:
        return point.x, point.y
    else:
        return None


def window_from_point(point: Tuple[int, int]) -> int:
    # https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-windowfrompoint
    return windll.user32.WindowFromPoint(POINT(point[0], point[1]))


def wait_thread_idle(process_id: int, handle: int):
    # https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-openprocess
    process = windll.kernel32.OpenProcess(0x0400, 0, process_id)
    # https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-ishungappwindow
    if windll.user32.IsHungAppWindow(handle):
        raise RuntimeError(f'Window (hwnd={handle}) is not responding!')
    # https://learn.microsoft.com/en-us/windows/win32/api/handleapi/nf-handleapi-closehandle
    windll.kernel32.CloseHandle(process)


def post_message(message, wparam=0, lparam=0):
    # https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-postmessagew
    return windll.user32.PostMessageW(self, message, wparam, lparam)


def close_handle(handle: int):
    from pywinauto.controls.hwndwrapper import HwndWrapper
    hwnd = HwndWrapper(handle)
    hwnd.close()


def screenshot(handle: int = None, filename: str = None) -> Image:
    # https://stackoverflow.com/questions/19695214/screenshot-of-inactive-window-printwindow-win32gui
    import win32gui
    import win32ui
    import win32api
    import win32con

    if handle:
        fullscreen = False
        rect = win32gui.GetWindowRect(handle)
        x, y, w, h = rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1]
    else:
        fullscreen = True
        handle = win32gui.GetDesktopWindow()
        x = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
        y = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)
        w = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
        h = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)

    window_dc = win32gui.GetWindowDC(handle)
    created_dc = win32ui.CreateDCFromHandle(window_dc)
    compatible_dc = created_dc.CreateCompatibleDC()

    bitmap = win32ui.CreateBitmap()
    bitmap.CreateCompatibleBitmap(created_dc, w, h)

    compatible_dc.SelectObject(bitmap)

    if fullscreen:
        compatible_dc.BitBlt((0, 0), (w, h), created_dc, (x, y), win32con.SRCCOPY)
    else:
        res = windll.user32.PrintWindow(handle, compatible_dc.GetSafeHdc(), 2)
        if not res:
            raise Exception()

    bitmap_info = bitmap.GetInfo()
    buffer = bitmap.GetBitmapBits(True)

    image = Image.frombuffer('RGB', (bitmap_info['bmWidth'], bitmap_info['bmHeight']), buffer, 'raw', 'BGRX', 0, 1)

    win32gui.DeleteObject(bitmap.GetHandle())
    compatible_dc.DeleteDC()
    created_dc.DeleteDC()
    win32gui.ReleaseDC(handle, window_dc)

    if filename:
        dirname = os.path.dirname(filename)
        if not os.path.exists(dirname):
            os.makedirs(dirname, exist_ok=True)
        image.save(filename)

    return image


def draw_outline(rect: Tuple[int, int, int, int], msg=None, color=0x0000ff):
    import ctypes
    import win32gui
    from pywinauto import win32structures
    from pywinauto import win32defines
    # create the pen (outline)
    pen_handle = ctypes.windll.gdi32.CreatePen(win32defines.PS_SOLID, 3, color)

    # create the brush (inside)
    brush = win32structures.LOGBRUSH()
    brush.lbStyle = win32defines.BS_NULL
    brush.lbHatch = win32defines.HS_DIAGCROSS
    brush_handle = ctypes.windll.gdi32.CreateBrushIndirect(ctypes.byref(brush))

    font = win32structures.LOGFONTW()
    font.lfHeight = 20
    font.lfWeight = win32defines.FW_BOLD
    font_handle = ctypes.windll.gdi32.CreateFontIndirectW(ctypes.byref(font))

    # get the Device Context
    dc = ctypes.windll.gdi32.CreateDCW("DISPLAY", None, None, None)

    # push our objects into it
    ctypes.windll.gdi32.SelectObject(dc, brush_handle)
    ctypes.windll.gdi32.SelectObject(dc, pen_handle)
    ctypes.windll.gdi32.SelectObject(dc, font_handle)
    win32gui.SetTextColor(dc, color)
    win32gui.SetBkMode(dc, win32defines.TRANSPARENT)

    ctypes.windll.gdi32.Rectangle(dc, rect[0], rect[1], rect[2], rect[3])
    if msg:
        ctypes.windll.gdi32.TextOutW(dc, rect[0], rect[1] - font.lfHeight, msg, len(msg))

    ctypes.windll.gdi32.DeleteObject(brush_handle)
    ctypes.windll.gdi32.DeleteObject(pen_handle)
    ctypes.windll.gdi32.DeleteDC(dc)
