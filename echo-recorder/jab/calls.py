import _ctypes
import os
from ctypes import cdll, byref, CFUNCTYPE
from ctypes.wintypes import HWND
from typing import Generator, Callable

import pythoncom
import win32event

from jab.packages import *


class JAB:
    def __init__(self, dll_path=None):
        self._loaded = False
        self._started = False
        self._dll = None
        if dll_path:
            self.load(dll_path)
            self.start()

    def load(self, dll_path):
        if self._loaded:
            return
        if not os.path.isfile(dll_path):
            raise FileNotFoundError(
                "WindowsAccessBridge dll not found, "
                "please set correct path for environment variable, "
                "or check the passed customized WindowsAccessBridge dll."
            )
        self._dll = cdll.LoadLibrary(dll_path)
        self._dll.Windows_run()
        self._loaded = True

    def start(self):
        if self._started:
            return
        stop_event = win32event.CreateEvent(None, 0, 0, None)
        other_event = win32event.CreateEvent(None, 0, 0, None)

        def setup_msg_pump() -> Generator:
            waitables = stop_event, other_event
            while True:
                rc = win32event.MsgWaitForMultipleObjects(
                    waitables,
                    0,  # Wait for all = false, so it waits for anyone
                    200,  # Timeout, ms (or win32event.INFINITE)
                    win32event.QS_ALLEVENTS,  # Accepts all input
                )
                if rc == win32event.WAIT_OBJECT_0:
                    break
                elif rc == win32event.WAIT_OBJECT_0 + 1:
                    # Our second event listed, "OtherEvent", was set. Do whatever needs
                    # to be done -- you can wait on as many kernel-waitable objects as
                    # needed (events, locks, processes, threads, notifications, and so on).
                    pass
                elif rc == win32event.WAIT_OBJECT_0 + len(waitables):
                    # A windows message is waiting - take care of it. (Don't ask me
                    # why a WAIT_OBJECT_MSG isn't defined < WAIT_OBJECT_0...!).
                    # This message-serving MUST be done for COM, DDE, and other
                    # Windowsy things to work properly!
                    if pythoncom.PumpWaitingMessages():
                        break
                elif rc == win32event.WAIT_TIMEOUT:
                    # Our timeout has elapsed.
                    # Do some work here (e.g, poll something you can't thread)
                    # or just feel good to be alive.
                    pass
                else:
                    raise RuntimeError("unexpected win32wait return value")

                # call functions here, if txtt doesn't take too long. It will
                # be executed at least every 200ms -- possibly a lot more often,
                # depending on the number of Windows messages received.
                try:
                    yield
                finally:
                    win32event.SetEvent(stop_event)

        gen = setup_msg_pump()
        gen.send(None)
        self._started = True

    def close(self):
        if self._dll:
            _ctypes.FreeLibrary(self._dll._handle)

    def releaseJavaObject(self, vmID: c_long, object: Java_Object):
        self._dll.releaseJavaObject(vmID, object)

    def getVersionInfo(self, vmID: c_long, info: AccessBridgeVersionInfo) -> BOOL:
        return self._dll.getVersionInfo(vmID, byref(info))

    def isJavaWindow(self, window: HWND) -> BOOL:
        return self._dll.isJavaWindow(window)

    def isSameObject(self, vmID: c_long, obj1: JOBJECT64, obj2: JOBJECT64) -> BOOL:
        return self._dll.isSameObject(vmID, obj1, obj2)

    def getAccessibleContextFromHWND(self, window: HWND, vmID: c_long, ac: AccessibleContext) -> BOOL:
        return self._dll.getAccessibleContextFromHWND(window, byref(vmID), byref(ac))

    def getHWNDFromAccessibleContext(self, vmID: c_long, ac: AccessibleContext) -> HWND:
        return self._dll.getHWNDFromAccessibleContext(vmID, byref(ac))

    def getAccessibleContextAt(self, vmID: c_long, acParent: AccessibleContext, x: jint, y: jint, ac: AccessibleContext) -> BOOL:
        return self._dll.getAccessibleContextAt(vmID, acParent, x, y, byref(ac))

    def getAccessibleContextWithFocus(self, window: HWND, vmID: c_long, ac: AccessibleContext) -> BOOL:
        return self._dll.getAccessibleContextWithFocus(window, byref(vmID), byref(ac))

    def getAccessibleContextInfo(self, vmID: c_long, ac: AccessibleContext, info: AccessibleContextInfo) -> BOOL:
        return self._dll.getAccessibleContextInfo(vmID, ac, byref(info))

    def getAccessibleChildFromContext(self, vmID: c_long, ac: AccessibleContext, index: jint) -> AccessibleContext:
        return self._dll.getAccessibleChildFromContext(vmID, ac, index)

    def getAccessibleParentFromContext(self, vmID: c_long, ac: AccessibleContext) -> AccessibleContext:
        return self._dll.getAccessibleParentFromContext(vmID, ac)

    def getAccessibleTableInfo(self, vmID: c_long, ac: AccessibleContext, tableInfo: AccessibleTableInfo) -> BOOL:
        return self._dll.getAccessibleTableInfo(vmID, ac, byref(tableInfo))

    def getAccessibleTableCellInfo(self, vmID: c_long, accessibleTable: AccessibleTable, row: jint, column: jint, tableCellInfo: AccessibleTableCellInfo) -> BOOL:
        return self._dll.getAccessibleTableCellInfo(vmID, accessibleTable, row, column, byref(tableCellInfo))

    def getAccessibleTableRowHeader(self, vmID: c_long, acParent: AccessibleContext, tableInfo: AccessibleTableInfo) -> BOOL:
        return self._dll.getAccessibleTableRowHeader(vmID, acParent, byref(tableInfo))

    def getAccessibleTableColumnHeader(self, vmID: c_long, acParent: AccessibleContext, tableInfo: AccessibleTableInfo) -> BOOL:
        return self._dll.getAccessibleTableColumnHeader(vmID, acParent, byref(tableInfo))

    def getAccessibleTableRowDescription(self, vmID: c_long, acParent: AccessibleContext, row: jint) -> AccessibleContext:
        return self._dll.getAccessibleTableRowDescription(vmID, acParent, row)

    def getAccessibleTableColumnDescription(self, vmID: c_long, acParent: AccessibleContext, column: jint) -> AccessibleContext:
        return self._dll.getAccessibleTableColumnDescription(vmID, acParent, column)

    def getAccessibleTableRowSelectionCount(self, vmID: c_long, table: AccessibleTable) -> jint:
        return self._dll.getAccessibleTableRowSelectionCount(vmID, table)

    def isAccessibleTableRowSelected(self, vmID: c_long, table: AccessibleTable, row: jint) -> BOOL:
        return self._dll.isAccessibleTableRowSelected(vmID, table, row)

    def getAccessibleTableRowSelections(self, vmID: c_long, table: AccessibleTable, count: jint, selections: jint) -> BOOL:
        return self._dll.getAccessibleTableRowSelections(vmID, table, count, byref(selections))

    def getAccessibleTableColumnSelectionCount(self, vmID: c_long, table: AccessibleTable) -> jint:
        return self._dll.getAccessibleTableColumnSelectionCount(vmID, table)

    def isAccessibleTableColumnSelected(self, vmID: c_long, table: AccessibleTable, column: jint) -> BOOL:
        return self._dll.isAccessibleTableColumnSelected(vmID, table, column)

    def getAccessibleTableColumnSelections(self, vmID: c_long, table: AccessibleTable, count: jint, selections: jint) -> BOOL:
        return self._dll.getAccessibleTableColumnSelections(vmID, table, count, byref(selections))

    def getAccessibleTableRow(self, vmID: c_long, table: AccessibleTable, index: jint) -> jint:
        return self._dll.getAccessibleTableRow(vmID, table, index)

    def getAccessibleTableColumn(self, vmID: c_long, table: AccessibleTable, index: jint) -> jint:
        return self._dll.getAccessibleTableColumn(vmID, table, index)

    def getAccessibleTableIndex(self, vmID: c_long, table: AccessibleTable, row: jint, column: jint) -> jint:
        return self._dll.getAccessibleTableIndex(vmID, table, row, column)

    def getAccessibleRelationSet(self, vmID: c_long, accessibleContext: AccessibleContext, relationSetInfo: AccessibleRelationSetInfo):
        return self._dll.getAccessibleRelationSet(vmID, accessibleContext, byref(relationSetInfo))

    def getAccessibleHypertext(self, vmID: c_long, accessibleContext: AccessibleContext, hypertextInfo: AccessibleHypertextInfo) -> BOOL:
        return self._dll.getAccessibleHypertext(vmID, accessibleContext, byref(hypertextInfo))

    def activateAccessibleHyperlink(self, vmID: c_long, accessibleContext: AccessibleContext, accessibleHyperlink: AccessibleHyperlink) -> BOOL:
        return self._dll.activateAccessibleHyperlink(vmID, accessibleContext, accessibleHyperlink)

    def getAccessibleHyperlinkCount(self, vmID: c_long, accessibleContext: AccessibleContext) -> jint:
        return self._dll.getAccessibleHyperlinkCount(vmID, accessibleContext)

    def getAccessibleHypertextExt(self, vmID: c_long, accessibleContext: AccessibleContext, nStartIndex: jint, hypertextInfo: AccessibleHypertextInfo) -> BOOL:
        return self._dll.getAccessibleHypertextExt(vmID, accessibleContext, nStartIndex, byref(hypertextInfo))

    def getAccessibleHypertextLinkIndex(self, vmID: c_long, hypertext: AccessibleHypertext, nIndex: jint) -> jint:
        return self._dll.getAccessibleHypertextLinkIndex(vmID, hypertext, nIndex)

    def getAccessibleHyperlink(self, vmID: c_long, hypertext: AccessibleHypertext, nIndex: jint, hyperlinkInfo: AccessibleHyperlinkInfo) -> BOOL:
        return self._dll.getAccessibleHyperlink(vmID, hypertext, nIndex, byref(hyperlinkInfo))

    def getAccessibleKeyBindings(self, vmID: c_long, accessibleContext: AccessibleContext, keyBindings: AccessibleKeyBindings) -> BOOL:
        return self._dll.getAccessibleKeyBindings(vmID, accessibleContext, byref(keyBindings))

    def getAccessibleIcons(self, vmID: c_long, accessibleContext: AccessibleContext, icons: AccessibleIcons) -> BOOL:
        return self._dll.getAccessibleIcons(vmID, accessibleContext, byref(icons))

    def getAccessibleActions(self, vmID: c_long, accessibleContext: AccessibleContext, actions: AccessibleActions) -> BOOL:
        return self._dll.getAccessibleActions(vmID, accessibleContext, byref(actions))

    def doAccessibleActions(self, vmID: c_long, accessibleContext: AccessibleContext, actionsToDo: AccessibleActionsToDo, failure: jint) -> BOOL:
        return self._dll.doAccessibleActions(vmID, accessibleContext, byref(actionsToDo), byref(failure))

    def getAccessibleTextInfo(self, vmID: c_long, at: AccessibleText, textInfo: AccessibleTextInfo, x: jint = 0, y: jint = 0) -> BOOL:
        return self._dll.getAccessibleTextInfo(vmID, at, byref(textInfo), x, y)

    def getAccessibleTextItems(self, vmID: c_long, at: AccessibleText, textItems: AccessibleTextItemsInfo, index: jint) -> BOOL:
        return self._dll.getAccessibleTextItems(vmID, at, byref(textItems), index)

    def getAccessibleTextSelectionInfo(self, vmID: c_long, at: AccessibleText, textSelection: AccessibleTextSelectionInfo) -> BOOL:
        return self._dll.getAccessibleTextSelectionInfo(vmID, at, byref(textSelection))

    def getAccessibleTextAttributes(self, vmID: c_long, at: AccessibleText, index: jint, attributes: AccessibleTextAttributesInfo) -> BOOL:
        return self._dll.getAccessibleTextAttributes(vmID, at, index, byref(attributes))

    def getAccessibleTextRect(self, vmID: c_long, at: AccessibleText, rectInfo: AccessibleTextRectInfo, index: jint) -> BOOL:
        return self._dll.getAccessibleTextRect(vmID, at, byref(rectInfo), index)

    def getAccessibleTextLineBounds(self, vmID: c_long, at: AccessibleText, index: jint, startIndex: jint, endIndex: jint) -> BOOL:
        return self._dll.getAccessibleTextLineBounds(vmID, at, index, byref(startIndex), byref(endIndex))

    def getAccessibleTextRange(self, vmID: c_long, at: AccessibleText, start: jint, end: jint, text: wchar_t, len: c_short) -> BOOL:
        return self._dll.getAccessibleTextRange(vmID, at, start, end, byref(text), len)

    def getCurrentAccessibleValueFromContext(self, vmID: c_long, av: AccessibleValue, value: wchar_t, len: c_short) -> BOOL:
        return self._dll.getCurrentAccessibleValueFromContext(vmID, av, byref(value), len)

    def getMaximumAccessibleValueFromContext(self, vmID: c_long, av: AccessibleValue, value: wchar_t, len: c_short) -> BOOL:
        return self._dll.getMaximumAccessibleValueFromContext(vmID, av, byref(value), len)

    def getMinimumAccessibleValueFromContext(self, vmID: c_long, av: AccessibleValue, value: wchar_t, len: c_short) -> BOOL:
        return self._dll.getMinimumAccessibleValueFromContext(vmID, av, byref(value), len)

    def addAccessibleSelectionFromContext(self, vmID: c_long, as_: AccessibleSelection, i: int):
        self._dll.addAccessibleSelectionFromContext(vmID, as_, i)

    def clearAccessibleSelectionFromContext(self, vmID: c_long, as_: AccessibleSelection):
        self._dll.clearAccessibleSelectionFromContext(vmID, as_)

    def getAccessibleSelectionFromContext(self, vmID: c_long, as_: AccessibleSelection, i: int) -> JOBJECT64:
        return self._dll.getAccessibleSelectionFromContext(vmID, as_, i)

    def getAccessibleSelectionCountFromContext(self, vmID: c_long, as_: AccessibleSelection) -> c_int:
        return self._dll.getAccessibleSelectionCountFromContext(vmID, as_)

    def isAccessibleChildSelectedFromContext(self, vmID: c_long, as_: AccessibleSelection, i: int) -> BOOL:
        return self._dll.isAccessibleChildSelectedFromContext(vmID, as_, i)

    def removeAccessibleSelectionFromContext(self, vmID: c_long, as_: AccessibleSelection, i: int):
        self._dll.removeAccessibleSelectionFromContext(vmID, as_, i)

    def selectAllAccessibleSelectionFromContext(self, vmID: c_long, as_: AccessibleSelection):
        self._dll.selectAllAccessibleSelectionFromContext(vmID, as_)

    def setTextContents(self, vmID: c_long, ac: AccessibleContext, text: wchar_t) -> BOOL:
        return self._dll.setTextContents(vmID, ac, byref(text))

    def getParentWithRole(self, vmID: c_long, ac: AccessibleContext, role: wchar_t) -> AccessibleContext:
        return self._dll.getParentWithRole(vmID, ac, byref(role))

    def getTopLevelObject(self, vmID: c_long, ac: AccessibleContext) -> AccessibleContext:
        return self._dll.getTopLevelObject(vmID, ac)

    def getParentWithRoleElseRoot(self, vmID: c_long, ac: AccessibleContext, role: wchar_t) -> AccessibleContext:
        return self._dll.getParentWithRoleElseRoot(vmID, ac, byref(role))

    def getObjectDepth(self, vmID: c_long, ac: AccessibleContext) -> int:
        return self._dll.getObjectDepth(vmID, ac)

    def getActiveDescendent(self, vmID: c_long, ac: AccessibleContext) -> AccessibleContext:
        return self._dll.getActiveDescendent(vmID, ac)

    def getVirtualAccessibleName(self, vmID: c_long, accessibleContext: AccessibleContext, name: wchar_t, len: int) -> BOOL:
        return self._dll.getVirtualAccessibleName(vmID, accessibleContext, byref(name), len)

    def requestFocus(self, vmID: c_long, accessibleContext: AccessibleContext) -> BOOL:
        return self._dll.requestFocus(vmID, accessibleContext)

    def selectTextRange(self, vmID: c_long, accessibleContext: AccessibleContext, startIndex: int, endIndex: int) -> BOOL:
        return self._dll.selectTextRange(vmID, accessibleContext, startIndex, endIndex)

    def getTextAttributesInRange(self, vmID: c_long, accessibleContext: AccessibleContext, startIndex: int, endIndex: int, attributes: AccessibleTextAttributesInfo, len: c_short) -> BOOL:
        return self._dll.getTextAttributesInRange(vmID, accessibleContext, startIndex, endIndex, byref(attributes), byref(len))

    def getVisibleChildrenCount(self, vmID: c_long, accessibleContext: AccessibleContext) -> int:
        return self._dll.getVisibleChildrenCount(vmID, accessibleContext)

    def getVisibleChildren(self, vmID: c_long, accessibleContext: AccessibleContext, startIndex: int, children: VisibleChildrenInfo) -> BOOL:
        return self._dll.getVisibleChildren(vmID, accessibleContext, startIndex, byref(children))

    def setCaretPosition(self, vmID: c_long, accessibleContext: AccessibleContext, position: int) -> BOOL:
        return self._dll.setCaretPosition(vmID, accessibleContext, position)

    def getCaretLocation(self, vmID: c_long, ac: AccessibleContext, rectInfo: AccessibleTextRectInfo, index: jint) -> BOOL:
        return self._dll.getCaretLocation(vmID, ac, byref(rectInfo), index)

    def getEventsWaiting(self) -> c_int:
        return self._dll.getEventsWaiting()

    def setJavaShutdownFP(self, fp: Callable[[c_long], None]):
        functype = CFUNCTYPE(None, c_long)
        self._dll.setJavaShutdownFP(functype(fp))

    def setFocusGainedFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64], None]):
        functype = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64)
        self._dll.setFocusGainedFP(functype(fp))

    def setFocusLostFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64], None]):
        functype = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64)
        self._dll.setFocusLostFP(functype(fp))

    def setCaretUpdateFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64], None]):
        functype = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64)
        self._dll.setCaretUpdateFP(functype(fp))

    def setMouseClickedFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64], None]):
        functype = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64)
        self._dll.setMouseClickedFP(functype(fp))

    def setMouseEnteredFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64], None]):
        functype = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64)
        self._dll.setMouseEnteredFP(functype(fp))

    def setMouseExitedFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64], None]):
        functype = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64)
        self._dll.setMouseExitedFP(functype(fp))

    def setMousePressedFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64], None]):
        functype = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64)
        self._dll.setMousePressedFP(functype(fp))

    def setMouseReleasedFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64], None]):
        functype = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64)
        self._dll.setMouseReleasedFP(functype(fp))

    def setMenuCanceledFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64], None]):
        functype = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64)
        self._dll.setMenuCanceledFP(functype(fp))

    def setMenuDeselectedFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64], None]):
        functype = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64)
        self._dll.setMenuDeselectedFP(functype(fp))

    def setMenuSelectedFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64], None]):
        functype = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64)
        self._dll.setMenuSelectedFP(functype(fp))

    def setPopupMenuCanceledFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64], None]):
        functype = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64)
        self._dll.setPopupMenuCanceledFP(functype(fp))

    def setPopupMenuWillBecomeInvisibleFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64], None]):
        functype = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64)
        self._dll.setPopupMenuWillBecomeInvisibleFP(functype(fp))

    def setPopupMenuWillBecomeVisibleFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64], None]):
        functype = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64)
        self._dll.setPopupMenuWillBecomeVisibleFP(functype(fp))

    def setPropertyNameChangeFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64, wchar_t, wchar_t], None]):
        functype = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64, wchar_t, wchar_t)
        self._dll.setPropertyNameChangeFP(functype(fp))

    def setPropertyDescriptionChangeFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64, wchar_t, wchar_t], None]):
        functype = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64, wchar_t, wchar_t)
        self._dll.setPropertyDescriptionChangeFP(functype(fp))

    def setPropertyStateChangeFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64, wchar_t, wchar_t], None]):
        functype = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64, wchar_t, wchar_t)
        self._dll.setPropertyStateChangeFP(functype(fp))

    def setPropertyValueChangeFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64, wchar_t, wchar_t], None]):
        functype = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64, wchar_t, wchar_t)
        self._dll.setPropertyValueChangeFP(functype(fp))

    def setPropertySelectionChangeFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64], None]):
        functype = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64)
        self._dll.setPropertySelectionChangeFP(functype(fp))

    def setPropertyTextChangeFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64], None]):
        functype = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64)
        self._dll.setPropertyTextChangeFP(functype(fp))

    def setPropertyCaretChangeFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64, int, int], None]):
        functype = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64, int, int)
        self._dll.setPropertyCaretChangeFP(functype(fp))

    def setPropertyVisibleDataChangeFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64], None]):
        functype = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64)
        self._dll.setPropertyVisibleDataChangeFP(functype(fp))

    def setPropertyChildChangeFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64, JOBJECT64, JOBJECT64], None]):
        functype = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64, JOBJECT64, JOBJECT64)
        self._dll.setPropertyChildChangeFP(functype(fp))

    def setPropertyActiveDescendentChangeFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64, JOBJECT64, JOBJECT64], None]):
        functype = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64, JOBJECT64, JOBJECT64)
        self._dll.setPropertyActiveDescendentChangeFP(functype(fp))

    def setPropertyTableModelChangeFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64, wchar_t, wchar_t], None]):
        functype = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64, wchar_t, wchar_t)
        self._dll.setPropertyTableModelChangeFP(functype(fp))
