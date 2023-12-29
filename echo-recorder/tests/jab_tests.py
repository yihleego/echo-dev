import ctypes
import encodings
import locale
import os
import platform
import random
import time
from ctypes.wintypes import tagPOINT
from typing import Optional

import pywinauto
import win32gui
from pywinauto import win32defines, win32structures, win32functions

from jab import JAB, AccessibleContext, AccessibleContextInfo, VisibleChildrenInfo, AccessibleTextInfo, AccessibleActions, AccessibleActionsToDo, JABDriver, Role
from utils.input import listener, Event, Key

OS_ARCH = platform.architecture()[0][:2]  # 32 or 64
JAB_VERSION = "2.0.2"
JAB_DLL_PATH = os.path.abspath("lib/javaaccessbridge%s/WindowsAccessBridge-%s.dll" % (JAB_VERSION, OS_ARCH))


def draw_outline(rect: tuple[int, int, int, int], msg=None):
    # color red
    color = 0x0000ff

    # create the pen(outline)
    pen_handle = win32functions.CreatePen(win32defines.PS_SOLID, 3, color)

    # create the brush (inside)
    brush = win32structures.LOGBRUSH()
    brush.lbStyle = win32defines.BS_NULL
    brush.lbHatch = win32defines.HS_DIAGCROSS
    brush_handle = win32functions.CreateBrushIndirect(ctypes.byref(brush))

    font = win32structures.LOGFONTW()
    font.lfHeight = 20
    font.lfWeight = win32defines.FW_BOLD
    font_handle = win32functions.CreateFontIndirect(ctypes.byref(font))

    # get the Device Context
    dc = win32functions.CreateDC("DISPLAY", None, None, None)

    # push our objects into it
    win32functions.SelectObject(dc, brush_handle)
    win32functions.SelectObject(dc, pen_handle)
    win32functions.SelectObject(dc, font_handle)
    win32gui.SetTextColor(dc, color)
    win32gui.SetBkMode(dc, win32defines.TRANSPARENT)

    win32functions.Rectangle(dc, rect[0], rect[1], rect[2], rect[3])
    if msg:
        win32functions.TextOut(dc, rect[0], rect[1] - font.lfHeight, msg, len(msg))

    win32functions.DeleteObject(brush_handle)
    win32functions.DeleteObject(pen_handle)
    win32functions.DeleteDC(dc)


def get_text_from_raw_bytes(
        buffer: bytes,
        chars_len: int,
        encoding: Optional[str] = None,
        errors_fallback: str = "replace",
) -> str:
    """[summary]

    Args:
        buffer (bytes): bytes object to convert to str.
        chars_len (int): character length for handle bytes.
        encoding (Optional[str], optional): encoding format for buffer. Defaults to None.
        errors_fallback (str, optional): error handling scheme for handling of decoding errors. Default: "replace".

    Returns:
        str: decoded text from buffer.
    """
    if encoding is None:
        if chars_len > 1 and any(buffer[chars_len:]):
            encoding = "utf_16_le"
        else:
            encoding = locale.getpreferredencoding()
    else:
        encoding = encodings.normalize_encoding(encoding).lower()
    if encoding.startswith("utf_16"):
        num_of_bytes = chars_len * 2
    elif encoding.startswith("utf_32"):
        num_of_bytes = chars_len * 4
    else:
        num_of_bytes = chars_len
    raw_text: bytes = buffer[:num_of_bytes]
    if not any(raw_text):
        return ""
    try:
        text = raw_text.decode(encoding, errors="surrogatepass")
    except UnicodeDecodeError:
        text = raw_text.decode(encoding, errors=errors_fallback)
    return text


