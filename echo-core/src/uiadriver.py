from abc import ABC, abstractmethod
from enum import Enum
from functools import cached_property
from typing import Optional, Callable

from pywinauto.application import Application
from pywinauto.controls.uiawrapper import UIAWrapper
from pywinauto.uia_element_info import UIAElementInfo

from .driver import Driver, Element
from .utils import win32


class Role(str, Enum):
    APP_BAR = "AppBar"
    BUTTON = "Button"
    CALENDAR = "Calendar"
    CHECK_BOX = "CheckBox"
    COMBO_BOX = "ComboBox"
    CUSTOM = "Custom"
    DATA_GRID = "DataGrid"
    DATA_ITEM = "DataItem"
    DOCUMENT = "Document"
    EDIT = "Edit"
    GROUP = "Group"
    HEADER = "Header"
    HEADER_ITEM = "HeaderItem"
    HYPERLINK = "Hyperlink"
    IMAGE = "Image"
    LIST = "List"
    LIST_ITEM = "ListItem"
    MENU_BAR = "MenuBar"
    MENU = "Menu"
    MENU_ITEM = "MenuItem"
    PANE = "Pane"
    PROGRESS_BAR = "ProgressBar"
    RADIO_BUTTON = "RadioButton"
    SCROLL_BAR = "ScrollBar"
    SEMANTIC_ZOOM = "SemanticZoom"
    SEPARATOR = "Separator"
    SLIDER = "Slider"
    SPINNER = "Spinner"
    SPLIT_BUTTON = "SplitButton"
    STATUS_BAR = "StatusBar"
    TAB = "Tab"
    TAB_ITEM = "TabItem"
    TABLE = "Table"
    TEXT = "Text"
    THUMB = "Thumb"
    TITLE_BAR = "TitleBar"
    TOOL_BAR = "ToolBar"
    TOOL_TIP = "ToolTip"
    TREE = "Tree"
    TREE_ITEM = "TreeItem"
    WINDOW = "Window"


class UIAElementProperties(ABC):

    @property
    @abstractmethod
    def info(self) -> UIAElementInfo:
        raise NotImplementedError

    @property
    @abstractmethod
    def text(self) -> Optional[str]:
        raise NotImplementedError

    @property
    def role(self) -> str:
        return self.info.control_type

    @property
    def name(self) -> str:
        return self.info.name

    @property
    def description(self) -> str:
        return self.info.rich_text

    @property
    def automation_id(self) -> int:
        return self.info.automation_id

    @property
    def class_name(self) -> int:
        return self.info.class_name

    @property
    def x(self) -> int:
        return self.info.rectangle.left

    @property
    def y(self) -> int:
        return self.info.rectangle.top

    @property
    def width(self) -> int:
        return self.info.rectangle.right - self.info.rectangle.left

    @property
    def height(self) -> int:
        return self.info.rectangle.bottom - self.info.rectangle.top

    @property
    def position(self) -> tuple[int, int]:
        info = self.info
        return info.rectangle.left, info.rectangle.top

    @property
    def size(self) -> tuple[int, int]:
        info = self.info
        return info.rectangle.right - info.rectangle.left, info.rectangle.bottom - info.rectangle.top

    @property
    def rectangle(self) -> tuple[int, int, int, int]:
        info = self.info
        return info.rectangle.left, info.rectangle.top, info.rectangle.right, info.rectangle.bottom

    @property
    def visible(self) -> bool:
        return self.info.visible

    @property
    def enabled(self) -> bool:
        return self.info.enabled

    def __str__(self) -> str:
        return (f"role='{self.role}', name='{self.name}', description='{self.description}', "
                f"automation_id='{self.automation_id}', class_name='{self.class_name}', description='{self.description}', "
                f"text='{self.text}', rectangle={self.rectangle}, visible={self.visible}, enabled={self.enabled}")


