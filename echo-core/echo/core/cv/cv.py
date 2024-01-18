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


import os
import sys
import time
import types

import cv2
import numpy as np
from PIL import Image
from six import PY2, PY3

from .errors import TargetNotFoundError, InvalidMatchingMethodError, NoModuleError, BaseError, FileNotExistError, TemplateInputError
from .matching.keypoint_matching import KAZEMatching, BRISKMatching, AKAZEMatching, ORBMatching, SIFTMatching, SURFMatching, BRIEFMatching
from .matching.template_matching import TemplateMatching, MultiScaleTemplateMatching


def cocos_min_strategy(w, h, sch_resolution, src_resolution, design_resolution=(960, 640)):
    """图像缩放规则: COCOS中的MIN策略."""
    # 输入参数: w-h待缩放图像的宽高，sch_resolution为待缩放图像的来源分辨率
    #           src_resolution 待适配屏幕的分辨率  design_resolution 软件的设计分辨率
    # 需要分别算出对设计分辨率的缩放比，进而算出src\sch有效缩放比。
    scale_sch = min(1.0 * sch_resolution[0] / design_resolution[0], 1.0 * sch_resolution[1] / design_resolution[1])
    scale_src = min(1.0 * src_resolution[0] / design_resolution[0], 1.0 * src_resolution[1] / design_resolution[1])
    scale = scale_src / scale_sch
    h_re, w_re = int(h * scale), int(w * scale)
    return w_re, h_re


class Settings(object):
    DEBUG = False
    LOG_DIR = None
    LOG_FILE = "log.txt"
    RESIZE_METHOD = staticmethod(cocos_min_strategy)
    # keypoint matching: kaze/brisk/akaze/orb, contrib: sift/surf/brief
    CVSTRATEGY = ["mstpl", "tpl", "sift", "brisk"]
    KEYPOINT_MATCHING_PREDICTION = True
    THRESHOLD = 0.7  # [0, 1]
    THRESHOLD_STRICT = None  # dedicated parameter for assert_exists
    OPDELAY = 0.1
    FIND_TIMEOUT = 20
    FIND_TIMEOUT_TMP = 3
    PROJECT_ROOT = os.environ.get("PROJECT_ROOT", "")  # for ``using`` other script
    SNAPSHOT_QUALITY = 10  # 1-100 https://pillow.readthedocs.io/en/5.1.x/handbook/image-file-formats.html#jpeg
    # Image compression size, e.g. 1200, means that the size of the screenshot does not exceed 1200*1200
    IMAGE_MAXSIZE = os.environ.get("IMAGE_MAXSIZE", None)
    SAVE_IMAGE = True


class TargetPos(object):
    """
    点击目标图片的不同位置，默认为中心点0
    1 2 3
    4 0 6
    7 8 9
    """
    LEFTUP, UP, RIGHTUP = 1, 2, 3
    LEFT, MID, RIGHT = 4, 5, 6
    LEFTDOWN, DOWN, RIGHTDOWN = 7, 8, 9

    def getXY(self, cvret, pos):
        if pos == 0 or pos == self.MID:
            return cvret["result"]
        rect = cvret.get("rectangle")
        if not rect:
            print("could not get rectangle, use mid point instead")
            return cvret["result"]
        w = rect[2][0] - rect[0][0]
        h = rect[2][1] - rect[0][1]
        if pos == self.LEFTUP:
            return rect[0]
        elif pos == self.LEFTDOWN:
            return rect[1]
        elif pos == self.RIGHTDOWN:
            return rect[2]
        elif pos == self.RIGHTUP:
            return rect[3]
        elif pos == self.LEFT:
            return rect[0][0], rect[0][1] + h / 2
        elif pos == self.UP:
            return rect[0][0] + w / 2, rect[0][1]
        elif pos == self.RIGHT:
            return rect[2][0], rect[2][1] - h / 2
        elif pos == self.DOWN:
            return rect[2][0] - w / 2, rect[2][1]
        else:
            print("invalid target_pos:%s, use mid point instead" % pos)
            return cvret["result"]


MATCHING_METHODS = {
    "tpl": TemplateMatching,
    "mstpl": MultiScaleTemplateMatching,
    "kaze": KAZEMatching,
    "brisk": BRISKMatching,
    "akaze": AKAZEMatching,
    "orb": ORBMatching,
    "sift": SIFTMatching,
    "surf": SURFMatching,
    "brief": BRIEFMatching,
}

