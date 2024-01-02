import unittest

from jab import *


class JABTestSuite(unittest.TestCase):

    def setUp(self):
        self.handle = win32.find_window(class_name="SunAwtFrame", window_name="Swing Example")
        self.driver: JABDriver = JABDriver()

    def tearDown(self):
        self.driver.close()

    def get_root(self):
        root = self.driver.find_window(handle=self.handle)
        if root:
            return root
        raise Exception('not found')

    def test_find_all_elements(self):
        root = self.get_root()

        all = root.find_all_elements()
        for e in all:
            print("-" * e.depth, e)
            e.release()

    def test_find_elements_by_kwargs(self):
        root = self.get_root()

        text_elems = root.find_elements(role=Role.TEXT)
        for e in text_elems:
            print("found text", e)
            e.input("sb")
            print('input', e.text)
            e.release()

        button_elems = root.find_elements(role=Role.PUSH_BUTTON, name="Click Me")
        for e in button_elems:
            print("found button", e)
            e.click()
            print('click', e)
            e.release()

        role_like_elems = root.find_elements(role_like="pane")
        for e in role_like_elems:
            print("found role_like", e)
            e.release()

        name_like_elems = root.find_elements(name_like="Me")
        for e in name_like_elems:
            print("found name_like", e)
            e.release()

        enabled_elems = root.find_elements(enabled=True)
        for e in enabled_elems:
            print("found enabled", e)
            e.release()

        kwargs_elems = root.find_elements(**{"role": Role.PUSH_BUTTON, "name": "Click Me"})
        for e in kwargs_elems:
            print("found kwargs", e)
            e.release()

    def test_find_elements_by_filters(self):
        root = self.get_root()

        filtered_elems = root.find_elements(
            lambda e: e.name == "Click Me",
            lambda e: e.role == Role.PUSH_BUTTON)
        for e in filtered_elems:
            print("filtered", e)
            e.release()

        root.release()

    def test_button(self):
        root = self.get_root()

        button_elems = root.find_elements(role=Role.PUSH_BUTTON)
        for e in button_elems:
            res = e.click()
            print('click', res, e)
            e.release()

        root.release()

    def test_text(self):
        root = self.get_root()

        text_elems = root.find_elements(role=Role.TEXT)
        for e in text_elems:
            print('before', e.text)
            res = e.input("Hello,World!")
            print('after', e.text, res)
            e.text = "setter"
            print('setter', e.text)
            res = e.input("😎-> 😭🕶👌")
            print('emoji', e.text, res)
            e.release()

        root.release()

    def test_checkbox(self):
        root = self.get_root()

        checkbox_elems = root.find_elements(role=Role.CHECK_BOX)
        for e in checkbox_elems:
            print('before', e.checked)
            res = e.click()
            print('after', e.checked, res)
            e.release()

        print(len(root.find_elements(checked=True)))

        root.release()

    def test_screenshot(self):
        root = self.get_root()
        root.screenshot("./screenshots/root.png")

        elem = root.find_element(role=Role.TEXT)
        elem.screenshot("./screenshots/text.png")

        elem.release()
        root.release()
