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


import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

import cv2
import numpy as np


@dataclass
class Matched:
    rectangle: tuple[int, int, int, int]  # left, top, right, bottom
    confidence: float  # 0.0 ~ 1.0
    cost: float  # seconds


class Matching(ABC):
    def __init__(self, im_search, im_source, threshold: float = 0.8, rgb: bool = True):
        super().__init__()
        self.im_source = im_source
        self.im_search = im_search
        self.threshold: float = threshold
        self.rgb: bool = rgb
        self.perf_count_last = 0

    @abstractmethod
    def find_all(self) -> list[Matched]:
        raise NotImplementedError

    @abstractmethod
    def find_best(self) -> Optional[Matched]:
        raise NotImplementedError

    def check_image_valid(self, im_source, im_search) -> bool:
        return im_source is not None \
            and im_search is not None \
            and im_source.any() \
            and im_search.any()

    def check_image_size(self, im_source, im_search) -> bool:
        # 图像格式, 确保输入图像为指定的矩阵格式:
        # 图像大小, 检查截图宽、高是否大于了截屏的宽、高:
        h_search, w_search = im_search.shape[:2]
        h_source, w_source = im_source.shape[:2]
        return h_search <= h_source and w_search <= w_source

    def start_perf_count(self):
        self.perf_count_last = time.perf_counter()

    def end_perf_count(self) -> float:
        cur = time.perf_counter()
        res = cur - self.perf_count_last
        self.perf_count_last = cur
        return res


def img_mat_rgb_2_gray(img_mat):
    """
    Turn img_mat into gray_scale, so that template match can figure the img data.
    "print(type(im_search[0][0])")  can check the pixel type.
    """
    assert isinstance(img_mat[0][0], np.ndarray), "input must be instance of np.ndarray"
    return cv2.cvtColor(img_mat, cv2.COLOR_BGR2GRAY)


def cal_ccoeff_confidence(im_source, im_search):
    """求取两张图片的可信度，使用TM_CCOEFF_NORMED方法."""
    # 扩展置信度计算区域
    im_source = cv2.copyMakeBorder(im_source, 10, 10, 10, 10, cv2.BORDER_REPLICATE)
    # 加入取值范围干扰，防止算法过于放大微小差异
    im_source[0, 0] = 0
    im_source[0, 1] = 255

    im_source, im_search = img_mat_rgb_2_gray(im_source), img_mat_rgb_2_gray(im_search)
    res = cv2.matchTemplate(im_source, im_search, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    return max_val


def cal_rgb_confidence(img_src_rgb, img_sch_rgb):
    """同大小彩图计算相似度."""
    # 减少极限值对hsv角度计算的影响
    img_src_rgb = np.clip(img_src_rgb, 10, 245)
    img_sch_rgb = np.clip(img_sch_rgb, 10, 245)
    # 转HSV强化颜色的影响
    img_src_rgb = cv2.cvtColor(img_src_rgb, cv2.COLOR_BGR2HSV)
    img_sch_rgb = cv2.cvtColor(img_sch_rgb, cv2.COLOR_BGR2HSV)

    # 扩展置信度计算区域
    img_src_rgb = cv2.copyMakeBorder(img_src_rgb, 10, 10, 10, 10, cv2.BORDER_REPLICATE)
    # 加入取值范围干扰，防止算法过于放大微小差异
    img_src_rgb[0, 0] = 0
    img_src_rgb[0, 1] = 255

    # 计算BGR三通道的confidence，存入bgr_confidence
    src_bgr, sch_bgr = cv2.split(img_src_rgb), cv2.split(img_sch_rgb)
    bgr_confidence = [0, 0, 0]
    for i in range(3):
        res_temp = cv2.matchTemplate(src_bgr[i], sch_bgr[i], cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res_temp)
        bgr_confidence[i] = max_val

    return min(bgr_confidence)


def crop_image(img, rect):
    """
        区域截图，同时返回截取结果 和 截取偏移;
        Crop image , rect = [x_min, y_min, x_max ,y_max].
        (airtest中有用到)
    """

    if isinstance(rect, (list, tuple)) and len(rect) == 4:
        height, width = img.shape[:2]
        # 获取在图像中的实际有效区域：
        x_min, y_min, x_max, y_max = [int(i) for i in rect]
        x_min, y_min = max(0, x_min), max(0, y_min)
        x_min, y_min = min(width - 1, x_min), min(height - 1, y_min)
        x_max, y_max = max(0, x_max), max(0, y_max)
        x_max, y_max = min(width - 1, x_max), min(height - 1, y_max)

        # 返回剪切的有效图像+左上角的偏移坐标：
        img_crop = img[y_min:y_max, x_min:x_max]
        return img_crop
    else:
        raise Exception("to crop a image, rect should be a list like: [x_min, y_min, x_max, y_max].")


def check_cv_version_is_new():
    """opencv版本是3.0或4.0以上, API接口与2.0的不同."""
    if cv2.__version__.startswith("3.") or cv2.__version__.startswith("4."):
        return True
    else:
        return False