ST = Settings
G = None


def loop_find(query, timeout=ST.FIND_TIMEOUT, threshold=None, interval=0.5, intervalfunc=None):
    """
    Search for image template in the screen until timeout

    Args:
        query: image template to be found in screenshot
        timeout: time interval how long to look for the image template
        threshold: default is None
        interval: sleep interval before next attempt to find the image template
        intervalfunc: function that is executed after unsuccessful attempt to find the image template

    Raises:
        TargetNotFoundError: when image template is not found in screenshot

    Returns:
        TargetNotFoundError if image template not found, otherwise returns the position where the image template has
        been found in screenshot

    """
    G.LOGGING.info("Try finding: %s", query)
    start_time = time.time()
    while True:
        screen = G.DEVICE.snapshot(filename=None, quality=ST.SNAPSHOT_QUALITY)

        if screen is None:
            G.LOGGING.warning("Screen is None, may be locked")
        else:
            if threshold:
                query.threshold = threshold
            match_pos = query.match_in(screen)
            if match_pos:
                try_log_screen(screen)
                return match_pos

        if intervalfunc is not None:
            intervalfunc()

        # 超时则raise，未超时则进行下次循环:
        if (time.time() - start_time) > timeout:
            try_log_screen(screen)
            raise TargetNotFoundError('Picture %s not found in screen' % query)
        else:
            time.sleep(interval)


def try_log_screen(screen=None, quality=None, max_size=None):
    """
    Save screenshot to file

    Args:
        screen: screenshot to be saved
        quality: The image quality, default is ST.SNAPSHOT_QUALITY
        max_size: the maximum size of the picture, e.g 1200

    Returns:
        {"screen": filename, "resolution": aircv.get_resolution(screen)}

    """
    if not ST.LOG_DIR or not ST.SAVE_IMAGE:
        return
    if not quality:
        quality = ST.SNAPSHOT_QUALITY
    if not max_size:
        max_size = ST.IMAGE_MAXSIZE
    if screen is None:
        screen = G.DEVICE.snapshot(quality=quality)
    filename = "%(time)d.jpg" % {'time': time.time() * 1000}
    filepath = os.path.join(ST.LOG_DIR, filename)
    if screen is not None:
        imwrite(filepath, screen, quality, max_size=max_size)
        return {"screen": filename, "resolution": get_resolution(screen)}
    return None


