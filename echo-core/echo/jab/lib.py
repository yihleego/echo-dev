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


import _ctypes
import os
import platform
import shutil
import subprocess
from ctypes import c_bool, c_char, c_wchar, c_wchar_p, c_int, c_int64, c_float, c_long, c_short, cdll, byref, CFUNCTYPE, Structure
from ctypes.wintypes import HWND
from typing import Generator, Callable, Optional

# AccessBridge versioning
ACCESS_BRIDGE_VERSION = "AccessBridge 2.0.2"
JAVA_ACCESS_BRIDGE_VERSION = ACCESS_BRIDGE_VERSION
WINDOW_ACCESS_BRIDGE_VERSION = ACCESS_BRIDGE_VERSION

# constants
MAX_BUFFER_SIZE = 10240
MAX_STRING_SIZE = 1024
SHORT_STRING_SIZE = 256
MAX_TABLE_SELECTIONS = 64
MAX_RELATION_TARGETS = 25
MAX_RELATIONS = 5
MAX_HYPERLINKS = 64
MAX_KEY_BINDINGS = 8
MAX_ICON_INFO = 8
MAX_ACTION_INFO = 256
MAX_ACTIONS_TO_DO = 32
MAX_VISIBLE_CHILDREN = 256
ACCESSIBLE_SHIFT_KEYSTROKE = 1
ACCESSIBLE_CONTROL_KEYSTROKE = 2
ACCESSIBLE_META_KEYSTROKE = 4
ACCESSIBLE_ALT_KEYSTROKE = 8
ACCESSIBLE_ALT_GRAPH_KEYSTROKE = 16
ACCESSIBLE_BUTTON1_KEYSTROKE = 32
ACCESSIBLE_BUTTON2_KEYSTROKE = 64
ACCESSIBLE_BUTTON3_KEYSTROKE = 128

# object types
jboolean = c_bool
jchar = c_char
jint = c_int
jlong = c_long
jfloat = c_float
jshort = c_short
wchar_t = c_wchar
BOOL = c_long
JOBJECT64 = c_int64
AccessibleContext = JOBJECT64
AccessibleText = JOBJECT64
AccessibleValue = JOBJECT64
AccessibleSelection = JOBJECT64
Java_Object = JOBJECT64
PropertyChangeEvent = JOBJECT64
FocusEvent = JOBJECT64
CaretEvent = JOBJECT64
MouseEvent = JOBJECT64
MenuEvent = JOBJECT64
AccessibleTable = JOBJECT64
AccessibleHyperlink = JOBJECT64
AccessibleHypertext = JOBJECT64

# Java event types
cPropertyChangeEvent = 0x1
cFocusGainedEvent = 0x2
cFocusLostEvent = 0x4
cCaretUpdateEvent = 0x8
cMouseClickedEvent = 0x10
cMouseEnteredEvent = 0x20
cMouseExitedEvent = 0x40
cMousePressedEvent = 0x80
cMouseReleasedEvent = 0x100
cMenuCanceledEvent = 0x200
cMenuDeselectedEvent = 0x400
cMenuSelectedEvent = 0x800
cPopupMenuCanceledEvent = 0x1000
cPopupMenuWillBecomeInvisibleEvent = 0x2000
cPopupMenuWillBecomeVisibleEvent = 0x4000
cJavaShutdownEvent = 0x8000

# Accessible Roles

# Object is used to alert the user about something.
ACCESSIBLE_ALERT = "alert"

# The header for a column of data.
ACCESSIBLE_COLUMN_HEADER = "column header"

# Object that can be drawn into and is used to trap
# events.
# see ACCESSIBLE_FRAME
# see ACCESSIBLE_GLASS_PANE
# see ACCESSIBLE_LAYERED_PANE
ACCESSIBLE_CANVAS = "canvas"

# A list of choices the user can select from.  Also optionally
# allows the user to enter a choice of their own.
ACCESSIBLE_COMBO_BOX = "combo box"

# An iconified internal frame in a DESKTOP_PANE.
# see ACCESSIBLE_DESKTOP_PANE
# see ACCESSIBLE_INTERNAL_FRAME
ACCESSIBLE_DESKTOP_ICON = "desktop icon"

# A frame-like object that is clipped by a desktop pane.  The
# desktop pane, internal frame, and desktop icon objects are
# often used to create multiple document interfaces within an
# application.
# see ACCESSIBLE_DESKTOP_ICON
# see ACCESSIBLE_DESKTOP_PANE
# see ACCESSIBLE_FRAME
ACCESSIBLE_INTERNAL_FRAME = "internal frame"

# A pane that supports internal frames and
# iconified versions of those internal frames.
# see ACCESSIBLE_DESKTOP_ICON
# see ACCESSIBLE_INTERNAL_FRAME
ACCESSIBLE_DESKTOP_PANE = "desktop pane"

# A specialized pane whose primary use is inside a DIALOG
# see ACCESSIBLE_DIALOG
ACCESSIBLE_OPTION_PANE = "option pane"

# A top level window with no title or border.
# see ACCESSIBLE_FRAME
# see ACCESSIBLE_DIALOG
ACCESSIBLE_WINDOW = "window"

# A top level window with a title bar, border, menu bar, etc.  It is
# often used as the primary window for an application.
# see ACCESSIBLE_DIALOG
# see ACCESSIBLE_CANVAS
# see ACCESSIBLE_WINDOW
ACCESSIBLE_FRAME = "frame"

# A top level window with title bar and a border.  A dialog is similar
# to a frame, but it has fewer properties and is often used as a
# secondary window for an application.
# see ACCESSIBLE_FRAME
# see ACCESSIBLE_WINDOW
ACCESSIBLE_DIALOG = "dialog"

# A specialized dialog that lets the user choose a color.
ACCESSIBLE_COLOR_CHOOSER = "color chooser"

