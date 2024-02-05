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
import zipfile
from ctypes import c_char, c_wchar, c_wchar_p, c_int, c_int64, c_float, c_long, c_short, c_void_p, cdll, byref, CFUNCTYPE, Structure, POINTER
from ctypes.wintypes import BOOL, HWND
from typing import Generator, Callable, Optional, Tuple, List

from echo.utils.singleton import singleton

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
        ("VMVersion", c_wchar * SHORT_STRING_SIZE),  # output of "java -version"
        ("bridgeJavaClassVersion", c_wchar * SHORT_STRING_SIZE),  # version of the AccessBridge.class
        ("bridgeJavaDLLVersion", c_wchar * SHORT_STRING_SIZE),  # version of JavaAccessBridge.dll
        ("bridgeWinDLLVersion", c_wchar * SHORT_STRING_SIZE),  # version of WindowsAccessBridge.dll
    ]


class AccessibleContextInfo(Structure):
    _fields_ = [
        ("name", c_wchar * MAX_STRING_SIZE),  # the AccessibleName of the object
        ("description", c_wchar * MAX_STRING_SIZE),  # the AccessibleDescription of the object
        ("role", c_wchar * SHORT_STRING_SIZE),  # localized AccessibleRole string
        ("role_en_US", c_wchar * SHORT_STRING_SIZE),  # AccessibleRole string in the en_US locale
        ("states", c_wchar * SHORT_STRING_SIZE),  # localized AccessibleStateSet string (comma separated)
        ("states_en_US", c_wchar * SHORT_STRING_SIZE),  # AccessibleStateSet string in the en_US locale (comma separated)
        ("indexInParent", c_int),  # index of object in parent
        ("childrenCount", c_int),  # # of children, if any
        ("x", c_int),  # screen coords in pixels
        ("y", c_int),
        ("width", c_int),  # pixel width of object
        ("height", c_int),  # pixel height of object
        ("accessibleComponent", BOOL),  # flags for various additional
        ("accessibleAction", BOOL),  # Java Accessibility interfaces
        ("accessibleSelection", BOOL),  # FALSE if this object doesn't
        ("accessibleText", BOOL),  # implement the additional interface
        # ("accessibleValue", BOOL),  # old BOOL indicating whether AccessibleValue is supported
        ("accessibleInterfaces", BOOL),  # new bitfield containing additional interface flags
    ]


class AccessibleTextInfo(Structure):
    _fields_ = [
        ("charCount", c_int),  # number of characters in the text
        ("caretIndex", c_int),  # index of caret
        ("indexAtPoint", c_int),  # index at the point
    ]


class AccessibleTextItemsInfo(Structure):
    _fields_ = [
        ("letter", c_wchar),  # letter at index
        ("word", c_wchar * SHORT_STRING_SIZE),  # word at index
        ("sentence", c_wchar * MAX_STRING_SIZE),  # sentence at index
    ]


class AccessibleTextSelectionInfo(Structure):
    _fields_ = [
        ("selectionStartIndex", c_int),  # start of selection
        ("selectionEndIndex", c_int),  # end of selection
        ("selectedText", c_wchar * MAX_STRING_SIZE),  # text of the selection
    ]


class AccessibleTextRectInfo(Structure):
    _fields_ = [
        ("x", c_int),  # x coord of bounding rect
        ("y", c_int),  # y coord of bounding rect
        ("width", c_int),  # width of bounding rect
        ("height", c_int),  # height of bounding rect
    ]


class AccessibleTextAttributesInfo(Structure):
    _fields_ = [
        ("bold", BOOL),  # is text bold?
        ("italic", BOOL),  # is text italic?
        ("underline", BOOL),  # is text underlined?
        ("strikethrough", BOOL),  # is text strikethrough?
        ("superscript", BOOL),  # is text superscript?
        ("subscript", BOOL),  # is text subscript?
        ("backgroundColor", c_wchar * SHORT_STRING_SIZE),  # background color
        ("foregroundColor", c_wchar * SHORT_STRING_SIZE),  # foreground color
        ("fontFamily", c_wchar * SHORT_STRING_SIZE),  # font family
        ("fontSize", c_int),  # font size
        ("alignment", c_int),  # alignment
        ("bidiLevel", c_int),  # bidi level
        ("firstLineIndent", c_float),  # first line indent
        ("leftIndent", c_float),  # left indent
        ("rightIndent", c_float),  # right indent
        ("lineSpacing", c_float),  # line spacing
        ("spaceAbove", c_float),  # space above
        ("spaceBelow", c_float),  # space below
        ("fullAttributesString", c_wchar * MAX_STRING_SIZE),  # full attributes?
    ]


class AccessibleTableInfo(Structure):
    _fields_ = [
        ("caption", JOBJECT64),  # AccessibleContext
        ("summary", JOBJECT64),  # AccessibleContext
        ("rowCount", c_int),
        ("columnCount", c_int),
        ("accessibleContext", JOBJECT64),
        ("accessibleTable", JOBJECT64),
    ]


class AccessibleTableCellInfo(Structure):
    _fields_ = [
        ("accessibleContext", JOBJECT64),
        ("index", c_int),
        ("row", c_int),
        ("column", c_int),
        ("rowExtent", c_int),
        ("columnExtent", c_int),
        ("isSelected", BOOL),
    ]


class AccessibleRelationInfo(Structure):
    _fields_ = [
        ("key", c_wchar * SHORT_STRING_SIZE),
        ("targetCount", c_int),
        ("targets", JOBJECT64 * MAX_RELATION_TARGETS),
    ]


class AccessibleRelationSetInfo(Structure):
    _fields_ = [
        ("relationCount", c_int),
        ("relations", AccessibleRelationInfo * MAX_RELATIONS),
    ]


class AccessibleHyperlinkInfo(Structure):
    _fields_ = [
        ("text", c_wchar * MAX_STRING_SIZE),
        ("startIndex", c_int),
        ("endIndex", c_int),
        ("accessibleHyperlink", JOBJECT64),
    ]


class AccessibleHypertextInfo(Structure):
    _fields_ = [
        ("linkCount", c_int),
        ("links", AccessibleHyperlinkInfo * MAX_HYPERLINKS),
        ("accessibleHypertext", JOBJECT64),
    ]


class AccessibleKeyBindingInfo(Structure):
    _fields_ = [
        ("character", c_char),
        ("modifiers", c_int),
    ]


class AccessibleKeyBindings(Structure):
    _fields_ = [
        ("keyBindingsCount", c_int),
        ("keyBindingInfo", AccessibleKeyBindingInfo * MAX_KEY_BINDINGS),
    ]


class AccessibleIconInfo(Structure):
    _fields_ = [
        ("description", c_wchar * MAX_STRING_SIZE),
        ("height", c_int),
        ("width", c_int),
    ]


