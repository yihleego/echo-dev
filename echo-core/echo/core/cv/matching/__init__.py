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


from .keypoint_matching import KAZEMatching, BRISKMatching, AKAZEMatching, ORBMatching, BRIEFMatching, SIFTMatching, SURFMatching
from .matching import Matched, Matching
from .template_matching import TemplateMatching, MultiScaleTemplateMatching, PresetMultiScaleTemplateMatching

__all__ = [
    'Matched',
    'Matching',
    'TemplateMatching',
    'MultiScaleTemplateMatching',
    'PresetMultiScaleTemplateMatching',
    'KAZEMatching',
    'BRISKMatching',
    'AKAZEMatching',
    'ORBMatching',
    'BRIEFMatching',
    'SIFTMatching',
    'SURFMatching',
]
