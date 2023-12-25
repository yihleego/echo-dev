import asyncio
import ctypes
import os
import platform
from ctypes.wintypes import tagPOINT

import pywinauto
import win32gui
from pywinauto import win32defines, win32structures, win32functions

from jab.call import JAB
from jab.packages import AccessibleContext, AccessibleContextInfo, VisibleChildrenInfo
from utils.input import listener, Event, Key, main

OS_ARCH = platform.architecture()[0][:2]  # 32 or 64
JAB_VERSION = "2.0.2"
JAB_DLL_PATH = os.path.abspath("lib/javaaccessbridge%s/WindowsAccessBridge-%s.dll" % (JAB_VERSION, OS_ARCH))


def draw_outline(rect: tuple[int, int, int, int], msg=None):
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
            print(f"{'-' * depth} name='{aci.name}' role='{aci.role}'")
            if not res:
                return

            count = dll.getVisibleChildrenCount(vmid, ac)
            # print('getVisibleChildrenCount', count)
            if count <= 0:
                return

            vci = VisibleChildrenInfo()
            res = dll.getVisibleChildren(vmid, ac, 0, vci)
            if not res:
                return

            for idx in range(vci.returnedChildrenCount):
                child = ctypes.c_long(vci.children[idx])
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
        #
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
        #
        # dll.releaseJavaObject(new_vmid, accessible_context)

    dll.free()


if __name__ == '__main__':
    asyncio.run(main())