class AccessibleIcons(Structure):
    _fields_ = [
        ("iconsCount", c_int),
        ("accessibleIcons", AccessibleIconInfo * MAX_ICON_INFO),
    ]


class AccessibleActionInfo(Structure):
    _fields_ = [
        ("name", c_wchar * SHORT_STRING_SIZE),
    ]


class AccessibleActions(Structure):
    _fields_ = [
        ("actionsCount", c_int),
        ("actionInfo", AccessibleActionInfo * MAX_ACTION_INFO),
    ]


class AccessibleActionsToDo(Structure):
    _fields_ = [
        ("actionsCount", c_int),
        ("actions", AccessibleActionInfo * MAX_ACTIONS_TO_DO),
    ]


class VisibleChildrenInfo(Structure):
    _fields_ = [
        ("returnedChildrenCount", c_int),
        ("children", AccessibleContext * MAX_VISIBLE_CHILDREN),
    ]


JavaShutdownFP = CFUNCTYPE(None, c_long)
FocusGainedFP = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64)
FocusLostFP = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64)
CaretUpdateFP = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64)
MouseClickedFP = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64)
MouseEnteredFP = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64)
MouseExitedFP = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64)
MousePressedFP = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64)
MouseReleasedFP = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64)
MenuCanceledFP = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64)
MenuDeselectedFP = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64)
MenuSelectedFP = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64)
PopupMenuCanceledFP = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64)
PopupMenuWillBecomeInvisibleFP = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64)
PopupMenuWillBecomeVisibleFP = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64)
PropertyChangeFP = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64, c_wchar_p, c_wchar_p, c_wchar_p)
PropertyNameChangeFP = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64, c_wchar_p, c_wchar_p)
PropertyDescriptionChangeFP = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64, c_wchar_p, c_wchar_p)
PropertyStateChangeFP = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64, c_wchar_p, c_wchar_p)
PropertyValueChangeFP = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64, c_wchar_p, c_wchar_p)
PropertySelectionChangeFP = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64)
PropertyTextChangedFP = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64)
PropertyCaretChangeFP = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64, c_int, c_int)
PropertyVisibleDataChangeFP = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64)
PropertyChildChangeFP = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64, JOBJECT64, JOBJECT64)
PropertyActiveDescendentChangeFP = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64, JOBJECT64, JOBJECT64)
PropertyTableModelChangeFP = CFUNCTYPE(None, c_long, JOBJECT64, JOBJECT64, c_wchar_p, c_wchar_p)


