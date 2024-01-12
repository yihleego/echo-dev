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


from unittest import TestCase, skip

from echo.cv.aircv import imread
from echo.cv.matching import *


class CVTestSuite(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def _test_find(self, cls, find_all=True, find_best=True):
        configs = [
            ("pypi_copy", imread("test_cv/sample_pypi_part_copy.png"), imread("test_cv/sample_pypi_full.png")),
            ("pypi_logo", imread("test_cv/sample_pypi_part_logo.png"), imread("test_cv/sample_pypi_full.png")),
            ("pypi_title", imread("test_cv/sample_pypi_part_title.png"), imread("test_cv/sample_pypi_full.png")),
            ("pypi_version", imread("test_cv/sample_pypi_part_version.png"), imread("test_cv/sample_pypi_full.png")),
        ]
        for c in configs:
            matching = cls(c[1], c[2])
            if find_all:
                results = matching.find_all()
                print(f'[{matching.name}] {c[0]} found all({len(results)}): {results}')
            if find_best:
                best = matching.find_best()
                print(f'[{matching.name}] {c[0]} found best: {best}')
            print('')

    def test_template_matching(self):
        self._test_find(TemplateMatching)

    def test_multi_scale_template_matching(self):
        self._test_find(MultiScaleTemplateMatching, find_all=False)

    def test_multi_scale_template_matching_pre(self):
        self._test_find(MultiScaleTemplateMatchingPre, find_all=False)

    def test_kaze_matching(self):
        self._test_find(KAZEMatching, find_all=False)

    def test_brisk_matching(self):
        self._test_find(BRISKMatching, find_all=False)

    def test_akaze_matching(self):
        self._test_find(AKAZEMatching, find_all=False)

    def test_orb_matching(self):
        self._test_find(ORBMatching, find_all=False)

    def test_brief_matching(self):
        self._test_find(BRIEFMatching, find_all=False)

    def test_sift_matching(self):
        self._test_find(SIFTMatching, find_all=False)

    @skip("surf is not supported")
    def test_surf_matching(self):
        self._test_find(SURFMatching, find_all=False)
