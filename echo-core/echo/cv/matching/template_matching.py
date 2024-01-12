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

from .matching import *
from ..aircv import TemplateInputError


class TemplateMatching(Matching):
    def __init__(self, im_search, im_source, threshold: float = 0.8, rgb: bool = True, max_result_size=10):
        super().__init__(im_search, im_source, threshold, rgb)
        self.max_result_size = max_result_size

    @property
    def name(self):
        return "Template Matching"

    def find_all(self):
        """基于模板匹配查找多个目标区域的方法."""
        # 第一步：校验图像输入
        if not self.check_image_size(self.im_source, self.im_search):
            return []
        # 第二步：计算模板匹配的结果矩阵res
        res = self._get_template_result_matrix()
        # 第三步：依次获取匹配结果
        result = []
        h, w = self.im_search.shape[:2]
        while True:
            # 本次循环中,取出当前结果矩阵中的最优值
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            # 求取可信度:
            confidence = self._get_confidence_from_matrix(max_loc, max_val, w, h)
            if confidence < self.threshold or len(result) > self.max_result_size:
                break
            # 求取识别位置: 目标中心 + 目标区域:
            middle_point, rectangle = self._get_target_rectangle(max_loc, w, h)
            one_good_match = generate_result(middle_point, rectangle, confidence)
            result.append(one_good_match)
            # 屏蔽已经取出的最优结果,进入下轮循环继续寻找:
            # cv2.floodFill(res, None, max_loc, (-1000,), max(max_val, 0), flags=cv2.FLOODFILL_FIXED_RANGE)
            cv2.rectangle(res, (int(max_loc[0] - w / 2), int(max_loc[1] - h / 2)), (int(max_loc[0] + w / 2), int(max_loc[1] + h / 2)), (0, 0, 0), -1)
        return result

    def find_best(self):
        """基于kaze进行图像识别，只筛选出最优区域."""
        """函数功能：找到最优结果."""
        # 第一步：校验图像输入
        if not self.check_image_size(self.im_source, self.im_search):
            return None
        # 第二步：计算模板匹配的结果矩阵res
        res = self._get_template_result_matrix()
        # 第三步：依次获取匹配结果
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        h, w = self.im_search.shape[:2]
        # 求取可信度:
        confidence = self._get_confidence_from_matrix(max_loc, max_val, w, h)
        # 求取识别位置: 目标中心 + 目标区域:
        middle_point, rectangle = self._get_target_rectangle(max_loc, w, h)
        best_match = generate_result(middle_point, rectangle, confidence)
        # LOGGING.debug("[%s] threshold=%s, result=%s" % (self.METHOD_NAME, self.threshold, best_match))

        return best_match if confidence >= self.threshold else None

    def _get_confidence_from_matrix(self, max_loc, max_val, w, h):
        """根据结果矩阵求出confidence."""
        # 求取可信度:
        if self.rgb:
            # 如果有颜色校验,对目标区域进行BGR三通道校验:
            img_crop = self.im_source[max_loc[1]:max_loc[1] + h, max_loc[0]: max_loc[0] + w]
            confidence = cal_rgb_confidence(img_crop, self.im_search)
        else:
            confidence = max_val

        return confidence

    def _get_template_result_matrix(self):
        """求取模板匹配的结果矩阵."""
        # 灰度识别: cv2.matchTemplate( )只能处理灰度图片参数
        s_gray, i_gray = img_mat_rgb_2_gray(self.im_search), img_mat_rgb_2_gray(self.im_source)
        return cv2.matchTemplate(i_gray, s_gray, cv2.TM_CCOEFF_NORMED)

    def _get_target_rectangle(self, left_top_pos, w, h):
        """根据左上角点和宽高求出目标区域."""
        x_min, y_min = left_top_pos
        # 中心位置的坐标:
        x_middle, y_middle = int(x_min + w / 2), int(y_min + h / 2)
        # 左下(min,max)->右下(max,max)->右上(max,min)
        left_bottom_pos, right_bottom_pos = (x_min, y_min + h), (x_min + w, y_min + h)
        right_top_pos = (x_min + w, y_min)
        # 点击位置:
        middle_point = (x_middle, y_middle)
        # 识别目标区域: 点序:左上->左下->右下->右上, 左上(min,min)右下(max,max)
        rectangle = (left_top_pos, left_bottom_pos, right_bottom_pos, right_top_pos)

        return middle_point, rectangle