@listener(Event.CLICK, Key.ctrl_l)
def on_click(x, y, button):
    dll = JAB(JAB_DLL_PATH)
    elem = pywinauto.uia_defines.IUIA().iuia.ElementFromPoint(tagPOINT(x, y))
    elem_info = pywinauto.uia_element_info.UIAElementInfo(elem)
    target = elem_info
    rectangle = target.rectangle
    if target.handle:
        hwnd = target.handle
        res = dll.isJavaWindow(hwnd)
        print('isJavaWindow', hex(hwnd), bool(res))
        if not res:
            return

        vmid = ctypes.c_long()
        accessible_context = AccessibleContext()
        res = dll.getAccessibleContextFromHWND(hwnd, vmid, accessible_context)
        print('getAccessibleContextFromHWND', bool(res), vmid.value, accessible_context.value)

        def print_tree(depth, ac):
            aci = AccessibleContextInfo()
            res = dll.getAccessibleContextInfo(vmid, ac, aci)
            if not res:
                return
            print(f"{'-' * depth} name='{aci.name}' role='{aci.role}'")

            if aci.accessibleText:
                ati = AccessibleTextInfo()
                res = dll.getAccessibleTextInfo(vmid, ac, ati)
                if res:
                    chars_start = ctypes.c_int(0)
                    chars_end = ati.charCount - 1
                    chars_len = ati.charCount
                    buffer = ctypes.create_string_buffer((chars_len + 1) * 2)
                    res = dll.getAccessibleTextRange(vmid, ac, chars_start, chars_end, buffer, chars_len)
                    if res:
                        text = get_text_from_raw_bytes(buffer=buffer, chars_len=chars_len, encoding="utf_16")
                        print(f"{'-' * depth} text='{text}'")

            if aci.accessibleAction:
                aa = AccessibleActions()
                res = dll.getAccessibleActions(vmid, ac, aa)
                if res:
                    for index in range(aa.actionsCount):
                        print(f"{'-' * depth} action='{aa.actionInfo[index].name}'")
                        if aa.actionInfo[index].name == '单击':
                            aatd = AccessibleActionsToDo()
                            aatd.actions[0].name = '单击'
                            aatd.actionsCount = 1
                            failure = ctypes.c_int(0)
                            dll.doAccessibleActions(vmid, ac, aatd, failure)
                            print(f"{'-' * depth} clicked")

            if aci.accessibleSelection:
                pass

            count = dll.getVisibleChildrenCount(vmid, ac)
            # print('getVisibleChildrenCount', count)
            if count <= 0:
                return

            vci = VisibleChildrenInfo()
            res = dll.getVisibleChildren(vmid, ac, 0, vci)
            if not res:
                return

            for idx in range(vci.returnedChildrenCount):
                child = AccessibleContext(vci.children[idx])
                print_tree(depth + 1, child)

        print_tree(0, accessible_context)
        dll.releaseJavaObject(vmid, accessible_context)

        # new_vmid = ctypes.c_long()
        # new_accessible_context = AccessibleContext()
        # res1 = dll.getAccessibleContextWithFocus(hwnd, new_vmid, new_accessible_context)

        # new_vmid = vmid
        # new_accessible_context = AccessibleContext()
        # res1 = dll.getAccessibleContextAt(new_vmid, accessible_context, x, y, new_accessible_context)

        # print('getAccessibleContextWithFocus', bool(res), new_vmid.value, new_accessible_context.value)

        # if res1 and new_accessible_context.value != 0:
        #     if not dll.isSameObject(accessible_context, new_accessible_context):
        #         aci = AccessibleContextInfo()
        #         res2 = dll.getAccessibleContextInfo(new_vmid, new_accessible_context, aci)
        #         print('getAccessibleContextInfo1', aci.name, aci.role, aci.x, aci.y, aci.width, aci.height)
        #         draw_outline((aci.x, aci.y, aci.width + aci.x, aci.height + aci.y), f"{aci.name} {aci.role} {aci.x} {aci.y} {aci.width} {aci.height}")
        #     else:
        #         aci = AccessibleContextInfo()
        #         res2 = dll.getAccessibleContextInfo(vmid, accessible_context, aci)
        #         print('getAccessibleContextInfo2', aci.name, aci.role, aci.x, aci.y, aci.width, aci.height)
        #         draw_outline((aci.x, aci.y, aci.width + aci.x, aci.height + aci.y), f"{aci.name} {aci.role} {aci.x} {aci.y} {aci.width} {aci.height}")
        #     dll.releaseJavaObject(new_vmid, new_accessible_context)

        # dll.releaseJavaObject(new_vmid, accessible_context)

    dll.close()


def test():
    driver = JABDriver()
    root = driver.find_window(handle=0x20600)
    if not root:
        print('not found')
        return
    root.screenshot("./screenshots/root_inactive.png", True)
    root.screenshot("./screenshots/root_foreground.png", False)

    input = root.find_elements(role=Role.TEXT)[0]
    button = root.find_elements(role=Role.PUSH_BUTTON, name="Click Me")[0]
    print('text:', input.text)
    time.sleep(1)
    input.set_focus()
    time.sleep(1)
    input.input(input.text + "append")
    button.click()
    print('input', input.rectangle)
    print('button', button.rectangle)

    input2 = root.find_elements(role=Role.TEXT)[0]
    button2 = root.find_elements(role=Role.PUSH_BUTTON, name="Click Me")[0]
    print('text:', input2.text)
    input2.input("sb")
    button2.click()

    input.release()
    button.release()
    input2.release()
    input2.release()

    root.set_foreground()
    time.sleep(1)
    rect = root.rectangle
    root.move(random.randint(0, rect[2] - rect[0]), random.randint(0, rect[3] - rect[1]))
    time.sleep(1)
    root.maximize()
    print('is_maximized', root.is_maximized(), 'is_minimized', root.is_minimized(), 'is_normal', root.is_normal(), 'ok' if root.is_maximized() else 'err')
    time.sleep(1)
    root.restore()
    print('is_maximized', root.is_maximized(), 'is_minimized', root.is_minimized(), 'is_normal', root.is_normal(), 'ok' if root.is_normal() else 'err')
    time.sleep(1)
    root.minimize()
    print('is_maximized', root.is_maximized(), 'is_minimized', root.is_minimized(), 'is_normal', root.is_normal(), 'ok' if root.is_minimized() else 'err')
    time.sleep(1)


if __name__ == '__main__':
    # asyncio.run(main())
    test()
