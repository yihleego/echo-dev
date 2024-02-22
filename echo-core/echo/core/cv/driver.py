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


from typing import Optional, Type, Tuple, List

import cv2
import numpy as np
from PIL import Image

from .matching import Matching, KAZEMatching, BRISKMatching, AKAZEMatching, ORBMatching, BRIEFMatching, SIFTMatching, SURFMatching
from ..driver import Driver, Element

RECOMMENDED_MATCHING_TYPES = [
    SIFTMatching,
    BRISKMatching,
]

ALL_MATCHING_TYPES = [
    KAZEMatching,
    BRISKMatching,
    AKAZEMatching,
    ORBMatching,
    BRIEFMatching,
    SIFTMatching,
    SURFMatching,
]


class CVDriver(Driver):
    def __init__(self, handle: int, process_id: int = None, process_name: str = None, window_name: str = None, class_name: str = None,
                 matching_types: List[Type[Matching]] = None):
        super().__init__(handle, process_id, process_name, window_name, class_name)
        self._matching_types: List[Type[Matching]] = matching_types or RECOMMENDED_MATCHING_TYPES

    def root(self) -> Optional['CVElement']:
        return CVElement(driver=self, rectangle=self.rectangle, confidence=1.0)

    def find_element(self, image) -> Optional['CVElement']:
        query, train = self._read(image)
        for matching_type in self._matching_types:
            matching = matching_type(query, train)
            found = matching.find_best()
            if found:
                return CVElement(driver=self, rectangle=found.rectangle, confidence=found.confidence)
        return None

    def _read(self, image):
        if isinstance(image, str):
            query = cv2.imread(image)
        elif isinstance(image, Image.Image):
            query = np.array(image)
        elif isinstance(image, np.ndarray):
            query = image
        else:
            raise ValueError(repr(type(image)))
        train = np.array(self.screenshot())
        return query, train


class CVElement(Element):
    def __init__(self, driver: CVDriver, rectangle: Tuple[int, int, int, int], confidence: float):
        self._driver: CVDriver = driver
        self._rectangle: Tuple[int, int, int, int] = rectangle
        self._confidence: float = confidence

    @property
    def driver(self) -> CVDriver:
        return self._driver

    @property
    def rectangle(self) -> Tuple[int, int, int, int]:
        return self._rectangle

    @property
    def confidence(self) -> float:
        return self._confidence

    @property
    def x(self) -> int:
        return self._rectangle[0]

    @property
    def y(self) -> int:
        return self._rectangle[1]

    @property
    def width(self) -> int:
        return self._rectangle[2] - self._rectangle[0]

    @property
    def height(self) -> int:
        return self._rectangle[3] - self._rectangle[1]

    @property
    def position(self) -> Tuple[int, int]:
        return self._rectangle[0], self._rectangle[1]

    @property
    def size(self) -> Tuple[int, int]:
        return self._rectangle[2] - self._rectangle[0], self._rectangle[3] - self._rectangle[1]

    def click(self, **kwargs):
        return self.simulate_click(**kwargs)

    def input(self, **kwargs):
        return self.simulate_input(**kwargs)

    def text(self):
        # TODO OCR
        raise NotImplementedError

    def __str__(self) -> str:
        return f"rectangle: {self.rectangle}, " \
               f"confidence: {self.confidence}"
