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
import threading
import time
from unittest import TestCase

from echo.utils.delayqueue import DelayQueue


class DelayQueueTestSuite(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_add(self):
        q = DelayQueue()

        now = time.time()
        q.add('e', now + 4)
        q.add('d', now + 3)
        q.add('a', now + 0)
        q.add('c', now + 2)
        q.add('b', now + 1)

        self.assertEqual(len(q), 5)
        self.assertEqual(q.get(), 'a')
        self.assertEqual(len(q), 4)
        self.assertEqual(q.get(), 'b')
        self.assertEqual(len(q), 3)
        self.assertEqual(q.get(), 'c')
        self.assertEqual(len(q), 2)
        self.assertEqual(q.get(), 'd')
        self.assertEqual(len(q), 1)
        self.assertEqual(q.get(), 'e')
        self.assertEqual(len(q), 0)

    def test_get(self):
        q = DelayQueue()

        def _test():
            print(datetime.datetime.now(), "thread:", threading.current_thread().name, "waiting")
            v = q.get()
            print(datetime.datetime.now(), "thread:", threading.current_thread().name, "value:", v)
            self.assertTrue(v is not None)

        threads = []
        for i in range(5):
            threads.append(threading.Thread(target=_test, name=str(i)))
        for t in threads:
            t.start()

        print(datetime.datetime.now(), 'started')

        now = time.time()
        q.add('e', now + 4)
        q.add('d', now + 3)
        q.add('a', now + 0)
        q.add('c', now + 2)
        q.add('b', now + 1)

        time.sleep(5)

    def test_get_boundary(self):
        q = DelayQueue()

        def _test():
            print(datetime.datetime.now(), "thread:", threading.current_thread().name, "waiting")
            v = q.get()
            print(datetime.datetime.now(), "thread:", threading.current_thread().name, "value:", v)
            self.assertTrue(v is not None)

        threads = []
        for i in range(5):
            threads.append(threading.Thread(target=_test, name=str(i), daemon=True))
        for t in threads:
            t.start()

        print(datetime.datetime.now(), 'started')

        now = time.time()
        q.add('e', now + 1)
        q.add('d', now)
        q.add('a', now - 3)
        q.add('c', now - 1)
        q.add('b', now - 2)

        time.sleep(2)

    def test_get_timeout(self):
        q = DelayQueue()

        def _test():
            targets = ['a', None, 'b', None, 'c', None]
            while True:
                v = q.get(timeout=1)
                print(datetime.datetime.now(), v)
                self.assertEqual(v, targets.pop(0))

        print(datetime.datetime.now(), 'started')

        now = time.time()
        q.add('a', now + 1)
        q.add('b', now + 3)
        q.add('c', now + 5)
        time.sleep(0.1)

        threading.Thread(target=_test, daemon=True).start()
        time.sleep(6)

    def test_get_timeout_boundary(self):
        q = DelayQueue()

        def _test():
            print(datetime.datetime.now(), "thread:", threading.current_thread().name, "waiting")
            v = q.get()
            print(datetime.datetime.now(), "thread:", threading.current_thread().name, "value:", v)
            self.assertTrue(v is not None)

        threads = []
        for i in range(5):
            threads.append(threading.Thread(target=_test, name=str(i)))

        print(datetime.datetime.now(), 'started')

        now = time.time()
        q.add('a', now - 5)
        q.add('b', now - 3)
        q.add('c', now)
        q.add('d', now + 1)
        q.add('e', now + 2)
        time.sleep(0.1)

        for t in threads:
            t.start()

        time.sleep(5)

    def test_priority(self):
        q = DelayQueue()

        now = time.time()
        q.add('a', now + 1, 1)
        q.add('b', now + 1, 0)

        v = q.get()
        print(datetime.datetime.now(), v)
        self.assertEqual(v, 'b')

        v = q.get()
        print(datetime.datetime.now(), v)
        self.assertEqual(v, 'a')

    def test_remove(self):
        q = DelayQueue()

        now = time.time()
        e1 = q.add('a', now + 1)
        e2 = q.add('b', now + 1)

        self.assertEqual(len(q), 2)
        self.assertTrue(q.remove(e1))
        self.assertFalse(q.remove(e1))
        self.assertEqual(len(q), 1)
        self.assertTrue(q.remove(e2))
        self.assertFalse(q.remove(e2))
        self.assertEqual(len(q), 0)

    def test_clear(self):
        q = DelayQueue()

        now = time.time()
        q.add('a', now + 1)
        q.add('b', now + 1)

        self.assertEqual(len(q), 2)
        q.clear()
        self.assertEqual(len(q), 0)

    def test_qsize(self):
        q = DelayQueue()

        now = time.time()
        q.add('e', now + 5)
        q.add('d', now + 4)
        q.add('a', now + 1)
        q.add('c', now + 3)
        q.add('b', now + 2)

        self.assertEqual(len(q), 5)
        self.assertEqual(q.qsize(), 5)