class Template(object):
    """
    picture as touch/swipe/wait/exists target and extra info for cv match
    filename: pic filename
    target_pos: ret which pos in the pic
    record_pos: pos in screen when recording
    resolution: screen resolution when recording
    rgb: 识别结果是否使用rgb三通道进行校验.
    scale_max: 多尺度模板匹配最大范围.
    scale_step: 多尺度模板匹配搜索步长.
    """

    def __init__(self, filename, threshold=None, target_pos=TargetPos.MID, record_pos=None, resolution=(), rgb=False, scale_max=800, scale_step=0.005):
        self.filename = filename
        self._filepath = None
        self.threshold = threshold or ST.THRESHOLD
        self.target_pos = target_pos
        self.record_pos = record_pos
        self.resolution = resolution
        self.rgb = rgb
        self.scale_max = scale_max
        self.scale_step = scale_step

    @property
    def filepath(self):
        if self._filepath:
            return self._filepath
        # for dirname in G.BASEDIR:
        #     filepath = os.path.join(dirname, self.filename)
        #     if os.path.isfile(filepath):
        #         self._filepath = filepath
        #         return self._filepath
        return self.filename

    def __repr__(self):
        filepath = self.filepath if PY3 else self.filepath.encode(sys.getfilesystemencoding())
        return "Template(%s)" % filepath

    def match_in(self, screen):
        match_result = self._cv_match(screen)
        # G.LOGGING.debug("match result: %s", match_result)
        if not match_result:
            return None
        focus_pos = TargetPos().getXY(match_result, self.target_pos)
        return focus_pos

    def match_in2(self, screen):
        match_result = self._cv_match(screen)
        # G.LOGGING.debug("match result: %s", match_result)
        if not match_result:
            return None
        rect = match_result.get("rectangle")
        return rect[0][0], rect[0][1], rect[2][0], rect[2][1]

    def match_all_in(self, screen):
        image = self._imread()
        image = self._resize_image(image, screen, ST.RESIZE_METHOD)
        return self._find_all_template(image, screen)

    # @logwrap
    def _cv_match(self, screen):
        # in case image file not exist in current directory:
        ori_image = self._imread()
        image = self._resize_image(ori_image, screen, ST.RESIZE_METHOD)
        ret = None
        for method in ST.CVSTRATEGY:
            # get function definition and execute:
            func = MATCHING_METHODS.get(method, None)
            if func is None:
                raise InvalidMatchingMethodError("Undefined method in CVSTRATEGY: '%s', try 'kaze'/'brisk'/'akaze'/'orb'/'surf'/'sift'/'brief' instead." % method)
            else:
                if method in ["mstpl", "gmstpl"]:
                    ret = self._try_match(func, ori_image, screen, threshold=self.threshold, rgb=self.rgb, record_pos=self.record_pos,
                                          resolution=self.resolution, scale_max=self.scale_max, scale_step=self.scale_step)
                else:
                    ret = self._try_match(func, image, screen, threshold=self.threshold, rgb=self.rgb)
            if ret:
                break
        return ret

    @staticmethod
    def _try_match(func, *args, **kwargs):
        # G.LOGGING.debug("try match with %s" % func.__name__)
        try:
            ret = func(*args, **kwargs).find_best()
        except NoModuleError as err:
            # G.LOGGING.warning("'surf'/'sift'/'brief' is in opencv-contrib module. You can use 'tpl'/'kaze'/'brisk'/'akaze'/'orb' in CVSTRATEGY, or reinstall opencv with the contrib module.")
            return None
        except BaseError as err:
            # G.LOGGING.debug(repr(err))
            return None
        else:
            return ret

    def _imread(self):
        return imread(self.filepath)

    def _find_all_template(self, image, screen):
        return TemplateMatching(image, screen, threshold=self.threshold, rgb=self.rgb).find_all()

    def _resize_image(self, image, screen, resize_method):
        """模板匹配中，将输入的截图适配成 等待模板匹配的截图."""
        # 未记录录制分辨率，跳过
        if not self.resolution:
            return image
        screen_resolution = get_resolution(screen)
        # 如果分辨率一致，则不需要进行im_search的适配:
        if tuple(self.resolution) == tuple(screen_resolution) or resize_method is None:
            return image
        if isinstance(resize_method, types.MethodType):
            resize_method = resize_method.__func__
        # 分辨率不一致则进行适配，默认使用cocos_min_strategy:
        h, w = image.shape[:2]
        w_re, h_re = resize_method(w, h, self.resolution, screen_resolution)
        # 确保w_re和h_re > 0, 至少有1个像素:
        w_re, h_re = max(1, w_re), max(1, h_re)
        # 调试代码: 输出调试信息.
        # G.LOGGING.debug("resize: (%s, %s)->(%s, %s), resolution: %s=>%s" % (w, h, w_re, h_re, self.resolution, screen_resolution))
        # 进行图片缩放:
        image = cv2.resize(image, (w_re, h_re))
        return image


class Predictor(object):
    """
    this class predicts the press_point and the area to search im_search.
    """

    DEVIATION = 100

    @staticmethod
    def count_record_pos(pos, resolution):
        """计算坐标对应的中点偏移值相对于分辨率的百分比."""
        _w, _h = resolution
        # 都按宽度缩放，针对G18的实验结论
        delta_x = (pos[0] - _w * 0.5) / _w
        delta_y = (pos[1] - _h * 0.5) / _w
        delta_x = round(delta_x, 3)
        delta_y = round(delta_y, 3)
        return delta_x, delta_y

    @classmethod
    def get_predict_point(cls, record_pos, screen_resolution):
        """预测缩放后的点击位置点."""
        delta_x, delta_y = record_pos
        _w, _h = screen_resolution
        target_x = delta_x * _w + _w * 0.5
        target_y = delta_y * _w + _h * 0.5
        return target_x, target_y

    @classmethod
    def get_predict_area(cls, record_pos, image_wh, image_resolution=(), screen_resolution=()):
        """Get predicted area in screen."""
        x, y = cls.get_predict_point(record_pos, screen_resolution)
        # The prediction area should depend on the image size:
        if image_resolution:
            predict_x_radius = int(image_wh[0] * screen_resolution[0] / (2 * image_resolution[0])) + cls.DEVIATION
            predict_y_radius = int(image_wh[1] * screen_resolution[1] / (2 * image_resolution[1])) + cls.DEVIATION
        else:
            predict_x_radius, predict_y_radius = int(image_wh[0] / 2) + cls.DEVIATION, int(image_wh[1] / 2) + cls.DEVIATION
        area = (x - predict_x_radius, y - predict_y_radius, x + predict_x_radius, y + predict_y_radius)
        return area


