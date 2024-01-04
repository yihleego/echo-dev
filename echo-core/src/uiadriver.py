from _ctypes import COMError
from enum import Enum
from typing import Optional, Callable

from pywinauto.application import Application
from pywinauto.controls.uia_controls import EditWrapper, ButtonWrapper, ListItemWrapper, TreeItemWrapper
from pywinauto.controls.uiawrapper import UIAWrapper
from pywinauto.uia_defines import NoPatternInterfaceError
from pywinauto.uia_element_info import UIAElementInfo

from .driver import Driver, Element
from .utils import win32, to_string


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


class UIAElement(Element):
    def __init__(self, app: Application, window: UIAWrapper, handle: int, process_id: int, process_name: str, root: 'UIAElement' = None, parent: 'UIAElement' = None):
        self._app: Application = app
        self._window: UIAWrapper = window
        self._handle: int = handle
        self._process_id: int = process_id
        self._process_name: str = process_name
        self._root: UIAElement = root or self  # TODO
        self._parent: Optional[UIAElement] = parent

    @property
    def handle(self) -> int:
        return self._handle

    @property
    def process_id(self) -> int:
        return self._process_id

    @property
    def process_name(self) -> str:
        return self._process_name

    @property
    def info(self) -> UIAElementInfo:
        return self._window.element_info

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
    def checked(self) -> bool:
        role = self.role
        if role == Role.CHECK_BOX and isinstance(self._window, ButtonWrapper):
            return self._window.get_toggle_state() == 1
        elif role == Role.LIST_ITEM and isinstance(self._window, ListItemWrapper):
            return self._window.is_checked()
        elif role == Role.TREE_ITEM and isinstance(self._window, TreeItemWrapper):
            return self._window.is_checked()
        return False

    @property
    def enabled(self) -> bool:
        return self.info.enabled

    @property
    def selected(self) -> bool:
        try:
            return self._window.is_selected() == 1
        except NoPatternInterfaceError:
            return False
        except Exception as e:
            raise e

    @property
    def text(self) -> Optional[str]:
        role = self.role
        if role == Role.EDIT and isinstance(self._window, EditWrapper):
            return self._window.get_value()
        return None

    def root(self) -> 'UIAElement':
        return self._root

    def parent(self) -> Optional['UIAElement']:
        # return if parent exists
        if self._parent is not None:
            return self._parent
        parent_window = self._window.parent()
        if parent_window is None:
            return None
        self._parent = UIAElement.create_element(window=parent_window, root=self._root)
        return self._parent

    def child(self, index: int) -> Optional['UIAElement']:
        children = self._window.children()
        count = len(children)
        if count <= 0 or count <= index:
            return None
        return UIAElement.create_element(window=children[index], root=self._root, parent=self)

    def children(self, *filters: Callable[['UIAElement'], bool], **criteria) -> list['UIAElement']:
        res = []
        for child_window in self._window.children():
            child = UIAElement.create_element(window=child_window, root=self._root, parent=self)
            if filters or criteria:
                matched = child.matches(*filters, **criteria)
                if matched:
                    res.append(child)
            else:
                res.append(child)
        return res

    @property
    def children_count(self) -> int:
        return len(self._window.children())

    def click(self, button="left") -> bool:
        if isinstance(self._window, ButtonWrapper):
            self._window.click()
        else:
            self._window.set_focus()
            self._window.click_input(button)
        return True

    def input(self, text: str) -> bool:
        if isinstance(self._window, EditWrapper):
            try:
                self._window.set_edit_text(text)
                return True
            except COMError:
                return self._window.get_value() == text
            except NoPatternInterfaceError:
                return False
            except Exception as e:
                if not self._window.get_value() == text:
                    raise Exception("failed to input", e)
        return False

    def set_focus(self) -> bool:
        self._window.set_focus()
        return True

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
        :key visible: state visible
        :key checked: state checked
        :key selected: state selected
        :key enabled: state enabled
        :return: True if matched
        """
        snapshot = self
        rules = {
            "role": ("role", ["eq", "like", "in", "in_like", "regex"]),
            "name": ("name", ["eq", "like", "in", "in_like", "regex"]),
            "description": ("description", ["eq", "like", "in", "in_like", "regex"]),
            "x": ("x", ["eq", "gt", "gte", "lt", "lte"]),
            "y": ("y", ["eq", "gt", "gte", "lt", "lte"]),
            "width": ("width", ["eq", "gt", "gte", "lt", "lte"]),
            "height": ("height", ["eq", "gt", "gte", "lt", "lte"]),
            "text": ("text", ["eq", "like", "in", "in_like", "regex"]),
            "visible": ("visible", ["eq"]),
            "checked": ("checked", ["eq"]),
            "selected": ("selected", ["eq"]),
            "enabled": ("enabled", ["eq"]),
        }
        return self._matches(snapshot, rules, *filters, **criteria)

    def find_all_elements(self) -> list['UIAElement']:
        found = [self]
        children = self.children()
        for child in children:
            found.extend(child.find_all_elements())
        return found

    def find_elements(self, *filters: Callable[['UIAElement'], bool], **criteria) -> list['UIAElement']:
        # return empty list if no filters or criteria
        if len(filters) == 0 and len(criteria) == 0:
            return []
        found = []
        children = self.children()
        for child in children:
            matched = child.matches(*filters, **criteria)
            if matched:
                found.append(child)
            # looking for deep elements
            found.extend(child.find_elements(*filters, **criteria))
        return found

    def find_element(self, *filters: Callable[['UIAElement'], bool], **criteria) -> Optional['UIAElement']:
        # return None if no filters or criteria
        if len(filters) == 0 and len(criteria) == 0:
            return None
        children = self.children()
        for child in children:
            matched = child.matches(*filters, **criteria)
            if matched:
                return child
        # looking for deep elements if not found
        for child in children:
            found = child.find_element(*filters, **criteria)
            if found is not None:
                return found
        return None

    def __str__(self) -> str:
        return to_string(self,'role', 'name', 'description', 'automation_id', 'class_name',
                         'rectangle', 'text', 'visible', 'checked', 'enabled', 'selected')


    @staticmethod
    def create_root(app: Application, window: UIAWrapper, handle: int) -> Optional['UIAElement']:
        process_id = win32.get_process_id_from_handle(handle)
        process_name = win32.get_process_name_by_process_id(process_id)
        return UIAElement(app=app, window=window, handle=handle, process_id=process_id, process_name=process_name)

    @staticmethod
    def create_element(window: UIAWrapper, root: 'UIAElement', parent: 'UIAElement' = None) -> 'UIAElement':
        return UIAElement(app=root._app, window=window, handle=root._handle,
                          process_id=root._process_id, process_name=root._process_name, root=root, parent=parent)

class UIADriver(Driver):
    def find_window(self, handle: int) -> Optional[UIAElement]:
        app = Application(backend='uia')
        app.connect(handle=handle)
        window = app.top_window()
        return UIAElement.create_root(app=app, window=window.wrapper_object(), handle=handle)

    def close(self):
        pass