# A pane that allows the user to navigate through
# and select the contents of a directory.  May be used
# by a file chooser.
# see ACCESSIBLE_FILE_CHOOSER
ACCESSIBLE_DIRECTORY_PANE = "directory pane"

# A specialized dialog that displays the files in the directory
# and lets the user select a file, browse a different directory,
# or specify a filename.  May use the directory pane to show the
# contents of a directory.
# see ACCESSIBLE_DIRECTORY_PANE
ACCESSIBLE_FILE_CHOOSER = "file chooser"

# An object that fills up space in a user interface.  It is often
# used in interfaces to tweak the spacing between components,
# but serves no other purpose.
ACCESSIBLE_FILLER = "filler"

# A hypertext anchor
ACCESSIBLE_HYPERLINK = "hyperlink"

# A small fixed size picture, typically used to decorate components.
ACCESSIBLE_ICON = "icon"

# An object used to present an icon or short string in an interface.
ACCESSIBLE_LABEL = "label"

# A specialized pane that has a glass pane and a layered pane as its
# children.
# see ACCESSIBLE_GLASS_PANE
# see ACCESSIBLE_LAYERED_PANE
ACCESSIBLE_ROOT_PANE = "root pane"

# A pane that is guaranteed to be painted on top
# of all panes beneath it.
# see ACCESSIBLE_ROOT_PANE
# see ACCESSIBLE_CANVAS
ACCESSIBLE_GLASS_PANE = "glass pane"

# A specialized pane that allows its children to be drawn in layers,
# providing a form of stacking order.  This is usually the pane that
# holds the menu bar as well as the pane that contains most of the
# visual components in a window.
# see ACCESSIBLE_GLASS_PANE
# see ACCESSIBLE_ROOT_PANE
ACCESSIBLE_LAYERED_PANE = "layered pane"

# An object that presents a list of objects to the user and allows the
# user to select one or more of them.  A list is usually contained
# within a scroll pane.
# see ACCESSIBLE_SCROLL_PANE
# see ACCESSIBLE_LIST_ITEM
ACCESSIBLE_LIST = "list"

# An object that presents an element in a list.  A list is usually
# contained within a scroll pane.
# see ACCESSIBLE_SCROLL_PANE
# see ACCESSIBLE_LIST
ACCESSIBLE_LIST_ITEM = "list item"

# An object usually drawn at the top of the primary dialog box of
# an application that contains a list of menus the user can choose
# from.  For example, a menu bar might contain menus for "File,"
# "Edit," and "Help."
# see ACCESSIBLE_MENU
# see ACCESSIBLE_POPUP_MENU
# see ACCESSIBLE_LAYERED_PANE
ACCESSIBLE_MENU_BAR = "menu bar"

# A temporary window that is usually used to offer the user a
# list of choices, and then hides when the user selects one of
# those choices.
# see ACCESSIBLE_MENU
# see ACCESSIBLE_MENU_ITEM
ACCESSIBLE_POPUP_MENU = "popup menu"

# An object usually found inside a menu bar that contains a list
# of actions the user can choose from.  A menu can have any object
# as its children, but most often they are menu items, other menus,
# or rudimentary objects such as radio buttons, check boxes, or
# separators.  For example, an application may have an "Edit" menu
# that contains menu items for "Cut" and "Paste."
# see ACCESSIBLE_MENU_BAR
# see ACCESSIBLE_MENU_ITEM
# see ACCESSIBLE_SEPARATOR
# see ACCESSIBLE_RADIO_BUTTON
# see ACCESSIBLE_CHECK_BOX
# see ACCESSIBLE_POPUP_MENU
ACCESSIBLE_MENU = "menu"

# An object usually contained in a menu that presents an action
# the user can choose.  For example, the "Cut" menu item in an
# "Edit" menu would be an action the user can select to cut the
# selected area of text in a document.
# see ACCESSIBLE_MENU_BAR
# see ACCESSIBLE_SEPARATOR
# see ACCESSIBLE_POPUP_MENU
ACCESSIBLE_MENU_ITEM = "menu item"

# An object usually contained in a menu to provide a visual
# and logical separation of the contents in a menu.  For example,
# the "File" menu of an application might contain menu items for
# "Open," "Close," and "Exit," and will place a separator between
# "Close" and "Exit" menu items.
# see ACCESSIBLE_MENU
# see ACCESSIBLE_MENU_ITEM
ACCESSIBLE_SEPARATOR = "separator"

# An object that presents a series of panels (or page tabs), one at a
# time, through some mechanism provided by the object.  The most common
# mechanism is a list of tabs at the top of the panel.  The children of
# a page tab list are all page tabs.
# see ACCESSIBLE_PAGE_TAB
ACCESSIBLE_PAGE_TAB_LIST = "page tab list"

# An object that is a child of a page tab list.  Its sole child is
# the panel that is to be presented to the user when the user
# selects the page tab from the list of tabs in the page tab list.
# see ACCESSIBLE_PAGE_TAB_LIST
ACCESSIBLE_PAGE_TAB = "page tab"

# A generic container that is often used to group objects.
ACCESSIBLE_PANEL = "panel"

# An object used to indicate how much of a task has been completed.
ACCESSIBLE_PROGRESS_BAR = "progress bar"

# A text object used for passwords, or other places where the
# text contents is not shown visibly to the user
ACCESSIBLE_PASSWORD_TEXT = "password text"

# An object the user can manipulate to tell the application to do
# something.
# see ACCESSIBLE_CHECK_BOX
# see ACCESSIBLE_TOGGLE_BUTTON
# see ACCESSIBLE_RADIO_BUTTON
ACCESSIBLE_PUSH_BUTTON = "push button"

# A specialized push button that can be checked or unchecked, but
# does not provide a separate indicator for the current state.
# see ACCESSIBLE_PUSH_BUTTON
# see ACCESSIBLE_CHECK_BOX
# see ACCESSIBLE_RADIO_BUTTON
ACCESSIBLE_TOGGLE_BUTTON = "toggle button"