class UIAElement(UIAElementProperties, Element):
    def __init__(self, app: Application, window: UIAWrapper, handle: int, process_id: int, root: 'UIAElement' = None, parent: 'UIAElement' = None):
        self._app: Application = app
        self._window: UIAWrapper = window
        self._handle: int = handle
        self._process_id: int = process_id
        self._process_name: str = None  # TODO
        self._root: UIAElement = root or self  # TODO
        self._parent: Optional[UIAElement] = parent

    @property
    def handle(self) -> int:
        return self._handle

    @property
    def process_id(self) -> int:
        return self._process_id

    @cached_property
    def info(self) -> UIAElementInfo:
        return self._window.element_info

    @property
    def text(self) -> Optional[str]:
        # TODO
        try:
            return self._window.get_value()
        except:
            return None

    @text.setter
    def text(self, value: str):
        self.input(value)

    @property
    def depth(self) -> int:
        # TODO
        return -1

    @property
    def root(self) -> 'UIAElement':
        return self._root

    @property
    def parent(self) -> Optional['UIAElement']:
        # the root does not have a parent
        if self.depth == 0:
            return None
        # return if parent exists
        if self._parent is not None:
            return self._parent
        parent_window = self._window.parent()
        self._parent = UIAElement.create_element(window=parent_window, root=self._root)
        return self._parent

    @property
    def children(self) -> list['UIAElement']:
        res = []
        for child_window in self._window.children():
            res.append(UIAElement.create_element(window=child_window, root=self._root, parent=self))
        return res

    def child(self, index: int) -> Optional['UIAElement']:
        children = self._window.children()
        count = len(children)
        if count <= 0 or count <= index:
            return None
        return UIAElement.create_element(window=children[index], root=self._root, parent=self)

    def click(self, button="left") -> bool:
        self._window.set_focus()
        return self._window.click_input(button)

    def input(self, text: str) -> bool:
        # TODO
        try:
            self._window.set_edit_text(text)
            return True
        except:
            return self._window.get_value() == text

    def wait(self, wait_for: str, timeout=None, interval=None):
        # TODO
        pass

    def set_focus(self) -> bool:
        self._window.set_focus()
        return True

    def _snapshot(self) -> 'UIAElement':
        return self

    def _rules(self):
        return {
            "role": ("role", ["eq", "like", "in", "in_like", "regex"]),
            "name": ("name", ["eq", "like", "in", "in_like", "regex"]),
            "description": ("description", ["eq", "like", "in", "in_like", "regex"]),
            "x": ("x", ["eq", "gt", "gte", "lt", "lte"]),
            "y": ("y", ["eq", "gt", "gte", "lt", "lte"]),
            "width": ("width", ["eq", "gt", "gte", "lt", "lte"]),
            "height": ("height", ["eq", "gt", "gte", "lt", "lte"]),
            "text": ("text", ["eq", "like", "in", "in_like", "regex"]),
            "visible": ("visible", ["eq"]),
            "enabled": ("enabled", ["eq"]),
        }

    def matches(self, *filters: Callable[['UIAElement'], bool], **criteria) -> bool:
        """
        Match element by criteria.
        :param filters: filters
        :key role: role equals
        :key role_like: role name contains
        :key role_in: role name in list
        :key role_in_like: role name contains in list
        :key role_regex: role name regex
        :key name: name equals
        :key name_like: name contains
        :key name_in: name in list
        :key name_in_like: name contains in list
        :key name_regex: name regex
        :key description: description equals
        :key description_like: description contains
        :key description_in: description in list
        :key description_in_like: description contains in list
        :key description_regex: description regex
        :key x: x equals
        :key y: y equals
        :key width: width equals
        :key height: height equals
        :key text: text equals
        :key text_like: text contains
        :key text_in: text in list
        :key text_in_like: text contains in list
        :key text_regex: text regex
        :key editable: state editable
        :key focusable: state focusable
        :key resizable: state resizable
        :key visible: state visible
        :key selectable: state selectable
        :key multiselectable: state multiselectable
        :key collapsed: state collapsed
        :key checked: state checked
        :key enabled: state enabled
        :key focused: state focused
        :key selected: state selected
        :key showing: state showing
        :key children_count: children count equals
        :key depth: depth equals
        :return: True if matched
        """
        return super().matches(*filters, **criteria)

    @staticmethod
    def create_root(app: Application, window: UIAWrapper, handle: int) -> Optional['UIAElement']:
        process_id = win32.get_process_id_from_handle(handle)
        return UIAElement(app=app, window=window, handle=handle, process_id=process_id)

    @staticmethod
    def create_element(window: UIAWrapper, root: 'UIAElement', parent: 'UIAElement' = None) -> 'UIAElement':
        return UIAElement(app=root._app, window=window, handle=root._handle, process_id=root._process_id, root=root, parent=parent)


class UIADriver(Driver):
    def find_window(self, handle: int) -> Optional[UIAElement]:
        app = Application(backend='uia')
        app.connect(handle=handle)
        window = app.top_window()
        return UIAElement.create_root(app=app, window=window.wrapper_object(), handle=handle)

    def close(self):
        pass
