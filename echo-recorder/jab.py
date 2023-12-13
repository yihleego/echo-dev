import ctypes
import os
import platform

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

aci = AccessibleContextInfo()
res = dll.getAccessibleContextInfo(vmid, accessible_context, aci)
print('getAccessibleContextInfo', bool(res), aci)

vci = VisibleChildrenInfo()
res = dll.getVisibleChildren(vmid, accessible_context, 0, vci)
print('getVisibleChildren', bool(res), vci)

dll.free()