# A choice that can be checked or unchecked and provides a
# separate indicator for the current state.
# see ACCESSIBLE_PUSH_BUTTON
# see ACCESSIBLE_TOGGLE_BUTTON
# see ACCESSIBLE_RADIO_BUTTON
ACCESSIBLE_CHECK_BOX = "check box"

# A specialized check box that will cause other radio buttons in the
# same group to become unchecked when this one is checked.
# see ACCESSIBLE_PUSH_BUTTON
# see ACCESSIBLE_TOGGLE_BUTTON
# see ACCESSIBLE_CHECK_BOX
ACCESSIBLE_RADIO_BUTTON = "radio button"

# The header for a row of data.
ACCESSIBLE_ROW_HEADER = "row header"

# An object that allows a user to incrementally view a large amount
# of information.  Its children can include scroll bars and a viewport.
# see ACCESSIBLE_SCROLL_BAR
# see ACCESSIBLE_VIEWPORT
ACCESSIBLE_SCROLL_PANE = "scroll pane"

# An object usually used to allow a user to incrementally view a
# large amount of data.  Usually used only by a scroll pane.
# see ACCESSIBLE_SCROLL_PANE
ACCESSIBLE_SCROLL_BAR = "scroll bar"

# An object usually used in a scroll pane.  It represents the portion
# of the entire data that the user can see.  As the user manipulates
# the scroll bars, the contents of the viewport can change.
# see ACCESSIBLE_SCROLL_PANE
ACCESSIBLE_VIEWPORT = "viewport"

# An object that allows the user to select from a bounded range.  For
# example, a slider might be used to select a number between 0 and 100.
ACCESSIBLE_SLIDER = "slider"

# A specialized panel that presents two other panels at the same time.
# Between the two panels is a divider the user can manipulate to make
# one panel larger and the other panel smaller.
ACCESSIBLE_SPLIT_PANE = "split pane"

# An object used to present information in terms of rows and columns.
# An example might include a spreadsheet application.
ACCESSIBLE_TABLE = "table"

# An object that presents text to the user.  The text is usually
# editable by the user as opposed to a label.
# see ACCESSIBLE_LABEL
ACCESSIBLE_TEXT = "text"

# An object used to present hierarchical information to the user.
# The individual nodes in the tree can be collapsed and expanded
# to provide selective disclosure of the tree's contents.
ACCESSIBLE_TREE = "tree"

# A bar or palette usually composed of push buttons or toggle buttons.
# It is often used to provide the most frequently used functions for an
# application.
ACCESSIBLE_TOOL_BAR = "tool bar"

# An object that provides information about another object.  The
# accessibleDescription property of the tool tip is often displayed
# to the user in a small L"help bubble" when the user causes the
# mouse to hover over the object associated with the tool tip.
ACCESSIBLE_TOOL_TIP = "tool tip"

# An AWT component, but nothing else is known about it.
# see ACCESSIBLE_SWING_COMPONENT
# see ACCESSIBLE_UNKNOWN
ACCESSIBLE_AWT_COMPONENT = "awt component"

# A Swing component, but nothing else is known about it.
# see ACCESSIBLE_AWT_COMPONENT
# see ACCESSIBLE_UNKNOWN
ACCESSIBLE_SWING_COMPONENT = "swing component"

# The object contains some Accessible information, but its role is
# not known.
# see ACCESSIBLE_AWT_COMPONENT
# see ACCESSIBLE_SWING_COMPONENT
ACCESSIBLE_UNKNOWN = "unknown"

# A STATUS_BAR is an simple component that can contain
# multiple labels of status information to the user.
ACCESSIBLE_STATUS_BAR = "status bar"

# A DATE_EDITOR is a component that allows users to edit
# java.util.Date and java.util.Time objects
ACCESSIBLE_DATE_EDITOR = "date editor"

# A SPIN_BOX is a simple spinner component and its main use
# is for simple numbers.
ACCESSIBLE_SPIN_BOX = "spin box"

# A FONT_CHOOSER is a component that lets the user pick various
# attributes for fonts.
ACCESSIBLE_FONT_CHOOSER = "font chooser"

# A GROUP_BOX is a simple container that contains a border
# around it and contains components inside it.
ACCESSIBLE_GROUP_BOX = "group box"

# A text header
ACCESSIBLE_HEADER = "header"

# A text footer
ACCESSIBLE_FOOTER = "footer"

# A text paragraph
ACCESSIBLE_PARAGRAPH = "paragraph"

# A ruler is an object used to measure distance
ACCESSIBLE_RULER = "ruler"

# A role indicating the object acts as a formula for
# calculating a value.  An example is a formula in
# a spreadsheet cell.
ACCESSIBLE_EDITBAR = "editbar"

# A role indicating the object monitors the progress
# of some operation.
PROGRESS_MONITOR = "progress monitor"

# Accessibility event types
cPropertyNameChangeEvent = 0x1
cPropertyDescriptionChangeEvent = 0x2
cPropertyStateChangeEvent = 0x4
cPropertyValueChangeEvent = 0x8
cPropertySelectionChangeEvent = 0x10
cPropertyTextChangeEvent = 0x20
cPropertyCaretChangeEvent = 0x40
cPropertyVisibleDataChangeEvent = 0x80
cPropertyChildChangeEvent = 0x100
cPropertyActiveDescendentChangeEvent = 0x200
cPropertyTableModelChangeEvent = 0x400

# optional AccessibleContext interfaces
cAccessibleValueInterface = 1  # 1 << 1 (TRUE)
cAccessibleActionInterface = 2  # 1 << 2
cAccessibleComponentInterface = 4  # 1 << 3
cAccessibleSelectionInterface = 8  # 1 << 4
cAccessibleTableInterface = 16  # 1 << 5
cAccessibleTextInterface = 32  # 1 << 6
cAccessibleHypertextInterface = 64  # 1 << 7

