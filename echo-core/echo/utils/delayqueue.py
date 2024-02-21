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


class Delayed(namedtuple('Delayed', 'value, time, priority')):
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
        cond = self._cond
        queue = self._queue
        if timeout is None:
            while True:
                with lock:
                    if not queue:
                        cond.wait()
                        continue
                    head = queue[0]
                    now = time.time()
                    if head.time > now:
                        cond.wait(head.time - now)
                    else:
                        heapq.heappop(queue)
                        return head.value
        else:
            st = time.perf_counter()
            et = st + timeout
            while True:
                with lock:
                    ct = time.perf_counter()
                    if ct > et:
                        return None
                    if not queue:
                        cond.wait(et - ct)
                        continue
                    head = queue[0]
                    now = time.time()
                    if head.time > now:
                        cond.wait(min(et - ct, head.time - now))
                    else:
                        heapq.heappop(queue)
                        return head.value

    def add(self, item: Union[Delayed, any], time: Union[int, float], priority: int = 0) -> Delayed:
        """
        Inserts the specified element into this delay queue.
        :param item: the item to add
        :param time: the time associated with the item
        :param priority: the priority of the element
        :return: the Delayed instance
        """
        lock = self._lock
        cond = self._cond
        queue = self._queue
        if isinstance(item, Delayed):
            e = item
        else:
            e = Delayed(item, time, priority)
        with lock:
            heapq.heappush(queue, e)
            cond.notify()
        return e

    def remove(self, item: Union[Delayed, any]) -> bool:
        """
        Remove the specified element from this delay queue.
        """
        lock = self._lock
        cond = self._cond
        queue = self._queue
        with lock:
            if isinstance(item, Delayed):
                try:
                    queue.remove(item)
                    heapq.heapify(queue)
                    cond.notify()
                    return True
                except ValueError:
                    return False
            else:
                for e in queue:
                    if e.value == item:
                        queue.remove(e)
                        heapq.heapify(queue)
                        cond.notify()
                        return True
                return False

    def contains(self, item: Union[Delayed, any]) -> bool:
        """
        Return True if item is in the queue.
        """
        with self._lock:
            if isinstance(item, Delayed):
                return item in self._queue
            else:
                for e in self._queue:
                    if e.value == item:
                        return True
            return False

    def clear(self):
        """
        Clear the queue.
        """
        with self._lock:
            self._queue.clear()
            self._cond.notify()

    def qsize(self):
        """
        Return the size of the queue.
        """
        with self._lock:
            return len(self._queue)

    def __contains__(self, item):
        return self.contains(item)

    def __len__(self):
        return self.qsize()
