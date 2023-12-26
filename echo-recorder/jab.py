import ctypes
import os
import platform
import time

from jab.call import JAB
from jab.packages import *

OS_ARCH = platform.architecture()[0][:2]  # 32 or 64
JAB_VERSION = "2.0.2"
JAB_DLL_PATH = os.path.abspath("lib/javaaccessbridge%s/WindowsAccessBridge-%s.dll" % (JAB_VERSION, OS_ARCH))

dll = JAB(JAB_DLL_PATH)

hwnd = 0x61184

res = dll.isJavaWindow(hwnd)
print('isJavaWindow', bool(res))

vmid = ctypes.c_long()
accessible_context = AccessibleContext()
res = dll.getAccessibleContextFromHWND(hwnd, vmid, accessible_context)
print('getAccessibleContextFromHWND', bool(res), vmid.value, accessible_context.value)

abvi = AccessBridgeVersionInfo()
res = dll.getVersionInfo(vmid, abvi)
print('getVersionInfo', bool(res), abvi)
dll.releaseJavaObject(vmid, abvi)


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
        child = AccessibleContext(vci.children[idx])
        print_tree(depth + 1, child)
        # print('getVisibleChildren', idx, bool(res), vci)


print_tree(0, accessible_context)

# def async_():
#     def set_focus_gained_fp(vmID, event, ac):
#         print('set_focus_gained_fp',vmID, ac.value)
#
#     dll.setFocusGainedFP(set_focus_gained_fp)
# my_thread = threading.Thread(target=async_)
# my_thread.start()

import win32gui

while True:
    # new_vmid = ctypes.c_long()
    # new_accessible_context = AccessibleContext()
    # res1 = dll.getAccessibleContextWithFocus(hwnd, new_vmid, new_accessible_context)

    pos = win32gui.GetCursorPos()
    new_vmid = vmid
    new_accessible_context = AccessibleContext()
    res1 = dll.getAccessibleContextAt(new_vmid, accessible_context, pos[0], pos[1], new_accessible_context)

    print('getAccessibleContextWithFocus', bool(res), new_vmid.value, new_accessible_context.value)

    if res1 and new_accessible_context.value != 0:
        aci = AccessibleContextInfo()
        res2 = dll.getAccessibleContextInfo(new_vmid, new_accessible_context, aci)
        print('getAccessibleContextInfo', aci.name, aci.role, aci.x, aci.y, aci.width, aci.height)

        dll.releaseJavaObject(new_vmid, new_accessible_context)

        if aci.name == ACCESSIBLE_RULER:
            break

    time.sleep(1)

dll.releaseJavaObject(vmid, accessible_context)

dll.close()
