import unittest

from pywinauto.application import Application

from src.uiadriver import UIADriver, Role
from src.utils import win32


class UIATestSuite(unittest.TestCase):

    def setUp(self):
        self.handle = win32.find_window(class_name="GlassWndClass-GlassWindowClass-2", window_name="Simple FX")
        self.driver = UIADriver()

    def tearDown(self):
        self.driver.close()

    def get_root(self):
        root = self.driver.find_window(handle=self.handle)
        if root:
            return root
        raise Exception('not found')

    def test_button(self):
        root = self.get_root()

        button_elems = root.find_elements(role=Role.BUTTON)
        for e in button_elems:
            res = e.click()
            print('click', res, e)

    def test_text(self):
        root = self.get_root()

        text_elems = root.find_elements(role=Role.EDIT)
        for e in text_elems:
            print('before', e.text)
            res = e.input("Hello,World!")
            print('after', e.text, res)
            res = e.input("😎-> 😭🕶👌")
            print('emoji', e.text, res)

    def test_wait(self):
        root = self.get_root()

        text_elem = root.find_element(role=Role.EDIT)
        text_elem.wait(lambda x: x.text == 'SB', timeout=10, interval=1)

    def test_screenshot(self):
        root = self.get_root()
        root.screenshot("./screenshots/root.png")

        elem = root.find_element(role=Role.TEXT)
        elem.screenshot("./screenshots/text.png")

    def test_any(self):
        app = Application(backend='uia')
        app.connect(handle=self.handle)
        window = app.top_window()
        text = window.child_window(control_type='Edit')
        print('text', text.get_value())
        if text.is_editable():
            text.type_keys('Hello world!1')
            text.set_text('Hello world!2')
        text_info = text.wrapper_object().element_info

        print(text_info.automation_id,
              text_info.children,
              text_info.class_name,
              text_info.control_id,
              text_info.control_type,
              text_info.descendants,
              text_info.dump_window,
              text_info.element,
              text_info.enabled,
              text_info.filter_with_depth,
              text_info.framework_id,
              text_info.from_point,
              text_info.handle,
              text_info.has_depth,
              text_info.iter_children,
              text_info.iter_descendants,
              text_info.name,
              text_info.parent,
              text_info.process_id,
              text_info.rectangle,
              text_info.rich_text,
              text_info.runtime_id,
              text_info.set_cache_strategy,
              text_info.top_from_point,
              text_info.visible)

        button = window.child_window(control_type='Button', title='Click')
        button.click_input()
        button_info = button.wrapper_object().element_info
        print(button_info.automation_id,
              button_info.children,
              button_info.class_name,
              button_info.control_id,
              button_info.control_type,
              button_info.descendants,
              button_info.dump_window,
              button_info.element,
              button_info.enabled,
              button_info.filter_with_depth,
              button_info.framework_id,
              button_info.from_point,
              button_info.handle,
              button_info.has_depth,
              button_info.iter_children,
              button_info.iter_descendants,
              button_info.name,
              button_info.parent,
              button_info.process_id,
              button_info.rectangle,
              button_info.rich_text,
              button_info.runtime_id,
              button_info.set_cache_strategy,
              button_info.top_from_point,
              button_info.visible)
