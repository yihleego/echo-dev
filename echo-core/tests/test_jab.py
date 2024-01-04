# -*- coding: utf-8 -*-
# Copyright (C) 2024  Echo Authors. All Rights Reserved.
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
            print("-" * e.depth, e)
            e.release()

    def test_find_elements_by_kwargs(self):
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
            lambda e: e.name == "Click",
            lambda e: e.role == Role.PUSH_BUTTON)
        for e in elems:
            print("filtered", e)
            e.release()

        root.release()

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

        root.release()

    def test_button(self):
        root = self.root

        elems = root.find_elements(role=Role.PUSH_BUTTON)
        for e in elems:
            res = e.click()
            print('click', res, e)
            e.release()

        root.release()

    def test_checkbox(self):
        root = self.root

        elems = root.find_elements(role=Role.CHECK_BOX)
        for e in elems:
            print('before', e.checked)
            res = e.click()
            print('after', e.checked, res)
            e.release()

        print(len(root.find_elements(checked=True)))

        root.release()

    def test_parent_is_root(self):
        root = self.root

        child = root.child(0)
        parent = child.parent()
        assert parent == root

        print('root', root)
        print('child', child)

        root.release()

    def test_screenshot(self):
        root = self.root
        root.screenshot("./screenshots/jab/root.png")

        text_elem = root.find_element(role=Role.TEXT)
        text_elem.screenshot("./screenshots/jab/text.png")

        button_elem = root.find_element(role=Role.PUSH_BUTTON)
        button_elem.screenshot("./screenshots/jab/button.png")

        button_elem.release()
        text_elem.release()
        root.release()
