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
import unittest

from echo.utils import win32


class CommonTestSuite(unittest.TestCase):

    def setUp(self):
        self.handle = win32.find_window(class_name="GlassWndClass-GlassWindowClass-2", window_name="Simple FX")

    def tearDown(self):
        pass

    def test_get_window_rect(self):
        rect = win32.get_window_rect(self.handle)
        print(rect)

        assert rect is not None

    def test_move_window(self):
        win32.set_foreground(self.handle)
        time.sleep(0.2)
        win32.move_window(self.handle, x=0, y=0)

    def test_screenshot(self):
        from echo.utils import win32

        # fullscreen
        fullscreen_filename = "./screenshots/win32/fullscreen.png"
        fullscreen_image = win32.screenshot(filename=fullscreen_filename)

        # window
        window_filename = "./screenshots/win32/window.png"
        window_image = win32.screenshot(handle=0xD034C, filename=window_filename)

        assert fullscreen_image is not None
        assert window_image is not None
        assert os.path.exists(fullscreen_filename)
        assert os.path.exists(window_filename)