cMemoryMappedNameSize = 255


# Accessibility information bundles
class AccessBridgeVersionInfo(Structure):
    _fields_ = [
        ("VMVersion", wchar_t * SHORT_STRING_SIZE),  # output of "java -version"
        ("bridgeJavaClassVersion", wchar_t * SHORT_STRING_SIZE),  # version of the AccessBridge.class
        ("bridgeJavaDLLVersion", wchar_t * SHORT_STRING_SIZE),  # version of JavaAccessBridge.dll
        ("bridgeWinDLLVersion", wchar_t * SHORT_STRING_SIZE),  # version of WindowsAccessBridge.dll
    ]


class AccessibleContextInfo(Structure):
    _fields_ = [
        ("name", wchar_t * MAX_STRING_SIZE),  # the AccessibleName of the object
        ("description", wchar_t * MAX_STRING_SIZE),  # the AccessibleDescription of the object
        ("role", wchar_t * SHORT_STRING_SIZE),  # localized AccesibleRole string
        ("role_en_US", wchar_t * SHORT_STRING_SIZE),  # AccesibleRole string in the en_US locale
        ("states", wchar_t * SHORT_STRING_SIZE),  # localized AccesibleStateSet string (comma separated)
        ("states_en_US", wchar_t * SHORT_STRING_SIZE),  # AccesibleStateSet string in the en_US locale (comma separated)
        ("indexInParent", jint),  # index of object in parent
        ("childrenCount", jint),  # # of children, if any
        ("x", jint),  # screen coords in pixels
        ("y", jint),
        ("width", jint),  # pixel width of object
        ("height", jint),  # pixel height of object
        ("accessibleComponent", BOOL),  # flags for various additional
        ("accessibleAction", BOOL),  # Java Accessibility interfaces
        ("accessibleSelection", BOOL),  # FALSE if this object doesn't
        ("accessibleText", BOOL),  # implement the additional interface
        # ("accessibleValue", BOOL),  # old BOOL indicating whether AccessibleValue is supported
        ("accessibleInterfaces", BOOL),  # new bitfield containing additional interface flags
    ]


class AccessibleTextInfo(Structure):
    _fields_ = [
        ("charCount", jint),  # number of characters in the text
        ("caretIndex", jint),  # index of caret
        ("indexAtPoint", jint),  # index at the point
    ]


class AccessibleTextItemsInfo(Structure):
    _fields_ = [
        ("letter", wchar_t),  # letter at index
        ("word", wchar_t * SHORT_STRING_SIZE),  # word at index
        ("sentence", wchar_t * MAX_STRING_SIZE),  # sentence at index
    ]


class AccessibleTextSelectionInfo(Structure):
    _fields_ = [
        ("selectionStartIndex", jint),  # start of selection
        ("selectionEndIndex", jint),  # end of selection
        ("selectedText", wchar_t * MAX_STRING_SIZE),  # text of the selection
    ]


class AccessibleTextRectInfo(Structure):
    _fields_ = [
        ("x", jint),  # x coord of bounding rect
        ("y", jint),  # y coord of bounding rect
        ("width", jint),  # width of bounding rect
        ("height", jint),  # height of bounding rect
    ]


class AccessibleTextAttributesInfo(Structure):
    _fields_ = [
        ("bold", BOOL),  # is text bold?
        ("italic", BOOL),  # is text italic?
        ("underline", BOOL),  # is text underlined?
        ("strikethrough", BOOL),  # is text strikethrough?
        ("superscript", BOOL),  # is text superscript?
        ("subscript", BOOL),  # is text subscript?
        ("backgroundColor", wchar_t * SHORT_STRING_SIZE),  # background color
        ("foregroundColor", wchar_t * SHORT_STRING_SIZE),  # foreground color
        ("fontFamily", wchar_t * SHORT_STRING_SIZE),  # font family
        ("fontSize", jint),  # font size
        ("alignment", jint),  # alignment
        ("bidiLevel", jint),  # bidi level
        ("firstLineIndent", jfloat),  # first line indent
        ("leftIndent", jfloat),  # left indent
        ("rightIndent", jfloat),  # right indent
        ("lineSpacing", jfloat),  # line spacing
        ("spaceAbove", jfloat),  # space above
        ("spaceBelow", jfloat),  # space below
        ("fullAttributesString", wchar_t * MAX_STRING_SIZE),  # full attributes?
    ]


class AccessibleTableInfo(Structure):
    _fields_ = [
        ("caption", JOBJECT64),  # AccesibleContext
        ("summary", JOBJECT64),  # AccessibleContext
        ("rowCount", jint),
        ("columnCount", jint),
        ("accessibleContext", JOBJECT64),
        ("accessibleTable", JOBJECT64),
    ]


class AccessibleTableCellInfo(Structure):
    _fields_ = [
        ("accessibleContext", JOBJECT64),
        ("index", jint),
        ("row", jint),
        ("column", jint),
        ("rowExtent", jint),
        ("columnExtent", jint),
        ("isSelected", BOOL),
    ]


class AccessibleRelationInfo(Structure):
    _fields_ = [
        ("key", wchar_t * SHORT_STRING_SIZE),
        ("targetCount", jint),
        ("targets", JOBJECT64 * MAX_RELATION_TARGETS),
    ]


class AccessibleRelationSetInfo(Structure):
    _fields_ = [
        ("relationCount", jint),
        ("relations", AccessibleRelationInfo * MAX_RELATIONS),
    ]


class AccessibleHyperlinkInfo(Structure):
    _fields_ = [
        ("text", wchar_t * MAX_STRING_SIZE),
        ("startIndex", jint),
        ("endIndex", jint),
        ("accessibleHyperlink", JOBJECT64),
    ]


