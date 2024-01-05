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


import os
import threading
import time
import unittest
import uuid

from echo.jabdriver import JABDriver, Role
from echo.utils import win32


class JABTestSuite(unittest.TestCase):

    def setUp(self):
        self.handle = win32.find_window(class_name="SunAwtFrame", window_name="Swing Example")
        self.driver = JABDriver()
        self.root = self.driver.find_window(handle=self.handle)
        assert self.root is not None

    def tearDown(self):
        self.root.release()
        self.driver.close()

    def test_find_all_elements(self):
        root = self.root

        elems = root.find_all_elements()
        for e in elems:
            print(f"{'--' * e.depth}{str(e)}")
            e.release()

        assert len(elems) > 0

    def test_find_elements_by_criteria(self):
        root = self.root

        text_elems = root.find_elements(role=Role.TEXT)
        for e in text_elems:
            s = str(uuid.uuid4())
            print("old text", e)
            e.input(s)
            print('new text', e.text)
            assert e.text == s
            e.release()

        button_elems = root.find_elements(role=Role.PUSH_BUTTON, name="Click")
        for e in button_elems:
            print("button", e)
            e.click()
            print('clicked', e)
            e.release()

        role_like_elems = root.find_elements(role_like="pane")
        for e in role_like_elems:
            print("found role_like", e)
            e.release()

        name_like_elems = root.find_elements(name_like="Click")
        for e in name_like_elems:
            print("found name_like", e)
            e.release()

        enabled_elems = root.find_elements(enabled=True)
        for e in enabled_elems:
            print("found enabled", e)
            e.release()

        kwargs_elems = root.find_elements(**{"role": Role.PUSH_BUTTON, "name": "Click"})
        for e in kwargs_elems:
            print("found kwargs", e)
            e.release()

    def test_find_elements_by_filters(self):
        root = self.root

        elems = root.find_elements(
            lambda x: x.name == "Click",
            lambda x: x.role == Role.PUSH_BUTTON)
        for e in elems:
            print("found", e)
            e.release()

        assert len(elems) > 0

    def test_find_elements_by_filters_and_criteria(self):
        root = self.root

        elems = root.find_elements(
            lambda x: x.role == Role.PUSH_BUTTON,
            ignore_case=True,
            name_like="click")
        for e in elems:
            print("found", e)

        assert len(elems) > 0

    def test_text(self):
        root = self.root

        elems = root.find_elements(role=Role.TEXT)
        for e in elems:
            print('before', e.text)
            res = e.input("Hello,World!")
            print('after', e.text, res)
            res = e.input("😎-> 😭🕶👌")
            print('emoji', e.text, res)
            e.release()

    def test_button(self):
        root = self.root

        elems = root.find_elements(role=Role.PUSH_BUTTON)
        for e in elems:
            print("button", e)
            e.click()
            print('clicked', e)

        assert len(elems) > 0

    def test_checkbox(self):
        root = self.root

        elems = root.find_elements(role=Role.CHECK_BOX)
        for e in elems:
            checked = e.checked
            print('checked', e.checked, e)
            e.click()
            print('checked', e.checked, e)
            assert e.checked != checked

        assert len(root.find_elements(checked=True)) > 0

    def test_radiobutton(self):
        root = self.root

        elems = root.find_elements(role=Role.RADIO_BUTTON)
        for e in elems:
            checked = e.checked
            print('checked', e.checked, e)
            e.click()
            print('checked', e.checked, e)
            if not checked:
                assert e.checked != checked

        assert len(root.find_elements(checked=True)) > 0

    def test_parent_is_root(self):
        root = self.root

        child = root.child(0)
        assert child is not None

        parent = child.parent()
        assert parent == root

        print('root', root)
        print('child', child)
        print('parent', parent)

    def test_screenshot(self):
        root = self.root
        root.screenshot("./screenshots/jab/root.png")

        text_elem = root.find_element(role=Role.TEXT)
        text_elem.screenshot("./screenshots/jab/text.png")

        button_elem = root.find_element(role=Role.PUSH_BUTTON)
        button_elem.screenshot("./screenshots/jab/button.png")

        button_elem.release()
        text_elem.release()

        assert os.path.exists("./screenshots/jab/root.png")
        assert os.path.exists("./screenshots/jab/text.png")
        assert os.path.exists("./screenshots/jab/button.png")

    def test_wait(self):
        root = self.root

        text_elem = root.find_element(role=Role.TEXT)
        text_elem.input("nothing")

        def _async_edit():
            time.sleep(3)
            text_elem.input("EXIT")

        threading.Thread(target=_async_edit).start()

        text_elem.wait(lambda x: x.text == "EXIT", timeout=5, interval=1)
