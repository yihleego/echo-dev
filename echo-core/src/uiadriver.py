from typing import Optional

from pywinauto.application import Application, WindowSpecification

from .driver import Driver, Element
from .utils import win32


class UIAElement(Element):
    def __init__(self, app: Application, window: WindowSpecification, handle: int, process_id: int, root: 'UIAElement' = None, parent: 'UIAElement' = None):
        self._app = app
        self._window = window
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

    def click(self) -> bool:
        return self._window.click_input()

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

    @staticmethod
    def create_root(app: Application, window: WindowSpecification, handle: int) -> Optional['UIAElement']:
        process_id = win32.get_process_id_from_handle(handle)
        return UIAElement(app=app, window=window, handle=handle, process_id=process_id)

    @staticmethod
    def create_element(window: WindowSpecification, root: 'UIAElement', parent: 'UIAElement' = None) -> 'UIAElement':
        return UIAElement(app=root._app, window=window, handle=root._handle, process_id=root._process_id,
                          root=root, parent=parent)


class UIADriver(Driver):
    def find_window(self, handle: int) -> Optional[UIAElement]:
        app = Application(backend='uia')
        app.connect(handle=handle)
        window = app.top_window()
        return UIAElement.create_root(app=app, window=window, handle=handle)

    def close(self):
        pass
