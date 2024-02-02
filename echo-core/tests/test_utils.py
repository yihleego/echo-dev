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


import datetime
import os
import time
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

    def test_retrying(self):
        from echo.utils.retrying import retryable

        counter = [0]

        def run(func, err, count=None):
            start = time.perf_counter()
            counter[0] = 0
            if err:
                try:
                    func()
                    raise
                except:
                    pass
            else:
                func()
            if count is not None:
                self.assertEqual(count, counter[0])
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

    def test_retrying_args(self):
        from echo.utils.retrying import retryable, retry

        def retry_args1(*args, **kwargs):
            print('retry_args1', args, kwargs)
            self.assertEqual(args, (1, 2, 3))
            self.assertEqual(kwargs, {"a": "a", "b": "b"})

        def retry_args2(one=None, two=None, three=None, a=None, b=None, none=None):
            print('retry_args2', (one, two, three), {"a": a, "b": b}, none)
            self.assertEqual((one, two, three), (1, 2, 3))
            self.assertEqual({"a": a, "b": b}, {"a": "a", "b": "b"})
            self.assertIsNone(none)

        @retryable
        def retry_args1_wrapper(*args, **kwargs):
            retry_args1(*args, **kwargs)

        @retryable
        def retry_args2_wrapper(one=None, two=None, three=None, a=None, b=None):
            retry_args2(one, two, three, a=a, b=b)

        retry(retry_args1, args=(1, 2, 3), kwargs={"a": "a", "b": "b"})
        retry_args1_wrapper(1, 2, 3, a="a", b="b")

        retry(retry_args2, args=(1, 2, 3), kwargs={"a": "a", "b": "b"})
        retry_args2_wrapper(1, 2, 3, a="a", b="b")

    def test_waiting(self):
        from echo.utils.waiting import wait_until

        counter = [0]

        def run(func, err, count=None):
            start = time.perf_counter()
            counter[0] = 0
            if err:
                try:
                    func()
                    raise
                except:
                    pass
            else:
                func()
            if count is not None:
                self.assertEqual(count, counter[0])
            end = time.perf_counter()
            print(f"run {func.__name__} in {format(end - start, '.6f')} ms")

        @wait_until
        def wait1():
            print('run wait1', datetime.datetime.now())
            counter[0] += 1
            return counter[0] > 1

        @wait_until(5)
        def wait2():
            print('run wait2', datetime.datetime.now())
            counter[0] += 1
            return counter[0] > 1

        @wait_until(timeout=5, use_logging=True)
        def wait3():
            print('run wait3', datetime.datetime.now())
            counter[0] += 1
            return counter[0] > 1

        @wait_until(validator=lambda x: x is False)
        def wait4():
            print('run wait4', datetime.datetime.now())
            counter[0] += 1
            return False

        run(wait1, err=False, count=2)
        run(wait2, err=False, count=2)
        run(wait3, err=False, count=2)
        run(wait4, err=False, count=1)

    def test_waiting_args(self):
        from echo.utils.waiting import wait_until, wait

        def wait_args1(*args, **kwargs):
            print('wait_args1', args, kwargs)
            self.assertEqual(args, (1, 2, 3))
            self.assertEqual(kwargs, {"a": "a", "b": "b"})
            return True

        def wait_args2(one=None, two=None, three=None, a=None, b=None, none=None):
            print('wait_args2', (one, two, three), {"a": a, "b": b}, none)
            self.assertEqual((one, two, three), (1, 2, 3))
            self.assertEqual({"a": a, "b": b}, {"a": "a", "b": "b"})
            self.assertIsNone(none)
            return True

        @wait_until
        def wait_args1_wrapper(*args, **kwargs):
            return wait_args1(*args, **kwargs)

        @wait_until
        def wait_args2_wrapper(one=None, two=None, three=None, a=None, b=None):
            return wait_args2(one, two, three, a=a, b=b)

        wait(wait_args1, args=(1, 2, 3), kwargs={"a": "a", "b": "b"})
        wait_args1_wrapper(1, 2, 3, a="a", b="b")

        wait(wait_args2, args=(1, 2, 3), kwargs={"a": "a", "b": "b"})
        wait_args2_wrapper(1, 2, 3, a="a", b="b")

    def test_kwargs(self):
        def _inner(*arg, val=None, **kwargs):
            print('arg', arg)
            print('kwargs', kwargs)
            print('val', val)
            self.assertEqual(arg, (1, 2))
            self.assertEqual(kwargs, {'a': None, 'b': 'b'})
            self.assertTrue("a" in kwargs)
            self.assertIsNotNone(val)

        _inner(1, 2, a=None, b='b', val=1)

    def test_screenshot(self):
        rect = (10, 10, 100, 100)
        filename = "./screenshots/utils/img.png"
        image = screenshot(rect, filename)
        self.assertIsNotNone(image)
        self.assertTrue(os.path.exists(filename))
