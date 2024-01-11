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
import time
import unittest

from pywinauto import mouse

from echo.cv.aircv.utils import pil_2_cv2
from echo.cv.cv import Template
from echo.cv.driver import CVDriver
from echo.utils import win32


class CVTestSuite(unittest.TestCase):

    def setUp(self):
        self.handle = win32.find_window(class_name="GlassWndClass-GlassWindowClass-2", window_name="Simple FX")
        self.driver = CVDriver(self.handle)
        self.root = self.driver.root()
        assert self.root is not None

    def tearDown(self):
        self.driver.close()

    def test_cv(self):
        self.root.set_foreground()
        time.sleep(0.2)

        t = Template("screenshots/uia/button.png")

        fullscreen_image = win32.screenshot()
        pos1 = t.match_in(pil_2_cv2(fullscreen_image))
        print('pos1', pos1)

        window_image = win32.screenshot(self.handle)
        pos2 = t.match_in(pil_2_cv2(window_image))
        print('pos2', pos2)

        rect = self.root.rectangle
        pos3 = (pos2[0] + rect[0], pos2[1] + rect[1])
        print('pos3', pos3, 'rect', rect)

        mouse.click(coords=pos3)