def imread(filename, flatten=False):
    """根据图片路径，将图片读取为cv2的图片处理格式."""
    if not os.path.isfile(filename):
        raise FileNotExistError("File not exist: %s" % filename)

    # choose image readin mode: cv2.IMREAD_UNCHANGED=-1, cv2.IMREAD_GRAYSCALE=0, cv2.IMREAD_COLOR=1,
    readin_mode = cv2.IMREAD_GRAYSCALE if flatten else cv2.IMREAD_COLOR

    if PY3:
        img = cv2.imdecode(np.fromfile(filename, dtype=np.uint8), readin_mode)
    else:
        filename = filename.encode(sys.getfilesystemencoding())
        img = cv2.imread(filename, readin_mode)

    return img


def imwrite(filename, img, quality=10, max_size=None):
    """写出图片到本地路径，压缩"""
    if PY2:
        filename = filename.encode(sys.getfilesystemencoding())
    pil_img = cv2_2_pil(img)
    compress_image(pil_img, filename, quality, max_size=max_size)


def get_resolution(img):
    h, w = img.shape[:2]
    return w, h


def print_run_time(func):
    def wrapper(self, *args, **kwargs):
        start_time = time.time()
        ret = func(self, *args, **kwargs)
        t = time.time() - start_time
        # LOGGING.debug("%s() run time is %.2f s." % (func.__name__, t))
        if ret and isinstance(ret, dict):
            ret["time"] = t
        return ret

    return wrapper


def generate_result(middle_point, pypts, confi):
    """Format the result: 定义图像识别结果格式."""
    ret = dict(result=middle_point,
               rectangle=pypts,
               confidence=confi)
    return ret


def check_image_valid(im_source, im_search):
    """Check if the input images valid or not."""
    if im_source is not None and im_source.any() and im_search is not None and im_search.any():
        return True
    else:
        return False


def check_source_larger_than_search(im_source, im_search):
    """检查图像识别的输入."""
    # 图像格式, 确保输入图像为指定的矩阵格式:
    # 图像大小, 检查截图宽、高是否大于了截屏的宽、高:
    h_search, w_search = im_search.shape[:2]
    h_source, w_source = im_source.shape[:2]
    if h_search > h_source or w_search > w_source:
        raise TemplateInputError("error: in template match, found im_search bigger than im_source.")


def img_mat_rgb_2_gray(img_mat):
    """
    Turn img_mat into gray_scale, so that template match can figure the img data.
    "print(type(im_search[0][0])")  can check the pixel type.
    """
    assert isinstance(img_mat[0][0], np.ndarray), "input must be instance of np.ndarray"
    return cv2.cvtColor(img_mat, cv2.COLOR_BGR2GRAY)


def pil_2_cv2(pil_image):
    open_cv_image = np.array(pil_image)
    # Convert RGB to BGR (method-1):
    open_cv_image = cv2.cvtColor(open_cv_image, cv2.COLOR_RGB2BGR)
    # Convert RGB to BGR (method-2):
    # b, g, r = cv2.split(open_cv_image)
    # open_cv_image = cv2.merge([r, g, b])
    return open_cv_image


def cv2_2_pil(cv2_image):
    cv2_im = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
    pil_im = Image.fromarray(cv2_im)
    return pil_im


def compress_image(pil_img, path, quality, max_size=None):
    """
    Save the picture and compress

    :param pil_img: PIL image
    :param path: save path
    :param quality: the image quality, integer in range [1, 99]
    :param max_size: the maximum size of the picture, e.g 1200
    :return:
    """
    if max_size:
        # The picture will be saved in a size <= max_size*max_size
        pil_img.thumbnail((max_size, max_size), Image.LANCZOS)
    quality = int(round(quality))
    if quality <= 0 or quality >= 100:
        raise Exception("SNAPSHOT_QUALITY (" + str(quality) + ") should be an integer in the range [1,99]")
    pil_img.save(path, quality=quality, optimize=True)
