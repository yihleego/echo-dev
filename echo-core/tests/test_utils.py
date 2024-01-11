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
import unittest

from echo.utils import deep_to_lower, deep_to_upper, deep_strip, matches, STR_EXPRS, INT_EXPRS
from echo.utils.screenshot import screenshot


class CommonTestSuite(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_deep_to_lower(self):
        t1 = deep_to_lower("VALUE")
        t2 = deep_to_lower(["VALUE1", "VALUE2"])
        t3 = deep_to_lower(("VALUE1", "VALUE2"))
        t4 = deep_to_lower({"VALUE1", "VALUE2"})
        t5 = deep_to_lower({"KEY": "VALUE"})
        print(f"{t1}\n{t2}\n{t3}\n{t4}\n{t5}")
        assert t1 == "value"
        assert t2 == ["value1", "value2"]
        assert t3 == ("value1", "value2")
        assert t4 == {"value1", "value2"}
        assert t5 == {"key": "value"}

    def test_deep_to_lower_non_str(self):
        t1 = deep_to_lower(1)
        t2 = deep_to_lower([1, 2])
        t3 = deep_to_lower((1, 2))
        t4 = deep_to_lower({1, 2})
        t5 = deep_to_lower({"Age": 18})
        print(f"{t1}\n{t2}\n{t3}\n{t4}\n{t5}")
        assert t1 == 1
        assert t2 == [1, 2]
        assert t3 == (1, 2)
        assert t4 == {1, 2}
        assert t5 == {"age": 18}

    def test_deep_to_upper(self):
        t1 = deep_to_upper("value")
        t2 = deep_to_upper(["value1", "value2"])
        t3 = deep_to_upper(("value1", "value2"))
        t4 = deep_to_upper({"value1", "value2"})
        t5 = deep_to_upper({"key": "value"})
        print(f"{t1}\n{t2}\n{t3}\n{t4}\n{t5}")
        assert t1 == "VALUE"
        assert t2 == ["VALUE1", "VALUE2"]
        assert t3 == ("VALUE1", "VALUE2")
        assert t4 == {"VALUE1", "VALUE2"}
        assert t5 == {"KEY": "VALUE"}

    def test_deep_strip(self):
        t1 = deep_strip(" Value ")
        t2 = deep_strip([" Value1 ", " Value2 "])
        t3 = deep_strip((" Value1 ", " Value2 "))
        t4 = deep_strip({" Value1 ", " Value2 "})
        t5 = deep_strip({" Key ": " Value "})
        print(f"{t1}\n{t2}\n{t3}\n{t4}\n{t5}")
        assert t1 == "Value"
        assert t2 == ["Value1", "Value2"]
        assert t3 == ("Value1", "Value2")
        assert t4 == {"Value1", "Value2"}
        assert t5 == {"Key": "Value"}

    def test_matches(self):
        class User:
            def __init__(self, name, age):
                self.name = name
                self.age = age
                self.job = None

        user = User('Echo', 18)
        rules = {
            "name": STR_EXPRS,
            "age": INT_EXPRS,
            "job": STR_EXPRS
        }
        assert matches(user, filters=[lambda x: x.name == "Echo"])
        assert matches(user, filters=(lambda x: x.name == "Echo",))
        assert matches(user, rules=rules, name="Echo")
        assert matches(user, rules=rules, name="echo", ignore_case=True)
        assert matches(user, rules=rules, name_like="ch")
        assert matches(user, rules=rules, name_in=["Echo", "RPA"])
        assert matches(user, rules=rules, name_in=["echo", "rpa"], ignore_case=True)
        assert matches(user, rules=rules, name_in_like=["ch", "RPA"])
        assert matches(user, rules=rules, name_in_like=["echo", "rpa"], ignore_case=True)
        assert matches(user, rules=rules, name_regex="^E.*o$")
        assert matches(user, rules=rules, age=18)
        assert matches(user, rules=rules, age_gt=17)
        assert matches(user, rules=rules, age_gte=17)
        assert matches(user, rules=rules, age_gte=18)
        assert ~matches(user, rules=rules, age_gte=19)
        assert matches(user, rules=rules, age_lt=19)
        assert matches(user, rules=rules, age_lte=19)
        assert matches(user, rules=rules, age_lte=18)
        assert ~matches(user, rules=rules, age_lte=17)
        assert matches(user, rules=rules, job_null=True)
        assert ~matches(user, rules=rules, job_null=False)
        assert matches(user, rules=rules, job_null=1)
        assert ~matches(user, rules=rules, job_null=0)

    def test_kwargs(self):
        def _inner(*arg, val=None, **kwargs):
            print('arg', arg)
            print('kwargs', kwargs)
            print('val', val)
            assert arg == (1, 2)
            assert kwargs == {'a': None, 'b': 'b'}
            assert "a" in kwargs
            assert val is not None

        _inner(1, 2, a=None, b='b', val=1)

    def test_screenshot(self):
        rect = (10, 10, 100, 100)
        filename = "./screenshots/utils/img.png"
        image = screenshot(rect, filename)
        assert image is not None
        assert os.path.exists(filename)

    def test_win32_screenshot(self):
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
