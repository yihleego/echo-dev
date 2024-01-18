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

from echo.core.jab import JABDriver, Role, JABLib
from echo.core.uia import UIADriver
from echo.utils import win32
from echo.utils.retrying import retryable


class UIATestSuite(TestCase):

    def setUp(self):
        self.jab_lib = JABLib()

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
        import uuid

        root = self.jab_root

        save_path = "C:\\Users\\leego\\Documents\\nc\\合并执行\\" + str(uuid.uuid4())
        os.makedirs(save_path, exist_ok=True)

        self.jab_driver.set_foreground()

        @retryable
        def _step1_open_tab():
            search_input_elem = root.find_element(role=Role.TEXT, depth=10)
            print('search input', search_input_elem)
            assert search_input_elem is not None
            search_input_elem.input("合并执行")
            time.sleep(1)

            search_item_elem = root.find_element(role=Role.LABEL, name="合并执行")
            assert search_item_elem is not None

            search_button_elem = root.find_element(role=Role.PUSH_BUTTON, depth=10)
            print('search input', search_button_elem)
            assert search_button_elem is not None
            search_button_elem.click()

        @retryable
        def _step2_enter_scheme():
            label_elem = root.find_element(name="合并方案")
            assert label_elem is not None

            panel_elem = label_elem.next()
            assert panel_elem is not None

            input_elem = panel_elem.find_element(role=Role.TEXT)
            button_elem = panel_elem.find_element(role=Role.PUSH_BUTTON)
            assert input_elem is not None
            assert button_elem is not None

            input_elem.simulate_click()
            input_elem.simulate_input("^a5")
            input_elem.simulate_input("{ENTER}", pause=1)

            time.sleep(1)
            assert input_elem.text == "财务合并报表-2023"

        @retryable
        def _step3_enter_date_and_query():
            label_elem = root.find_element(name="月")
            assert label_elem is not None

            panel_elem = label_elem.next()
            assert panel_elem is not None

            input_elem = panel_elem.find_element(role=Role.TEXT)
            button_elem = panel_elem.find_element(role=Role.PUSH_BUTTON)
            assert input_elem is not None
            assert button_elem is not None

            input_elem.simulate_click()
            input_elem.simulate_input("^a2023-12-31{ENTER}")

            time.sleep(1)
            assert input_elem.text == "2023-12-31"

            all_sub_radio_elem = root.find_element(role=Role.RADIO_BUTTON, name="所有下级")
            assert all_sub_radio_elem is not None
            all_sub_radio_elem.click()
            assert all_sub_radio_elem.checked

            clear_button_elem = root.find_element(role=Role.PUSH_BUTTON, name="清空值")
            assert clear_button_elem is not None

            query_button_elem = clear_button_elem.next()
            assert query_button_elem is not None and query_button_elem.name == "查询"
            query_button_elem.click()

            label_elem = root.find_element(role=Role.LABEL, name_like="每页行数", width_gte=1)
            assert label_elem is not None

            input_elem = label_elem.next()
            assert input_elem is not None

            if input_elem.text == "500":
                return

            input_elem.simulate_click()
            input_elem.simulate_input("^a500{ENTER}")

        @retryable
        def _step4_click_export_button():
            table_elem = root.find_element(role=Role.TABLE, depth=26)
            table_elem.simulate_click(coords=table_elem.position)
            table_elem.simulate_input('^a')

            export_button_elem = root.find_element(role=Role.PUSH_BUTTON, name="导出")
            export_button_elem.simulate_click()
            time.sleep(1)

            menu_window = self.uia_root.find_element(class_name="SunAwtWindow")
            menu_driver = JABDriver(menu_window.handle)
            menu_root = menu_driver.root()

            export_item_elem = menu_root.find_element(role=Role.MENU_ITEM, name="合并报表")
            export_item_elem.simulate_click()
            time.sleep(1)

        @retryable
        def _step5_export_data():
            dialog_window = self.uia_root.find_element(class_name="SunAwtDialog", name="保存")
            dialog_driver = JABDriver(dialog_window.handle)
            dialog_root = dialog_driver.root()
            time.sleep(1)

            save_input_elem = dialog_root.find_element(role=Role.TEXT)
            save_input_elem.input(save_path)
            time.sleep(1)

            save_button_elem = dialog_root.find_element(role=Role.PUSH_BUTTON, name="保存")

            @retryable(max_retries=5)
            def _click():
                clicked = save_button_elem.click()
                if not clicked:
                    raise Exception("click failed")

            _click()

        _step1_open_tab()
        time.sleep(1)
        _step2_enter_scheme()
        time.sleep(1)
        _step3_enter_date_and_query()
        time.sleep(1)
        _step4_click_export_button()
        time.sleep(1)
        _step5_export_data()
        time.sleep(10)

        files = os.listdir(save_path)
        print(save_path, len(files), files)
        assert len(files) > 0

    def test_export_report_query(self):
        import uuid

        root = self.jab_root

        save_path = "C:\\Users\\leego\\Documents\\nc\\报表数据\\" + str(uuid.uuid4())
        os.makedirs(save_path, exist_ok=True)

        self.jab_driver.set_foreground()

        @retryable
        def _step1_open_tab():
            search_input_elem = root.find_element(role=Role.TEXT, depth=10)
            print('search input', search_input_elem)
            assert search_input_elem is not None
            search_input_elem.input("报表数据查询")
            time.sleep(1)

            search_item_elem = root.find_element(role=Role.LABEL, name="报表数据查询")
            assert search_item_elem is not None

            search_button_elem = root.find_element(role=Role.PUSH_BUTTON, depth=10)
            print('search input', search_button_elem)
            assert search_button_elem is not None
            search_button_elem.click()

        @retryable
        def _step2_enter_scheme():
            label_elem = root.find_element(name="报表主组织")
            assert label_elem is not None

            panel_elem = label_elem.next()
            assert panel_elem is not None

            input_elem = panel_elem.find_element(role=Role.TEXT)
            button_elem = panel_elem.find_element(role=Role.PUSH_BUTTON)
            assert input_elem is not None
            assert button_elem is not None

            input_elem.simulate_click()
            input_elem.simulate_input("^a11401")
            input_elem.simulate_input("{ENTER}", pause=1)

            time.sleep(1)
            assert input_elem.text == "杭州热联集团股份有限公司"

            label_elem = root.find_element(name="任务")
            assert label_elem is not None

            panel_elem = label_elem.next()
            assert panel_elem is not None

            input_elem = panel_elem.find_element(role=Role.TEXT)
            button_elem = panel_elem.find_element(role=Role.PUSH_BUTTON)
            assert input_elem is not None
            assert button_elem is not None

            input_elem.simulate_click()
            input_elem.simulate_input("^a00201")
            input_elem.simulate_input("{ENTER}", pause=1)

            time.sleep(1)
            assert input_elem.text.startswith("合并报表底表")

        @retryable
        def _step3_select_report_tree():
            label_elem = root.find_element(name="报表选择")
            assert label_elem is not None

            panel_elem = label_elem.next()
            assert panel_elem is not None

            input_elem = panel_elem.find_element(role=Role.TEXT)
            button_elem = panel_elem.find_element(role=Role.PUSH_BUTTON)
            assert input_elem is not None
            assert button_elem is not None

            button_elem.simulate_click()

            dialog_handle = win32.find_window(class_name="SunAwtDialog", window_name="任务报表选择")
            dialog_driver = JABDriver(dialog_handle)
            dialog_root = dialog_driver.root()
            time.sleep(1)

            report_tree_elem = dialog_root.find_element(role=Role.CHECK_BOX, name="任务报表树")
            report_tree_elem.simulate_click()
            time.sleep(1)
            if report_tree_elem.checked:
                report_tree_elem.simulate_click()
            time.sleep(1)

            item_elems = dialog_root.find_elements(role=Role.CHECK_BOX, name_in=["(会合02表2023)合并利润表", "(会合01表2023)合并资产负债表", "(会合03表2023)合并现金流量表"])
            assert len(item_elems) == 3
            for elem in item_elems:
                if not elem.checked:
                    elem.simulate_click()

            confirm_elem = dialog_root.find_element(role=Role.PUSH_BUTTON, name="确定(Y)")
            confirm_elem.click()

        @retryable
        def _step4_enter_date_and_query():
            label_elem = root.find_element(name="月")
            assert label_elem is not None

            panel_elem = label_elem.next()
            assert panel_elem is not None

            input_elem = panel_elem.find_element(role=Role.TEXT)
            button_elem = panel_elem.find_element(role=Role.PUSH_BUTTON)
            assert input_elem is not None
            assert button_elem is not None

            input_elem.simulate_click()
            input_elem.simulate_input("^a2023-12-31{ENTER}")

            time.sleep(1)
            assert input_elem.text == "2023-12-31"

            all_sub_radio_elem = root.find_element(role=Role.RADIO_BUTTON, name="所有下级")
            assert all_sub_radio_elem is not None
            all_sub_radio_elem.click()
            assert all_sub_radio_elem.checked

            query_button_elem = root.find_element(role=Role.PUSH_BUTTON, name="查询", description="查询(Ctrl+Enter)")
            assert query_button_elem is not None
            query_button_elem.click()

            label_elem = root.find_element(role=Role.LABEL, name_like="每页行数", width_gte=1)
            assert label_elem is not None

            input_elem = label_elem.next()
            assert input_elem is not None

            if input_elem.text == "500":
                return

            input_elem.simulate_click()
            input_elem.simulate_input("^a500{ENTER}")

        @retryable
        def _step5_click_export_button():
            table_elem = root.find_element(role=Role.TABLE, depth=26)
            table_elem.simulate_click(coords=table_elem.position)
            table_elem.simulate_input('^a')

            export_button_elem = root.find_element(role=Role.PUSH_BUTTON, name="导入导出")
            export_button_elem.simulate_click()
            time.sleep(1)

            menu_window = self.uia_root.find_element(class_name="SunAwtWindow")
            menu_driver = JABDriver(menu_window.handle)
            menu_root = menu_driver.root()

            export_item_elem = menu_root.find_element(role=Role.MENU_ITEM, name="导出Excel")
            export_item_elem.simulate_click()
            time.sleep(1)

        @retryable
        def _step6_export_data():
            dialog_handle = win32.find_window(class_name="SunAwtDialog", window_name="报表数据查询-Excel导出")
            dialog_driver = JABDriver(dialog_handle)
            dialog_root = dialog_driver.root()
            time.sleep(1)

            save_label_elem = dialog_root.find_element(role=Role.LABEL, name="Excel文件名")

            save_input_elem = save_label_elem.next()
            save_input_elem.input(save_path)
            time.sleep(1)

            advance_elem = dialog_root.find_element(role=Role.PANEL, index_in_parent=2, depth=6)
            advance_elem.simulate_click(coords=advance_elem.position)
            time.sleep(1)

            item_elem = dialog_root.find_element(role=Role.CHECK_BOX, name="单一文件")
            assert item_elem is not None
            item_elem.click()

            sheet_elem = dialog_root.find_element(role=Role.PANEL, name="Sheet名称")
            assert sheet_elem is not None

            item_elems = sheet_elem.find_elements(role=Role.CHECK_BOX, name_in=["报表名称", "报表编码", "单位"])
            assert len(item_elems) == 3
            for elem in item_elems:
                if not elem.checked:
                    elem.click()

            confirm_elem = dialog_root.find_element(role=Role.PUSH_BUTTON, name="确定(Y)")

            @retryable(max_retries=5)
            def _click():
                clicked = confirm_elem.click()
                if not clicked:
                    raise Exception("click failed")

            _click()

        _step1_open_tab()
        time.sleep(1)
        _step2_enter_scheme()
        time.sleep(1)
        _step3_select_report_tree()
        time.sleep(1)
        _step4_enter_date_and_query()
        time.sleep(1)
        _step5_click_export_button()
        time.sleep(1)
        _step6_export_data()
        time.sleep(10)

        files = os.listdir(save_path)
        print(save_path, len(files), files)
        assert len(files) > 0
