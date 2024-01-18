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

from echo.core.driver import Driver, Element


class CVDriver(Driver):
    def root(self) -> Optional['CVElement']:
        return CVElement(driver=self)

    def find_elements(self, filename: str) -> list['CVElement']:
        # TODO
        pass

    def close(self):
        pass


class CVElement(Element):
    def __init__(self, driver: CVDriver, root: 'CVElement' = None, parent: 'CVElement' = None):
        self._driver: CVDriver = driver
        self._root: CVElement = root or self  # TODO root
        self._parent: Optional[CVElement] = parent

    @property
    def driver(self) -> CVDriver:
        return self._driver

    @property
    def role(self) -> str:
        # TODO
        return ""

    @property
    def rectangle(self) -> tuple[int, int, int, int]:
        # TODO
        return 0, 0, 0, 0

    def __str__(self) -> str:
        return f"role: {self.role}, " \
               f"rectangle: {self.rectangle}"
