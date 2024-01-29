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


from setuptools import find_packages, setup

setup(
    name='echo',
    description='',
    author='Leego',
    author_email='leegodev@hotmail.com',
    python_requires='>=3.8.13',
    install_requires=[
        'opencv-python==4.9.0.80',
        'opencv-contrib-python==4.9.0.80',
        'numpy==1.26.3',
        'pillow==10.1.0',
        'pywinauto==0.6.8',
        'psutil==5.9.7',
        'pynput==1.7.6',
    ],
    packages=find_packages(),
)
