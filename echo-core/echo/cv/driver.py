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


from typing import Optional

from echo.driver import Driver, Element
from echo.utils import win32, to_string


class CVElement(Element):
    def __init__(self, handle: int, process_id: int, process_name: str, root: 'CVElement' = None, parent: 'CVElement' = None):
        self._handle: int = handle
        self._process_id: int = process_id
        self._process_name: str = process_name
        self._root: CVElement = root or self  # TODO root
        self._parent: Optional[CVElement] = parent

    @property
    def handle(self) -> int:
        return self._handle

    @property
    def process_id(self) -> int:
        return self._process_id

    @property
    def process_name(self) -> str:
        return self._process_name

    @property
    def rectangle(self) -> tuple[int, int, int, int]:
        return win32.get_window_rect(self.handle)

    def __str__(self) -> str:
        return to_string(self, 'handle', 'process_id', 'process_name')

    @staticmethod
    def create_root(handle: int) -> Optional['CVElement']:
        process_id = win32.get_process_id_from_handle(handle)
        process_name = win32.get_process_name_by_process_id(process_id)
        return CVElement(handle=handle, process_id=process_id, process_name=process_name)

    @staticmethod
    def create_element(root: 'CVElement', parent: 'CVElement' = None) -> 'CVElement':
        return CVElement(handle=root._handle, process_id=root._process_id, process_name=root._process_name, root=root, parent=parent)


class CVDriver(Driver):
    def find_window(self, handle: int) -> Optional[CVElement]:
        return CVElement.create_root(handle=handle)

    def close(self):
        pass
