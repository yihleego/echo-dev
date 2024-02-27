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


import random
from unittest import TestCase, skip

from echo.core.cv.matching import *


class CVTestSuite(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def _test_find_all(self, cls):
        configs = [
            ("pypi_copy", imread("samples/sample_pypi_part_copy.png"), imread("samples/sample_pypi_full_duplicate.png")),
            ("pypi_logo", imread("samples/sample_pypi_part_logo.png"), imread("samples/sample_pypi_full_duplicate.png")),
            ("pypi_title", imread("samples/sample_pypi_part_title.png"), imread("samples/sample_pypi_full_duplicate.png")),
            ("pypi_version", imread("samples/sample_pypi_part_version.png"), imread("samples/sample_pypi_full_duplicate.png")),
        ]
        for c in configs:
            matching = cls(c[1], c[2])
            results = matching.find_all()
            print(f'[{cls.__name__}] {c[0]} found all({len(results)}): {results}')
            print('')

    def _test_find_best(self, cls):
        configs = [
            ("pypi_copy", imread("samples/sample_pypi_part_copy.png"), imread("samples/sample_pypi_full.png")),
            ("pypi_copy_small", imread("samples/sample_pypi_part_copy_small.png"), imread("samples/sample_pypi_full.png")),
            ("pypi_copy_large", imread("samples/sample_pypi_part_copy_large.png"), imread("samples/sample_pypi_full.png")),
            ("pypi_logo", imread("samples/sample_pypi_part_logo.png"), imread("samples/sample_pypi_full.png")),
            ("pypi_logo_small", imread("samples/sample_pypi_part_logo_small.png"), imread("samples/sample_pypi_full.png")),
            ("pypi_logo_large", imread("samples/sample_pypi_part_logo_large.png"), imread("samples/sample_pypi_full.png")),
            ("pypi_title", imread("samples/sample_pypi_part_title.png"), imread("samples/sample_pypi_full.png")),
            ("pypi_title_small", imread("samples/sample_pypi_part_title_small.png"), imread("samples/sample_pypi_full.png")),
            ("pypi_title_large", imread("samples/sample_pypi_part_title_large.png"), imread("samples/sample_pypi_full.png")),
            ("pypi_version", imread("samples/sample_pypi_part_version.png"), imread("samples/sample_pypi_full.png")),
            ("pypi_version_small", imread("samples/sample_pypi_part_version_small.png"), imread("samples/sample_pypi_full.png")),
            ("pypi_version_large", imread("samples/sample_pypi_part_version_large.png"), imread("samples/sample_pypi_full.png")),
        ]
        for c in configs:
            matching = cls(c[1], c[2])
            best = matching.find_best()
            print(f'[{cls.__name__}] {c[0]} found best: {best}')
            print('')

    def _test_random(self, clses):
        train = imread("samples/QQ20240205-134306@2x.png")
        h, w = train.shape[:2]
        left, top = random.randint(0, w / 2), random.randint(0, h / 2)
        right, bottom = random.randint(left + 10, w), random.randint(top + 10, h)
        # right, bottom = left + 200, top + 200
        rect = (left, top, right, bottom)
        query = train[top:bottom, left:right]
        print(f'rect: {rect}')
        for cls in clses:
            try:
                matching = cls(query, train)
                best = matching.show_result()
                print(f'[{cls.__name__}] found best: {best}')
            except:
                pass

    def test_kaze_matching(self):
        self._test_find_best(KAZEMatching)

    def test_brisk_matching(self):
        self._test_find_best(BRISKMatching)

    def test_akaze_matching(self):
        self._test_find_best(AKAZEMatching)

    def test_orb_matching(self):
        self._test_find_best(ORBMatching)

    def test_brief_matching(self):
        self._test_find_best(BRIEFMatching)

    def test_sift_matching(self):
        self._test_find_best(SIFTMatching)

    @skip("surf is not supported")
    def test_surf_matching(self):
        self._test_find_best(SURFMatching)

    # def test_111(self):
    #     self._test_random([
    #         SIFTMatching, ])


def imread(filename, flatten=False):
    # choose image readin mode: cv2.IMREAD_UNCHANGED=-1, cv2.IMREAD_GRAYSCALE=0, cv2.IMREAD_COLOR=1,
    readin_mode = cv2.IMREAD_GRAYSCALE if flatten else cv2.IMREAD_COLOR
    img = cv2.imdecode(np.fromfile(filename, dtype=np.uint8), readin_mode)
    return img