class AccessibleHypertextInfo(Structure):
    _fields_ = [
        ("linkCount", jint),
        ("links", AccessibleHyperlinkInfo * MAX_HYPERLINKS),
        ("accessibleHypertext", JOBJECT64),
    ]


class AccessibleKeyBindingInfo(Structure):
    _fields_ = [
        ("character", jchar),
        ("modifiers", jint),
    ]


class AccessibleKeyBindings(Structure):
    _fields_ = [
        ("keyBindingsCount", jint),
        ("keyBindingInfo", AccessibleKeyBindingInfo * MAX_KEY_BINDINGS),
    ]


class AccessibleIconInfo(Structure):
    _fields_ = [
        ("description", wchar_t * MAX_STRING_SIZE),
        ("height", jint),
        ("width", jint),
    ]


class AccessibleIcons(Structure):
    _fields_ = [
        ("iconsCount", jint),
        ("accessibleIcons", AccessibleIconInfo * MAX_ICON_INFO),
    ]


class AccessibleActionInfo(Structure):
    _fields_ = [
        ("name", wchar_t * SHORT_STRING_SIZE),
    ]


class AccessibleActions(Structure):
    _fields_ = [
        ("actionsCount", jint),
        ("actionInfo", AccessibleActionInfo * MAX_ACTION_INFO),
    ]


class AccessibleActionsToDo(Structure):
    _fields_ = [
        ("actionsCount", jint),
        ("actions", AccessibleActionInfo * MAX_ACTIONS_TO_DO),
    ]


class VisibleChildrenInfo(Structure):
    _fields_ = [
        ("returnedChildrenCount", c_int),
        ("children", AccessibleContext * MAX_VISIBLE_CHILDREN),
    ]