class MultiScaleTemplateMatching(Matching):
    """多尺度模板匹配."""

    def __init__(self, im_search, im_source, threshold: float = 0.8, rgb: bool = True, record_pos=None, resolution=(), scale_max=800, scale_step=0.005, deviation=150):
        super().__init__(im_search, im_source, threshold, rgb)
        self.record_pos = record_pos
        self.resolution = resolution
        self.scale_max = scale_max
        self.scale_step = scale_step
        self.deviation = deviation

    @property
    def name(self):
        return "Multi-scale Template Matching"

    def find_all(self):
        raise NotImplementedError

    def find_best(self):
        """函数功能：找到最优结果."""
        # 第一步：校验图像输入
        if not self.check_image_size(self.im_source, self.im_search):
            return None

        # 第二步：计算模板匹配的结果矩阵res
        s_gray, i_gray = img_mat_rgb_2_gray(self.im_search), img_mat_rgb_2_gray(self.im_source)
        confidence, max_loc, w, h, _ = self.multi_scale_search(i_gray, s_gray, ratio_min=0.01, ratio_max=0.99, src_max=self.scale_max, step=self.scale_step, threshold=self.threshold)

        # 求取识别位置: 目标中心 + 目标区域:
        middle_point, rectangle = self._get_target_rectangle(max_loc, w, h)
        best_match = generate_result(middle_point, rectangle, confidence)
        # LOGGING.debug("[%s] threshold=%s, result=%s" %(self.METHOD_NAME, self.threshold, best_match))

        return best_match if confidence >= self.threshold else None

    def _get_confidence_from_matrix(self, max_loc, w, h):
        """根据结果矩阵求出confidence."""
        sch_h, sch_w = self.im_search.shape[0], self.im_search.shape[1]
        if self.rgb:
            # 如果有颜色校验,对目标区域进行BGR三通道校验:
            img_crop = self.im_source[max_loc[1]:max_loc[1] + h, max_loc[0]: max_loc[0] + w]
            confidence = cal_rgb_confidence(cv2.resize(img_crop, (sch_w, sch_h)), self.im_search)
        else:
            img_crop = self.im_source[max_loc[1]:max_loc[1] + h, max_loc[0]: max_loc[0] + w]
            confidence = cal_ccoeff_confidence(cv2.resize(img_crop, (sch_w, sch_h)), self.im_search)

        return confidence

    def _get_target_rectangle(self, left_top_pos, w, h):
        """根据左上角点和宽高求出目标区域."""
        x_min, y_min = left_top_pos
        # 中心位置的坐标:
        x_middle, y_middle = int(x_min + w / 2), int(y_min + h / 2)
        # 左下(min,max)->右下(max,max)->右上(max,min)
        left_bottom_pos, right_bottom_pos = (x_min, y_min + h), (x_min + w, y_min + h)
        right_top_pos = (x_min + w, y_min)
        # 点击位置:
        middle_point = (x_middle, y_middle)
        # 识别目标区域: 点序:左上->左下->右下->右上, 左上(min,min)右下(max,max)
        rectangle = (left_top_pos, left_bottom_pos, right_bottom_pos, right_top_pos)

        return middle_point, rectangle

    @staticmethod
    def _resize_by_ratio(src, templ, ratio=1.0, templ_min=10, src_max=800):
        """根据模板相对屏幕的长边 按比例缩放屏幕"""
        # 截屏最大尺寸限制
        sr = min(src_max / max(src.shape), 1.0)
        src = cv2.resize(src, (int(src.shape[1] * sr), int(src.shape[0] * sr)))
        # 截图尺寸缩放
        h, w = src.shape[0], src.shape[1]
        th, tw = templ.shape[0], templ.shape[1]
        if th / h >= tw / w:
            tr = (h * ratio) / th
        else:
            tr = (w * ratio) / tw
        templ = cv2.resize(templ, (max(int(tw * tr), 1), max(int(th * tr), 1)))
        return src, templ, tr, sr

    @staticmethod
    def _org_size(max_loc, w, h, tr, sr):
        """获取原始比例的框"""
        max_loc = (int((max_loc[0] / sr)), int((max_loc[1] / sr)))
        w, h = int((w / sr)), int((h / sr))
        return max_loc, w, h

    def multi_scale_search(self, org_src, org_templ, templ_min=10, src_max=800, ratio_min=0.01, ratio_max=0.99, step=0.01, threshold=0.8, time_out=3.0):
        """多尺度模板匹配"""
        mmax_val = 0
        max_info = None
        r = ratio_min
        t = time.time()
        while r <= ratio_max:
            src, templ, tr, sr = self._resize_by_ratio(
                org_src.copy(), org_templ.copy(), r, src_max=src_max)
            if min(templ.shape) > templ_min:
                src[0, 0] = templ[0, 0] = 0
                src[0, 1] = templ[0, 1] = 255
                result = cv2.matchTemplate(src, templ, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                h, w = templ.shape
                if mmax_val < max_val:
                    mmax_val = max_val
                    max_info = (r, max_val, max_loc, w, h, tr, sr)
                time_cost = time.time() - t
                if time_cost > time_out and max_val >= threshold:
                    omax_loc, ow, oh = self._org_size(max_loc, w, h, tr, sr)
                    confidence = self._get_confidence_from_matrix(omax_loc, ow, oh)
                    if confidence >= threshold:
                        return confidence, omax_loc, ow, oh, r
            r += step
        if max_info is None:
            return 0, (0, 0), 0, 0, 0
        max_r, max_val, max_loc, w, h, tr, sr = max_info
        omax_loc, ow, oh = self._org_size(max_loc, w, h, tr, sr)
        confidence = self._get_confidence_from_matrix(omax_loc, ow, oh)
        return confidence, omax_loc, ow, oh, max_r


class MultiScaleTemplateMatchingPre(MultiScaleTemplateMatching):
    """基于截图预设条件的多尺度模板匹配."""

    DEVIATION = 150

    @property
    def name(self):
        return "Multi-scale Template Matching Pre"

    def find_best_result(self):
        """函数功能：找到最优结果."""
        if self.resolution != ():
            # 第一步：校验图像输入
            if not self.check_image_size(self.im_source, self.im_search):
                return None

            if self.resolution[0] < self.im_search.shape[1] or self.resolution[1] < self.im_search.shape[0]:
                raise TemplateInputError("error: resolution is too small.")
            # 第二步：计算模板匹配的结果矩阵res
            if not self.record_pos is None:
                area, self.resolution = self._get_area_scope(self.im_source, self.im_search, self.record_pos, self.resolution)
                self.im_source = crop_image(self.im_source, area)
                if not self.check_image_size(self.im_source, self.im_search):
                    return None
            r_min, r_max = self._get_ratio_scope(
                self.im_source, self.im_search, self.resolution)
            s_gray, i_gray = img_mat_rgb_2_gray(self.im_search), img_mat_rgb_2_gray(self.im_source)
            confidence, max_loc, w, h, _ = self.multi_scale_search(
                i_gray, s_gray, ratio_min=r_min, ratio_max=r_max, step=self.scale_step,
                threshold=self.threshold, time_out=1.0)
            if not self.record_pos is None:
                max_loc = (max_loc[0] + area[0], max_loc[1] + area[1])

            # 求取识别位置: 目标中心 + 目标区域:
            middle_point, rectangle = self._get_target_rectangle(max_loc, w, h)
            best_match = generate_result(middle_point, rectangle, confidence)
            # LOGGING.debug("[%s] threshold=%s, result=%s" % (self.METHOD_NAME, self.threshold, best_match))

            return best_match if confidence >= self.threshold else None
        else:
            return None

    def _get_ratio_scope(self, src, templ, resolution):
        """预测缩放比的上下限."""
        H, W = src.shape[0], src.shape[1]
        th, tw = templ.shape[0], templ.shape[1]
        w, h = resolution
        rmin = min(H / h, W / w)  # 新旧模板比下限
        rmax = max(H / h, W / w)  # 新旧模板比上限
        ratio = max(th / H, tw / W)  # 小图大图比
        r_min = ratio * rmin
        r_max = ratio * rmax
        return max(r_min, self.scale_step), min(r_max, 0.99)

    def get_predict_point(self, record_pos, screen_resolution):
        """预测缩放后的点击位置点."""
        delta_x, delta_y = record_pos
        _w, _h = screen_resolution
        target_x = delta_x * _w + _w * 0.5
        target_y = delta_y * _w + _h * 0.5
        return target_x, target_y

    def _get_area_scope(self, src, templ, record_pos, resolution):
        """预测搜索区域."""
        H, W = src.shape[0], src.shape[1]
        th, tw = templ.shape[0], templ.shape[1]
        w, h = resolution
        x, y = self.get_predict_point(record_pos, (W, H))
        predict_x_radius = max(int(tw * W / (w)), self.DEVIATION)
        predict_y_radius = max(int(th * H / (h)), self.DEVIATION)
        area = (
            max(x - predict_x_radius, 0),
            max(y - predict_y_radius, 0),
            min(x + predict_x_radius, W),
            min(y + predict_y_radius, H),
        )
        return area, (w * (area[3] - area[1]) / W, h * (area[2] - area[0]) / H)
