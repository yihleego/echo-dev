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

from echo.uiadriver import UIADriver, Role
from echo.utils import win32


class UIATestSuite(unittest.TestCase):

    def setUp(self):
        self.handle = win32.find_window(class_name="GlassWndClass-GlassWindowClass-2", window_name="Simple FX")
        self.driver = UIADriver()
        self.root = self.driver.find_window(handle=self.handle)
        assert self.root is not None

    def tearDown(self):
        self.driver.close()

    def test_find_all_elements(self):
        root = self.root

        elems = root.find_all_elements()
        for e in elems:
            print(e)

    def test_find_elements_by_kwargs(self):
        root = self.root

        text_elems = root.find_elements(role=Role.EDIT)
        for e in text_elems:
            s = str(uuid.uuid4())
            print("old text", e.text)
            e.input(s)
            print('new text', e.text)
            assert e.text == s

        button_elems = root.find_elements(role=Role.BUTTON, name="Click")
        for e in button_elems:
            print("button", e)
            e.click()
            print('clicked', e)

        role_like_elems = root.find_elements(role_like="pane")
        for e in role_like_elems:
            print("found role_like", e)

        name_like_elems = root.find_elements(name_like="Click")
        for e in name_like_elems:
            print("found name_like", e)

        enabled_elems = root.find_elements(enabled=True)
        for e in enabled_elems:
            print("found enabled", e)

        kwargs_elems = root.find_elements(**{"role": Role.BUTTON, "name": "Click"})
        for e in kwargs_elems:
            print("found kwargs", e)

    def test_find_elements_by_filters(self):
        root = self.root

        elems = root.find_elements(
            lambda x: x.name == "Click",
            lambda x: x.role == Role.BUTTON)
        for e in elems:
            print("filtered", e)

    def test_text(self):
        root = self.root

        elems = root.find_elements(role=Role.EDIT)
        for e in elems:
            s = str(uuid.uuid4())
            print('old text', e.text)
            e.input(s)
            print('new text', e.text)
            assert e.text == s

            e.input("😎-> 😭🕶👌")
            print('emoji', e.text)
            assert e.text == "😎-> 😭🕶👌"

    def test_button(self):
        root = self.root

        button_elems = root.find_elements(role=Role.BUTTON)
        for e in button_elems:
            print("button", e)
            res = e.click()
            print('clicked', res, e)

    def test_checkbox(self):
        root = self.root

        elems = root.find_elements(role=Role.CHECK_BOX)
        for e in elems:
            checked = e.checked
            print('checked', e.checked, e)
            e.click()
            print('checked', e.checked, e)
            assert e.checked != checked

        print(len(root.find_elements(checked=True)))

    def test_radiobutton(self):
        root = self.root

        elems = root.find_elements(role=Role.RADIO_BUTTON)
        for e in elems:
            selected = e.selected
            print('selected', e.selected, e)
            e.click()
            print('selected', e.selected, e)
            if not selected:
                assert e.selected != selected

        print(len(root.find_elements(selected=True)))

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
        root.screenshot("./screenshots/uia/root.png")

        edit_elem = root.find_element(role=Role.EDIT)
        edit_elem.screenshot("./screenshots/uia/edit.png")

        button_elem = root.find_element(role=Role.BUTTON)
        button_elem.screenshot("./screenshots/uia/button.png")

    def test_wait(self):
        root = self.root

        text_elem = root.find_element(role=Role.EDIT)
        text_elem.wait(lambda x: x.text == 'EXIT', timeout=10, interval=1)
