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

from echo.utils import deep_to_lower, deep_to_upper, deep_strip


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

    def test_kwargs(self):
        def _inner(**kwargs):
            print(kwargs)
            assert "a" in kwargs

        _inner(a=None)
