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


import heapq
import threading
import time
from collections import namedtuple
from typing import Union


class Delayed(namedtuple('Event', 'value, time, priority')):
    __slots__ = []

    def __eq__(self, o): return (self.value, self.time, self.priority) == (o.value, o.time, o.priority)

    def __lt__(self, o): return (self.time, self.priority) < (o.time, o.priority)

    def __le__(self, o): return (self.time, self.priority) <= (o.time, o.priority)

    def __gt__(self, o): return (self.time, self.priority) > (o.time, o.priority)

    def __ge__(self, o): return (self.time, self.priority) >= (o.time, o.priority)


class DelayQueue:
    def __init__(self):
        """
        Creates a new DelayQueue that is initially empty.
        """
        self._queue = []
        self._lock = threading.RLock()
        self._cond = threading.Condition(self._lock)

    def get(self, timeout: Union[int, float] = None) -> any:
        """
        Retrieves and removes the head of this queue, waiting if necessary
        until an element with an expired delay is available on this queue,
        or the specified wait time expires.
        :param timeout: timeout in seconds, if None, wait forever
        :return: the head of this queue, or None if the
                 specified waiting time elapses before an element with
                 an expired delay becomes available
        """
        lock = self._lock
        queue = self._queue
        if timeout is None:
            while True:
                with lock:
                    if not queue:
                        self._cond.wait()
                        continue
                    _value, _time, _priority = queue[0]
                    now = time.time()
                    if _time > now:
                        self._cond.wait(_time - now)
                    else:
                        heapq.heappop(queue)
                        return _value
        else:
            _st = time.perf_counter()
            _et = _st + timeout
            _ct = _st
            while True:
                with lock:
                    _ct = time.perf_counter()
                    if _ct > _et:
                        return None
                    if not queue:
                        self._cond.wait(_et - _ct)
                        continue
                    _value, _time, _priority = queue[0]
                    now = time.time()
                    if _time > now:
                        self._cond.wait(min(_et - _ct, _time - now))
                    else:
                        heapq.heappop(queue)
                        return _value

    def add(self, value: any, time: Union[int, float], priority: int = 0) -> Delayed:
        """
        Inserts the specified element into this delay queue.
        :param value: the value to add
        :param time: the time associated with the value
        :param priority: the priority of the element
        :return: the Delayed instance
        """
        if isinstance(value, Delayed):
            e = value
        else:
            e = Delayed(value, time, priority)
        with self._lock:
            heapq.heappush(self._queue, e)
            self._cond.notify()
        return e

    def remove(self, e: Delayed) -> bool:
        """
        Remove the specified element from this delay queue.
        """
        with self._lock:
            try:
                self._queue.remove(e)
                heapq.heapify(self._queue)
                self._cond.notify()
                return True
            except ValueError:
                return False

    def clear(self):
        """
        Clear the queue.
        """
        with self._lock:
            self._queue.clear()

    def qsize(self):
        """
        Return the size of the queue.
        """
        with self._lock:
            return len(self._queue)

    def __len__(self):
        """
        Return the size of the queue.
        """
        with self._lock:
            return len(self._queue)
