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
import uuid
from unittest import TestCase

from echo.core.uia import UIADriver, Role
from echo.utils import win32


class UIATestSuite(TestCase):

    def setUp(self):
        self.handle = win32.find_window(class_name="GlassWndClass-GlassWindowClass-2", window_name="Simple FX")
        self.driver = UIADriver(self.handle)
        self.root = self.driver.root()
        self.assertIsNotNone(self.root)

    def tearDown(self):
        self.driver.close()

    def test_find_all_elements(self):
        root = self.root

        elems = root.find_all_elements()
        for e in elems:
            print(f"{'--' * e.depth}{str(e)}")

        self.assertTrue(len(elems) > 0)

    def test_find_elements_by_criteria(self):
        root = self.root

        text_elems = root.find_elements(role=Role.EDIT)
        for e in text_elems:
            s = str(uuid.uuid4())
            print("old text", e.text)
            e.input(s)
            print('new text', e.text)
            self.assertEqual(e.text, s)

        button_elems = root.find_elements(role=Role.BUTTON, name="Click")
        for e in button_elems:
            print("button", e)
            e.click()
            print('clicked', e)

        role_like_elems = root.find_elements(role_like="bar", ignore_case=True)
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
            print("found", e)

        self.assertTrue(len(elems) > 0)

    def test_find_elements_by_filters_and_criteria(self):
        root = self.root

        elems = root.find_elements(
            lambda x: x.role == Role.BUTTON,
            ignore_case=True,
            name_like="click")
        for e in elems:
            print("found", e)

        self.assertTrue(len(elems) > 0)

    def test_text(self):
        root = self.root

        elems = root.find_elements(role=Role.EDIT)
        for e in elems:
            s = str(uuid.uuid4())
            print('old text', e.text)
            e.input(s)
            print('new text', e.text)
            self.assertEqual(e.text, s)

            e.input("😎-> 😭🕶👌")
            print('emoji', e.text)
            self.assertEqual(e.text, "😎-> 😭🕶👌")

    def test_button(self):
        root = self.root

        elems = root.find_elements(role=Role.BUTTON, name_like="click", ignore_case=True)
        for e in elems:
            print("button", e)
            res = e.click()
            print('clicked', res, e)

        self.assertTrue(len(elems) > 0)

    def test_checkbox(self):
        root = self.root

        elems = root.find_elements(role=Role.CHECK_BOX)
        for e in elems:
            checked = e.checked
            print('checked', e.checked, e)
            e.click()
            print('checked', e.checked, e)
            self.assertNotEqual(e.checked, checked)

        self.assertTrue(len(root.find_elements(checked=True)) > 0)

    def test_radiobutton(self):
        root = self.root

        elems = root.find_elements(role=Role.RADIO_BUTTON)
        for e in elems:
            selected = e.selected
            print('selected', e.selected, e)
            e.click()
            print('selected', e.selected, e)
            if not selected:
                self.assertNotEqual(e.selected, selected)

        self.assertTrue(len(root.find_elements(selected=True)) > 0)

    def test_parent_is_root(self):
        root = self.root

        child = root.child(0)
        self.assertIsNotNone(child)

        parent = child.parent()
        self.assertEqual(parent, root)

        print('root', root)
        print('child', child)
        print('parent', parent)

    def test_parent(self):
        root = self.root

        elem = root.find_element(role=Role.BUTTON, name="Click")
        self.assertIsNotNone(elem)

        parent = elem.parent()
        self.assertIsNotNone(parent)

        print('child', elem)
        print('parent', parent)

    def test_previous_next(self):
        root = self.root

        elem = root.find_element(role=Role.BUTTON, name="Click")
        self.assertIsNotNone(elem)

        previous = elem.previous()
        next = elem.next()
        self.assertIsNotNone(previous)
        self.assertIsNotNone(next)

        print('previous', previous)
        print('next', next)

    def test_screenshot(self):
        root = self.root
        driver = self.driver

        driver.screenshot("./screenshots/uia/window.png")

        root.screenshot("./screenshots/uia/root.png")

        edit_elem = root.find_element(role=Role.EDIT)
        edit_elem.screenshot("./screenshots/uia/edit.png")

        button_elem = root.find_element(role=Role.BUTTON)
        button_elem.screenshot("./screenshots/uia/button.png")

        self.assertTrue(os.path.exists("./screenshots/uia/window.png"))
        self.assertTrue(os.path.exists("./screenshots/uia/root.png"))
        self.assertTrue(os.path.exists("./screenshots/uia/edit.png"))
        self.assertTrue(os.path.exists("./screenshots/uia/button.png"))

    def test_wait(self):
        root = self.root

        text_elem = root.find_element(role=Role.EDIT)
        text_elem.input("nothing")

        def _async_edit():
            time.sleep(3)
            text_elem.input("EXIT")

        threading.Thread(target=_async_edit).start()

        text_elem.wait(lambda x: x.text == "EXIT", timeout=5, interval=1)
