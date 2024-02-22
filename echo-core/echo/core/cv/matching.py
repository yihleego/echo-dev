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
from collections import namedtuple
from typing import Optional

import cv2
import numpy as np

from .errors import HomographyError

Matched = namedtuple('Matched', ['rectangle', 'confidence', 'cost'])
Matched.rectangle.__doc__ = 'left, top, right, bottom'
Matched.confidence.__doc__ = '0.0 ~ 1.0'
Matched.cost.__doc__ = 'seconds'


class Matching(ABC):
    def __init__(self, query, train, threshold: float = 0.8, rgb: bool = True):
        super().__init__()
        self.query = query
        self.train = train
        self.threshold: float = threshold
        self.rgb: bool = rgb

    @abstractmethod
    def find_best(self) -> Optional[Matched]:
        pass

    def _cal_ccoeff_confidence(self, query, train) -> float:
        """
        Calculate the confidence of two images, Use the TM_CCOEFF_NORMED method.
        """
        train = cv2.copyMakeBorder(train, 10, 10, 10, 10, cv2.BORDER_REPLICATE)
        train[0, 0] = 0
        train[0, 1] = 255

        image = cv2.cvtColor(train, cv2.COLOR_BGR2GRAY)
        templ = cv2.cvtColor(query, cv2.COLOR_BGR2GRAY)
        res = cv2.matchTemplate(image, templ, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        return max_val

    def _cal_rgb_confidence(self, query, train) -> float:
        """
        Calculate the confidence of two RGB images of the same size.
        """
        train = np.clip(train, 10, 245)
        query = np.clip(query, 10, 245)
        train = cv2.cvtColor(train, cv2.COLOR_BGR2HSV)
        query = cv2.cvtColor(query, cv2.COLOR_BGR2HSV)

        train = cv2.copyMakeBorder(train, 10, 10, 10, 10, cv2.BORDER_REPLICATE)
        train[0, 0] = 0
        train[0, 1] = 255

        image_bgr, template_bgr = cv2.split(train), cv2.split(query)
        bgr_confidence = [0, 0, 0]
        for i in range(3):
            res = cv2.matchTemplate(image_bgr[i], template_bgr[i], cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            bgr_confidence[i] = max_val
        return sum(bgr_confidence) / 3


class KeypointMatching(Matching, ABC):
    def __init__(self, query, train, threshold: float = 0.8, rgb: bool = True, filter_ratio: float = 0.59):
        super().__init__(query, train, threshold, rgb)
        self.filter_ratio = filter_ratio
        self.detector = None
        self.matcher = None
        self._init_detector()

    @abstractmethod
    def _init_detector(self):
        pass

    def find_best(self) -> Optional[Matched]:
        perf_start = time.perf_counter()

        query_keypoints, train_keypoints, good_matches = self._get_keypoints()
        good_matches_len = len(good_matches)
        if good_matches_len <= 1:
            return None
        elif good_matches_len == 2:
            origin_result = self._handle_two_good_points(query_keypoints, train_keypoints, good_matches)
        elif good_matches_len == 3:
            origin_result = self._handle_three_good_points(query_keypoints, train_keypoints, good_matches)
        else:
            origin_result = self._handle_more_good_points(query_keypoints, train_keypoints, good_matches)
        if origin_result is None:
            return None
        middle_point, pypts, w_h_range = origin_result

        x_min, x_max, y_min, y_max, w, h = w_h_range
        target_img = self.train[y_min:y_max, x_min:x_max]
        resize_img = cv2.resize(target_img, (w, h))
        confidence = self._cal_confidence(resize_img)
        if confidence < self.threshold:
            return None
        rectangle = (x_min, y_min, x_max, y_max)
        return Matched(rectangle, confidence, time.perf_counter() - perf_start)

    def _get_keypoints(self):
        query_keypoints, query_descriptors = self._get_keypoints_and_descriptors(self.query)
        train_keypoints, train_descriptors = self._get_keypoints_and_descriptors(self.train)
        matches = self._match_descriptors(query_descriptors, train_descriptors)

        filtered = [m for m, n in matches if m.distance < self.filter_ratio * n.distance]
        good_matches, temp_points = [], [[]]
        for m in filtered:
            pt = [int(train_keypoints[m.trainIdx].pt[0]), int(train_keypoints[m.trainIdx].pt[1])]
            if pt not in temp_points:
                good_matches.append(m)
                temp_points.append(pt)
        return query_keypoints, train_keypoints, good_matches

    def _get_keypoints_and_descriptors(self, image):
        keypoints, descriptors = self.detector.detectAndCompute(image, None)
        return keypoints, descriptors

    def _match_descriptors(self, query_descriptors, train_descriptors):
        return self.matcher.knnMatch(query_descriptors, train_descriptors, k=2)

    def _handle_two_good_points(self, kp_sch, kp_src, good):
        pts_sch1 = int(kp_sch[good[0].queryIdx].pt[0]), int(kp_sch[good[0].queryIdx].pt[1])
        pts_sch2 = int(kp_sch[good[1].queryIdx].pt[0]), int(kp_sch[good[1].queryIdx].pt[1])
        pts_src1 = int(kp_src[good[0].trainIdx].pt[0]), int(kp_src[good[0].trainIdx].pt[1])
        pts_src2 = int(kp_src[good[1].trainIdx].pt[0]), int(kp_src[good[1].trainIdx].pt[1])
        return self._get_origin_result_with_two_points(pts_sch1, pts_sch2, pts_src1, pts_src2)

    def _handle_three_good_points(self, kp_sch, kp_src, good):
        pts_sch1 = int(kp_sch[good[0].queryIdx].pt[0]), int(kp_sch[good[0].queryIdx].pt[1])
        pts_sch2 = int((kp_sch[good[1].queryIdx].pt[0] + kp_sch[good[2].queryIdx].pt[0]) / 2), int((kp_sch[good[1].queryIdx].pt[1] + kp_sch[good[2].queryIdx].pt[1]) / 2)
        pts_src1 = int(kp_src[good[0].trainIdx].pt[0]), int(kp_src[good[0].trainIdx].pt[1])
        pts_src2 = int((kp_src[good[1].trainIdx].pt[0] + kp_src[good[2].trainIdx].pt[0]) / 2), int((kp_src[good[1].trainIdx].pt[1] + kp_src[good[2].trainIdx].pt[1]) / 2)
        return self._get_origin_result_with_two_points(pts_sch1, pts_sch2, pts_src1, pts_src2)

    def _get_origin_result_with_two_points(self, pts_sch1, pts_sch2, pts_src1, pts_src2):
        middle_point = [int((pts_src1[0] + pts_src2[0]) / 2), int((pts_src1[1] + pts_src2[1]) / 2)]
        pypts = []
        if pts_sch1[0] == pts_sch2[0] or pts_sch1[1] == pts_sch2[1] or pts_src1[0] == pts_src2[0] or pts_src1[1] == pts_src2[1]:
            return None
        h, w = self.query.shape[:2]
        h_s, w_s = self.train.shape[:2]
        x_scale = abs(1.0 * (pts_src2[0] - pts_src1[0]) / (pts_sch2[0] - pts_sch1[0]))
        y_scale = abs(1.0 * (pts_src2[1] - pts_src1[1]) / (pts_sch2[1] - pts_sch1[1]))
        sch_middle_point = int((pts_sch1[0] + pts_sch2[0]) / 2), int((pts_sch1[1] + pts_sch2[1]) / 2)
        middle_point[0] = middle_point[0] - int((sch_middle_point[0] - w / 2) * x_scale)
        middle_point[1] = middle_point[1] - int((sch_middle_point[1] - h / 2) * y_scale)
        middle_point[0] = max(middle_point[0], 0)
        middle_point[0] = min(middle_point[0], w_s - 1)
        middle_point[1] = max(middle_point[1], 0)
        middle_point[1] = min(middle_point[1], h_s - 1)

        x_min, x_max = int(max(middle_point[0] - (w * x_scale) / 2, 0)), int(min(middle_point[0] + (w * x_scale) / 2, w_s - 1))
        y_min, y_max = int(max(middle_point[1] - (h * y_scale) / 2, 0)), int(min(middle_point[1] + (h * y_scale) / 2, h_s - 1))
        pts = np.float32([[x_min, y_min], [x_min, y_max], [x_max, y_max], [x_max, y_min]]).reshape(-1, 1, 2)
        for npt in pts.astype(int).tolist():
            pypts.append(tuple(npt[0]))
        return middle_point, pypts, [x_min, x_max, y_min, y_max, w, h]

    def _handle_more_good_points(self, kp_sch, kp_src, good):
        sch_pts, img_pts = np.float32([kp_sch[m.queryIdx].pt for m in good]).reshape(-1, 1, 2), np.float32([kp_src[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
        M, mask = self._find_homography(sch_pts, img_pts)
        matches_mask = mask.ravel().tolist()
        selected = [v for k, v in enumerate(good) if matches_mask[k]]

        sch_pts, img_pts = np.float32([kp_sch[m.queryIdx].pt for m in selected]).reshape(-1, 1, 2), np.float32([kp_src[m.trainIdx].pt for m in selected]).reshape(-1, 1, 2)
        M, mask = self._find_homography(sch_pts, img_pts)
        h, w = self.query.shape[:2]
        h_s, w_s = self.train.shape[:2]
        pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
        dst = cv2.perspectiveTransform(pts, M)

        def cal_rect_pts(dst):
            return [tuple(npt[0]) for npt in dst.astype(int).tolist()]

        pypts = cal_rect_pts(dst)
        lt, br = pypts[0], pypts[2]
        middle_point = int((lt[0] + br[0]) / 2), int((lt[1] + br[1]) / 2)
        x_min, x_max = min(lt[0], br[0]), max(lt[0], br[0])
        y_min, y_max = min(lt[1], br[1]), max(lt[1], br[1])
        x_min, x_max = int(max(x_min, 0)), int(max(x_max, 0))
        x_min, x_max = int(min(x_min, w_s - 1)), int(min(x_max, w_s - 1))
        y_min, y_max = int(max(y_min, 0)), int(max(y_max, 0))
        y_min, y_max = int(min(y_min, h_s - 1)), int(min(y_max, h_s - 1))
        pts = np.float32([[x_min, y_min], [x_min, y_max], [x_max, y_max], [x_max, y_min]]).reshape(-1, 1, 2)
        pypts = cal_rect_pts(pts)

        return middle_point, pypts, [x_min, x_max, y_min, y_max, w, h]

    def _find_homography(self, sch_pts, src_pts):
        try:
            M, mask = cv2.findHomography(sch_pts, src_pts, cv2.RANSAC, 5.0)
        except Exception:
            import traceback
            traceback.print_exc()
            raise HomographyError("OpenCV error in _find_homography()...")
        else:
            if mask is None:
                raise HomographyError("In _find_homography(), find no transformation matrix...")
            else:
                return M, mask

    def _cal_confidence(self, resize_img):
        if self.rgb:
            confidence = self._cal_rgb_confidence(self.query, resize_img)
        else:
            confidence = self._cal_ccoeff_confidence(self.query, resize_img)
        return (1 + confidence) / 2


class KAZEMatching(KeypointMatching):
    def _init_detector(self):
        self.detector = cv2.KAZE_create()
        self.matcher = cv2.BFMatcher(cv2.NORM_L1)


class BRISKMatching(KeypointMatching):
    def _init_detector(self):
        self.detector = cv2.BRISK_create()
        self.matcher = cv2.BFMatcher(cv2.NORM_HAMMING)


class AKAZEMatching(KeypointMatching):
    def _init_detector(self):
        self.detector = cv2.AKAZE_create()
        self.matcher = cv2.BFMatcher(cv2.NORM_L1)


class ORBMatching(KeypointMatching):
    def _init_detector(self):
        self.detector = cv2.ORB_create()
        self.matcher = cv2.BFMatcher(cv2.NORM_HAMMING)


class BRIEFMatching(KeypointMatching):
    def _init_detector(self):
        try:
            self.star_detector = cv2.xfeatures2d.StarDetector_create()
            self.brief_extractor = cv2.xfeatures2d.BriefDescriptorExtractor_create()
        except:
            raise ModuleNotFoundError("There is no BRIEF module in your OpenCV environment, please install contrib module!")
        self.matcher = cv2.BFMatcher(cv2.NORM_L1)

    def _get_keypoints_and_descriptors(self, image):
        # find the keypoints with STAR
        keypoints = self.star_detector.detect(image, None)
        # compute the descriptors with BRIEF
        keypoints, descriptors = self.brief_extractor.compute(image, keypoints)
        return keypoints, descriptors


class SIFTMatching(KeypointMatching):
    def _init_detector(self):
        FLANN_INDEX_KDTREE = 0
        try:
            self.detector = cv2.SIFT_create(edgeThreshold=10)
        except AttributeError:
            try:
                self.detector = cv2.xfeatures2d.SIFT_create(edgeThreshold=10)
            except:
                raise ModuleNotFoundError("There is no SIFT module in your OpenCV environment, please install contrib module!")
        self.matcher = cv2.FlannBasedMatcher({'algorithm': FLANN_INDEX_KDTREE, 'trees': 5}, dict(checks=50))


class SURFMatching(KeypointMatching):
    def _init_detector(self):
        FLANN_INDEX_KDTREE = 0
        HESSIAN_THRESHOLD = 400
        UPRIGHT = 0
        try:
            self.detector = cv2.xfeatures2d.SURF_create(HESSIAN_THRESHOLD, upright=UPRIGHT)
        except:
            raise ModuleNotFoundError("There is no SURF module in your OpenCV environment, please install contrib module!")
        self.matcher = cv2.FlannBasedMatcher({'algorithm': FLANN_INDEX_KDTREE, 'trees': 5}, dict(checks=50))
