import unittest

from pywinauto.application import Application

from src.utils import win32


class UIATestSuite(unittest.TestCase):

    def setUp(self):
        self.handle = win32.find_window(class_name="GlassWndClass-GlassWindowClass-2", window_name="Simple FX")

    def tearDown(self):
        pass

    def test_any(self):
        app = Application(backend='uia')
        app.connect(handle=self.handle)
        window = app.top_window()
        text = window.child_window(control_type='Edit')
        text.type_keys('Hello world!')
        button = window.child_window(control_type='Button', title='Click')
        button.click_input()
