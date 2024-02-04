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


from unittest import TestCase

from echo.utils.deprecated import deprecated


class DeprecatedTestSuite(TestCase):

    def test_deprecated_func_no_args_kwargs_no_parentheses(self):
        @deprecated
        def _func(a, b):
            return a + b

        self.assertEqual(_func(1, 2), 3)

    def test_deprecated_func_no_args_kwargs(self):
        @deprecated()
        def _func(a, b):
            return a + b

        self.assertEqual(_func(1, 2), 3)

    def test_deprecated_func_with_args(self):
        @deprecated("please use other instead", "1.0.0")
        def _func(a, b):
            return a + b

        self.assertEqual(_func(1, 2), 3)

    def test_deprecated_func_with_kwargs(self):
        @deprecated(reason="please use other instead", version="1.0.0")
        def _func(a, b):
            return a + b

        self.assertEqual(_func(1, 2), 3)

    def test_deprecated_class_no_args_kwargs_no_parentheses(self):
        @deprecated
        class Clz:
            pass

        obj = Clz()
        self.assertTrue(isinstance(obj, Clz))

    def test_deprecated_class_no_args_kwargs(self):
        @deprecated()
        class Clz:
            pass

        obj = Clz()
        self.assertTrue(isinstance(obj, Clz))

    def test_deprecated_class_with_args(self):
        @deprecated("please use other instead", "1.0.0")
        class Clz:
            pass

        obj = Clz()
        self.assertTrue(isinstance(obj, Clz))

    def test_deprecated_class_with_kwargs(self):
        @deprecated(reason="please use other instead", version="1.0.0")
        class Clz:
            pass

        obj = Clz()
        self.assertTrue(isinstance(obj, Clz))

    def test_method_no_args_kwargs_no_parentheses(self):
        class Clz:
            @deprecated
            def test(self, a, b):
                return a + b

        obj = Clz()
        res = obj.test(1, 2)
        self.assertEqual(res, 3)

    def test_method_no_args_kwargs(self):
        class Clz:
            @deprecated()
            def test(self, a, b):
                return a + b

        obj = Clz()
        res = obj.test(1, 2)
        self.assertEqual(res, 3)

    def test_method_with_args(self):
        class Clz:
            @deprecated("please use other instead", "1.0.0")
            def test(self, a, b):
                return a + b

        obj = Clz()
        res = obj.test(1, 2)
        self.assertEqual(res, 3)

    def test_method_with_kwargs(self):
        class Clz:
            @deprecated(reason="please use other instead", version="1.0.0")
            def test(self, a, b):
                return a + b

        obj = Clz()
        res = obj.test(1, 2)
        self.assertEqual(res, 3)

    def test_staticmethod_no_args_kwargs_no_parentheses(self):
        class Clz:
            @staticmethod
            @deprecated
            def create():
                return Clz()

        obj = Clz.create()
        self.assertTrue(isinstance(obj, Clz))

    def test_staticmethod_no_args_kwargs(self):
        class Clz:
            @staticmethod
            @deprecated()
            def create():
                return Clz()

        obj = Clz.create()
        self.assertTrue(isinstance(obj, Clz))

    def test_staticmethod_with_args(self):
        class Clz:
            @staticmethod
            @deprecated("please use other instead", "1.0.0")
            def create():
                return Clz()

        obj = Clz.create()
        self.assertTrue(isinstance(obj, Clz))

    def test_staticmethod_with_kwargs(self):
        class Clz:
            @staticmethod
            @deprecated(reason="please use other instead", version="1.0.0")
            def create():
                return Clz()

        obj = Clz.create()
        self.assertTrue(isinstance(obj, Clz))
