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
from unittest import TestCase

from echo.core.driver import match, gen_match_docs, STR_EXPRS, INT_EXPRS, BOOL_EXPRS
from echo.utils.screenshot import screenshot
from echo.utils.strings import deep_to_lower, deep_to_upper, deep_strip


class CommonTestSuite(TestCase):

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
        self.assertEqual(t1, "value")
        self.assertEqual(t2, ["value1", "value2"])
        self.assertEqual(t3, ("value1", "value2"))
        self.assertEqual(t4, {"value1", "value2"})
        self.assertEqual(t5, {"key": "value"})

    def test_deep_to_lower_non_str(self):
        t1 = deep_to_lower(1)
        t2 = deep_to_lower([1, 2])
        t3 = deep_to_lower((1, 2))
        t4 = deep_to_lower({1, 2})
        t5 = deep_to_lower({"Age": 18})
        print(f"{t1}\n{t2}\n{t3}\n{t4}\n{t5}")
        self.assertEqual(t1, 1)
        self.assertEqual(t2, [1, 2])
        self.assertEqual(t3, (1, 2))
        self.assertEqual(t4, {1, 2})
        self.assertEqual(t5, {"age": 18})

    def test_deep_to_upper(self):
        t1 = deep_to_upper("value")
        t2 = deep_to_upper(["value1", "value2"])
        t3 = deep_to_upper(("value1", "value2"))
        t4 = deep_to_upper({"value1", "value2"})
        t5 = deep_to_upper({"key": "value"})
        print(f"{t1}\n{t2}\n{t3}\n{t4}\n{t5}")
        self.assertEqual(t1, "VALUE")
        self.assertEqual(t2, ["VALUE1", "VALUE2"])
        self.assertEqual(t3, ("VALUE1", "VALUE2"))
        self.assertEqual(t4, {"VALUE1", "VALUE2"})
        self.assertEqual(t5, {"KEY": "VALUE"})

    def test_deep_strip(self):
        t1 = deep_strip(" Value ")
        t2 = deep_strip([" Value1 ", " Value2 "])
        t3 = deep_strip((" Value1 ", " Value2 "))
        t4 = deep_strip({" Value1 ", " Value2 "})
        t5 = deep_strip({" Key ": " Value "})
        print(f"{t1}\n{t2}\n{t3}\n{t4}\n{t5}")
        self.assertEqual(t1, "Value")
        self.assertEqual(t2, ["Value1", "Value2"])
        self.assertEqual(t3, ("Value1", "Value2"))
        self.assertEqual(t4, {"Value1", "Value2"})
        self.assertEqual(t5, {"Key": "Value"})

    def test_match(self):
        class User:
            def __init__(self, name, age):
                self.name = name
                self.age = age
                self.job = None
                self.enabled = True

        user = User('Echo', 18)
        rules = {
            "name": STR_EXPRS,
            "age": INT_EXPRS,
            "job": STR_EXPRS,
            "enabled": BOOL_EXPRS
        }
        self.assertTrue(match(user, filters=[lambda x: x.name == "Echo"]))
        self.assertTrue(match(user, filters=(lambda x: x.name == "Echo",)))
        self.assertTrue(match(user, rules=rules, name="Echo"))
        self.assertTrue(match(user, rules=rules, ignore_case=True, name="echo"))
        self.assertTrue(match(user, rules=rules, name_like="ch"))
        self.assertTrue(match(user, rules=rules, name_in=["Echo", "RPA"]))
        self.assertTrue(match(user, rules=rules, ignore_case=True, name_in=["echo", "rpa"]))
        self.assertTrue(match(user, rules=rules, name_in_like=["ch", "RPA"]))
        self.assertTrue(match(user, rules=rules, ignore_case=True, name_in_like=["echo", "rpa"]))
        self.assertTrue(match(user, rules=rules, name_regex="^E.*o$"))
        self.assertTrue(match(user, rules=rules, age=18))
        self.assertTrue(match(user, rules=rules, age_gt=17))
        self.assertTrue(match(user, rules=rules, age_gte=17))
        self.assertTrue(match(user, rules=rules, age_gte=18))
        self.assertFalse(match(user, rules=rules, age_gte=19))
        self.assertTrue(match(user, rules=rules, age_lt=19))
        self.assertTrue(match(user, rules=rules, age_lte=19))
        self.assertTrue(match(user, rules=rules, age_lte=18))
        self.assertFalse(match(user, rules=rules, age_lte=17))
        self.assertTrue(match(user, rules=rules, job_null=True))
        self.assertFalse(match(user, rules=rules, job_null=False))
        self.assertTrue(match(user, rules=rules, job_null=1))
        self.assertFalse(match(user, rules=rules, job_null=0))

    def test_match_docs(self):
        rules = {
            "name": STR_EXPRS,
            "size": INT_EXPRS,
            "enabled": BOOL_EXPRS,
        }
        print(gen_match_docs(rules))

    def test_screenshot(self):
        rect = (10, 10, 100, 100)
        filename = "./screenshots/utils/img.png"
        image = screenshot(rect, filename)
        self.assertIsNotNone(image)
        self.assertTrue(os.path.exists(filename))