@singleton
class JABLib:
    def __init__(self, dll_path=None):
        self._loaded: bool = False
        self._started: bool = False
        self._paths: List[Tuple[str, str]] = []
        self._dll = None
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
        cur_dir = os.path.dirname(__file__)
        lib_dir = os.path.join(cur_dir, "lib")
        lib_zip = os.path.join(cur_dir, "lib.zip")
        for fn, dst in self._paths:
            dst_path = os.path.join(dst, fn)
            if os.path.exists(dst_path):
                continue
            # copy if target files do not exist
            src_path = os.path.join(lib_dir, fn)
            # unzip if source files do not exist
            if not os.path.exists(src_path):
                with zipfile.ZipFile(lib_zip, 'r') as f:
                    f.extractall(cur_dir)
            shutil.copy(src_path, dst_path)

    def uninstall(self):
        for fn, dst in self._paths:
            dst_path = os.path.join(dst, fn)
            if os.path.exists(dst_path):
                os.remove(dst_path)

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
        self._dll = cdll.LoadLibrary(dll_path)
        self._define_functions()
        self._define_callbacks()
        self._loaded = True

    def start(self):
        if self._started:
            return

        self._dll.Windows_run()

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
        if self._dll:
            _ctypes.FreeLibrary(self._dll._handle)

    def _define_functions(self):
        # void Windows_run()
        self._dll.Windows_run.argtypes = []
        self._dll.Windows_run.restype = None

        # void ReleaseJavaObject(long vmID, JOBJECT64 object)
        self._dll.releaseJavaObject.argtypes = [c_long, JOBJECT64]
        self._dll.releaseJavaObject.restype = None

        # BOOL GetVersionInfo(long vmID, AccessBridgeVersionInfo *info)
        self._dll.getVersionInfo.argtypes = [c_long, POINTER(AccessBridgeVersionInfo)]
        self._dll.getVersionInfo.restype = BOOL

        # Accessible context
        # BOOL isJavaWindow(HWND window)
        self._dll.isJavaWindow.argtypes = [HWND]
        self._dll.isJavaWindow.restype = BOOL
        # BOOL isSameObject(long vmID, JOBJECT64 obj1, JOBJECT64 obj2)
        self._dll.isSameObject.argtypes = [c_long, JOBJECT64, JOBJECT64]
        self._dll.isSameObject.restype = BOOL
        # BOOL GetAccessibleContextFromHWND(HWND window, long *vmID, AccessibleContext *ac)
        self._dll.getAccessibleContextFromHWND.argtypes = [HWND, POINTER(c_long), POINTER(AccessibleContext)]
        self._dll.getAccessibleContextFromHWND.restype = BOOL
        # HWND getHWNDFromAccessibleContext(long vmID, AccessibleContext ac)
        self._dll.getHWNDFromAccessibleContext.argtypes = [c_long, AccessibleContext]
        self._dll.getHWNDFromAccessibleContext.restype = HWND
        # BOOL getAccessibleContextAt(long vmID, AccessibleContext acParent, int x, int y, AccessibleContext *ac)
        self._dll.getAccessibleContextAt.argtypes = [c_long, AccessibleContext, c_int, c_int, POINTER(AccessibleContext)]
        self._dll.getAccessibleContextAt.restype = BOOL
        # BOOL GetAccessibleContextWithFocus(HWND window, long *vmID, AccessibleContext *ac)
        self._dll.getAccessibleContextWithFocus.argtypes = [HWND, c_long, POINTER(AccessibleContext)]
        self._dll.getAccessibleContextWithFocus.restype = BOOL
        # BOOL getAccessibleContextInfo(long vmID, AccessibleContext ac, AccessibleContextInfo *info)
        self._dll.getAccessibleContextInfo.argtypes = [c_long, AccessibleContext, POINTER(AccessibleContextInfo)]
        self._dll.getAccessibleContextInfo.restype = BOOL
        # AccessibleContext getAccessibleChildFromContext(long vmID, AccessibleContext ac, int i)
        self._dll.getAccessibleChildFromContext.argtypes = [c_long, AccessibleContext, c_int]
        self._dll.getAccessibleChildFromContext.restype = AccessibleContext
        # AccessibleContext getAccessibleParentFromContext(long vmID, AccessibleContext ac)
        self._dll.getAccessibleParentFromContext.argtypes = [c_long, AccessibleContext]
        self._dll.getAccessibleParentFromContext.restype = AccessibleContext

        # Accessible table
        # BOOL getAccessibleTableInfo(long vmID, AccessibleContext ac, AccessibleTableInfo *tableInfo)
        self._dll.getAccessibleTableInfo.argtypes = [c_long, AccessibleContext, POINTER(AccessibleTableInfo)]
        self._dll.getAccessibleTableInfo.restype = BOOL
        # BOOL getAccessibleTableCellInfo(long vmID, AccessibleTable accessibleTable, int row, int column, AccessibleTableCellInfo *tableCellInfo)
        self._dll.getAccessibleTableCellInfo.argtypes = [c_long, AccessibleTable, c_int, c_int, POINTER(AccessibleTableCellInfo)]
        self._dll.getAccessibleTableCellInfo.restype = BOOL
        # BOOL getAccessibleTableRowHeader(long vmID, AccessibleContext acParent, AccessibleTableInfo *tableInfo)
        self._dll.getAccessibleTableRowHeader.argtypes = [c_long, AccessibleContext, POINTER(AccessibleTableInfo)]
        self._dll.getAccessibleTableRowHeader.restype = BOOL
        # BOOL getAccessibleTableColumnHeader(long vmID, AccessibleContext acParent, AccessibleTableInfo *tableInfo)
        self._dll.getAccessibleTableColumnHeader.argtypes = [c_long, AccessibleContext, POINTER(AccessibleTableInfo)]
        self._dll.getAccessibleTableColumnHeader.restype = BOOL
        # AccessibleContext getAccessibleTableRowDescription(long vmID, AccessibleContext acParent, int row)
        self._dll.getAccessibleTableRowDescription.argtypes = [c_long, AccessibleContext, c_int]
        self._dll.getAccessibleTableRowDescription.restype = AccessibleContext
        # AccessibleContext getAccessibleTableColumnDescription(long vmID, AccessibleContext acParent, int row)
        self._dll.getAccessibleTableColumnDescription.argtypes = [c_long, AccessibleContext, c_int]
        self._dll.getAccessibleTableColumnDescription.restype = AccessibleContext
        # int getAccessibleTableRowSelectionCount(long vmID, AccessibleTable table)
        self._dll.getAccessibleTableRowSelectionCount.argtypes = [c_long, AccessibleTable]
        self._dll.getAccessibleTableRowSelectionCount.restype = c_int
        # BOOL isAccessibleTableRowSelected(long vmID, AccessibleTable table, int row)
        self._dll.isAccessibleTableRowSelected.argtypes = [c_long, AccessibleTable, c_int]
        self._dll.isAccessibleTableRowSelected.restype = BOOL
        # BOOL getAccessibleTableRowSelections(long vmID, AccessibleTable table, int count, int *selections)
        self._dll.getAccessibleTableRowSelections.argtypes = [c_long, AccessibleTable, c_int, POINTER(c_int)]
        self._dll.getAccessibleTableRowSelections.restype = BOOL
        # int getAccessibleTableColumnSelectionCount(long vmID, AccessibleTable table)
        self._dll.getAccessibleTableColumnSelectionCount.argtypes = [c_long, AccessibleTable]
        self._dll.getAccessibleTableColumnSelectionCount.restype = c_int
        # BOOL isAccessibleTableColumnSelected(long vmID, AccessibleTable table, int column)
        self._dll.isAccessibleTableColumnSelected.argtypes = [c_long, AccessibleTable, c_int]
        self._dll.isAccessibleTableColumnSelected.restype = BOOL
        # BOOL getAccessibleTableColumnSelections(long vmID, AccessibleTable table, int count, int *selections)
        self._dll.getAccessibleTableColumnSelections.argtypes = [c_long, AccessibleTable, c_int, POINTER(c_int)]
        self._dll.getAccessibleTableColumnSelections.restype = BOOL
        # int getAccessibleTableRow(long vmID, AccessibleTable table, int index)
        self._dll.getAccessibleTableRow.argtypes = [c_long, AccessibleTable, c_int]
        self._dll.getAccessibleTableRow.restype = c_int
        # int getAccessibleTableColumn(long vmID, AccessibleTable table, int index)
        self._dll.getAccessibleTableColumn.argtypes = [c_long, AccessibleTable, c_int]
        self._dll.getAccessibleTableColumn.restype = c_int
        # int getAccessibleTableIndex(long vmID, AccessibleTable table, int row, int column)
        self._dll.getAccessibleTableIndex.argtypes = [c_long, AccessibleTable, c_int, c_int]
        self._dll.getAccessibleTableIndex.restype = c_int

        # AccessibleRelationSet
        # BOOL getAccessibleRelationSet(long vmID, AccessibleContext accessibleContext, AccessibleRelationSetInfo *relationSetInfo)
        self._dll.getAccessibleRelationSet.argtypes = [c_long, AccessibleContext, POINTER(AccessibleRelationSetInfo)]
        self._dll.getAccessibleRelationSet.restype = BOOL

        # AccessibleHypertext
        # BOOL getAccessibleHypertext(long vmID, AccessibleContext accessibleContext, AccessibleHypertextInfo *hypertextInfo)
        self._dll.getAccessibleHypertext.argtypes = [c_long, AccessibleContext, POINTER(AccessibleHypertextInfo)]
        self._dll.getAccessibleHypertext.restype = BOOL
        # BOOL activateAccessibleHyperlink(long vmID, AccessibleContext accessibleContext, AccessibleHyperlink accessibleHyperlink)
        self._dll.activateAccessibleHyperlink.argtypes = [c_long, AccessibleContext, AccessibleHyperlink]
        self._dll.activateAccessibleHyperlink.restype = BOOL
        # int getAccessibleHyperlinkCount(long vmID, AccessibleContext accessibleContext)
        self._dll.getAccessibleHyperlinkCount.argtypes = [c_long, AccessibleContext]
        self._dll.getAccessibleHyperlinkCount.restype = c_int
        # BOOL getAccessibleHypertextExt(long vmID, AccessibleContext accessibleContext, int nStartIndex, AccessibleHypertextInfo *hypertextInfo)
        self._dll.getAccessibleHypertextExt.argtypes = [c_long, AccessibleContext, c_int, POINTER(AccessibleHypertextInfo)]
        self._dll.getAccessibleHypertextExt.restype = BOOL
        # int getAccessibleHypertextLinkIndex(long vmID, AccessibleHypertext hypertext, int nIndex)
        self._dll.getAccessibleHypertextLinkIndex.argtypes = [c_long, AccessibleHypertext, c_int]
        self._dll.getAccessibleHypertextLinkIndex.restype = c_int
        # BOOL getAccessibleHyperlink(long vmID, AccessibleHypertext hypertext, int nIndex, AccessibleHyperlinkInfo *hyperlinkInfo)
        self._dll.getAccessibleHyperlink.argtypes = [c_long, AccessibleHypertext, c_int, POINTER(AccessibleHyperlinkInfo)]
        self._dll.getAccessibleHyperlink.restype = BOOL

        # Accessible KeyBindings, Icons and Actions
        # BOOL getAccessibleKeyBindings(long vmID, AccessibleContext accessibleContext, AccessibleKeyBindings *keyBindings)
        self._dll.getAccessibleKeyBindings.argtypes = [c_long, AccessibleContext, POINTER(AccessibleKeyBindings)]
        self._dll.getAccessibleKeyBindings.restype = BOOL
        # BOOL getAccessibleIcons(long vmID, AccessibleContext accessibleContext, AccessibleIcons *icons)
        self._dll.getAccessibleIcons.argtypes = [c_long, AccessibleContext, POINTER(AccessibleIcons)]
        self._dll.getAccessibleIcons.restype = BOOL
        # BOOL getAccessibleActions(long vmID, AccessibleContext accessibleContext, AccessibleActions *actions)
        self._dll.getAccessibleActions.argtypes = [c_long, AccessibleContext, POINTER(AccessibleActions)]
        self._dll.getAccessibleActions.restype = BOOL
        # BOOL doAccessibleActions(long vmID, AccessibleContext accessibleContext, AccessibleActionsToDo *actionsToDo, int *failure_index)
        self._dll.doAccessibleActions.argtypes = [c_long, AccessibleContext, POINTER(AccessibleActionsToDo), POINTER(c_int)]
        self._dll.doAccessibleActions.restype = BOOL

        # AccessibleText
        # BOOL GetAccessibleTextInfo(long vmID, AccessibleContext at, AccessibleTextInfo *info, int x, int y)
        self._dll.getAccessibleTextInfo.argtypes = [c_long, AccessibleText, POINTER(AccessibleTextInfo), c_int, c_int]
        self._dll.getAccessibleTextInfo.restype = BOOL
        # BOOL GetAccessibleTextItems(long vmID, AccessibleContext at, AccessibleTextItemsInfo *textItems, int index)
        self._dll.getAccessibleTextItems.argtypes = [c_long, AccessibleText, POINTER(AccessibleTextItemsInfo), c_int]
        self._dll.getAccessibleTextItems.restype = BOOL
        # BOOL GetAccessibleTextSelectionInfo(long vmID, AccessibleContext at, AccessibleTextSelectionInfo *textSelection)
        self._dll.getAccessibleTextSelectionInfo.argtypes = [c_long, AccessibleText, POINTER(AccessibleTextSelectionInfo)]
        self._dll.getAccessibleTextSelectionInfo.restype = BOOL
        # BOOL getAccessibleTextAttributes(long vmID, AccessibleContext at, int index, AccessibleTextAttributesInfo *attributesInfo)
        self._dll.getAccessibleTextAttributes.argtypes = [c_long, AccessibleText, c_int, POINTER(AccessibleTextAttributesInfo)]
        self._dll.getAccessibleTextAttributes.restype = BOOL
        # BOOL getAccessibleTextRect(long vmID, AccessibleContext at, AccessibleTextRectInfo *rectInfo, int index)
        self._dll.getAccessibleTextRect.argtypes = [c_long, AccessibleText, POINTER(AccessibleTextRectInfo), c_int]
        self._dll.getAccessibleTextRect.restype = BOOL
        # BOOL getAccessibleTextLineBounds(long vmID, AccessibleContext at, int index, int *startIndex, int *endIndex)
        self._dll.getAccessibleTextLineBounds.argtypes = [c_long, AccessibleText, c_int, POINTER(c_int), POINTER(c_int)]
        self._dll.getAccessibleTextLineBounds.restype = BOOL
        # BOOL getAccessibleTextRange(long vmID, AccessibleContext at, int start, int end, c_wchar *text, short len)
        self._dll.getAccessibleTextRange.argtypes = [c_long, AccessibleText, c_int, c_int, c_wchar_p, c_short]
        self._dll.getAccessibleTextRange.restype = BOOL

        # AccessibleValue
        # BOOL getCurrentAccessibleValueFromContext(long vmID, AccessibleValue av, c_wchar *value, short len)
        self._dll.getCurrentAccessibleValueFromContext.argtypes = [c_long, AccessibleValue, c_wchar_p, c_short]
        self._dll.getCurrentAccessibleValueFromContext.restype = BOOL
        # BOOL getMaximumAccessibleValueFromContext(long vmID, AccessibleValue av, c_wchar *value, short len)
        self._dll.getMaximumAccessibleValueFromContext.argtypes = [c_long, AccessibleValue, c_wchar_p, c_short]
        self._dll.getMaximumAccessibleValueFromContext.restype = BOOL
        # BOOL getMinimumAccessibleValueFromContext(long vmID, aAccessibleValue av, c_wchar *value, short len)
        self._dll.getMinimumAccessibleValueFromContext.argtypes = [c_long, AccessibleValue, c_wchar_p, c_short]
        self._dll.getMinimumAccessibleValueFromContext.restype = BOOL

        # AccessibleSelection
        # void addAccessibleSelectionFromContext(long vmID, AccessibleSelection as, int i)
        self._dll.addAccessibleSelectionFromContext.argtypes = [c_long, AccessibleSelection, c_int]
        self._dll.addAccessibleSelectionFromContext.restype = None
        # void clearAccessibleSelectionFromContext(long vmID, AccessibleSelection as)
        self._dll.clearAccessibleSelectionFromContext.argtypes = [c_long, AccessibleSelection]
        self._dll.clearAccessibleSelectionFromContext.restype = None
        # JOBJECT64 getAccessibleSelectionFromContext(long vmID, AccessibleSelection as, int i)
        self._dll.getAccessibleSelectionFromContext.argtypes = [c_long, AccessibleSelection, c_int]
        self._dll.getAccessibleSelectionFromContext.restype = JOBJECT64
        # int getAccessibleSelectionCountFromContext(long vmID, AccessibleContext as)
        self._dll.getAccessibleSelectionCountFromContext.argtypes = [c_long, AccessibleSelection]
        self._dll.getAccessibleSelectionCountFromContext.restype = c_int
        # BOOL isAccessibleChildSelectedFromContext(long vmID, AccessibleSelection as, int i)
        self._dll.isAccessibleChildSelectedFromContext.argtypes = [c_long, AccessibleSelection, c_int]
        self._dll.isAccessibleChildSelectedFromContext.restype = BOOL
        # void removeAccessibleSelectionFromContext(long vmID, AccessibleSelection as, int i)
        self._dll.removeAccessibleSelectionFromContext.argtypes = [c_long, AccessibleSelection, c_int]
        self._dll.removeAccessibleSelectionFromContext.restype = None
        # void selectAllAccessibleSelectionFromContext(long vmID, AccessibleSelection as)
        self._dll.selectAllAccessibleSelectionFromContext.argtypes = [c_long, AccessibleSelection]
        self._dll.selectAllAccessibleSelectionFromContext.restype = None

        # Utility
        # BOOL setTextContents(long vmID, AccessibleContext ac, c_wchar *text)
        self._dll.setTextContents.argtypes = [c_long, AccessibleContext, c_wchar_p]
        self._dll.setTextContents.restype = BOOL
        # AccessibleContext getParentWithRole(long vmID, AccessibleContext ac, c_wchar *role)
        self._dll.getParentWithRole.argtypes = [c_long, AccessibleContext, c_wchar_p]
        self._dll.getParentWithRole.restype = AccessibleContext
        # AccessibleContext getParentWithRoleElseRoot(long vmID, AccessibleContext ac, c_wchar *role)
        self._dll.getParentWithRoleElseRoot.argtypes = [c_long, AccessibleContext, c_wchar_p]
        self._dll.getParentWithRoleElseRoot.restype = AccessibleContext
        # AccessibleContext getTopLevelObject(long vmID, AccessibleContext ac)
        self._dll.getTopLevelObject.argtypes = [c_long, AccessibleContext]
        self._dll.getTopLevelObject.restype = AccessibleContext
        # int getObjectDepth(long vmID, AccessibleContext ac)
        self._dll.getObjectDepth.argtypes = [c_long, AccessibleContext]
        self._dll.getObjectDepth.restype = c_int
        # AccessibleContext getActiveDescendent(long vmID, AccessibleContext ac)
        self._dll.getActiveDescendent.argtypes = [c_long, AccessibleContext]
        self._dll.getActiveDescendent.restype = AccessibleContext

        # BOOL getVirtualAccessibleNameFP(long vmID, AccessibleContext context, c_wchar *name, int len)
        self._dll.getVirtualAccessibleName.argtypes = [c_long, AccessibleContext, c_wchar_p, c_int]
        self._dll.getVirtualAccessibleName.restype = BOOL
        # BOOL requestFocus(long vmID, AccessibleContext context)
        self._dll.requestFocus.argtypes = [c_long, AccessibleContext]
        self._dll.requestFocus.restype = BOOL
        # BOOL selectTextRange(long vmID, AccessibleContext context, int startIndex, int endIndex)
        self._dll.selectTextRange.argtypes = [c_long, AccessibleContext, c_int, c_int]
        self._dll.selectTextRange.restype = BOOL
        # BOOL getTextAttributesInRange(long vmID, AccessibleContext context, int startIndex, int endIndex, AccessibleTextAttributesInfo *attributes, short *len)
        self._dll.getTextAttributesInRange.argtypes = [c_long, AccessibleContext, c_int, c_int, POINTER(AccessibleTextAttributesInfo), POINTER(c_short)]
        self._dll.getTextAttributesInRange.restype = BOOL
        # int getVisibleChildrenCount(long vmID, AccessibleContext context)
        self._dll.getVisibleChildrenCount.argtypes = [c_long, AccessibleContext]
        self._dll.getVisibleChildrenCount.restype = c_int
        # BOOL getVisibleChildren(long vmID, AccessibleContext context, int startIndex, VisibleChildrenInfo *children)
        self._dll.getVisibleChildren.argtypes = [c_long, AccessibleContext, c_int, POINTER(VisibleChildrenInfo)]
        self._dll.getVisibleChildren.restype = BOOL
        # BOOL setCaretPosition(long vmID, AccessibleContext context, int position)
        self._dll.setCaretPosition.argtypes = [c_long, AccessibleContext, c_int]
        self._dll.setCaretPosition.restype = BOOL
        # BOOL getCaretLocation(long vmID, AccessibleContext context, AccessibleTextRectInfo *rectInfo, int index)
        self._dll.getCaretLocation.argtypes = [c_long, AccessibleContext, POINTER(AccessibleTextRectInfo), c_int]
        self._dll.getCaretLocation.restype = BOOL
        # int getEventsWaiting()
        self._dll.getEventsWaiting.argtypes = []
        self._dll.getEventsWaiting.restype = c_int

    def _define_callbacks(self):
        # Property events
        self._dll.setPropertyChangeFP.argtypes = [c_void_p]
        self._dll.setPropertyChangeFP.restype = None
        self._dll.setPropertyNameChangeFP.argtypes = [c_void_p]
        self._dll.setPropertyNameChangeFP.restype = None
        self._dll.setPropertyDescriptionChangeFP.argtypes = [c_void_p]
        self._dll.setPropertyDescriptionChangeFP.restype = None
        self._dll.setPropertyStateChangeFP.argtypes = [c_void_p]
        self._dll.setPropertyStateChangeFP.restype = None
        self._dll.setPropertyValueChangeFP.argtypes = [c_void_p]
        self._dll.setPropertyValueChangeFP.restype = None
        self._dll.setPropertySelectionChangeFP.argtypes = [c_void_p]
        self._dll.setPropertySelectionChangeFP.restype = None
        self._dll.setPropertyTextChangeFP.argtypes = [c_void_p]
        self._dll.setPropertyTextChangeFP.restype = None
        self._dll.setPropertyCaretChangeFP.argtypes = [c_void_p]
        self._dll.setPropertyCaretChangeFP.restype = None
        self._dll.setPropertyVisibleDataChangeFP.argtypes = [c_void_p]
        self._dll.setPropertyVisibleDataChangeFP.restype = None
        self._dll.setPropertyChildChangeFP.argtypes = [c_void_p]
        self._dll.setPropertyChildChangeFP.restype = None
        self._dll.setPropertyActiveDescendentChangeFP.argtypes = [c_void_p]
        self._dll.setPropertyActiveDescendentChangeFP.restype = None
        self._dll.setPropertyTableModelChangeFP.argtypes = [c_void_p]
        self._dll.setPropertyTableModelChangeFP.restype = None
        # Menu events
        self._dll.setMenuSelectedFP.argtypes = [c_void_p]
        self._dll.setMenuSelectedFP.restype = None
        self._dll.setMenuDeselectedFP.argtypes = [c_void_p]
        self._dll.setMenuDeselectedFP.restype = None
        self._dll.setMenuCanceledFP.argtypes = [c_void_p]
        self._dll.setMenuCanceledFP.restype = None
        # Focus events
        self._dll.setFocusGainedFP.argtypes = [c_void_p]
        self._dll.setFocusGainedFP.restype = None
        self._dll.setFocusLostFP.argtypes = [c_void_p]
        self._dll.setFocusLostFP.restype = None
        # Caret update events
        self._dll.setCaretUpdateFP.argtypes = [c_void_p]
        self._dll.setCaretUpdateFP.restype = None
        # Mouse events
        self._dll.setMouseClickedFP.argtypes = [c_void_p]
        self._dll.setMouseClickedFP.restype = None
        self._dll.setMouseEnteredFP.argtypes = [c_void_p]
        self._dll.setMouseEnteredFP.restype = None
        self._dll.setMouseExitedFP.argtypes = [c_void_p]
        self._dll.setMouseExitedFP.restype = None
        self._dll.setMousePressedFP.argtypes = [c_void_p]
        self._dll.setMousePressedFP.restype = None
        self._dll.setMouseReleasedFP.argtypes = [c_void_p]
        self._dll.setMouseReleasedFP.restype = None
        # Popup menu events
        self._dll.setPopupMenuCanceledFP.argtypes = [c_void_p]
        self._dll.setPopupMenuCanceledFP.restype = None
        self._dll.setPopupMenuWillBecomeInvisibleFP.argtypes = [c_void_p]
        self._dll.setPopupMenuWillBecomeInvisibleFP.restype = None
        self._dll.setPopupMenuWillBecomeVisibleFP.argtypes = [c_void_p]
        self._dll.setPopupMenuWillBecomeVisibleFP.restype = None

    def releaseJavaObject(self, vmID: c_long, obj: JOBJECT64):
        self._dll.releaseJavaObject(vmID, obj)

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

    def getAccessibleContextAt(self, vmID: c_long, acParent: AccessibleContext, x: c_int, y: c_int, ac: AccessibleContext) -> BOOL:
        return self._dll.getAccessibleContextAt(vmID, acParent, x, y, byref(ac))

    def getAccessibleContextWithFocus(self, window: HWND, vmID: c_long, ac: AccessibleContext) -> BOOL:
        return self._dll.getAccessibleContextWithFocus(window, byref(vmID), byref(ac))

    def getAccessibleContextInfo(self, vmID: c_long, ac: AccessibleContext, info: AccessibleContextInfo) -> BOOL:
        return self._dll.getAccessibleContextInfo(vmID, ac, byref(info))

    def getAccessibleChildFromContext(self, vmID: c_long, ac: AccessibleContext, index: c_int) -> AccessibleContext:
        return self._dll.getAccessibleChildFromContext(vmID, ac, index)

    def getAccessibleParentFromContext(self, vmID: c_long, ac: AccessibleContext) -> AccessibleContext:
        return self._dll.getAccessibleParentFromContext(vmID, ac)

    def getAccessibleTableInfo(self, vmID: c_long, ac: AccessibleContext, tableInfo: AccessibleTableInfo) -> BOOL:
        return self._dll.getAccessibleTableInfo(vmID, ac, byref(tableInfo))

    def getAccessibleTableCellInfo(self, vmID: c_long, accessibleTable: AccessibleTable, row: c_int, column: c_int, tableCellInfo: AccessibleTableCellInfo) -> BOOL:
        return self._dll.getAccessibleTableCellInfo(vmID, accessibleTable, row, column, byref(tableCellInfo))

    def getAccessibleTableRowHeader(self, vmID: c_long, acParent: AccessibleContext, tableInfo: AccessibleTableInfo) -> BOOL:
        return self._dll.getAccessibleTableRowHeader(vmID, acParent, byref(tableInfo))

    def getAccessibleTableColumnHeader(self, vmID: c_long, acParent: AccessibleContext, tableInfo: AccessibleTableInfo) -> BOOL:
        return self._dll.getAccessibleTableColumnHeader(vmID, acParent, byref(tableInfo))

    def getAccessibleTableRowDescription(self, vmID: c_long, acParent: AccessibleContext, row: c_int) -> AccessibleContext:
        return self._dll.getAccessibleTableRowDescription(vmID, acParent, row)

    def getAccessibleTableColumnDescription(self, vmID: c_long, acParent: AccessibleContext, column: c_int) -> AccessibleContext:
        return self._dll.getAccessibleTableColumnDescription(vmID, acParent, column)

    def getAccessibleTableRowSelectionCount(self, vmID: c_long, table: AccessibleTable) -> c_int:
        return self._dll.getAccessibleTableRowSelectionCount(vmID, table)

    def isAccessibleTableRowSelected(self, vmID: c_long, table: AccessibleTable, row: c_int) -> BOOL:
        return self._dll.isAccessibleTableRowSelected(vmID, table, row)

    def getAccessibleTableRowSelections(self, vmID: c_long, table: AccessibleTable, count: c_int, selections: c_int) -> BOOL:
        return self._dll.getAccessibleTableRowSelections(vmID, table, count, byref(selections))

    def getAccessibleTableColumnSelectionCount(self, vmID: c_long, table: AccessibleTable) -> c_int:
        return self._dll.getAccessibleTableColumnSelectionCount(vmID, table)

    def isAccessibleTableColumnSelected(self, vmID: c_long, table: AccessibleTable, column: c_int) -> BOOL:
        return self._dll.isAccessibleTableColumnSelected(vmID, table, column)

    def getAccessibleTableColumnSelections(self, vmID: c_long, table: AccessibleTable, count: c_int, selections: c_int) -> BOOL:
        return self._dll.getAccessibleTableColumnSelections(vmID, table, count, byref(selections))

    def getAccessibleTableRow(self, vmID: c_long, table: AccessibleTable, index: c_int) -> c_int:
        return self._dll.getAccessibleTableRow(vmID, table, index)

    def getAccessibleTableColumn(self, vmID: c_long, table: AccessibleTable, index: c_int) -> c_int:
        return self._dll.getAccessibleTableColumn(vmID, table, index)

    def getAccessibleTableIndex(self, vmID: c_long, table: AccessibleTable, row: c_int, column: c_int) -> c_int:
        return self._dll.getAccessibleTableIndex(vmID, table, row, column)

    def getAccessibleRelationSet(self, vmID: c_long, accessibleContext: AccessibleContext, relationSetInfo: AccessibleRelationSetInfo):
        return self._dll.getAccessibleRelationSet(vmID, accessibleContext, byref(relationSetInfo))

    def getAccessibleHypertext(self, vmID: c_long, accessibleContext: AccessibleContext, hypertextInfo: AccessibleHypertextInfo) -> BOOL:
        return self._dll.getAccessibleHypertext(vmID, accessibleContext, byref(hypertextInfo))

    def activateAccessibleHyperlink(self, vmID: c_long, accessibleContext: AccessibleContext, accessibleHyperlink: AccessibleHyperlink) -> BOOL:
        return self._dll.activateAccessibleHyperlink(vmID, accessibleContext, accessibleHyperlink)

    def getAccessibleHyperlinkCount(self, vmID: c_long, accessibleContext: AccessibleContext) -> c_int:
        return self._dll.getAccessibleHyperlinkCount(vmID, accessibleContext)

    def getAccessibleHypertextExt(self, vmID: c_long, accessibleContext: AccessibleContext, nStartIndex: c_int, hypertextInfo: AccessibleHypertextInfo) -> BOOL:
        return self._dll.getAccessibleHypertextExt(vmID, accessibleContext, nStartIndex, byref(hypertextInfo))

    def getAccessibleHypertextLinkIndex(self, vmID: c_long, hypertext: AccessibleHypertext, nIndex: c_int) -> c_int:
        return self._dll.getAccessibleHypertextLinkIndex(vmID, hypertext, nIndex)

    def getAccessibleHyperlink(self, vmID: c_long, hypertext: AccessibleHypertext, nIndex: c_int, hyperlinkInfo: AccessibleHyperlinkInfo) -> BOOL:
        return self._dll.getAccessibleHyperlink(vmID, hypertext, nIndex, byref(hyperlinkInfo))

    def getAccessibleKeyBindings(self, vmID: c_long, accessibleContext: AccessibleContext, keyBindings: AccessibleKeyBindings) -> BOOL:
        return self._dll.getAccessibleKeyBindings(vmID, accessibleContext, byref(keyBindings))

    def getAccessibleIcons(self, vmID: c_long, accessibleContext: AccessibleContext, icons: AccessibleIcons) -> BOOL:
        return self._dll.getAccessibleIcons(vmID, accessibleContext, byref(icons))

    def getAccessibleActions(self, vmID: c_long, accessibleContext: AccessibleContext, actions: AccessibleActions) -> BOOL:
        return self._dll.getAccessibleActions(vmID, accessibleContext, byref(actions))

    def doAccessibleActions(self, vmID: c_long, accessibleContext: AccessibleContext, actionsToDo: AccessibleActionsToDo, failure: c_int) -> BOOL:
        return self._dll.doAccessibleActions(vmID, accessibleContext, byref(actionsToDo), byref(failure))

    def getAccessibleTextInfo(self, vmID: c_long, at: AccessibleText, textInfo: AccessibleTextInfo, x: c_int, y: c_int) -> BOOL:
        return self._dll.getAccessibleTextInfo(vmID, at, byref(textInfo), x, y)

    def getAccessibleTextItems(self, vmID: c_long, at: AccessibleText, textItems: AccessibleTextItemsInfo, index: c_int) -> BOOL:
        return self._dll.getAccessibleTextItems(vmID, at, byref(textItems), index)

    def getAccessibleTextSelectionInfo(self, vmID: c_long, at: AccessibleText, textSelection: AccessibleTextSelectionInfo) -> BOOL:
        return self._dll.getAccessibleTextSelectionInfo(vmID, at, byref(textSelection))

    def getAccessibleTextAttributes(self, vmID: c_long, at: AccessibleText, index: c_int, attributes: AccessibleTextAttributesInfo) -> BOOL:
        return self._dll.getAccessibleTextAttributes(vmID, at, index, byref(attributes))

    def getAccessibleTextRect(self, vmID: c_long, at: AccessibleText, rectInfo: AccessibleTextRectInfo, index: c_int) -> BOOL:
        return self._dll.getAccessibleTextRect(vmID, at, byref(rectInfo), index)

    def getAccessibleTextLineBounds(self, vmID: c_long, at: AccessibleText, index: c_int, startIndex: c_int, endIndex: c_int) -> BOOL:
        return self._dll.getAccessibleTextLineBounds(vmID, at, index, byref(startIndex), byref(endIndex))

    def getAccessibleTextRange(self, vmID: c_long, at: AccessibleText, start: c_int, end: c_int, text: c_wchar_p, len: c_short) -> BOOL:
        return self._dll.getAccessibleTextRange(vmID, at, start, end, text, len)

    def getCurrentAccessibleValueFromContext(self, vmID: c_long, av: AccessibleValue, value: c_wchar, len: c_short) -> BOOL:
        return self._dll.getCurrentAccessibleValueFromContext(vmID, av, byref(value), len)

    def getMaximumAccessibleValueFromContext(self, vmID: c_long, av: AccessibleValue, value: c_wchar, len: c_short) -> BOOL:
        return self._dll.getMaximumAccessibleValueFromContext(vmID, av, byref(value), len)

    def getMinimumAccessibleValueFromContext(self, vmID: c_long, av: AccessibleValue, value: c_wchar, len: c_short) -> BOOL:
        return self._dll.getMinimumAccessibleValueFromContext(vmID, av, byref(value), len)

    def addAccessibleSelectionFromContext(self, vmID: c_long, as_: AccessibleSelection, i: c_int):
        self._dll.addAccessibleSelectionFromContext(vmID, as_, i)

    def clearAccessibleSelectionFromContext(self, vmID: c_long, as_: AccessibleSelection):
        self._dll.clearAccessibleSelectionFromContext(vmID, as_)

    def getAccessibleSelectionFromContext(self, vmID: c_long, as_: AccessibleSelection, i: c_int) -> JOBJECT64:
        return self._dll.getAccessibleSelectionFromContext(vmID, as_, i)

    def getAccessibleSelectionCountFromContext(self, vmID: c_long, as_: AccessibleSelection) -> c_int:
        return self._dll.getAccessibleSelectionCountFromContext(vmID, as_)

    def isAccessibleChildSelectedFromContext(self, vmID: c_long, as_: AccessibleSelection, i: c_int) -> BOOL:
        return self._dll.isAccessibleChildSelectedFromContext(vmID, as_, i)

    def removeAccessibleSelectionFromContext(self, vmID: c_long, as_: AccessibleSelection, i: c_int):
        self._dll.removeAccessibleSelectionFromContext(vmID, as_, i)

    def selectAllAccessibleSelectionFromContext(self, vmID: c_long, as_: AccessibleSelection):
        self._dll.selectAllAccessibleSelectionFromContext(vmID, as_)

    def setTextContents(self, vmID: c_long, ac: AccessibleContext, text: c_wchar_p) -> BOOL:
        return self._dll.setTextContents(vmID, ac, text)

    def getParentWithRole(self, vmID: c_long, ac: AccessibleContext, role: c_wchar_p) -> AccessibleContext:
        return self._dll.getParentWithRole(vmID, ac, role)

    def getTopLevelObject(self, vmID: c_long, ac: AccessibleContext) -> AccessibleContext:
        return self._dll.getTopLevelObject(vmID, ac)

    def getParentWithRoleElseRoot(self, vmID: c_long, ac: AccessibleContext, role: c_wchar_p) -> AccessibleContext:
        return self._dll.getParentWithRoleElseRoot(vmID, ac, role)

    def getObjectDepth(self, vmID: c_long, ac: AccessibleContext) -> c_int:
        return self._dll.getObjectDepth(vmID, ac)

    def getActiveDescendent(self, vmID: c_long, ac: AccessibleContext) -> AccessibleContext:
        return self._dll.getActiveDescendent(vmID, ac)

    def getVirtualAccessibleName(self, vmID: c_long, accessibleContext: AccessibleContext, name: c_wchar, len: c_int) -> BOOL:
        return self._dll.getVirtualAccessibleName(vmID, accessibleContext, byref(name), len)

    def requestFocus(self, vmID: c_long, accessibleContext: AccessibleContext) -> BOOL:
        return self._dll.requestFocus(vmID, accessibleContext)

    def selectTextRange(self, vmID: c_long, accessibleContext: AccessibleContext, startIndex: c_int, endIndex: c_int) -> BOOL:
        return self._dll.selectTextRange(vmID, accessibleContext, startIndex, endIndex)

    def getTextAttributesInRange(self, vmID: c_long, accessibleContext: AccessibleContext, startIndex: c_int, endIndex: c_int, attributes: AccessibleTextAttributesInfo, len: c_short) -> BOOL:
        return self._dll.getTextAttributesInRange(vmID, accessibleContext, startIndex, endIndex, byref(attributes), byref(len))

    def getVisibleChildrenCount(self, vmID: c_long, accessibleContext: AccessibleContext) -> c_int:
        return self._dll.getVisibleChildrenCount(vmID, accessibleContext)

    def getVisibleChildren(self, vmID: c_long, accessibleContext: AccessibleContext, startIndex: c_int, children: VisibleChildrenInfo) -> BOOL:
        return self._dll.getVisibleChildren(vmID, accessibleContext, startIndex, byref(children))

    def setCaretPosition(self, vmID: c_long, accessibleContext: AccessibleContext, position: c_int) -> BOOL:
        return self._dll.setCaretPosition(vmID, accessibleContext, position)

    def getCaretLocation(self, vmID: c_long, ac: AccessibleContext, rectInfo: AccessibleTextRectInfo, index: c_int) -> BOOL:
        return self._dll.getCaretLocation(vmID, ac, byref(rectInfo), index)

    def getEventsWaiting(self) -> c_int:
        return self._dll.getEventsWaiting()

    def setJavaShutdownFP(self, fp: Callable[[c_long], None]):
        self._dll.setJavaShutdownFP(JavaShutdownFP(fp))

    def setFocusGainedFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64], None]):
        self._dll.setFocusGainedFP(FocusGainedFP(fp))

    def setFocusLostFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64], None]):
        self._dll.setFocusLostFP(FocusLostFP(fp))

    def setCaretUpdateFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64], None]):
        self._dll.setCaretUpdateFP(CaretUpdateFP(fp))

    def setMouseClickedFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64], None]):
        self._dll.setMouseClickedFP(MouseClickedFP(fp))

    def setMouseEnteredFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64], None]):
        self._dll.setMouseEnteredFP(MouseEnteredFP(fp))

    def setMouseExitedFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64], None]):
        self._dll.setMouseExitedFP(MouseExitedFP(fp))

    def setMousePressedFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64], None]):
        self._dll.setMousePressedFP(MousePressedFP(fp))

    def setMouseReleasedFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64], None]):
        self._dll.setMouseReleasedFP(MouseReleasedFP(fp))

    def setMenuCanceledFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64], None]):
        self._dll.setMenuCanceledFP(MenuCanceledFP(fp))

    def setMenuDeselectedFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64], None]):
        self._dll.setMenuDeselectedFP(MenuDeselectedFP(fp))

    def setMenuSelectedFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64], None]):
        self._dll.setMenuSelectedFP(MenuSelectedFP(fp))

    def setPopupMenuCanceledFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64], None]):
        self._dll.setPopupMenuCanceledFP(PopupMenuCanceledFP(fp))

    def setPopupMenuWillBecomeInvisibleFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64], None]):
        self._dll.setPopupMenuWillBecomeInvisibleFP(PopupMenuWillBecomeInvisibleFP(fp))

    def setPopupMenuWillBecomeVisibleFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64], None]):
        self._dll.setPopupMenuWillBecomeVisibleFP(PopupMenuWillBecomeVisibleFP(fp))

    def setPropertyChangeFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64, c_wchar_p, c_wchar_p, c_wchar_p], None]):
        self._dll.setPropertyChangeFP(PropertyChangeFP(fp))

    def setPropertyNameChangeFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64, c_wchar_p, c_wchar_p], None]):
        self._dll.setPropertyNameChangeFP(PropertyNameChangeFP(fp))

    def setPropertyDescriptionChangeFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64, c_wchar_p, c_wchar_p], None]):
        self._dll.setPropertyDescriptionChangeFP(PropertyDescriptionChangeFP(fp))

    def setPropertyStateChangeFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64, c_wchar_p, c_wchar_p], None]):
        self._dll.setPropertyStateChangeFP(PropertyStateChangeFP(fp))

    def setPropertyValueChangeFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64, c_wchar_p, c_wchar_p], None]):
        self._dll.setPropertyValueChangeFP(PropertyValueChangeFP(fp))

    def setPropertySelectionChangeFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64], None]):
        self._dll.setPropertySelectionChangeFP(PropertySelectionChangeFP(fp))

    def setPropertyTextChangeFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64], None]):
        self._dll.setPropertyTextChangeFP(PropertyTextChangedFP(fp))

    def setPropertyCaretChangeFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64, c_int, c_int], None]):
        self._dll.setPropertyCaretChangeFP(PropertyCaretChangeFP(fp))

    def setPropertyVisibleDataChangeFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64], None]):
        self._dll.setPropertyVisibleDataChangeFP(PropertyVisibleDataChangeFP(fp))

    def setPropertyChildChangeFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64, JOBJECT64, JOBJECT64], None]):
        self._dll.setPropertyChildChangeFP(PropertyChildChangeFP(fp))

    def setPropertyActiveDescendentChangeFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64, JOBJECT64, JOBJECT64], None]):
        self._dll.setPropertyActiveDescendentChangeFP(PropertyActiveDescendentChangeFP(fp))

    def setPropertyTableModelChangeFP(self, fp: Callable[[c_long, JOBJECT64, JOBJECT64, c_wchar_p, c_wchar_p], None]):
        self._dll.setPropertyTableModelChangeFP(PropertyTableModelChangeFP(fp))
