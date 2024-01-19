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

from echo.core.driver import matches, gen_matches_kwargs, STR_EXPRS, INT_EXPRS, BOOL_EXPRS
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
                self.enabled = True

        user = User('Echo', 18)
        rules = {
            "name": STR_EXPRS,
            "age": INT_EXPRS,
            "job": STR_EXPRS,
            "enabled": BOOL_EXPRS
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

    def test_matches_docs(self):
        rules = {
            "name": STR_EXPRS,
            "size": INT_EXPRS,
            "enabled": BOOL_EXPRS,
        }
        print(gen_matches_kwargs(rules))

    def test_retrying(self):
        from echo.utils.retrying import retryable

        counter = [0]

        def run(func, err, count=None):
            start = time.perf_counter()
            counter[0] = 0
            if err:
                try:
                    func()
                    assert False
                except:
                    pass
            else:
                func()
            if count is not None:
                assert count == counter[0]
            end = time.perf_counter()
            print(f"run {func.__name__} in {format(end - start, '.6f')} ms")

        @retryable
        def retry1():
            print('run retry1', counter[0])
            if counter[0] < 1:
                counter[0] += 1
                raise Exception()

        @retryable(1)
        def retry2():
            print('run retry2', counter[0])
            if counter[0] < 1:
                counter[0] += 1
                raise Exception()

        @retryable(2)
        def retry3():
            print('run retry3', counter[0])
            if counter[0] < 2:
                counter[0] += 1
                raise Exception()

        @retryable(max_retries=1)
        def retry4():
            print('run retry4', counter[0])
            if counter[0] < 1:
                counter[0] += 1
                raise Exception()

        @retryable(max_retries=1, delay=1)
        def retry5():
            print('run retry5', counter[0])
            if counter[0] < 1:
                counter[0] += 1
                raise Exception()

        @retryable
        def retry6():
            print('run retry6', counter[0])
            counter[0] += 1
            raise Exception()

        @retryable(1)
        def retry7():
            print('run retry7', counter[0])
            counter[0] += 1
            raise Exception()

        @retryable(2)
        def retry8():
            print('run retry8', counter[0])
            counter[0] += 1
            raise Exception()

        @retryable(max_retries=1)
        def retry9():
            print('run retry9', counter[0])
            counter[0] += 1
            raise Exception()

        @retryable(max_retries=1, delay=1)
        def retry10():
            print('run retry10', counter[0])
            counter[0] += 1
            raise Exception()

        class FooException(Exception):
            pass

        class BarException(Exception):
            pass

        @retryable(exception_type=BarException)
        def retry11():
            print('run retry11', counter[0])
            counter[0] += 1
            raise FooException()

        @retryable(exception_type=BarException)
        def retry12():
            print('run retry12', counter[0])
            counter[0] += 1
            raise BarException()

        run(retry1, err=False, count=1)
        run(retry2, err=False, count=1)
        run(retry3, err=False, count=2)
        run(retry4, err=False, count=1)
        run(retry5, err=False, count=1)
        run(retry6, err=True, count=2)
        run(retry7, err=True, count=2)
        run(retry8, err=True, count=3)
        run(retry9, err=True, count=2)
        run(retry10, err=True, count=2)
        run(retry11, err=True, count=1)
        run(retry12, err=True, count=2)

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
