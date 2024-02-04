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
from unittest import TestCase

from echo.utils.retrying import retryable, retry


class Adder:
    _val = 0

    def incr(self):
        self._val += 1
        return self._val

    def reset(self):
        self._val = 0

    @property
    def value(self):
        return self._val

    def __eq__(self, other):
        return self._val == other

    def __str__(self):
        return str(self._val)


class RetryingTestSuite(TestCase):
    def setUp(self):
        self.adder = Adder()

    def _test_retrying(self, func, cost_time_range=None, adder_value=None, result_value=None, err=False):
        self.adder.reset()
        start = time.perf_counter()
        res = None
        msg = None
        raised = False
        try:
            res = func()
        except Exception as e:
            raised = True
            msg = str(e)
        end = time.perf_counter()
        print(f"cost: {end - start}, value: {self.adder.value}, result: {res}, error: {msg}")
        if cost_time_range:
            self.assertTrue(cost_time_range[0] <= end - start <= cost_time_range[1])
        if adder_value:
            self.assertTrue(self.adder == adder_value)
        if result_value:
            self.assertTrue(res == result_value)
        if err:
            self.assertTrue(raised)
        return res

    def test_retryable_no_args_kwargs_no_parentheses(self):
        # max_retries=1, delay=0
        @retryable
        def _retry():
            self.adder.incr()

        self._test_retrying(_retry, cost_time_range=(0, 0.1), adder_value=1)

    def test_retryable_no_args_kwargs(self):
        # max_retries=1, delay=0
        @retryable()
        def _retry():
            self.adder.incr()

        self._test_retrying(_retry, cost_time_range=(0, 0.1), adder_value=1)

    def test_retryable_with_args(self):
        # max_retries=1, delay=0
        @retryable(5, 1)
        def _retry():
            self.adder.incr()

        self._test_retrying(_retry, cost_time_range=(0, 0.1), adder_value=1)

    def test_retryable_with_kwargs(self):
        @retryable(max_retries=1, delay=0)
        def _retry():
            self.adder.incr()

        self._test_retrying(_retry, cost_time_range=(0, 0.1), adder_value=1)

    def test_retryable_with_error(self):
        @retryable(max_retries=3, delay=1)
        def _retry():
            self.adder.incr()
            if self.adder.value <= 2:
                raise Exception("error")

        self._test_retrying(_retry, cost_time_range=(2, 2.1), adder_value=3)

    def test_retryable_with_exception_type(self):
        class FooException(Exception):
            def __init__(self, message):
                super().__init__(message)

        class BarException(Exception):
            def __init__(self, message):
                super().__init__(message)

        @retryable(max_retries=3, delay=1, exception_type=FooException)
        def _retry1():
            self.adder.incr()
            if self.adder.value <= 2:
                raise FooException("foo")

        @retryable(max_retries=3, delay=1, exception_type=FooException)
        def _retry2():
            self.adder.incr()
            if self.adder.value <= 2:
                raise BarException("bar")

        self._test_retrying(_retry1, cost_time_range=(2, 2.1), adder_value=3)
        self._test_retrying(_retry2, cost_time_range=(0, 0.1), adder_value=1, err=True)

    def test_retryable_with_error_message(self):
        @retryable(error_message="Customized error messages")
        def _retry():
            raise Exception("Hello")
            pass

        self._test_retrying(_retry, err=True)

    def test_retryable_with_logging(self):
        @retryable(max_retries=3, delay=1, use_logging=True)
        def _retry():
            self.adder.incr()
            if self.adder.value <= 2:
                raise Exception("error")

        self._test_retrying(_retry, cost_time_range=(2, 2.1), adder_value=3)

    def test_retryable_with_invalid_max_retries(self):
        @retryable(max_retries=-1, delay=1)
        def _retry():
            self.adder.incr()

        self._test_retrying(_retry, err=True)

    def test_retryable_pass_args(self):
        @retryable()
        def _func(a, b, c):
            self.assertEqual(a, 1)
            self.assertEqual(b, 2)
            self.assertEqual(c, 3)

        _func(1, 2, 3)
        retry(_func, args=(1, 2, 3))

    def test_retryable_pass_kwargs(self):
        @retryable()
        def _func(a, b, c):
            self.assertEqual(a, 1)
            self.assertEqual(b, 2)
            self.assertEqual(c, 3)

        _func(a=1, b=2, c=3)
        retry(_func, kwargs={'a': 1, 'b': 2, 'c': 3})

    def test_retryable_pass_args_kwargs(self):
        @retryable()
        def _func(*args, **kwargs):
            self.assertEqual(args, (1, 2, 3))
            self.assertEqual(kwargs, {"a": "a", "b": "b", "c": "c"})

        _func(1, 2, 3, a="a", b="b", c="c")
        retry(_func, args=(1, 2, 3), kwargs={"a": "a", "b": "b", "c": "c"})

    def test_retry_pass_args(self):
        def _func(a, b, c):
            self.assertEqual(a, 1)
            self.assertEqual(b, 2)
            self.assertEqual(c, 3)

        retry(_func, args=(1, 2, 3))

    def test_retry_pass_kwargs(self):
        def _func(a, b, c):
            self.assertEqual(a, 1)
            self.assertEqual(b, 2)
            self.assertEqual(c, 3)

        retry(_func, kwargs={'a': 1, 'b': 2, 'c': 3})

    def test_retry_pass_args_kwargs(self):
        def _func(*args, **kwargs):
            self.assertEqual(args, (1, 2, 3))
            self.assertEqual(kwargs, {"a": "a", "b": "b", "c": "c"})

        retry(_func, args=(1, 2, 3), kwargs={"a": "a", "b": "b", "c": "c"})
