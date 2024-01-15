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
import time
from unittest import TestCase

from echo.jab import JABDriver, Role
from echo.uia import UIADriver
from echo.utils import win32


class UIATestSuite(TestCase):

    def setUp(self):
        self.uia_handle = win32.find_window(class_name="YonyouUWnd", window_name="Yonyou UClient")
        self.uia_driver = UIADriver(self.uia_handle)
        self.uia_root = self.uia_driver.root()
        assert self.uia_root is not None

        self.jab_canvas = self.uia_root.find_element(class_name="SunAwtCanvas")
        assert self.jab_canvas is not None

        self.jab_handle = self.jab_canvas.handle
        self.jab_driver = JABDriver(self.jab_handle)
        self.jab_root = self.jab_driver.root()
        assert self.jab_root is not None

    def tearDown(self):
        self.uia_driver.close()
        self.jab_driver.close()

    def test_find_all_elements(self):
        root = self.jab_root

        elems = root.find_all_elements()
        for e in elems:
            print(f"{'--' * e.depth}{str(e)}")

        assert len(elems) > 0

    def test_export_merge(self):
        import pyautogui
        import uuid

        root = self.jab_root

        save_path = "C:\\Users\\leego\\Documents\\nc\\" + str(uuid.uuid4())
        os.makedirs(save_path, exist_ok=True)

        def _step1_open_tab():
            search_input_elem = root.find_element(role=Role.TEXT, depth=10)
            print('search input', search_input_elem)
            assert search_input_elem is not None

            search_button_elem = root.find_element(role=Role.PUSH_BUTTON, depth=10)
            print('search input', search_button_elem)
            assert search_button_elem is not None

            search_input_elem.input("合并执行")
            time.sleep(1)

            search_item_elem = root.find_element(role=Role.LABEL, name="合并执行")
            assert search_item_elem is not None

            search_button_elem.click()

        def _step2_enter_scheme():
            self.jab_driver.set_foreground()

            label_elem = root.find_element(name="合并方案")
            assert label_elem is not None

            panel_elem = label_elem.next()
            assert panel_elem is not None

            input_elem = panel_elem.find_element(role=Role.TEXT)
            button_elem = panel_elem.find_element(role=Role.PUSH_BUTTON)
            assert input_elem is not None
            assert button_elem is not None

            input_elem.input("5")
            time.sleep(1)
            input_elem.set_focus()

            pyautogui.press("enter")

            time.sleep(1)
            assert input_elem.text == "财务合并报表-2023"

        def _step3_enter_date_and_query():
            self.jab_driver.set_foreground()

            label_elem = root.find_element(name="月")
            assert label_elem is not None

            panel_elem = label_elem.next()
            assert panel_elem is not None

            input_elem = panel_elem.find_element(role=Role.TEXT)
            button_elem = panel_elem.find_element(role=Role.PUSH_BUTTON)
            assert input_elem is not None
            assert button_elem is not None

            input_elem.input("2023-12-31")
            time.sleep(1)
            input_elem.set_focus()

            pyautogui.press("enter")

            time.sleep(1)
            assert input_elem.text == "2023-12-31"

            all_sub_radio_elem = root.find_element(role=Role.RADIO_BUTTON, name="所有下级")
            all_sub_radio_elem.click()

            time.sleep(1)

            query_button_elem = root.find_element(role=Role.PUSH_BUTTON, name="查询")
            query_button_elem.click()

            label_elem = root.find_element(role=Role.LABEL, name_like="每页行数")
            assert label_elem is not None

            input_elem = label_elem.next()
            assert input_elem is not None

            input_elem.input("500")
            time.sleep(1)
            input_elem.set_focus()

            pyautogui.press("enter")

            time.sleep(1)
            query_button_elem.click()

        def _step4_export_data():
            self.jab_driver.set_foreground()

            table_elem = root.find_element(role=Role.TABLE, depth=26)
            table_elem.click()
            table_elem.set_focus()
            with pyautogui.hold("ctrl"):
                pyautogui.press("a")

            export_button_elem = root.find_element(role=Role.PUSH_BUTTON, name="导出")
            export_button_elem.click()
            time.sleep(1)

            menu_window = self.uia_root.find_element(class_name="SunAwtWindow")
            menu_driver = JABDriver(menu_window.handle)
            menu_root = menu_driver.root()

            export_item_elem = menu_root.find_element(role=Role.MENU_ITEM, name="合并报表")
            export_item_elem.click()
            time.sleep(1)

            dialog_window = self.uia_root.find_element(class_name="SunAwtDialog")
            dialog_driver = JABDriver(dialog_window.handle)
            dialog_root = dialog_driver.root()

            save_input_elem = dialog_root.find_element(role=Role.TEXT)
            save_input_elem.input(save_path)
            time.sleep(1)

            save_button_elem = dialog_root.find_element(role=Role.PUSH_BUTTON, name="保存")
            save_button_elem.click()

            menu_driver.close()
            dialog_driver.close()

        _step1_open_tab()
        time.sleep(1)

        _step2_enter_scheme()
        time.sleep(1)

        _step3_enter_date_and_query()
        time.sleep(1)

        _step4_export_data()
        time.sleep(20)

        files = os.listdir(save_path)
        print(files)
        time.sleep(1)

    def test_event(self):
        from echo.utils.event import listener, Event, Key, main
        import asyncio
        @listener(Event.KEYUP)
        def on_click(x, y, key):
            if key == Key.f5:
                self.test_find_all_elements()

        asyncio.run(main())
