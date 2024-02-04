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

from echo.utils.waiting import wait_until, wait


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


class WaitingTestSuite(TestCase):
    def setUp(self):
        self.adder = Adder()

    def _test_waiting(self, func, cost_time_range=None, adder_value=None, result_value=None, err=False):
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

    def test_wait_until_no_args_kwargs_no_parentheses(self):
        # timeout=5, delay=1
        @wait_until
        def _wait():
            self.adder.incr()

        self._test_waiting(_wait, cost_time_range=(5, 5.1), adder_value=5)

    def test_wait_until_no_args_kwargs(self):
        # timeout=5, delay=1
        @wait_until()
        def _wait():
            self.adder.incr()

        self._test_waiting(_wait, cost_time_range=(5, 5.1), adder_value=5)

    def test_wait_until_with_args(self):
        # timeout=5, delay=1
        @wait_until(5, 1)
        def _wait():
            self.adder.incr()

        self._test_waiting(_wait, cost_time_range=(5, 5.1), adder_value=5)

    def test_wait_until_with_kwargs(self):
        @wait_until(timeout=3, delay=0.5)
        def _wait():
            self.adder.incr()

        self._test_waiting(_wait, cost_time_range=(3, 3.1), adder_value=6)

    def test_wait_until_with_validator(self):
        @wait_until(validator=lambda x: x > 1)
        def _wait():
            self.adder.incr()
            return self.adder.value

        self._test_waiting(_wait, cost_time_range=(1, 1.1), adder_value=2)

    def test_wait_until_with_logging(self):
        @wait_until(use_logging=True)
        def _wait():
            self.adder.incr()

        self._test_waiting(_wait, cost_time_range=(5, 5.1), adder_value=5)

    def test_wait_until_with_invalid_timeout(self):
        @wait_until(timeout=-1, delay=1)
        def _wait():
            self.adder.incr()

        self._test_waiting(_wait, err=True)

    def test_wait_until_with_no_delay(self):
        @wait_until(timeout=3, delay=0)
        def _wait():
            self.adder.incr()
            return True

        self._test_waiting(_wait, cost_time_range=(0, 0.1), adder_value=1, err=True)

    def test_wait_until_with_return_true(self):
        @wait_until(timeout=2, delay=1)
        def _wait():
            self.adder.incr()
            if self.adder.value > 1:
                return True

        self._test_waiting(_wait, cost_time_range=(1, 1.1), adder_value=2, err=True)

    def test_wait_until_with_return_value(self):
        @wait_until(timeout=2, delay=1)
        def _wait():
            self.adder.incr()
            if self.adder.value > 1:
                return 'ok'

        self._test_waiting(_wait, cost_time_range=(1, 1.1), adder_value=2, result_value='ok')

    def test_wait_until_pass_args(self):
        @wait_until()
        def _func(a, b, c):
            self.assertEqual(a, 1)
            self.assertEqual(b, 2)
            self.assertEqual(c, 3)
            return True

        _func(1, 2, 3)

    def test_wait_until_pass_kwargs(self):
        @wait_until()
        def _func(a, b, c):
            self.assertEqual(a, 1)
            self.assertEqual(b, 2)
            self.assertEqual(c, 3)
            return True

        _func(a=1, b=2, c=3)

    def test_wait_until_pass_args_kwargs(self):
        @wait_until()
        def _func(*args, **kwargs):
            self.assertEqual(args, (1, 2, 3))
            self.assertEqual(kwargs, {"a": "a", "b": "b", "c": "c"})
            return True

        _func(1, 2, 3, a="a", b="b", c="c")

    def test_wait_pass_args(self):
        def _func(a, b, c):
            self.assertEqual(a, 1)
            self.assertEqual(b, 2)
            self.assertEqual(c, 3)
            return True

        wait(_func, args=(1, 2, 3))

    def test_wait_pass_kwargs(self):
        def _func(a, b, c):
            self.assertEqual(a, 1)
            self.assertEqual(b, 2)
            self.assertEqual(c, 3)
            return True

        wait(_func, kwargs={'a': 1, 'b': 2, 'c': 3})

    def test_wait_pass_args_kwargs(self):
        def _func(*args, **kwargs):
            self.assertEqual(args, (1, 2, 3))
            self.assertEqual(kwargs, {"a": "a", "b": "b", "c": "c"})
            return True

        wait(_func, args=(1, 2, 3), kwargs={"a": "a", "b": "b", "c": "c"})