class JABLib:
    def __init__(self, dll_path=None):
        self._loaded: bool = False
        self._started: bool = False
        self._paths: list[tuple[str, str]] = []
        self._lib = None
        self.init()
        self.install()
        self.load(dll_path)
        self.start()

    def init(self):
        def _get_system_root_dir() -> Optional[str]:
            return os.environ.get("SYSTEMROOT") or "C:\\Windows"

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

        # https://docs.oracle.com/javase/accessbridge/2.0.2/setup.htm
        os_arch = platform.architecture()[0][:2]  # 32 or 64
        system_root_dir = _get_system_root_dir()
        java_home_dir = _get_java_home_dir()
        # Java Access Bridge File -> Destination Directory
        paths = [
            (f"WindowsAccessBridge-{os_arch}.dll", os.path.join(system_root_dir, "System32")),
            (f"JavaAccessBridge-{os_arch}.dll", os.path.join(java_home_dir, "bin")),
            (f"JAWTAccessBridge-{os_arch}.dll", os.path.join(java_home_dir, "bin")),
            (f"accessibility.properties", os.path.join(java_home_dir, "lib")),
            (f"access-bridge-{os_arch}.jar", os.path.join(java_home_dir, "lib", "ext")),
            (f"jaccess.jar", os.path.join(java_home_dir, "lib", "ext")),
        ]
        self._paths = paths

    def install(self):
        for fn, dst in self._paths:
            path = os.path.join(dst, fn)
            if not os.path.exists(path):
                shutil.copy(fn, path)

    def uninstall(self):
        for fn, dst in self._paths:
            path = os.path.join(dst, fn)
            if os.path.exists(path):
                os.remove(path)

    def load(self, dll_path):
        if self._loaded:
            return
        if not dll_path:
            dll_path = os.path.join(self._paths[0][1], self._paths[0][0])
        if not os.path.isfile(dll_path):
            raise FileNotFoundError(
                "WindowsAccessBridge dll not found, "
                "please set correct path for environment variable, "
                "or check the passed customized WindowsAccessBridge dll."
            )
        self._lib = cdll.LoadLibrary(dll_path)
        self._lib.Windows_run()
        self._loaded = True

    def start(self):
        if self._started:
            return

        import win32event
        import pythoncom
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
                    # Windows things to work properly!
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

    def stop(self):
        if self._lib:
            _ctypes.FreeLibrary(self._lib._handle)

    def releaseJavaObject(self, vmID: c_long, object: Java_Object):
        self._lib.releaseJavaObject(vmID, object)

    def getVersionInfo(self, vmID: c_long, info: AccessBridgeVersionInfo) -> BOOL:
        return self._lib.getVersionInfo(vmID, byref(info))

    def isJavaWindow(self, window: HWND) -> BOOL:
        return self._lib.isJavaWindow(window)

    def isSameObject(self, vmID: c_long, obj1: JOBJECT64, obj2: JOBJECT64) -> BOOL:
        return self._lib.isSameObject(vmID, obj1, obj2)

    def getAccessibleContextFromHWND(self, window: HWND, vmID: c_long, ac: AccessibleContext) -> BOOL:
        return self._lib.getAccessibleContextFromHWND(window, byref(vmID), byref(ac))

    def getHWNDFromAccessibleContext(self, vmID: c_long, ac: AccessibleContext) -> HWND:
        return self._lib.getHWNDFromAccessibleContext(vmID, byref(ac))

    def getAccessibleContextAt(self, vmID: c_long, acParent: AccessibleContext, x: jint, y: jint, ac: AccessibleContext) -> BOOL:
        return self._lib.getAccessibleContextAt(vmID, acParent, x, y, byref(ac))

    def getAccessibleContextWithFocus(self, window: HWND, vmID: c_long, ac: AccessibleContext) -> BOOL:
        return self._lib.getAccessibleContextWithFocus(window, byref(vmID), byref(ac))

    def getAccessibleContextInfo(self, vmID: c_long, ac: AccessibleContext, info: AccessibleContextInfo) -> BOOL:
        return self._lib.getAccessibleContextInfo(vmID, ac, byref(info))

    def getAccessibleChildFromContext(self, vmID: c_long, ac: AccessibleContext, index: jint) -> AccessibleContext:
        return self._lib.getAccessibleChildFromContext(vmID, ac, index)

    def getAccessibleParentFromContext(self, vmID: c_long, ac: AccessibleContext) -> AccessibleContext:
        return self._lib.getAccessibleParentFromContext(vmID, ac)

    def getAccessibleTableInfo(self, vmID: c_long, ac: AccessibleContext, tableInfo: AccessibleTableInfo) -> BOOL:
        return self._lib.getAccessibleTableInfo(vmID, ac, byref(tableInfo))

    def getAccessibleTableCellInfo(self, vmID: c_long, accessibleTable: AccessibleTable, row: jint, column: jint, tableCellInfo: AccessibleTableCellInfo) -> BOOL:
        return self._lib.getAccessibleTableCellInfo(vmID, accessibleTable, row, column, byref(tableCellInfo))

    def getAccessibleTableRowHeader(self, vmID: c_long, acParent: AccessibleContext, tableInfo: AccessibleTableInfo) -> BOOL:
        return self._lib.getAccessibleTableRowHeader(vmID, acParent, byref(tableInfo))

    def getAccessibleTableColumnHeader(self, vmID: c_long, acParent: AccessibleContext, tableInfo: AccessibleTableInfo) -> BOOL:
        return self._lib.getAccessibleTableColumnHeader(vmID, acParent, byref(tableInfo))

    def getAccessibleTableRowDescription(self, vmID: c_long, acParent: AccessibleContext, row: jint) -> AccessibleContext:
        return self._lib.getAccessibleTableRowDescription(vmID, acParent, row)

    def getAccessibleTableColumnDescription(self, vmID: c_long, acParent: AccessibleContext, column: jint) -> AccessibleContext:
        return self._lib.getAccessibleTableColumnDescription(vmID, acParent, column)

    def getAccessibleTableRowSelectionCount(self, vmID: c_long, table: AccessibleTable) -> jint:
        return self._lib.getAccessibleTableRowSelectionCount(vmID, table)

    def isAccessibleTableRowSelected(self, vmID: c_long, table: AccessibleTable, row: jint) -> BOOL:
        return self._lib.isAccessibleTableRowSelected(vmID, table, row)

    def getAccessibleTableRowSelections(self, vmID: c_long, table: AccessibleTable, count: jint, selections: jint) -> BOOL:
        return self._lib.getAccessibleTableRowSelections(vmID, table, count, byref(selections))

    def getAccessibleTableColumnSelectionCount(self, vmID: c_long, table: AccessibleTable) -> jint:
        return self._lib.getAccessibleTableColumnSelectionCount(vmID, table)

    def isAccessibleTableColumnSelected(self, vmID: c_long, table: AccessibleTable, column: jint) -> BOOL:
        return self._lib.isAccessibleTableColumnSelected(vmID, table, column)

    def getAccessibleTableColumnSelections(self, vmID: c_long, table: AccessibleTable, count: jint, selections: jint) -> BOOL:
        return self._lib.getAccessibleTableColumnSelections(vmID, table, count, byref(selections))

    def getAccessibleTableRow(self, vmID: c_long, table: AccessibleTable, index: jint) -> jint:
        return self._lib.getAccessibleTableRow(vmID, table, index)

    def getAccessibleTableColumn(self, vmID: c_long, table: AccessibleTable, index: jint) -> jint:
        return self._lib.getAccessibleTableColumn(vmID, table, index)

    def getAccessibleTableIndex(self, vmID: c_long, table: AccessibleTable, row: jint, column: jint) -> jint:
        return self._lib.getAccessibleTableIndex(vmID, table, row, column)

    def getAccessibleRelationSet(self, vmID: c_long, accessibleContext: AccessibleContext, relationSetInfo: AccessibleRelationSetInfo):
        return self._lib.getAccessibleRelationSet(vmID, accessibleContext, byref(relationSetInfo))

    def getAccessibleHypertext(self, vmID: c_long, accessibleContext: AccessibleContext, hypertextInfo: AccessibleHypertextInfo) -> BOOL:
        return self._lib.getAccessibleHypertext(vmID, accessibleContext, byref(hypertextInfo))

    def activateAccessibleHyperlink(self, vmID: c_long, accessibleContext: AccessibleContext, accessibleHyperlink: AccessibleHyperlink) -> BOOL:
        return self._lib.activateAccessibleHyperlink(vmID, accessibleContext, accessibleHyperlink)

    def getAccessibleHyperlinkCount(self, vmID: c_long, accessibleContext: AccessibleContext) -> jint:
        return self._lib.getAccessibleHyperlinkCount(vmID, accessibleContext)

    def getAccessibleHypertextExt(self, vmID: c_long, accessibleContext: AccessibleContext, nStartIndex: jint, hypertextInfo: AccessibleHypertextInfo) -> BOOL:
        return self._lib.getAccessibleHypertextExt(vmID, accessibleContext, nStartIndex, byref(hypertextInfo))

    def getAccessibleHypertextLinkIndex(self, vmID: c_long, hypertext: AccessibleHypertext, nIndex: jint) -> jint:
        return self._lib.getAccessibleHypertextLinkIndex(vmID, hypertext, nIndex)

    def getAccessibleHyperlink(self, vmID: c_long, hypertext: AccessibleHypertext, nIndex: jint, hyperlinkInfo: AccessibleHyperlinkInfo) -> BOOL:
        return self._lib.getAccessibleHyperlink(vmID, hypertext, nIndex, byref(hyperlinkInfo))

    def getAccessibleKeyBindings(self, vmID: c_long, accessibleContext: AccessibleContext, keyBindings: AccessibleKeyBindings) -> BOOL:
        return self._lib.getAccessibleKeyBindings(vmID, accessibleContext, byref(keyBindings))

    def getAccessibleIcons(self, vmID: c_long, accessibleContext: AccessibleContext, icons: AccessibleIcons) -> BOOL:
        return self._lib.getAccessibleIcons(vmID, accessibleContext, byref(icons))

    def getAccessibleActions(self, vmID: c_long, accessibleContext: AccessibleContext, actions: AccessibleActions) -> BOOL:
        return self._lib.getAccessibleActions(vmID, accessibleContext, byref(actions))

    def doAccessibleActions(self, vmID: c_long, accessibleContext: AccessibleContext, actionsToDo: AccessibleActionsToDo, failure: jint) -> BOOL:
        return self._lib.doAccessibleActions(vmID, accessibleContext, byref(actionsToDo), byref(failure))

    def getAccessibleTextInfo(self, vmID: c_long, at: AccessibleText, textInfo: AccessibleTextInfo, x: jint = 0, y: jint = 0) -> BOOL:
        return self._lib.getAccessibleTextInfo(vmID, at, byref(textInfo), x, y)

    def getAccessibleTextItems(self, vmID: c_long, at: AccessibleText, textItems: AccessibleTextItemsInfo, index: jint) -> BOOL:
        return self._lib.getAccessibleTextItems(vmID, at, byref(textItems), index)

    def getAccessibleTextSelectionInfo(self, vmID: c_long, at: AccessibleText, textSelection: AccessibleTextSelectionInfo) -> BOOL:
        return self._lib.getAccessibleTextSelectionInfo(vmID, at, byref(textSelection))

    def getAccessibleTextAttributes(self, vmID: c_long, at: AccessibleText, index: jint, attributes: AccessibleTextAttributesInfo) -> BOOL:
        return self._lib.getAccessibleTextAttributes(vmID, at, index, byref(attributes))

    def getAccessibleTextRect(self, vmID: c_long, at: AccessibleText, rectInfo: AccessibleTextRectInfo, index: jint) -> BOOL:
        return self._lib.getAccessibleTextRect(vmID, at, byref(rectInfo), index)

    def getAccessibleTextLineBounds(self, vmID: c_long, at: AccessibleText, index: jint, startIndex: jint, endIndex: jint) -> BOOL:
        return self._lib.getAccessibleTextLineBounds(vmID, at, index, byref(startIndex), byref(endIndex))

    def getAccessibleTextRange(self, vmID: c_long, at: AccessibleText, start: jint, end: jint, text: wchar_t, len: c_short) -> BOOL:
        return self._lib.getAccessibleTextRange(vmID, at, start, end, byref(text), len)

    def getCurrentAccessibleValueFromContext(self, vmID: c_long, av: AccessibleValue, value: wchar_t, len: c_short) -> BOOL:
        return self._lib.getCurrentAccessibleValueFromContext(vmID, av, byref(value), len)

    def getMaximumAccessibleValueFromContext(self, vmID: c_long, av: AccessibleValue, value: wchar_t, len: c_short) -> BOOL:
        return self._lib.getMaximumAccessibleValueFromContext(vmID, av, byref(value), len)

    def getMinimumAccessibleValueFromContext(self, vmID: c_long, av: AccessibleValue, value: wchar_t, len: c_short) -> BOOL:
        return self._lib.getMinimumAccessibleValueFromContext(vmID, av, byref(value), len)

    def addAccessibleSelectionFromContext(self, vmID: c_long, as_: AccessibleSelection, i: int):
        self._lib.addAccessibleSelectionFromContext(vmID, as_, i)

    def clearAccessibleSelectionFromContext(self, vmID: c_long, as_: AccessibleSelection):
        self._lib.clearAccessibleSelectionFromContext(vmID, as_)

    def getAccessibleSelectionFromContext(self, vmID: c_long, as_: AccessibleSelection, i: int) -> JOBJECT64:
        return self._lib.getAccessibleSelectionFromContext(vmID, as_, i)

    def getAccessibleSelectionCountFromContext(self, vmID: c_long, as_: AccessibleSelection) -> c_int:
        return self._lib.getAccessibleSelectionCountFromContext(vmID, as_)

    def isAccessibleChildSelectedFromContext(self, vmID: c_long, as_: AccessibleSelection, i: int) -> BOOL:
        return self._lib.isAccessibleChildSelectedFromContext(vmID, as_, i)

    def removeAccessibleSelectionFromContext(self, vmID: c_long, as_: AccessibleSelection, i: int):
        self._lib.removeAccessibleSelectionFromContext(vmID, as_, i)

    def selectAllAccessibleSelectionFromContext(self, vmID: c_long, as_: AccessibleSelection):
        self._lib.selectAllAccessibleSelectionFromContext(vmID, as_)

    def setTextContents(self, vmID: c_long, ac: AccessibleContext, text: c_wchar_p) -> BOOL:
        return self._lib.setTextContents(vmID, ac, text)

    def getParentWithRole(self, vmID: c_long, ac: AccessibleContext, role: wchar_t) -> AccessibleContext:
        return self._lib.getParentWithRole(vmID, ac, byref(role))

    def getTopLevelObject(self, vmID: c_long, ac: AccessibleContext) -> AccessibleContext:
        return self._lib.getTopLevelObject(vmID, ac)

    def getParentWithRoleElseRoot(self, vmID: c_long, ac: AccessibleContext, role: wchar_t) -> AccessibleContext:
        return self._lib.getParentWithRoleElseRoot(vmID, ac, byref(role))

    def getObjectDepth(self, vmID: c_long, ac: AccessibleContext) -> int:
        return self._lib.getObjectDepth(vmID, ac)

    def getActiveDescendent(self, vmID: c_long, ac: AccessibleContext) -> AccessibleContext:
        return self._lib.getActiveDescendent(vmID, ac)

    def getVirtualAccessibleName(self, vmID: c_long, accessibleContext: AccessibleContext, name: wchar_t, len: int) -> BOOL:
        return self._lib.getVirtualAccessibleName(vmID, accessibleContext, byref(name), len)

    def requestFocus(self, vmID: c_long, accessibleContext: AccessibleContext) -> BOOL:
        return self._lib.requestFocus(vmID, accessibleContext)

    def selectTextRange(self, vmID: c_long, accessibleContext: AccessibleContext, startIndex: int, endIndex: int) -> BOOL:
        return self._lib.selectTextRange(vmID, accessibleContext, startIndex, endIndex)

    def getTextAttributesInRange(self, vmID: c_long, accessibleContext: AccessibleContext, startIndex: int, endIndex: int, attributes: AccessibleTextAttributesInfo, len: c_short) -> BOOL:
        return self._lib.getTextAttributesInRange(vmID, accessibleContext, startIndex, endIndex, byref(attributes), byref(len))

    def getVisibleChildrenCount(self, vmID: c_long, accessibleContext: AccessibleContext) -> int:
        return self._lib.getVisibleChildrenCount(vmID, accessibleContext)

    def getVisibleChildren(self, vmID: c_long, accessibleContext: AccessibleContext, startIndex: int, children: VisibleChildrenInfo) -> BOOL:
        return self._lib.getVisibleChildren(vmID, accessibleContext, startIndex, byref(children))

    def setCaretPosition(self, vmID: c_long, accessibleContext: AccessibleContext, position: int) -> BOOL:
        return self._lib.setCaretPosition(vmID, accessibleContext, position)

    def getCaretLocation(self, vmID: c_long, ac: AccessibleContext, rectInfo: AccessibleTextRectInfo, index: jint) -> BOOL:
        return self._lib.getCaretLocation(vmID, ac, byref(rectInfo), index)

    def getEventsWaiting(self) -> c_int:
        return self._lib.getEventsWaiting()

    def setJavaShutdownFP(self, fp: Callable[[c_long], None]):
        functype = CFUNCTYPE(None, c_long)
        self._lib.setJavaShutdownFP(functype(fp))

    def setFocusGainedFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64], None]):
        functype = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64)
        self._lib.setFocusGainedFP(functype(fp))

    def setFocusLostFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64], None]):
        functype = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64)
        self._lib.setFocusLostFP(functype(fp))

    def setCaretUpdateFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64], None]):
        functype = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64)
        self._lib.setCaretUpdateFP(functype(fp))

    def setMouseClickedFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64], None]):
        functype = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64)
        self._lib.setMouseClickedFP(functype(fp))

    def setMouseEnteredFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64], None]):
        functype = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64)
        self._lib.setMouseEnteredFP(functype(fp))

    def setMouseExitedFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64], None]):
        functype = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64)
        self._lib.setMouseExitedFP(functype(fp))

    def setMousePressedFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64], None]):
        functype = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64)
        self._lib.setMousePressedFP(functype(fp))

    def setMouseReleasedFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64], None]):
        functype = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64)
        self._lib.setMouseReleasedFP(functype(fp))

    def setMenuCanceledFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64], None]):
        functype = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64)
        self._lib.setMenuCanceledFP(functype(fp))

    def setMenuDeselectedFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64], None]):
        functype = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64)
        self._lib.setMenuDeselectedFP(functype(fp))

    def setMenuSelectedFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64], None]):
        functype = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64)
        self._lib.setMenuSelectedFP(functype(fp))

    def setPopupMenuCanceledFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64], None]):
        functype = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64)
        self._lib.setPopupMenuCanceledFP(functype(fp))

    def setPopupMenuWillBecomeInvisibleFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64], None]):
        functype = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64)
        self._lib.setPopupMenuWillBecomeInvisibleFP(functype(fp))

    def setPopupMenuWillBecomeVisibleFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64], None]):
        functype = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64)
        self._lib.setPopupMenuWillBecomeVisibleFP(functype(fp))

    def setPropertyNameChangeFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64, wchar_t, wchar_t], None]):
        functype = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64, wchar_t, wchar_t)
        self._lib.setPropertyNameChangeFP(functype(fp))

    def setPropertyDescriptionChangeFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64, wchar_t, wchar_t], None]):
        functype = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64, wchar_t, wchar_t)
        self._lib.setPropertyDescriptionChangeFP(functype(fp))

    def setPropertyStateChangeFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64, wchar_t, wchar_t], None]):
        functype = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64, wchar_t, wchar_t)
        self._lib.setPropertyStateChangeFP(functype(fp))

    def setPropertyValueChangeFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64, wchar_t, wchar_t], None]):
        functype = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64, wchar_t, wchar_t)
        self._lib.setPropertyValueChangeFP(functype(fp))

    def setPropertySelectionChangeFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64], None]):
        functype = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64)
        self._lib.setPropertySelectionChangeFP(functype(fp))

    def setPropertyTextChangeFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64], None]):
        functype = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64)
        self._lib.setPropertyTextChangeFP(functype(fp))

    def setPropertyCaretChangeFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64, int, int], None]):
        functype = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64, int, int)
        self._lib.setPropertyCaretChangeFP(functype(fp))

    def setPropertyVisibleDataChangeFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64], None]):
        functype = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64)
        self._lib.setPropertyVisibleDataChangeFP(functype(fp))

    def setPropertyChildChangeFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64, JOBJECT64, JOBJECT64], None]):
        functype = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64, JOBJECT64, JOBJECT64)
        self._lib.setPropertyChildChangeFP(functype(fp))

    def setPropertyActiveDescendentChangeFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64, JOBJECT64, JOBJECT64], None]):
        functype = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64, JOBJECT64, JOBJECT64)
        self._lib.setPropertyActiveDescendentChangeFP(functype(fp))

    def setPropertyTableModelChangeFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64, wchar_t, wchar_t], None]):
        functype = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64, wchar_t, wchar_t)
        self._lib.setPropertyTableModelChangeFP(functype(fp))
