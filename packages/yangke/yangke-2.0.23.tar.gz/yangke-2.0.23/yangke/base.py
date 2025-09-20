# 对自己编写的其他模块都不依赖的方法放置在这里，放置模块交叉引用导致的问题
import copy
import ctypes
import inspect
import math
import os
import re
import time
import traceback
from typing import Optional
import threading

import pywintypes
from pathlib2 import Path  # pathlib的更新版本
import argparse
import sys
from loguru import logger
import numpy as np
import base64
import socket
import select
import datetime
import pickle
import pandas as pd
from functools import wraps

try:
    from PIL import Image, ImageDraw
    import matplotlib.pyplot as plt
except:
    print(f"目前32位python3.10不支持安装pillow和matplotlib，建议切换成64位python")


class PolyCurve:
    """
    多项式曲线，根据一系列x和y坐标根据最小二乘法拟合多项式曲线
    """

    def __init__(self, x_list, y_list, deg=1):
        """
        多项式拟合曲线，根据x_list和y_list拟合多项式曲线，只能拟合y=ax+b形式的曲线，对多元方法无效，多元方法请参考fit_surface()

        :param x_list: 已知的x点列表
        :param y_list: 一致的y点列表
        :param deg: 多项式阶次
        """
        self.x = np.array(x_list)
        self.y = np.array(y_list)
        self.z = np.polyfit(self.x, self.y, deg)
        self.func = np.poly1d(self.z)

    def get_value(self, x):
        """
        获取曲线上x点上对应的y值

        :param x:
        :return:
        """
        return self.func(x)

    def plot(self, xlim=None, ylim=None):
        xp = np.linspace(min(self.x), max(self.x))
        _ = plt.plot(self.x, self.y, '.', xp, self.func(xp), '-')
        if xlim is not None:
            plt.xlim()
        if ylim is not None:
            plt.ylim()
        plt.show()


def get_key_value(cls):
    """
    装饰Enum子类的装饰器，被该装饰器装饰的Enum类可以使用.get_keys()和get_values()方法获取类的键列表和值列表。
    例如：
    @get_key_value
    class Tags(Enum):
        电功率1 = "N1DCS"
        电功率2 = "N2DCS"
        电功率3 = "N3DCS"

    print(Tags.get_keys())  # 输出['电功率1', '电功率2', '电功率3']
    print(Tags.get_values())  # 输出['N1DCS', 'N2DCS', 'N3DCS']
    print(Tags.get("电功率1"))  # 输出"N1DCS"
    print(Tags("N1DCS").name)  # 输出"电功率1"

    :param cls:
    :return:
    """
    cls_name = cls.__name__

    def get_keys():
        return list(cls.__members__.keys())

    def get_values():
        return [v.value for _, v in cls.__members__.items()]

    def get(key):
        if key in cls.get_keys():
            return cls.__members__.get(key).value
        else:
            return None

    cls.get_keys = get_keys
    cls.get_values = get_values
    cls.get = get
    return cls


def read_from_yaml(file: str, encoding="utf8"):
    """
    不能删除，因为base模块在使用

    :param file:
    :param encoding:
    :return:
    """
    import yaml  # pip install pyyaml 32位python使用
    if not os.path.exists(file):  # 文件不存在，返回空字典
        return {}
    with open(file, 'r', encoding=encoding) as f:
        content = f.read()
    """
    Loader的几种加载方式 
    BaseLoader--仅加载最基本的YAML 
    SafeLoader--安全地加载YAML语言的子集。建议用于加载不受信任的输入。 
    FullLoader--加载完整的YAML语言。避免任意代码执行。这是当前（PyYAML 5.1）默认加载器调用 
            yaml.load(input)（发出警告后）。
    UnsafeLoader--（也称为Loader向后兼容性）原始的Loader代码，可以通过不受信任的数据输入轻松利用。"""
    try:
        obj = yaml.load(content, Loader=yaml.FullLoader)
    except:
        traceback.print_exc()
    return obj


def get_args(setting_file: str = "default", args_name: dict = None):
    """
    处理命令行参数，默认从"settings.yaml"中加载参数配置，也可以通过参数出入。
    如果setting_file取值"default"，则从项目目录加载settings.yml或者settings.yaml文件。
    setting_file的优先级更高，args_name提供的相当于是默认值
    如果既不存在命令行参数，也不存在配置文件，则返回None
    yaml文件示例如下：
--------------------------settings.yaml----------------------------------
args:
  description: "args of app1"
  kv:
    - short: n
      long: name
      default: get
      description: "the name of image"
    - short: t
      long: tag
      default: latest
      description: "the tag of image"
  k:
    - short: d
      long: debug
      default: True
      description: "run in debug mode"
--------------------------settings.yaml----------------------------------
    命令行有两种参数：
    第一种是开关型的，有存在和不存在两种状态，如 docker -i -t -d 等；可以从命令行获得bool值
    第二种是键值型的，存在时则必须赋值，如 docker -n <name> --tag <tag> 等；可以从命令行获得str值
    使用方法：
    具体则为:
        args={'kv': [{'short': 'n', 'long': 'name', 'default': 'get', 'description': 'the name of image'},
                     {'short': 't', 'long': 'tag', 'default': None, 'description': 'the tag of image'}],
               'k': [{'short': 'd', 'long': 'debug', 'default': True, 'description': 'run in debug mode'}]
             }
        args=getArgs(args_name=args)  # 返回的是字典，返回值不分类
        i=args.n 或者 getattr(args, "n")
        ...
    如果只存在一个短名或长名，则另一个用None代替
    如果运行时不存在第二种类型的参数，则返回值为None代替对应的值，如没有设置tag，则返回的tag值为None
    > somescript.py -n "tony"
    args={"kv": [{'short': 'n', 'long': 'name'}]}
    args=getArgs(args_name=args)
    args.get("name") -> "tony"

    :param args_name : 以字典方式传入args
    :param setting_file: 从配置文件中加载args
    """

    def item_in_list(item, args_list):
        for i in args_list:
            if item.get("short") == i.get("short") or item.get("long") == i.get("long"):
                return True
        return False

    def merge_args(list1: list, list2: list):
        """
        合并两个列表中的字典的值，如果同时存在，则dict2会覆盖dict1，传入的是列表，列表项都是对应地址的引用，改列表项就是对
        原列表进行修改，因此无需返回值，类似于字典类型的dict1.update(dict2)
        """
        # 确保两个列表中的描述同一个参数的short-long值没有冲突
        for item1 in list1:
            short1 = item1.get("short")
            long1 = item1.get("long")
            if short1 is not None and long1 is not None:  # short和long任何一个为None，则两个列表项都不会冲突
                for item2 in list2:
                    short2 = item2.get("short")
                    long2 = item2.get("long")
                    if short2 is not None and long2 is not None:
                        # 如果简写相同且全称不同或者简写不同且全称相同，则定义冲突
                        if (short1 == short2 and long1 != long2) or (short1 != short2 and long1 == long2):
                            print("同一个参数在多个地方定义，且定义冲突")
                            item1 = item2

        # 处理list1和list2共有的列表项，用list2覆盖list1
        for arg1 in list1:
            short1, long1 = arg1.get('short'), arg1.get('long')
            assert short1 is not None or long1 is not None, "short name或者long name必须至少有一个不为空"
            if short1 is not None:
                for arg2 in list2:
                    short2 = arg2.get('short')
                    if short1 == short2:
                        arg1 = arg2  # 这个会直接修改到list1中的值，从而返回调用者的list1中去
            elif long1 is not None:
                for arg2 in list2:
                    long2 = arg2.get('long')
                    if long1 == long2:
                        arg1 = arg2

        # 处理list2独有的参数项，将其添加到list1中
        for item in list2:
            if not item_in_list(item, list1):
                list1.append(item)
        return list1

    if setting_file == "default":
        setting_file = "settings.yml" if os.path.exists("settings.yml") else None
        setting_file = setting_file or "settings.yaml"
    args = {}
    if setting_file is not None and args_name is None:  # 当传入配置文件时
        if isinstance(setting_file, str):
            args = read_from_yaml(setting_file)
            args = args.get('args')
        elif isinstance(setting_file, dict):
            args = setting_file
    elif setting_file is None and args_name is not None:  # 当传入argsName字典时
        args = args_name
    elif setting_file is not None and args_name is not None:  # 当同时传入二者时
        # 同时传入配置文件和argsName列表
        if not os.path.exists(os.path.abspath(setting_file)):  # 传入的配置文件不存在
            print("指定的配置文件不存在{}".format(os.path.abspath(setting_file)))
            args = args_name
        else:
            args = read_from_yaml(setting_file).get('args') or {}
            args1 = args_name
            args["k"] = merge_args(args1.get('k'), args.get('k') or {})
            args["kv"] = merge_args(args1.get('kv'), args.get('kv') or {})
    else:
        # 当不传入任何参数时，尝试加载配置文件，如果配置文件不存在，则args={}
        if os.path.exists("settings.yaml"):
            setting_file = os.path.abspath("settings.yaml")
        elif os.path.exists("settings.yml"):  # 不传入任何参数时
            setting_file = os.path.abspath("settings.yml")
        else:
            args = sys.argv[1:]
        args = read_from_yaml(setting_file)
        args = args.get('args') or {}

    parser = argparse.ArgumentParser(args.get('description'))
    type_kv = args.get('kv') or []
    type_k = args.get('k') or []
    for item_dict in type_kv:  # 键值型参数
        item_dict = dict(item_dict)
        short, long, default = item_dict.get('short'), item_dict.get('long'), item_dict.get('default')
        help_ = item_dict.get('help') or ""
        description = item_dict.get('description') or ""
        if short is not None and long is not None:
            parser.add_argument('-{}'.format(short), '--{}'.format(long), default=default,
                                help=help_)  # 如果不提供command参数，默认取值"debug"
        elif short is None:
            parser.add_argument('--{}'.format(long), default=default,
                                help=help_)  # 如果不提供command参数，默认取值"debug"
        elif long is None:
            parser.add_argument('-{}'.format(short), default=default,
                                help=help_)  # 如果不提供command参数，默认取值"debug"
    # parser.add_argument('-s', '--{}'.format(argsName[1]), default='600666', help='操作的股票代码', type=str)
    for item_dict in type_k:  # 开关型参数
        item_dict = dict(item_dict)
        short, long, default = item_dict.get('short'), item_dict.get('long'), item_dict.get('default')
        help_ = item_dict.get('help') or ""
        description = item_dict.get('description') or ""
        # python *.py，则debug=False，而python *.py --debug，则debug=True
        if short is not None and long is not None:
            parser.add_argument('-{}'.format(short), '--{}'.format(long), default=default, action='store_true',
                                help=help_)  # 如果不提供command参数，默认取值"debug"
        elif short is None:
            parser.add_argument('--{}'.format(long), default=default, action='store_true',
                                help=help_)  # 如果不提供command参数，默认取值"debug"
        elif long is None:
            parser.add_argument('-{}'.format(short), default=default, action='store_true',
                                help=help_)  # 如果不提供command参数，默认取值"debug"

    args1 = parser.parse_args()
    # result = [args1.__getattribute__(arg) for arg in argsName]
    return args1  # , result


class YkDict(dict):
    def __init__(self, data_dict):
        super(YkDict, self).__init__(data_dict)

    def get_settings(self, item):
        settings = copy.deepcopy(self)
        if item is not None:
            item_list = item.split('.')
            for i in item_list:
                if isinstance(settings, list):
                    return YkDict({})
                settings = settings.get(i)
                if settings is None:
                    settings = {}
                    break
        if isinstance(settings, dict):
            return YkDict(settings)
        else:
            return settings


def get_settings(item: str = None, setting_file: Optional[str] = "default"):
    """
    从配置文件中加载配置，优先加载"settings.yml"

    :param item: 使用 mysql.port 类型的字符串指定需要查询的配置项，如果不设置，则返回整个yaml文件的字典
    :param setting_file: 默认配置文件为项目根目录下的settings.yml或settings.yaml，目前不支持更改配置文件，强行修改可能会导致某些配置失效
    :return: 配置项的字典，如果具体到项，则返回的是字符串
    """
    if setting_file == "default":
        setting_file = "settings.yml" if os.path.exists("settings.yml") else None
        setting_file = setting_file or "settings.yaml"
        settings = read_from_yaml(setting_file) or {}
    else:
        settings = read_from_yaml(setting_file) or {}

    if item is not None:
        item_list = item.split('.')
        for i in item_list:
            settings = settings.get(i)
            if settings is None:
                settings = {}
                break
    if isinstance(settings, dict):
        return YkDict(settings)
    else:
        return settings


def getAbsPath(folder, file):
    """
    根据目录和文件路径获得绝对路径，folder或file都可能是绝对路径或相对路径
    """
    assert file is not None, "The file path is None"
    if os.path.isabs(file):
        return file
    folder = folder or ""  # 确保folder不为None
    file = os.path.join(folder, file)  # 无论folder是不是绝对路径，都可以直接join
    file = os.path.abspath(file)
    return file


def show_pic(pic, method="cv2"):
    """
    在调试过程中显示图片，yangke库中所有图像的颜色通道顺序默认为RGB

    :param pic:
    :param method: 显示图像的方法
    :return:
    """
    #
    if isinstance(pic, list):
        # 显示多张图片
        for p in pic:
            show_pic(p)
        return
    pic = pic2ndarray(pic)
    if method == "cv2":
        import cv2
        pic1 = pic.copy()  # 将原图复制一份，因为cv2默认以BGR模式显示图像，因此需要将图片的颜色通道顺序转换一下，复制后不影响原图
        cv2.cvtColor(pic, cv2.COLOR_RGB2BGR, pic1)  # 转换图像颜色通道顺序
        cv2.imshow('temp', pic1)
        cv2.waitKey()
    else:
        Image.fromarray(pic).show("temp")


def get_pic_size(pic):
    shape = pic2ndarray(pic).shape
    return shape[1], shape[0]


def pic2base64(pic):
    """
    将转入的图片格式转换为base64字符串

    :param pic: 可以是本地文件名，ndarray, url, base64编码的字符串
    :return: rgb顺序的ndarray
    """
    pic2ndarray(pic, save_file="temp_pic.jpg")  # 将任意来源的图片转换为jpeg格式，并存储成temp_pic.jpg文件
    with open("temp_pic.jpg", 'rb') as f:
        base64_data = base64.b64encode(f.read())
        s = base64_data.decode()
        s = f'data:image/jpeg;base64,{s}'
    return s


def pic2qpixmap(pic):
    import cv2
    from yangke.common.QtImporter import QPixmap, QImage
    if len(pic) == 0:
        print("图片数组为空")
        return None
    s1 = cv2.cvtColor(pic, cv2.COLOR_RGB2BGR)
    image = QImage(s1, s1.shape[1], s1.shape[0], s1.shape[1] * 3, QImage.Format_BGR888)
    pixmap = QPixmap.fromImage(image)
    return pixmap


def pic2qlabel(pic, parent=None):
    from yangke.common.QtImporter import QLabel
    pixmap = pic2qpixmap(pic)

    label = QLabel(parent)
    label.setContentsMargins(0, 0, 0, 0)
    label.setMargin(0)
    label.setScaledContents(True)
    # label.setAutoFillBackground(False)
    if pixmap is None:
        return label
    label.setPixmap(pixmap)
    return label


def pic2ndarray(pic, save_file=None, mode='RGB', alpha=255, need_info: str = None):
    """
    将转入的图片格式转换为ndarray

    :param pic: 可以是本地文件名，ndarray, url, base64编码的字符串
    :param save_file: 如果传入save_file，则会保存pic到指定文件
    :param mode: 以什么模式转换ndarray数组，有些图片有alpha通道，需要注意。可以取值RGB/RGBA
    :param alpha: 当给3通道图像添加alpha通道式，透明通道的值，默认是255
    :param need_info: 是否需要转换的详细信息，用以在转换出错时，获取详细错误类别
    :return: rgb顺序的ndarray
    """
    mode = mode or "RGB"

    def add_alpha(pic_3channel: np.ndarray, alpha1=255):
        """
        给3通道的图像数据添加alpha通道
        :param pic_3channel:
        :param alpha1: 透明通道的值
        :return:
        """
        shape = list(pic_3channel.shape)
        if shape[-1] == 4:
            return pic_3channel
        else:
            shape[-1] = 1  # RGB通道后添加1列，形状不变，因此构件的新数组为(width, height, 1)
            return np.c_[pic_3channel, np.ones(shape).astype(int) * alpha1]

    def load_local_file_as_ndarray(file_path):
        img = Image.open(file_path).convert(mode)
        # noinspection all
        img = np.asarray(img)  # 使用pillow的方法读取文件，支持中文名
        # pic = cv2.cvtColor(pic, cv2.COLOR_BGR2RGB)
        return img

    def base64_to_ndarray(base64data: str):
        # 如果使用PIL解码
        import io
        # noinspection all
        img = np.asarray(Image.open(io.BytesIO(base64data)).convert(mode))
        # 或者也可以使用cv解码
        # img_int_str = np.fromstring(base64data, np.uint8)
        # img_bgr = cv2.imdecode(img_int_str, cv2.IMREAD_COLOR)
        # img = cv2.cvtColor(img_int_str, cv2.COLOR_BGR2RGB)
        return img

    import binascii
    if isinstance(pic, str):
        # 判断传入的pic是不是路径

        if len(pic) < 200 and os.path.exists(pic):  # 如果是本地路径，本地路径不能太长，否则os.path.exist方法会报错
            # pic = cv2.imread(pic)  # cv2.imread()方法不支持中文路径或中文文件名，这里避免使用
            # pic = cv2.cvtColor(pic, cv2.COLOR_BGR2RGB)
            # noinspection all
            pic = np.asarray(Image.open(pic))  # 使用pillow的方法读取文件，支持中文名，Image.open()的结果可以直接转换为ndarray

        elif pic.startswith('http'):  # 如果是url
            from urllib.request import urlretrieve
            try:
                urlretrieve(pic, 'temp_file.png')
            except:
                return None
            pic = load_local_file_as_ndarray('temp_file.png')
            os.remove('temp_file.png')
        elif pic.startswith("data:image/"):  # base64的图片数据会以这些字符串开头
            pic = pic[pic.index(',') + 1:]  # 去除前缀
            try:
                pic = pic.replace(" ", "+")  # 无论如何需要将传入的数据中的空格替换为加号
                img_b64decode = base64.b64decode(pic)
            except binascii.Error:
                return None, "base64编码有误" if need_info else None
            pic = base64_to_ndarray(img_b64decode)
        else:  # 还可能是不以data:image/开头的base64数据，或不以http开头的url，这里不考虑不以http开头的url
            try:
                pic = pic.replace(" ", "+")
                img_b64decode = base64.b64decode(pic)
            except binascii.Error:
                return None, "base64编码有误" if need_info else None
            # 如果base64解码没出错，则处理
            pic = base64_to_ndarray(img_b64decode)

    elif isinstance(pic, np.ndarray):
        pass
    else:
        info = "不支持传入的图片数据类型：{}".format(type(pic))
        return None, info if need_info else None

    if len(pic) == 0:  # pic == []
        return
    if mode == "RGB" and len(pic[0][0]) == 4:
        pic = pic[:, :, :3]
    elif mode == "RGBA" and len(pic[0][0]) == 3:
        pic = add_alpha(pic, alpha1=alpha)
    if save_file is not None:
        im = Image.fromarray(pic)
        im.save(save_file)
    return pic


def get_draw_element_on_pic_handle(pic, handle_type="pillow"):
    """
    获取在图片上画点、线等图元的操作对象。获得后可以使用对应的方法，绘制完成后可以使用img = np.asarray(img)将图片转换为数组

    示例：
    handle = get_draw_element_on_pic_handle(pic)
    handle.text(xy=(0,20), text="测试文字", fill="red", align="left")
    """
    if handle_type is None or handle_type == "cv2":
        from functools import partial
        return
    else:  # pillow
        pic = pic2ndarray(pic)  # 确保图片为ndarray格式
        img = Image.fromarray(pic)  # 将ndarray转为PIL的Image格式
        draw = ImageDraw.Draw(img)  # 创建绘图对象
        return draw, img


def draw_element_on_pic(pic, need_show=False, **kwargs):
    """
    在图片上画点、线、
    kwargs传入需要绘制的图像元素，与ImageDraw.Draw().draw().

    使用示例：
    draw_element_on_pic(self.before_action, False, circle={"center": (0, 0), "radius": 20, "fill": "red", "outline": "yellow"})

    :param need_show:
    :param pic: ndarray格式或图片文件名，ndarray接受的颜色顺序为RGB
    :return:
    """
    pic = pic2ndarray(pic)  # 确保图片为ndarray格式
    point = kwargs.get('points')
    line = kwargs.get('lines')
    rect = kwargs.get('rectangles')
    arc = kwargs.get('arcs')
    circle = kwargs.get('circle')
    text = kwargs.get("text")

    img = Image.fromarray(pic)  # 将ndarray转为PIL的Image格式
    draw = ImageDraw.Draw(img)  # 创建绘图对象
    if point is not None:
        draw.point(point.get('xy'), point.get('fill'))
    if line is not None:
        draw.line(line.get('xy'), fill=line.get('fill'), width=line.get('width'))
    if rect is not None:
        draw.arc(arc.get('xy'), start=arc.get('start'), end=arc.get('end'), fill=arc.get('fill'),
                 width=arc.get('width'))
    if arc is not None:
        draw.rectangle(rect.get('xy'), fill=rect.get('fill'), outline=rect.get('outline'), width=rect.get('width'))
    if circle is not None:
        center_x, center_y, radius = circle.get('center')[0], circle.get('center')[1], circle.get('radius')
        xy = (center_x - radius, center_y - radius, center_x + radius, center_y + radius)
        draw.ellipse(xy, fill=circle.get('fill'), outline=circle.get('outline'))
    if text is not None:
        draw.text()

    if need_show:
        img.show()
    # noinspection all
    img = np.asarray(img)
    return img


def get_encoding_of_file(file, extras=False):
    """
    判断文件的编码
    :param file:
    :param extras: 是否返回探测的额外信息，默认不返回，也就是只返回encoding
    :return:
    """
    # with open(file, "rb") as f:  # 该方法判断不准确，不适用于中文
    #     msg = f.read()
    #     result = chardet.detect(msg)
    # if extras:
    #     return result
    # else:
    #     return result["encoding"]
    encoding_csv = "utf-8"
    sep = ","
    try:
        # data = pd.read_csv(file, sep=sep, error_bad_lines=False, encoding=encoding_csv)
        data = pd.read_csv(file, sep=sep, on_bad_lines='skip', encoding=encoding_csv)
        return encoding_csv
    except UnicodeDecodeError:
        encoding_csv = "gb18030"
        try:
            # data = pd.read_csv(file, sep=sep, error_bad_lines=False, encoding=encoding_csv)
            data = pd.read_csv(file, sep=sep, on_bad_lines='skip', encoding=encoding_csv)
            return encoding_csv
        except UnicodeDecodeError:
            encoding_csv = "utf-16"
            # data = pd.read_csv(file, sep=sep, error_bad_lines=False, encoding=encoding_csv)
            data = pd.read_csv(file, sep=sep, on_bad_lines='skip', encoding=encoding_csv)
            return encoding_csv
    except pd.errors.ParserError:
        # 说明pandas发现列数不一致，导致报错
        to_file = os.path.join(os.path.dirname(file), f"{os.path.basename(file).split('.')[0]}_add_sep.csv")
        add_sep_to_csv(file, sep, to_file=to_file)
        os.remove(to_file)
        return get_encoding_of_file(to_file, extras)


def is_base64_code(s):
    '''Check s is Base64.b64encode'''
    if not isinstance(s, str) or not s:
        return "params s not string or None"

    _base64_code = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I',
                    'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R',
                    'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'a',
                    'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
                    'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's',
                    't', 'u', 'v', 'w', 'x', 'y', 'z', '0', '1',
                    '2', '3', '4', '5', '6', '7', '8', '9', '+',
                    '/', '=']
    _base64_code_set = set(_base64_code)  # 转为set增加in判断时候的效率
    # Check base64 OR codeCheck % 4
    code_fail = [i for i in s if i not in _base64_code_set]
    if code_fail or len(s) % 4 != 0:
        return False
    return True


# ... existing code ...
def save_as_xlsx(file, engine="WPS", ext="xlsx", visible=False):
    """
    将.xls文件另存为.xlsx文件，以便pandas等类库处理

    :param file:  需要另存为的xls文件的绝对路径
    :param engine: 默认使用的软件引擎，默认使用WPS进行另存为，也可赋值为"Office"，WPS对中文的兼容性更好，当某个引擎出错时会自动尝试其他引擎
    :param ext: 另存为文件的后缀名，支持"xlsx"/"csv"
    :param visible: 另存为过程是否可见，默认为False
    :return:  返回的文件路径
    """
    import win32com.client

    excel_app = None
    if engine.lower() == "office":
        dispatch = ["Excel.Application", "et.Application", "ket.Application"]
    else:
        dispatch = ["et.Application", "ket.Application", "Excel.Application"]

    import pythoncom
    # noinspection all
    pythoncom.CoInitialize()  # 有些时候必须初始化
    for dis in dispatch:
        from win32com.universal import com_error
        try:
            excel_app = win32com.client.Dispatch(dis)  #
            break
        except com_error:
            continue
    if excel_app is None:
        print("另存为.xls文件为.xlsx文件时，未找到系统中安装的Office或WPS软件")
        sys.exit(0)

    excel_app.Visible = 1 if visible else 0  # 显示Excel界面

    # 处理受保护视图窗口的情况
    workbook = None
    try:
        # 尝试直接打开文件
        workbook = excel_app.Workbooks.Open(file, ReadOnly=False)
    except com_error as e:
        # 如果因为受保护视图导致无法打开，则尝试从受保护视图窗口中获取
        try:
            if excel_app.ProtectedViewWindows.Count > 0:
                # 如果存在受保护的视图窗口，从第一个窗口中编辑副本
                protected_view = excel_app.ProtectedViewWindows(1)
                workbook = protected_view.Edit()
        except com_error:
            pass

    # 如果仍然无法打开工作簿，则抛出异常
    if workbook is None:
        raise Exception(f"无法打开Excel文件: {file}")

    out_file = os.path.join(os.path.dirname(file), os.path.basename(file)[:-4] + "ignore." + ext)
    if os.path.exists(out_file):
        os.remove(out_file)
    if ext == "csv":  # 无法保存为csv格式，还需进一步寻找方法
        # "xlCSV"表示csv格式
        # 1表示不更改文件的访问模式，也可取值2，表示共享列表，或3，表示独占模式
        workbook.SaveAs(out_file, "xlCSV")
    elif ext == "xlsx":
        try:
            workbook.SaveAs(out_file)
        except pywintypes.com_error as e:
            workbook.SaveAs(
                Filename=out_file,
                FileFormat=51,  # 51 表示 xlsx 格式
                AccessMode=1,  # 1 表示 xlNoChange 不更改文件访问模式
                ConflictResolution=2  # 2 表示 xlLocalSessionChanges 本地会话更改
            )
    excel_app.Quit()
    if ext == "csv" and engine.lower() == "wps":
        encoding = get_encoding_of_file(out_file)
        data = pd.read_csv(out_file, sep="\t", encoding=encoding)
        os.remove(out_file)
        data.to_csv(out_file, index=None)
    return out_file


# ... existing code ...


def is_datetime(string: str):
    """
    判断一个字符串是否是日期或时间类型

    :param string:
    :return:
    """
    try:
        # noinspection all
        _ = pd.Timestamp(string)
        return True
    except ValueError:
        return False


def is_number(string: str):
    """
    判断一个字符串是否为数字

    :param string:
    :return:
    """
    try:
        _ = float(string)
        return True
    except (ValueError, TypeError):
        return False


def extend_list_by_alternative_symbols(origin_list, alternative_symbol: dict):
    """
    将列表中的可替换字符串更换形式，从而形成更全面的字符串

    例如：
    origin=["1号高加进汽压力"]
    origin=extend_list_by_alternative_symbols(origin, {"1": "一", "汽": "气"})
    则结果为：
    origin=['1号高加进汽压力', '一号高加进汽压力', '1号高加进气压力', '一号高加进气压力']

    :param origin_list:
    :param alternative_symbol:
    :return:
    """
    for item in origin_list:
        for k, v in alternative_symbol.items():
            new_item = item.replace(k, v)
            if new_item not in origin_list:
                origin_list.append(new_item)
            new_item = item.replace(v, k)
            if new_item not in origin_list:
                origin_list.append(new_item)
    return origin_list


def crop_pic(pic, left, top, right, bottom, save_to: str = None):
    """
    裁剪图片，返回图片的ndarray列表

    :param save_to: 如果传入了保存路径，则会保存
    :param pic: 本地图片路径或ndarray格式图片，cv2.imread()
    :param left:
    :param top:
    :param bottom:
    :param right:
    :return: ndarray格式的图片数据
    """
    pic = pic2ndarray(pic)  # 确保图片为ndarray格式
    if pic is None:
        return pic
    top, bottom = int(top), int(bottom)
    left, right = int(left), int(right)
    pic = pic[top:bottom, left:right]
    if save_to is not None and save_to != "memory":  # 如果传入了保存路径，就保存图片到本地
        import cv2
        pic1 = pic.copy()
        cv2.cvtColor(pic1, cv2.COLOR_RGB2BGR, pic1)
        # noinspection all
        cv2.imwrite(save_to, pic1)
    return pic, '裁剪成功'


def get_camel_case_type(name: str):
    """
    判断变量名的命名方式

    :param name:
    :return: 'CamelCase'、'camelCase'、'camelcase'、'camel_case'、'Camel_Case'、'camel_Case'
    """
    if isinstance(name, int):
        return 'PureDigit'
    upper_char = [char for char in name if char.isupper()]
    underscores = [char for char in name if char == "_"]
    if len(upper_char) > 0 and len(underscores) == 0 and name[0].isupper():  # 没有下划线且有超过1个大写字母且首字母大写
        return 'CamelCase'
    elif len(upper_char) > 0 and len(underscores) == 0 and name[0].islower():  # 存在大写，不存在下划线，第一个字母小写
        return 'camelCase'
    elif len(upper_char) == 0 and len(underscores) == 0:  # 不存在大写，不存在下划线
        return 'camelcase'
    elif len(upper_char) == 0 and len(underscores) > 0:
        return 'camel_case'
    elif len(upper_char) > 0 and len(underscores) > 0 and name[0].isupper():
        return 'Camel_Case'
    elif len(upper_char) > 0 and len(underscores) > 0 and name[0].islower():
        return 'camel_Case'


def name_transfer(name, transfer_type='CamelCase'):
    """
    转换变量名的命名规则为 'CamelCase'

    :param name: 可以为str, list, dict，如果是列表或字典，则递归转换列表或字典中的变量名
    :param transfer_type: 命名规则有CamelCase、camelCase、Camel-Case、camel_case等，任意转换
    :return:
    """
    if isinstance(name, str):
        name_type = get_camel_case_type(name)
        if name_type == transfer_type:
            return name
        if name_type == 'Camel_Case' or name_type == "camel_case" or name_type == "camel_Case":  # 将下划线命名改为驼峰命名
            name_field = name.split("_")
            name_field = [field.lower() for field in name_field]
        elif name_type == "camelCase" or name_type == "CamelCase":
            name_field = []
            field = ""
            for char in name:
                if char.islower():
                    field = field + char
                else:
                    if field != "":
                        name_field.append(field.lower())
                    field = char
            name_field.append(field.lower())
        else:
            name_field = [name]

        if transfer_type == "CamelCase":
            return "".join([field.capitalize() for field in name_field])
        elif transfer_type == "camel_case":
            return "_".join(name_field)
        elif transfer_type == "Camel_Case":
            return "_".join([field.capitalize() for field in name_field])
        elif transfer_type == "camelcase":
            return "".join(name_field)
        elif transfer_type == "camel_Case":
            name_field = [field.capitalize() if idx != 0 else field for idx, field in enumerate(name_field)]
            return "_".join(name_field)
        elif transfer_type == "camelCase":
            name_field = [field.capitalize() if idx != 0 else field for idx, field in enumerate(name_field)]
            return "".join(name_field)
        else:
            return name
    elif isinstance(name, dict):
        new_dict = {}
        dictionary = name
        for k, v in dictionary.items():
            if isinstance(v, dict):  # 如果value仍是一个字典，则递归修改命名规则
                v = name_transfer(v, transfer_type)
            elif isinstance(v, list):  # 如果value是一个列表，判断该列表的子元素是否有字典
                v = name_transfer(v, transfer_type)
            if isinstance(k, int):  # 字典键的类型为整数时，不转换
                new_dict[k] = v
            else:
                new_dict[name_transfer(k, transfer_type)] = v
        return new_dict
    elif isinstance(name, float) or isinstance(name, int):
        return name
    else:
        new_list = []
        for item in name:
            item = name_transfer(item, transfer_type=transfer_type)
            new_list.append(item)
        return new_list


def start_threads(targets, args_list=(), timeout=10, engine="_thread"):
    """
    开启新进程运行target方法，并等待超时timeout s

    已知问题：
    1. 发现当pyqt5使用engine="threading"模式启动多线程是会报错Process finished with exit code -1073741819 (0xC0000005)或
    Process finished with exit code -1073740940 (0xC0000374)，参考网上的解决方法没有解决。因此增加engine="_thread"模式。
    但当前engine="_thread"只支持额外启动一个线程，启动多个线程会自动切换到threading库。
       解决方法：pyqt5在后台进程中更新前台UI界面是可能会出现上述问题，参考 https://github.com/zhang-ray/easy-voice-call/issues/10，
       其提供的解决方法是使用QEvent来从后台向前台传递事件，实现方法参考
       https://www.pythonheidong.com/blog/article/359642/1d97a1f6029b69bbbce5，即必须定义一个信号类，使用该信号作为子线程触发
       父线程UI变化的触发器。而在父线程中实现UI变化的具体方法。


    :param args_list:
    :param targets: 需要运行的函数或函数列表
    :param timeout: 单位秒
    :param engine: 使用哪种多线程库进行开启新线程，支持"_thread"/"threading"
    :return:
    """

    if engine == "_thread" and not isinstance(targets, list):
        import _thread

        try:
            args_list = tuple(args_list)
            exit_code = _thread.start_new_thread(targets, args_list)
            return exit_code
        # noinspection all
        except:
            print("Error: 无法启动线程")
            traceback.print_exc()
    else:
        from threading import Thread

        if isinstance(targets, list):
            threads = []
            for target, args in zip(targets, args_list):
                threads.append(Thread(target=target, args=args))
            for t in threads:
                t.setDaemon(True)
                t.start()
            for t in threads:
                t.join(timeout)
            return threads
        else:
            thread = Thread(target=targets, args=args_list)
            thread.daemon = True  # 不添加改属性，主进程结束，但子线程不会结束，添加后确保子线程可以随主进程结束而结束
            exit_code = thread.start()
            # thread_id = thread.ident
            return thread, exit_code


def stop_threads(thread):
    """
    强行结束线程，或线程列表，示例如下：
    threads = start_threads(func, args_list=(), timeout=10, engine="thread"):
    stop_thread(threads)

    :param thread:
    :return:
    """
    from threading import Thread

    def _async_raise(tid, exctype):
        """raises the exception, performs cleanup if needed"""
        tid = ctypes.c_long(tid)
        if not inspect.isclass(exctype):
            exctype = type(exctype)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
        if res == 0:
            raise ValueError("invalid thread id")
        elif res != 1:
            # """if it returns a number greater than one, you're in trouble,
            # and you should call it again with exc=NULL to revert the effect"""
            ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
            raise SystemError("PyThreadState_SetAsyncExc failed")

    if isinstance(thread, Thread):
        tid = thread.ident
        _async_raise(tid, SystemExit)
        return 0
    elif isinstance(thread, int):
        # 已经推出了

        # _async_raise(thread, SystemExit)
        pass
    elif isinstance(thread, list):
        for t in thread:
            stop_threads(t)
        return 0


def get_localhost_ip():
    """
    获取当前运行环境的ip地址
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


def get_available_port():
    """
    获取一个本机可用的端口

    :return:
    """
    for port in range(10000, 30000):
        if not net_is_used(port):
            return port


def net_is_used(port, ip='127.0.0.1'):
    """
    判断指定ip的端口是否占用，默认检测本机端口

    :param port:
    :param ip:
    :return:
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ip, port))
        s.shutdown(2)
        print('%s:%d is used' % (ip, port))
        return True
    except:
        print('%s:%d is unused' % (ip, port))
        return False


def is_ip_address(ip_str) -> bool:
    """
    判断传入的字符串是否为ip地址
    """
    import re
    m = re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip_str)
    if m:
        return True
    else:
        return False


def tcp_client(host_ip, port):
    # AF_INET：基于网络的套接字，AF_UNIX：基于文件的套接字
    # SOCK_STREAM：TCP套接字，SOCK_DGRAM：UDP套接字
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host_ip, port))
    s.send(b'GET / HTTP/1.1\r\nHost: www.sina.com.cn\r\nConnection:close\r\n\r\n')

    buffer = []
    while True:
        d = s.recv(1024)
        if d:
            buffer.append(d)
        else:
            break
    data = b''.join(buffer)
    s.close()
    header, html = data.split(b'\r\n\r\n', 1)
    print(header.decode('utf-8'))


def tcp_server(address=('0.0.0.0', 9999), timeout=10):
    """
    linux系统下使用epoll模式，windows系统下只能使用select模式
    :return:
    """
    import threading
    # 创建socket对象
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 允许地址服用，这样即使在这个端口被其他程序监听，也可以使用bind来绑定端口，没有该设置，epoll会报错
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # 绑定地址和端口
    s.bind(address)
    # 监听，并设置最大连接数
    # noinspection all
    s.listen(backlog=10)
    print("服务器启动成功，监听IP：{}".format(address))
    # 服务端设置非阻塞
    s.setblocking(False)
    # 创建epoll事件对象，后续要监控的时间添加到其中
    _ = select.epoll()
    import sys

    def tcp_link(sock1, address1):
        print('Accept new connection from %s:%s...' % address1)
        sock1.send(b'Welcome!')
        while True:
            data = sock1.recv(1024)
            if not data or data.decode('utf-8') == 'exit':
                break
            sock1.send(('Hello, %s' % data.decode('utf-8')).encode('utf-8'))
        sock1.close()
        print('Connection from %s:%s closed.' % address1)

    while True:
        sock, address = s.accept()
        t = threading.Thread(target=tcp_link, args=(sock, address))
        t.start()


def udp_client():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('127.0.0.1', 9999))

    print('Bind UDP on 9999....')
    while True:
        data, address = s.recvfrom(1024)
        print(f'Received from {address}.')
        s.sendto(b'Hello, %s!' % data, address)


def udp_server():
    """
    udp广播，向指定ip发送信息
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    for data in [b'Michael', b'Tracy', b'Sarah']:
        s.sendto(data, ('127.0.0.1', 9999))
        print(s.recv(1024).decode('utf-8'))
    s.close()


def web_available():
    """
    判断网络是否连通
    """
    ret = os.system("ping baidu.com -n 1 > NUL")
    return True if ret == 0 else False


def get_init_func_from_code(code: str) -> str:
    """
    从类代码字符串中获取类的初始化函数__init__() ...的代码。类代码一般来自inspect.getsource(cls)
    :return:
    """
    import re
    # 如果findall的pattern用.*(def\s+__init__).*之类的全匹配对字符串code进行匹配，则只返回括号内的内容为匹配结果
    # 如果findall的pattern="def\s+__init__"进行部分匹配，则返回所有可以和pattern匹配的子字符串，
    # 如get_member_of_class_by_code(code: str)中的用法
    init_ = re.findall(".*(def\\s+__init__\\(.*)", code, re.DOTALL)[0]  # 匹配def __init__直到code末尾
    # (def\s+__init__.*)def\s.*因为正则默认会尽量匹配更多的字符，因此，该正则会匹配到类定义中最后一个def之前。而在.*后加?会让其尽量匹配最少
    # 的字符，因此会匹配到第二个def.*之前就截止
    init = re.findall("(def\\s+__init__.*?)def\\s.*", init_, re.DOTALL)  # 匹配第二个 def 之前的所有代码，即去掉
    if len(init) == 0:
        return init_
    else:
        return init[0]


def get_member_of_class_by_code(code: str, initialized=False) -> list:
    """
    从类代码字符串中解析类的成员变量，只解析__init__方法中定义的成员变量。
    类代码一般来自inspect.getsource(cls)。

    :param initialized: 过滤初始化过的成员变量，默认不过滤，如果为True，则只返回经过self.var=None初始化的成员变量
    :param code: 类代码或__init__函数的代码字符串
    :return:
    """
    import re
    if len(re.findall("\\sclass\\s.*", code, re.DOTALL)) > 0:  # 说明是class，否则就认为是__init__方法
        code = get_init_func_from_code(code)

    if initialized:
        temp1 = re.findall("self\\.[a-zA-Z0-9_]+\\s*=\\s*None\\s", code, re.DOTALL)
        res = [m.replace("=", "") for m in temp1]
        res = [m.replace("None", "").strip() for m in res]
    else:
        temp1 = re.findall("self\\.[a-zA-Z0-9_]+\\s*=", code, re.DOTALL)
        res = [m.replace("=", "").strip() for m in temp1]
    return res


class AutoSavePara:
    """
    该类被auto_save_para(cls)方法引用
    """

    def update_auto_save_para(self, key, value):
        """
        用于添加到类的成员方法，用来处理硬盘变量的读取与存储

        :param self: 因为这是要注册的成员变量，所以第一个参数是类自己的引用self
        :param key: 成员变量名
        :param value: 使用时赋给硬盘变量的变量值
        :return:
        """

        import yangke.common.fileOperate as fo  # 不能删除，因为这是要被写入新文件中的代码
        import os
        temp_file = os.path.join(os.path.abspath(os.getcwd()), "temp_auto_save_para")
        temp_dict: dict = fo.read_from_pickle(temp_file)

        if value is None:
            if temp_dict is None:
                temp_dict = {key: None}
                fo.write_as_pickle(temp_file, temp_dict)
                return None
            if key in temp_dict:
                ...
            else:
                temp_dict.update({key: None})
                fo.write_as_pickle(temp_file, temp_dict)
        else:
            temp_dict.update({key: value})
            fo.write_as_pickle(temp_file, temp_dict)
        return temp_dict[key]


def auto_save_para(cls):
    """
    装饰器，本装饰器只能用于装饰类对象。用于将类中初始化为None的成员变量动态保存到硬盘。即如果需要保存，则必须以
    self.var = None # 这种方式定义，必须初始化为None，则程序下一次运行时，会在初始化语句这儿从硬盘加载变量值

    被装饰的类中的成员变量会成为硬盘变量，每一次变量的修改都会直接写入硬盘，下一次重新运行该程序时会从硬盘载入对应的变量值（如果硬盘
    变量存储文件没有被删除的话，该文件一般位于工作目录下）。程序员无需关心硬盘变量的存储路径，装饰器会在特定硬盘位置创建文件保存硬盘变量。

    硬盘变量必须要初始化为None，否则程序不知道运行到哪里时该从硬盘加载变量值
    程序发现硬盘变量赋值为None时，会在硬盘上查找该变量的保存记录，找到就加载硬盘中的变量值
    程序发现硬盘变量赋值为非None时，会修改变量值，并将新值立即更新到硬盘
    硬盘变量的赋值必须在类中，不能在类外直接赋值
    如果需要在类外修改硬盘变量值，可以定义成员方法self.setter()方法进行赋值
    装饰的类中代码无法正常调试，但是同模块中类外的代码可以正常调试
    装饰的类代码调试，可以首先运行程序后，找到生成的temp_auto_save_para.py打断点调试

    目前没有考虑模块中存在多个@auto_save_para的情况，可能会出错，因此模块中的硬盘变量应放在同一个类中存储

    :param cls: 被装饰的类
    :return:
    """
    import inspect
    import re
    from yangke.common.config import logger
    import yangke.common.fileOperate as fileOperate

    lines_module = inspect.getsource(inspect.getmodule(cls))  # 类所在module的源代码
    lines_cls = inspect.getsource(cls)  # 类的源代码
    init = get_init_func_from_code(lines_cls)  # 取到类的构造函数
    members = get_member_of_class_by_code(init, True)  # 获取类构造函数中定义的成员变量
    lines_cls_new = lines_cls

    def equal_update(matched):
        print(matched)
        line = matched.string[matched.regs[0][0]:matched.regs[0][1]]
        line = line.split("#")
        kv = line[0] if len(line) <= 2 else logger.error("成员变量定义行发现多个注释符'#'，解析失败")
        key, value = kv.split("=")
        res = f"{key.strip()} = self.update_auto_save_para('{key.strip()}', {value.strip()})"
        return res

    # 修改修饰类中硬盘变量的赋值语句
    for m in members:
        # ls = re.findall(f"{m}\s*=.*", lines_cls)
        lines_cls_new = re.sub(f"{m}\\s*=.*", equal_update, lines_cls_new)
    # 给被修饰的类加父类，使其具有update_auto_save_para()成员方法
    class_def: str = re.findall(".*(class.*?):", lines_cls_new, re.DOTALL)[0]
    if ")" in class_def:
        class_def = class_def.rstrip(")")
        lines_cls_new = lines_cls_new.replace(class_def, class_def + ", AutoSavePara")
    else:
        lines_cls_new = lines_cls_new.replace(class_def, class_def + "(AutoSavePara)")
    if "AutoSavePara" not in lines_module:
        lines_module = "from yangke.base import AutoSavePara\n" + lines_module

    lines_module_new = lines_module.replace(lines_cls, lines_cls_new)

    # --------------------- 删除cls之后的所有代码，防止后面存在模块级的代码直接运行在下面第7行时直接运行 --------------
    _idx = lines_module_new.find(lines_cls_new)  # 删除注释的模块之后的所有代码，防止后面存在模块级的代码直接运行
    lines_module_new = lines_module_new.replace(lines_module_new[_idx:], lines_cls_new)
    # --------------------- 删除cls之后的所有代码，防止后面存在模块级的代码直接运行在下面第7行时直接运行 --------------

    lines_module_new = re.sub("@auto_save_para.*", "", lines_module_new, re.X)  # .默认不匹配换行符，删除@auto_save_para行
    class_name = cls.__name__
    temp_module_file = os.path.join(os.path.abspath(os.getcwd()), f"{class_name}_temp.py")
    fileOperate.write_line(temp_module_file, lines_module_new)
    del cls
    exec(f"from {class_name}_temp import {class_name}")
    logger.debug(f"调试{class_name}类中方法，请在{class_name}_temp.py中相应位置打断点")
    # os.remove(temp_module_file)  # 类加载之后删除临时文件可能导致错误，最好不要删除
    return eval(f"{class_name}")


def is_js_str(code: str):
    """
    判断字符串是否是js代码片段
    :param code:
    :return:
    """
    tag_list = ["html", "div", "button", "label", "address", "body",
                "figure", "font", "frame", "img", "input", "legend",
                "script", "table", "template", "textarea", ]
    code = code.lower().strip()
    if code.endswith(">"):
        for tag in tag_list:
            if code.startswith(f"<{tag}"):
                return True
    return False


def timeout(seconds=5, callback=None):
    """
    超时函数，作为装饰器修饰函数，如果超过指定时间，则强行终止函数执行，否则返回函数执行结果
    示例：
    @timeout(seconds=5, callback=None)
    def long_running_function():
        time.sleep(3)
        return "Function completed"
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 定义一个线程局部变量来存储函数结果
            result = None
            exception = None

            def target():
                nonlocal result, exception
                try:
                    result = func(*args, **kwargs)
                except Exception as e:
                    exception = e

            # 创建并启动线程
            thread = threading.Thread(target=target)
            thread.start()

            # 等待线程完成，最多等待 seconds 秒
            thread.join(seconds)

            # 如果线程仍然存活，说明函数执行超时
            if thread.is_alive():
                if callback is not None:
                    callback()  # 调用回调函数
                raise TimeoutError(f"Function {func.__name__} timed out after {seconds} seconds")

            # 如果函数抛出了异常，重新抛出
            if exception is not None:
                raise exception

            return result

        return wrapper

    return decorator


def timeit(func):
    """
    装饰器函数
    对方法的时间执行耗时进行统计
    @timeit
    def test():
        for i in range(10000):
            time.sleep(1)

    则调用test()方法时会自动统计方法的执行时间

    :param func:
    :return:
    """

    def wrapped(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        logger.debug("Function '{}' executed in {:f} s", func.__name__, end - start)
        return result

    return wrapped


def run_once(f):
    """
    装饰器函数，使函数只会运行一次，后续的调用会被忽略，如果函数有返回值，则永远返回第一次运行的结果
    :return:
    """
    run_time = [0]  # 不可变对象无法在内层函数引用
    result = [object]  # 保存第一次的运行结果，后续运行直接返回

    # has_run = False

    def wrapper(*args, **kwargs):
        if run_time[0] == 0:
            run_time[0] = run_time[0] + 1
            result[0] = f(*args, **kwargs)
            return result[0]
        else:
            return result[0]

    return wrapper


class TempPara(object):
    """
    在项目运行时，有时会需要存储一些临时变量，该方法提供该功能。
    用于项目运行过程中存储临时变量。一般用于：1.网络请求过程中保存具有一定有效期的session信息、token信息等
    存储时使用TempPara().save

    示例：
    声明临时变量：
    stock_price = 27.22
    a = TempPara("stock_price", 3600*24)
    临时变量赋值时：
    a.save(stock_price)
    使用时：
    stock_price = a.get()

    注：该类一般不显示调用，实现相应功能可以使用get_temp_para()和save_temp_para()方法，他们是对该类的进一步封装

    和auto_save_para(cls)功能有些类似，将来可能合并
    """

    def __init__(self, para_name, expires_in=0, folder='temp'):
        """
        创建临时变量对象

        :param para_name: 需要保存的临时变量的名称，注意不是变量的值，变量的值通过该类的save方法传入
        :param expires_in: 临时变量的有效时长，单位为秒，当为0时表示永不失效
        :param folder: 临时变量存储的文件夹，一般无需设置
        """
        if folder is None:
            folder = 'temp'
        self.folder = self.get_temp_folder(folder)
        self.temp_file = os.path.join(self.folder, 'temp_settings')
        self.para_name = para_name  # 需要保存的参数名
        self.expire = expires_in
        self.para_value = None
        self.time = None  # 临时变量创建的时间，考虑到有些临时变量有失效时间，需要记录创建时间

    def save(self, para_value, time=datetime.datetime.now(), expires_in=None):
        self.para_value = para_value  # 需要保存的参数
        self.time = time  # 参数保存的时间
        self.expire = expires_in if expires_in is not None else self.expire
        # self.folder必然是存在的
        # 构建要保存的字典对象
        settings_item = {
            self.para_name: {
                "value": self.para_value,
                "expire": self.expire,
                "time": self.time,
            }
        }
        if os.path.exists(self.temp_file):
            with open(self.temp_file, 'rb') as f:
                settings = pickle.load(f)
                settings.update(settings_item)
        else:
            settings = settings_item
        with open(self.temp_file, 'wb') as f:
            pickle.dump(settings, f)

    def get(self):
        if not os.path.exists(self.temp_file):
            return None
        with open(self.temp_file, 'rb') as f:
            settings = pickle.load(f)
        para = settings.get(self.para_name)
        if para is None:
            return None
        self.para_value = para.get('value')
        self.time = para.get('time')
        self.expire = para.get('expire')
        if self.expire <= 0:  # 如果没有失效时间
            return self.para_value
        else:
            delta_time: datetime.timedelta = datetime.datetime.now() - self.time
            if delta_time.seconds > self.expire:  # 如果时间差已经超过了失效时间，则当前值失效，返回空
                return None
            else:
                return self.para_value

    @staticmethod
    def get_temp_folder(folder):
        """
        创建临时变量存储的文件夹

        :return: 临时文件夹的绝对路径
        """
        # cwd_folder = os.getcwd()
        folder = os.path.abspath(folder)
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f'temp folder created: {folder}')
        return folder


def get_temp_para(para_name, get_func_or_default_value, folder=None, expires_in=0, **kwargs):
    """
    获取临时变量的值，该方法是对TempPara的进一步包装，当项目运行时，有些时候需要多次向网络请求某个参数，为了减少请求次数，可以
    使用该方法，在请求参数的有效时间内，该方法会直接使用之前请求得到的值，从而减少请求次数，一方面减少延迟，同时防止请求次数
    过多被服务器封禁。

    该方法相当于将临时参数的管理交给了第三方，当请求一次后，第三方会维护临时变量列表，当再次请求同样的参数时，第三方会查询当前
    维护的临时变量列表，如果找到对应的临时变量（且未失效），则直接返回对应的参数值。

    如果值是自己的程序改变的，需要使用save_temp_para更新硬盘上的临时变量值

    使用示例：
    access_token = get_temp_para('access_token', expires_in=2500000, get_func=_get_token)

    :param folder:
    :param para_name: 请求的参数名称
    :param get_func_or_default_value: 参数失效或不存在时具体的请求方法，get_func()返回请求的数据，可以是任何类型
    :param expires_in: 请求参数的有效时长，单位为秒
    :param kwargs: get_func的参数可以通过kwargs传入
    :return: 请求得到的参数值
    """
    temp_para = TempPara(para_name, expires_in=expires_in, folder=folder)
    para_value = temp_para.get()
    if para_value is None:
        if type(get_func_or_default_value).__name__ == "function":
            para_value = get_func_or_default_value(**kwargs)
        else:
            para_value = get_func_or_default_value
        temp_para.save(para_value)
    return para_value


def save_temp_para(para_name, value, folder=None):
    """

    :param para_name:
    :param value:
    :param folder: 临时参数的储存位置，默认是在主程序所在目录中，可以根据需要修改到其他目录
    :return:
    """
    temp_para = TempPara(para_name, folder=folder)  # 这里构建的temp_para没有失效时间
    temp_para.save(value)  # 这里保存时，如果本地硬盘存储的对象已经存在失效时间，则会自动应用本地硬盘存储的失效时间


def interpolate_value_simple(x, x1, y1, x2, y2):
    """
    获取插值的数值

    根据点(x1, y1)、(x2, y2)插值，并求x处的y值，y1，y2可以是列表，例如：
    res = interpolate_value_simple(2, x1=1, y1=[3,3], x2=3, y2=[4,6])
    则res = [3.5, 4.5]

    :param x:
    :param x1:
    :param y1:
    :param x2:
    :param y2:
    :return:
    """
    if x1 == x2:
        logger.error(f"给定的两个参考点x值相等，无法插值:({x1}, {y1})和({x2}, {y2})")
        return None
    if x == x2:
        return y2
    else:
        if isinstance(y1, list) and isinstance(y2, list):
            y1 = np.array(y1)
            y2 = np.array(y2)
        if isinstance(y1, np.ndarray) and isinstance(y2, np.ndarray):
            try:
                res = y1 + (y1 - y2) * (x - x1) / (x1 - x2)
            except:
                if y1.dtype.type.__name__ not in ['float64', 'int32']:  # DCS中导出的数据中有些带有质量标记，如'-4.503 B'
                    y1 = np.array([float(i) if is_number(i) else np.nan for i in y1])
                if y2.dtype.type.__name__ not in ['float64', 'int32']:
                    y2 = np.array([float(i) if is_number(i) else np.nan for i in y2])
                res = y1 + (y1 - y2) * (x - x1) / (x1 - x2)
        else:
            res = float(y1 + (y1 - y2) * (x - x1) / (x1 - x2))
        return res


class Line(object):
    def __init__(self, k=None, b=None, point1=None, point2=None):
        """
        直线方程 y = kx + b
        注意：当直线垂直于x轴时，k=None, b=x0，即如果需要表示x=1这条直线，则line=Line(k=None, b=1),
        当直线垂直于y轴时，k=0，b=y0，即如果需要表示y=1这条直线，则line=Line(k=0, b=1)

        也可以通过给定两个点定义直线或线段，如果point1为None则认为是线段，当判断点是否在Line上时，结果可能是点在直线上，但不在线段上

        :param k:
        :param b:
        :param point1: (0,0), [0,0]
        :param point2: (0,0), [0,0]
        """
        if point1 is not None and point2 is not None:
            # 如果直线不垂直于x轴，则将左边点的坐标赋值给self.point1，右边点赋值给self.point2
            # 如果垂直于x轴，则将下方的点赋值给self.point1，上边的点赋值给self.point2
            if point1[0] < point2[0]:
                self.point1, self.point2 = point1, point2
            elif point1[0] == point2[0]:
                if point1[1] < point2[1]:
                    self.point1, self.point2 = point1, point2
                else:
                    self.point1, self.point2 = point2, point1
            else:
                self.point1, self.point2 = point2, point1

        if k is None and b is None:  # 如果k和b是None，则根据point1和point2坐标初始化直线类
            if point1[0] - point2[0] == 0:  # 垂直于x轴的直线，x=self.b
                self.k = None
                self.b = point1[0]
            else:
                self.k = (point2[1] - point1[1]) / (point2[0] - point1[0])
                self.b = point1[1] - point1[0] * self.k
        else:
            self.k = k
            self.b = b

    def cross_point(self, line2):
        """
        判断当前直线与目标直线line2是否相交，如果相交则返回交点坐标

        :param line2:
        :return:
        """
        is_cross = False
        x, y = 0, 0
        if self.k is None:
            if line2.k is not None:
                x = self.b
                y = line2.k * x + line2.b
                is_cross = True
        elif line2.k is None:
            x = line2.b
            y = self.k * x + self.b
            is_cross = True
        elif self.k != line2.k:
            x = (line2.b - self.b) / (self.k - line2.k)
            y = self.k * x + self.b
            is_cross = True

        return (x, y), is_cross

    def contains_point(self, point=(0, 0), as_line_segment=False, torlence=0.1):
        """
        判断点是否在Line上，分两种情况。
        一种是当前Line是直线，则只判断点是否位于直线方程上。

        另一种是当前Line是线段，则除了判断点是否位于直线方程上，还需要判断点在线段的区间内。

        :param point:
        :param as_line_segment: 是否作为线段，只有通过point1和point2定义时才能取True
        :param torlence: 允许的距离偏差，因为点很难准确的在线上，允许存在一定的偏差，默认为0.1
        :return:
        """
        if self.point1 is None or self.point2 is None:
            as_line_segment = False

        if self.k is None:  # 垂直于x轴的直线
            if point[0] == self.b:
                if as_line_segment:
                    if self.point1[1] <= point[1] <= self.point2[1]:  # 这里self.point1必然位于self.point2下方
                        return True  # 点位于线段上
                    else:
                        return False  # 点位于直线上，但不位于线段上
                else:
                    return True  # 点位于直线上
            else:
                return False
        elif abs(self.k * point[0] + self.b - point[1]) < torlence:  # 垂直于y轴的曲线也符合该规律
            if as_line_segment:
                if self.point1[0] < point[0] < self.point2[0]:
                    return True  # 点位于线段上
                else:
                    return False  # 点位于直线上，但不位于线段上
            else:
                return True  # 点位于直线上
        else:
            return False  # 点不位于直线上

    def distance(self, point=(0, 0), need_project_point=False):
        """
        判断直线与点的距离。计算方法为：如果直线的方程为Ax+By+C=0，则点(x0,y0)与之间的距离为：
        |A*x0+B*y0+C|/sqrt(A^2+B^2)
        如果A为0，则距离为：abs(C/B-y0)



        y=kx+b
        kx-y+b=0

        :param need_project_point: 是否需要垂足点坐标
        :param point:
        :return:
        """
        a = self.k
        b = -1
        c = self.b
        x0 = point[0]
        y0 = point[1]
        [].sort()
        if a is None:  # 直线垂直于x轴，方程为x=self.b
            dis = abs(self.b - x0)
        else:
            dis = abs(a * x0 + b * y0 + c) / math.sqrt(a * a + b * b)
        if need_project_point:
            if a is None:
                cz_x = self.b  # 直线
                cz_y = self.point1[1]
            else:
                cz_x = (b * b * x0 - a * b * y0 - a * c) / (a * a + b * b)
                cz_y = (a * a * y0 - a * b * x0 - b * c) / (a * a + b * b)
            return dis, (cz_x, cz_y)
        else:
            return dis


def interpolate_value_complex(x, points=None, x_list=None, y_list=None, need_sort=True):
    """
    获取插值的数值。
    根据点的列表求取x处的y值。点列表可以是乱序。
    如果传入的x超出采样点的x取值范围，则默认根据最外侧的两个点外插传入的x点对应的y值。

    示例2：
    x_list=[1,2,3]
    y_list=[[2,4], [3,3], [6,7]]
    res = interpolate_value_complex(1.5, x_list=x_list, y_list=y_list)
    则res = [2.5, 3.5]

    :param x:
    :param points: 以点的形式传入点数据（tuple/list的列表），例如[(1, 2), (3.3, 5), (5, 2.3), (6, 4)]。两种形式任选其一
    :param x_list: 以x列表和y列表的形式传入点数据，两种形式任选其一
    :param y_list: list/ndarray/Series 以x列表和y列表的形式传入点数据，两种形式任选其一，y的每个元素可以是一个列表，见实例2
    :param need_sort: 传入的数据x坐标是否按照顺序排列，如果已经按照顺序排列，则need_sort=False
    :return:
    """

    def get_y(_x, _points):
        for p in _points:
            if p[0] == _x:
                if isinstance(p[1], list) or isinstance(p[1], np.ndarray):
                    return list(p[1])  # y_list是个列表，则次数p[1]就是列表
                else:
                    return float(p[1])

    if points is None and (x_list is None or y_list is None):
        print("插值数据不全")
        raise AttributeError("插值数据不全")
    if points is None:
        points = []
        for i, x1 in enumerate(x_list):
            points.append((x1, y_list[i]))
    points = sorted(points, key=lambda p: p[0]) if need_sort else points  # 将点按照x坐标排序
    x1, x2 = find_nearest_points(x, [p[0] for p in points], extend_bound="extend")
    if x2 == "exact_point":
        return get_y(x1, points)
    else:
        y1 = get_y(x1, points)
        y2 = get_y(x2, points)
        return interpolate_value_simple(x, x1, y1, x2, y2)


def interpolate_2d(x=None, y=None, z=None,
                   dataframe: pd.DataFrame = None, input_titles=None, output_title=None,
                   xi=None,
                   method='rbf', **kwargs):
    """
    空间插值方法，根据已有的x,y,z，插值求新的x,y对应的z

    示例：
    x_list = y_list = z_list = [1,2,3]
    func = interpolate_2d(x_list,y_list,z_list)
    # 求取(0.5,0.5)处的值
    value = func(0.5,0.5)

    :param xi: 待求点的坐标，如果不指定，则返回拟合得到的插值函数，然后可以调用插值函数计算待求点的值，如果指定，则直接返回插值后的数据
    :param x: Union[ndarray, Iterable, int, float]
    :param y: Union[ndarray, Iterable, int, float]
    :param z: Union[ndarray, Iterable, int, float]
    :param dataframe: 以dataframe形式传入数据时使用
    :param input_titles: 以dataframe形式传入数据时，该参数指定自变量的列标题，即x,y的列标题
    :param output_title: 以dataframe形式传入数据时，该参数指定因变量的列标题，即z的列标题
    :param method: linear/cubic/rbf/sbs/lsgbs/kriging
    :return: 返回一个可以调用的插值函数
    """
    from scipy.interpolate import interp2d, Rbf, fitpack2

    if x is None and dataframe is not None:
        x = dataframe[input_titles[0]].to_numpy().flatten()
        y = dataframe[input_titles[1]].to_numpy().flatten()
        z = dataframe[output_title].to_numpy().flatten()
    if isinstance(x, list):
        x = np.array(x)
        y = np.array(y)
        z = np.array(z)
    if method == 'linear' or method == 'cubic':
        f = interp2d(x, y, z, kind=method)
    elif method == 'rbf':
        f = Rbf(x, y, z, epsilon=kwargs.get('epsilon', 2))
    elif method == 'sbs':
        # 可能会报错dfitpack.error: (m>=(kx+1)*(ky+1)) failed for hidden m: surfit_smth:m=8，改用'rbf'方法即可
        f = fitpack2.SmoothBivariateSpline(x, y, z, s=kwargs.get('s'))
    elif method == 'lsqbs':
        f = fitpack2.LSQBivariateSpline(x, y, z)
    elif method == 'kriging':
        in_data = np.vstack((x, y)).transpose()
        k = kriging(in_data, z)

        def f(x_p, y_p):
            return k.predict([x_p, y_p])
    else:
        f = None
    if xi is None:
        return f
    else:
        return f(xi)


def interpolate_nd(xi=None, data_input_nd=None, data_y=None,
                   dataframe: pd.DataFrame = None, df_x_titles=None, df_y_title=None,
                   method="linear"):
    """
    多维插值，只支持已知数据点是网格化数据点的情况，不支持任意数据点

    当method="linear"时，相当于分别对输入参数的每一维度进行interpolate_value_complex()插值，
    但本方法无法外插。该插值方法是性能试验计算的Excel程序中最常用
    的插值方法。参见示例2对管径和流速进行插值求基本传热系数（参见DL/T 932 附录C求K0）。

    示例1：
    points = [
        (450, 23, 0.8, 5.9341),
        (500, 23, 0.8, 6.3983),
        (450, 25, 0.8, 6.3121),
        (500, 25, 0.8, 6.7834),
        (450, 23, 0.9, 6.1882),
        (500, 23, 0.9, 6.6575),
        (450, 25, 0.9, 6.6011),
        (500, 25, 0.9, 7.0780)
    ]
    dataframe = pd.DataFrame(points, columns=["x1", "x2", "x3", "y"])
    interpolate_nd(xi=(470, 24.2, 0.87), dataframe=dataframe, df_x_titles=["x1", "x2", "x3"], df_y_title=["y"])

    示例2：
    sample = pd.DataFrame(
            data=[
                [2743.0, 3004.8, 3245.6, 3469.7, 3576.4, 3680.1,
                 3781.0, 3879.2, 3975.0, 4068.5, 4160.0, 4249.4,
                 4405.0, 4550.1, 4686.1, 4814.0, 4933.8, 5047.0],
                [2717.0, 2976.3, 3214.8, 3436.8, 3542.5, 3645.2,
                 3745.1, 3842.4, 3937.3, 4030.0, 4120.5, 4209.2,
                 4363.1, 4506.0, 4640.1, 4766.0, 4884.0, 4995.2],
                [2691.0, 2947.8, 3184.0, 3403.9, 3508.6, 3610.4,
                 3709.3, 3805.6, 3899.6, 3991.4, 4081.1, 4168.9,
                 4320.9, 4461.2, 4592.9, 4716.7, 4832.4, 4941.5],
                [2665.0, 2919.4, 3153.3, 3371.0, 3474.7, 3575.5,
                 3673.4, 3768.9, 3862.0, 3952.8, 4041.7, 4128.6,
                 4278.5, 4415.9, 4544.8, 4666.4, 4779.3, 4886.1],
                [2639.0, 2890.9, 3122.5, 3338.1, 3440.8, 3540.6,
                 3637.6, 3732.1, 3824.3, 3914.3, 4002.2, 4088.3,
                 4236.6, 4372.2, 4499.4, 4619.0, 4730.1, 4835.4],
                [2613.0, 2862.4, 3091.7, 3305.2, 3406.9, 3505.7,
                 3601.8, 3695.3, 3786.6, 3875.7, 3962.8, 4048.0,
                 4193.6, 4327.4, 4452.8, 4570.6, 4680.1, 4783.9],
            ],
            columns=[1.0, 1.2, 1.4, 1.6, 1.7, 1.8,
                     1.9, 2.0, 2.1, 2.2, 2.3, 2.4,
                     2.6, 2.8, 3.0, 3.2, 3.4, 3.6],
            index=[18, 22, 26, 30, 34, 38]
        )
    data = []
    for d in sample.index:
        for v in sample.columns:
            data.append([d, v, sample.loc[d, v]])

    df = pd.DataFrame(data=data, columns=['外径', '流速', '基本传热系数'])

    res_ = interpolate_nd((管子外径, 管内平均流速), dataframe=df, df_x_titles=['外径', '流速'],
                          df_y_title=['基本传热系数'])

    :param xi: 插值点自变量取值
    :param data_input_nd: 已知的自变量点列表
    :param data_y: 与data_input_nd对应的因变量取值
    :param dataframe: 使用dataframe传递数据时的dataframe数据
    :param df_x_titles: 已知自变量在dataframe的列标题列表
    :param df_y_title: 已知y在dataframe中的列标题
    :param method: 插值方法，默认"linear"
    :return:
    """
    import numpy as np
    from scipy.interpolate import griddata
    if data_input_nd is None and dataframe is not None:
        points = dataframe[df_x_titles]
        values = dataframe[df_y_title]
        points = points.to_numpy()
        values = values.to_numpy()
    else:
        points = np.asarray(data_input_nd)
        values = np.asarray(data_y)
    if xi is not None:
        if isinstance(xi, list):
            xi = tuple(xi)

        res = griddata(points, values, method=method, xi=xi)
        if isinstance(res, np.ndarray):
            if len(res) == 1:
                res = float(res)
        return res
    else:
        # 如果不传入待求点的坐标，则返回一个函数，可以单独调用以求待求点的值
        def func(x):
            res = griddata(points, values, x, method=method)
            if isinstance(res, np.ndarray):
                if len(res) == 1:
                    res = float(res)
            return res

        return func


def find_file(file_re="*.*", base_dir=None):
    """
    根据正则表达式在指定目录下查找文件

    :param file_re: 匹配的正则表达式，如"*/*.xlsx"
    :param base_dir: 指定的目录
    :return:
    """
    p = Path(base_dir)
    files = list(p.glob(file_re))
    return files


def find_nearest_points(x, x_list, extend_bound=None):
    """
    查找x_list中距离x最近的两个值.
    例如：
    x_list=[0, 1, 1.4, 2.3, 5, 6]
    当x=1.9时
        则该函数返回(1.4, 2.3)
    当x=6.2时
        返回(6,"max_nearest")，如果extend_bound=None
        返回6，如果extend_bound="repeat"
        返回(5,6)，如果extend_bound="extend"
    当x=-1时
        返回(0,"min_nearest")，如果extend_bound=None
        返回0，如果extend_bound="repeat"
        返回(0,1)，如果extend_bound="extend"
    如果x=1.4
        则返回(1.4,"exact_point")

    需要注意的是，当x数据类型不是整形时，exact_point可能由于精度问题取不到

    :param x:
    :param x_list:
    :param extend_bound: 边界处理方式
    :return:
    """
    sorted(x_list)
    if x > max(x_list):
        if extend_bound is None:
            return x_list[-1], "max_nearest"
        elif extend_bound == "repeat":
            return x_list[-1]
        elif extend_bound == "extend":
            return x_list[-2], x_list[-1]
    if x < min(x_list):
        if extend_bound is None:
            return x_list[0], "min_nearest"
        elif extend_bound == "repeat":
            return x_list[0]
        elif extend_bound == "extend":
            return x_list[0], x_list[1]
    for index, xx in enumerate(x_list):
        if x > xx:
            continue
        elif x == xx:
            return xx, "exact_point"
        else:
            return x_list[index - 1], xx


def kriging(in_data=None, out_data=None, optimizer='pso', dataframe=None, x_title=None, y_title=None):
    """
    根据输入和输出数据建立克里金模型，使用
    k=Kriging(in_data, out_data)  #获得克里金模型
    k.predict(in_data[0])  #进行预测
    当点的数量超过100个时，拟合速度很慢，不建议使用该方法，推荐使用

    示例：
    data=pd.DataFrame()
    k = kriging(dataframe=data, x_title=["功率", "热负荷", "环境温度"], y_title=["背压", "热耗率"])
    k.predict([660, 435, 22])

    :param in_data: Union[ndarray, Iterable, int, float]
    :param out_data: Union[ndarray, Iterable, int, float]，y只支持1维
    :param dataframe: 使用dataframe传递数据时使用
    :param x_title: 输入参数的标题，是一个列表
    :param y_title: 输出参数的标题，只支持一个参数
    :param optimizer:
    :return:
    """
    from pyKriging.krige import kriging
    # =================================获取X和Y数据===================================
    if in_data is None:
        in_data = dataframe[x_title].values
        out_data = dataframe[y_title].values
    else:
        if isinstance(in_data, list):
            in_data = np.array(in_data)
            out_data = np.array(out_data)
    k = kriging(in_data, out_data, name='simple')
    start = datetime.datetime.now()
    print("开始训练Kriging模型...")
    k.train(optimizer='ga')
    end = datetime.datetime.now()
    print(f"训练耗时：{(end - start).seconds}s")
    # k.infill()
    # k.addPoint()
    return k


def fit_nd_function(x, y, k_num, function=None, return_type: int = 0):
    """
    根据输入和输出拟合n元n次方程，通过function_type传入方程的形式，默认为n元1次方程。n为x的长度

    示例：
    def func(p,x):
        return p[0]*x[0]**2+p[1]*x[1]**2+p[2]*x[0]*x[1]+p[3]*x[0]+p[4]*x[1]+p[5]
    x = [[1,2], [1,3], [3, 6]]
    y = [2, 3, 5]
    k_num = 6  # 因为func函数中使用了6个p中的参数，有6个未知系数
    fit_nd_function(x, y, 6, func, 0)

    :param x:
    :param y:
    :param k_num: 需要拟合的函数中未知系数的个数
    :param function_type:
    :param return_type:
    :return:
    """
    from scipy.optimize import leastsq  # 最小二乘法曲面拟合

    p0 = np.asarray([1] * k_num)  # 系数的初始值
    if isinstance(x, list):
        x = np.array(x)
        y = np.array(y)

    def plane_err(p, x, y):
        return y - function(p, x)

    tparap = leastsq(plane_err, p0, args=(x, y))
    # print(f"拟合曲面方程的系数为：{tparap[0]}")
    if return_type == 0:
        return tparap[0]
    else:
        p_copy = list(tparap[0].copy())
        p_copy.extend([0] * (16 - num_args))  # 将p扩展到长度为16的数组

        def func(x, y):
            a0, a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, a11, a12, a13, a14, a15 = p_copy  # 必须置于func定义之内，否则会导致a0等系数找不到
            z = eval(expression)
            return z

        return func


def fit_surface(x, y, z, surface_type=None, return_type: int = 0):
    """
    根据散点拟合出一个曲面，曲面方程格式为默认是 z = a0 * x ** 2 + a1 * y ** 2 + a2 * x + a3 * y + a4 * x * y + a5。
    曲面方程可以由surface_type传入，例如surface_type="z=a0*x+a1*y+a2"。
    需要注意的是，python中的乘方是**，而不是^。例如，x的平方为x**2，不能写为x^2。

    示例：
    x = [1, 1, 3, 4, 5]
    y = [2, 1, 4, 5, 6]
    z = [3, 2, 7, 9, 11]
    fit_surface(x, y, z)
    fit_surface(x, y, z, surface_type="z=a0*x**2 + a1*x*y +a2"

    如果是需要根据实验点测量值绘制曲面，在不知道曲面阶次时不建议使用该方法，推荐使用Kriging方法


    :param x:
    :param y:
    :param z:
    :param surface_type: 拟合的曲面类型，取值必须是正确的python表达式，表达式中最多支持16个待拟合的系数，分别为a0, a1, a2, ..., a15
    :param return_type: 返回类型，0表示返回函数对象，1表示返回方程对应的系数，默认返回系数
    :return:
    """
    from scipy.optimize import leastsq  # 最小二乘法曲面拟合

    if surface_type is None:
        surface_type = "z=a0 * x ** 2 + a1 * y ** 2 + a2 * x + a3 * y + a4 * x * y + a5"
    expression = surface_type.split("=")[-1]
    num_args = len(expression.split("+"))

    def plane(p0, x, y):
        p_copy = list(p0.copy())
        p_copy.extend([0] * (16 - num_args))  # 将p扩展到长度为16的数组
        a0, a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, a11, a12, a13, a14, a15 = p_copy
        z = eval(expression)
        return z

    def plane_err(p, x, y, z):
        """
        误差函数，用来计算拟合函数预测值与实际值之间的误差，该函数最多接收两个参数

        :param p: 需要拟合的参数的值，需要传入初始值，计算过程中由scipy库更新
        :param x: 实际的散点x坐标
        :param y: 实际的散点y坐标
        :param z: 实际的散点z坐标
        :return:
        """
        return plane(p, x, y) - z

    if isinstance(x, list):
        x = np.array(x)
        y = np.array(y)
        z = np.array(z)
    p0 = np.asarray([1] * num_args)  # 系数的初始值

    # leastsq(func, x0, args=())    #
    # func是拟合曲面的误差函数
    # x0是拟合函数中变量的初始值，一般不影响拟合结果，可以随便给
    # args是实际的散点数值。
    tparap = leastsq(plane_err, p0, args=(x, y, z))
    print(f"拟合曲面方程的系数为：{tparap[0]}")
    if return_type == 0:
        return tparap[0]
    else:
        p_copy = list(tparap[0].copy())
        p_copy.extend([0] * (16 - num_args))  # 将p扩展到长度为16的数组

        def func(x, y):
            a0, a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, a11, a12, a13, a14, a15 = p_copy  # 必须置于func定义之内，否则会导致a0等系数找不到
            z = eval(expression)
            return z

        return func


def update_matplotlib_font_config():
    from matplotlib import rcParams
    import matplotlib.pyplot as plot
    config = {
        "font.family": 'serif',
        "font.size": 16,
        "pgf.rcfonts": False,
        "text.usetex": True,
        "pgf.preamble": [
            r"\usepackage{unicode-math}",
            r"\setmainfont{Times New Roman}",
            r"\usepackage{xeCJK}",
            r"\setCJKmainfont{SimSun}",
        ]
    }
    plot.rcParams['font.size'] = 16
    # rcParams.update(config)
    plot.rcParams['font.sans-serif'] = ['STSong']
    plot.rcParams['axes.unicode_minus'] = False
    plot.rcParams['xtick.direction'] = 'in'
    plot.rcParams['ytick.direction'] = 'in'  # 刻度内测，out外侧


def plot_2d_scatter(x: list, y: list, x_label="X", y_label="Y",
                    x_ticks=None, y_ticks=None, draw_legend=False,
                    point_label=None, s: float = 40, point_color="#0072BD",
                    method=None,
                    alpha=0.4, save_to=None, show=True, plot=None, font_size=20):
    """
    绘制二维图

    :param font_size:
    :param plot:
    :param y_ticks:
    :param x_ticks:
    :param draw_legend: 如果是多次绘制，必须在最后一次绘制时设置该参数
    :param x:
    :param y:
    :param x_label:
    :param y_label:
    :param point_label:
    :param s: 散点图中点的大小
    :param point_color:
    :param alpha:
    :param method: 取值为None，表示是独立的绘图方法，如果是append，则表示在上一次的plot中继续绘制
    :param save_to: 如果需要保存二维图片，只需要给该参数指定对应的<图片文件路径>即可
    :param show: 是否显示，如果为真，则程序会在该方法处暂停，并显示指定的数据图片，关闭后才能继续运行，默认为True
    :return:  plt实例，可以利用plt实例进一步绘制图元
    """
    if plot is None:
        from matplotlib import pyplot as plot
        if method is None:
            plot.clf()
    # 解决中文显示问题
    if x_ticks is not None:
        plot.xticks(x_ticks)
    if y_ticks is not None:
        plot.yticks(y_ticks)
    if x_label is not None:
        plot.xlabel(x_label)
    if y_label is not None:
        plot.ylabel(y_label)
    plot.scatter(x, y, s, c=point_color, alpha=alpha, label=point_label)
    if save_to is not None:
        if draw_legend:
            plot.legend()
        plot.savefig(save_to, dpi=300)
    if show:
        plot.show()
    return plot


def plot_2d_line(x: list, y: list, marker="*", x_label=None, y_label=None,
                 x_ticks=None, y_ticks=None, draw_legend=False,
                 line_label=None, line_color="#0072BD",
                 plot=None, save_to=None, show=True, method=None):
    """
    绘制折线图，不支持中文标签

    :param y_ticks:
    :param x_ticks:
    :param method: 取值为None，表示是独立的绘图方法，如果是append，则表示在上一次的plot中继续绘制
    :param draw_legend: 如果是多次绘制，必须在最后一次绘制时设置该参数
    :param x:
    :param y:
    :param marker:
    :param x_label:
    :param y_label:
    :param line_label:
    :param line_color:
    :param plot:
    :param save_to:
    :param show:
    :return:
    """
    if plot is None:
        from matplotlib import pyplot as plot
        if method is None:
            plot.clf()
    # 解决中文显示问题
    # plot.rcParams['font.sans-serif'] = ['SimHei']
    # plot.rcParams['axes.unicode_minus'] = False
    if x_ticks is not None:
        plot.xticks(x_ticks)
    if y_ticks is not None:
        plot.yticks(y_ticks)
    if x_label is not None:
        plot.xlabel(x_label)
    if y_label is not None:
        plot.ylabel(y_label)
    plot.plot(x, y, marker=marker, label=line_label, color=line_color)
    if save_to is not None:
        if draw_legend:
            plot.legend()
        plot.savefig(save_to, dpi=300)
    if show:
        plot.show()
    return plot


def xyz_split(xyz):
    """
    将xyz坐标点转换为单独的x_list, y_list和z_list，以便于进行plot_3d调用。支持DataFrame、numpy.ndarray和List三种类型，数据的
    形状只能是为(3, *)或(*, 3)，如果形状不是(3,3)，则本方法会自动识别点坐标是按行还是按列排列。如果形状是(3,3)，则本方法认为第一列是
    x，第二列是y，第三列是z。

    :param xyz: DataFrame,np.ndarray或List
    :return: x_list, y_list, z_list
    """
    if isinstance(xyz, pd.DataFrame):
        shape = xyz.shape
        if shape[1] == 3:
            x_list = xyz.iloc[:, 0].to_list()
            y_list = xyz.iloc[:, 1].to_list()
            z_list = xyz.iloc[:, 2].to_list()
        else:
            x_list = xyz.iloc[0].to_list()
            y_list = xyz.iloc[1].to_list()
            z_list = xyz.iloc[2].to_list()
    elif isinstance(xyz, np.ndarray):
        shape = xyz.shape
        if shape[1] == 3:
            x_list = xyz[:, 0]
            y_list = xyz[:, 1]
            z_list = xyz[:, 2]
        else:
            x_list = xyz[0]
            y_list = xyz[1]
            z_list = xyz[2]
    elif isinstance(xyz, list):
        return xyz_split(np.array(xyz))
    else:  # 格式未识别，以后可能会添加对tensor的支持
        return None
    return x_list, y_list, z_list


def plot_3d(x: list = None, y: list = None, z: list = None, xyz=None, x_range=None, y_range=None, z_range=None,
            x_label=None, y_label=None, z_label=None, title=None,
            scatter=True, projection=True, surface=True,
            method='rbf', backend=None, show=True, **kwargs):
    """
    绘制三维图

    示例：
    plot_3d(x, y, z, x_range=np.arange(0, 10, 0.1), y_range=np.arange(0, 10, 0.1), ,method='sbs', **{"s":10})
    plot_3d(x,y,z, backend="PyQt5")  # 返回一个QWidget类型的图形对象

    :param z_range:
    :param title:
    :param x: x坐标列表
    :param y: y坐标列表
    :param z: z坐标列表/函数定义，函数定义是根据(x,y)计算z的坐标
    :param xyz: 点坐标的替代输入方式，可以传入一个DataFrame、ndarray或者二维List，但行和列中必须有一个长度为3，且如果xyz传值，则会忽略单独的x,y,z参数
    :param x_range: x坐标显示范围，range()和np.arange()定义的范围都可以，np.arange()支持float类型
    :param y_range: y坐标显示范围，range()和np.arange()定义的范围都可以，np.arange()支持float类型
    :param scatter: 是否绘制散点，散点参数通过kwargs设置
    :param x_label: x坐标轴的标签
    :param y_label: y坐标轴的标签
    :param z_label: z坐标轴的标签
    :param projection: 是否绘制投影图，即投影到x-y、y-z或x-z的投影图，投影图的参数在kwargs中设置
    :param surface: 是否绘制曲面图，曲面图的参数在kwargs中设置
    :param method: 插值方法，可取值 'rbf','sbs','linear','cubic'
    :param backend: 绘制目标库，一般用于将绘制图形整合到其他图形界面中时设置该项
    :param kwargs: 某些插值方法可以设置额外参数，以控制插值结果，例如 rbf的epsilon，sbs的s值都可以在kwargs中设置，可以设置参数名及说明如下：
    {
    'surface_cmap': '可取值"coolwarm"或"rainbow"，表示曲面图的配色',
    'surface_rcount': '取整数，表示x方向的grid个数',
    'surface_ccount': '取整数，表示y方向的grid个数',
    'surface_rstride': 'number，表示x方向的grid间距，不能和rcount两个参数同时给定',
    'surface_cstride': 'number，表示y方向的grid间距，不能和ccount两个参数同时给定',
    'proj_zdir': '可取值"x","y","z","[x,y]","[x,y,z]",设置需要哪几个面的投影图',
    'proj_offset': '可取值10，[10,10], [10,10,10]，需要与proj_zdir对应投影图在对应坐标轴上的距离，如 proj_zdir='x', proj_offset=10，则在x=10的平面上绘制投影图,
    'proj_fill': '可取值True,False,表示投影图是否需要填充',
    'proj_cmap': '可取值"coolwarm"或"rainbow"，表示投影云图的配色',
    'proj_levels': '取整数，控制等高线的数量',
    }
    :return: None/QWidget
    """
    from matplotlib import pyplot as plot
    from mpl_toolkits.mplot3d import Axes3D  # 用来给出三位坐标系
    if xyz is not None:
        x, y, z = xyz_split(xyz)
    f = interpolate_2d(x, y, z, method=method, **kwargs)  # 根据已有数据点获得插值函数
    if isinstance(x, list):
        x = np.array(x)
        y = np.array(y)
        z = np.array(z)
    if x_range is None:
        x_range = np.arange(min(x), max(x) + (max(x) - min(x)) / 10, (max(x) - min(x)) / 10)
    if y_range is None:
        y_range = np.arange(min(y), max(y) + (max(y) - min(y)) / 10, (max(y) - min(y)) / 10)
    x_grid, y_grid = np.meshgrid(x_range, y_range)  # 限定图形的样式是网格线的样式

    z_grid = np.zeros((len(x_grid), len(y_grid)))
    for i in range(len(x_grid)):
        for j in range(len(y_grid)):
            z_grid[i, j] = f(x_grid[i, j], y_grid[i, j])
    # 设置中文支持
    # import matplotlib.font_manager as font_manager
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False  # 运行配置参数总的轴（axes）正常显示正负号（minus）
    # try:
    #     # noinspection all
    #     font_manager._rebuild()
    # except AttributeError:
    #     ...

    if backend is None:
        figure = plot.figure()
        # figure, axes = plot.subplots()
        # axes = plot.axes(projection='3d')
        axes = Axes3D(figure)
        figure.add_axes(axes)  # 3.9版本以后必须加此语句才能绘制出图形
        # ===========================控制拟合曲面的绘制格式==========================================================
        if surface:
            surf_rc = kwargs.get('surf_rcount')
            surf_cc = kwargs.get('surf_ccount')
            surf_rs = kwargs.get('surf_rstride')
            surf_cs = kwargs.get('surf_cstride')
            args_dict = {}
            if surf_rc is not None:
                args_dict.update({"rcount": surf_rc})
            if surf_cc is not None:
                args_dict.update({"ccount": surf_cc})
            if surf_rs is not None:
                args_dict.update({"rstride": surf_rs})
            if surf_cs is not None:
                args_dict.update({"cstride": surf_cs})
            surf_cmap = kwargs.get('proj_cmap', 'rainbow')
            axes.plot_surface(x_grid, y_grid, z_grid, cmap=surf_cmap, **args_dict)
        # ===========================控制拟合曲面的绘制格式==========================================================
        # ============================控制投影面的绘制格式===========================================================
        if projection:
            proj_fill = kwargs.get('proj_fill', True)
            proj_cmap = kwargs.get('proj_cmap', 'viridis')
            proj_levels = kwargs.get('proj_levels', 10)
            if proj_fill:
                axes.contourf3D(x_grid, y_grid, z_grid, levels=proj_levels, zdir=kwargs.get('zdir', 'z'),
                                offset=kwargs.get('offset', min(z)),
                                cmap=proj_cmap)
            else:
                axes.contour3D(x_grid, y_grid, z_grid, zdir=kwargs.get('zdir', 'z'),
                               offset=kwargs.get('offset', min(z)))
        # ============================控制投影面的绘制格式===========================================================
        # ==============================控制散点图的绘制格式=========================================================
        if scatter:
            axes.scatter3D(x, y, z)
        # ==============================控制散点图的绘制格式=========================================================
        # =================================设置z轴范围=============================================================
        if z_range is not None:
            if isinstance(z_range, np.ndarray):
                axes.set_zlim(min(z_range), max(z_range))
            else:
                axes.set_zlim(z_range.train_model, z_range.stop)
        # =================================设置z轴范围=============================================================
        axes.set_xlabel(x_label or "x")
        axes.set_ylabel(y_label or "y")
        axes.set_zlabel(z_label or "z")
        if title is not None:
            plot.title(title)

        # plot.show()
        plot.show(block=True)
    elif backend.lower() == "pyqt5":
        import matplotlib
        # matplotlib.use("TkAgg")
        matplotlib.use("Qt5Agg")
        from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
        from matplotlib.figure import Figure

        class Qt5Figure(FigureCanvas):
            def __init__(self, figsize=None, dpi=None, facecolor=None, edgecolor=None, linewidth=0.0,
                         frameon=None, subplotpars=None, tight_layout=None, constrained_layout=None):
                self.figure = Figure(figsize=figsize, dpi=dpi, facecolor=facecolor, edgecolor=edgecolor,
                                     linewidth=linewidth, frameon=frameon, tight_layout=tight_layout,
                                     subplotpars=subplotpars, constrained_layout=constrained_layout)

                # 在父类中激活Figure窗口，此句必不可少，否则不能显示图形
                super(Qt5Figure, self).__init__(self.figure)
                self.axes = self.figure.add_subplot(111, projection='3d')
                self.axes.plot_surface(x_grid, y_grid, z_grid, cmap='rainbow')
                self.axes.set_xlabel(x_label or "x")
                self.axes.set_ylabel(y_label or "y")
                self.axes.set_zlabel(z_label or "z")

        res = Qt5Figure()
        if show:
            res.show()

        return Qt5Figure()


def characters_2_number(characters: str):
    """
    将大写的数字转换为数值。
    例如：
    '二零一一'转换为'2011'

    :param characters:
    :return:
    """
    # ============================ 清洗字符串，去除字符串中的所有空字符 =============================
    temp_chars = []
    for char in characters:
        if char.strip() != '':
            temp_chars.append(char)
    characters = ''.join(temp_chars)
    # ============================ 清洗字符串 =============================
    common_used_numerals_tmp = {'○': '0', '零': '0', '一': '1', '二': '2', '三': '3', '四': '4',
                                '五': '5', '六': '6', '日': '7', '八': '8', '九': '9',
                                '点': '.',
                                }
    xci = ['十', '百', '千', '万', '亿']
    result = []
    for char in characters:
        if char in xci:  # 如果是虚词中的汉字，则判断是否左边还有数字，有则不转义为数字，没有且char=='十'时需要转义为1
            if characters.find(char) == 0 and char == "十":
                result.append("1")
                continue
        result.append(common_used_numerals_tmp.get(char))
    result = ''.join(result)
    result = float(result) if '.' in result else int(result)
    return result


def between_time(time_series: "Series of Datetime.Datetime or str or pd.Timestamp",
                 start_time_str, end_time_str):
    """
    根据time_series中的时间记录是否处于start_time和end_time之间返回bool的Series

    :param end_time_str: 结束时间的str，原则上格式应为"%Y-%m-%d %H:%M"
    :param start_time_str: 开始时间的str，原则上格式应为"%Y-%m-%d %H:%M"
    :param time_series: datatime.datetime类对象组成的Series
    :return:
    """
    time1 = datetime.datetime.strptime(start_time_str, "%Y-%m-%d %H:%M")
    time2 = datetime.datetime.strptime(end_time_str, "%Y-%m-%d %H:%M")
    result = []
    for time_n in time_series:  # 逐行判断是否需要
        try:
            # pandas读入的数据格式直接是datetime.datetime类型
            if isinstance(time_n, str):
                # noinspection all
                time_n = pd.Timestamp(time_n)  # pd.Timestamp类可以和datetime类直接比较大小
            if time1 <= time_n <= time2:
                result.append(True)
            else:
                result.append(False)
        except (ValueError, TypeError):
            # ValueError是无法转为日期格式导致的错误，TypeError是pandas转换空行为nan，而nan与日期比较产生的错误
            result.append(False)
    return result


def search_file_in_folders(basename: str, folders: str or list, need_all: bool = False):
    """
    在指定目录下搜索指定文件，可以使用通配符，但是如果要保证查找到的文件是需要的文件，需要确保能被匹配的是唯一的文件，而不是很多文件都可以匹配。

    :param basename: 被搜索文件的文件名
    :param folders: 单一路径或路径的列表，会在这些路径中开始搜索，默认返回查找到的第一个
    :param need_all: 是否查找所有
    :return: 返回找到的文件
    """
    if isinstance(folders, str):
        res = sorted(Path(folders).rglob(basename))
    else:
        res = []
        for folder in folders:
            tmp = sorted(Path(folder).rglob(basename))
            if tmp is not None and len(tmp) > 0:
                res.extend(tmp)
                if not need_all:
                    return res[0]

    if need_all:
        return res
    else:
        if len(res) > 0:
            return res[0]
        else:
            return None


def get_datetime_col_of_dataframe(df, judgement_row=None, need_datetime_format=False):
    """
    获取dataframe中的日期时间列，返回找到的第一个日期时间列名，确保df不为空DataFrame，返回时间列的列标签名，如果df.index是时间则返回-1

    :param df:
    :param judgement_row: 判断是否是时间列的依据行，即该行哪一列为时间字符串则返回对应的列名，考虑到数据区域前后可能存在非数据航，默认取中间行判断（当df总行数>10时），如果df总行数<10，则取最后一行判断
    :param need_datetime_format: 是否同时返回日期时间的格式
    :return: 如果没有数据列，则返回None
    """
    if len(df) <= 0:
        return None
    time_col_name = None

    if str(df.index.dtype) == 'object':  # df.index.dtype.NAME == 'object'会报错，没有NAME属性
        try:
            _ = pd.Timestamp(df.index[0])
            return -1
        except ValueError:
            pass
    elif str(df.index.dtype).startswith('datetime'):
        return -1
    if judgement_row is None:
        if len(df) < 10:
            judgement_row = -1
        else:
            judgement_row = len(df) // 2

    for col_name, dt in df.dtypes.items():
        if str(dt) == 'object':
            try:
                judge_obj = df[col_name].values[judgement_row]
                _ = pd.Timestamp(judge_obj)
                time_col_name = col_name
                if need_datetime_format:
                    dt_format = get_datetime_format(str(judge_obj))
                    return time_col_name, dt_format
                break
            except ValueError:
                continue
        elif str(dt) == 'datetime64[ns]':
            if need_datetime_format:
                judge_obj = df[col_name].values[judgement_row]
                return col_name, get_datetime_format(str(judge_obj))
            return col_name
    return time_col_name


def sort_dataframe_by_datetime(df: pd.DataFrame, time_col=None):
    """
    将dataframe的行按时间排序

    :param df:
    :param time_col: 如果是int，则表示时间列的索引，如果是str，则表示时间列的标题名称
    :return:
    """
    if len(df) <= 0:
        return df

    if time_col is not None:
        if isinstance(time_col, str):
            data_v = df.sort_values(time_col, ascending=True)
        else:
            data_v = df.sort_values(df.columns[time_col].NAME, ascending=True)
        return data_v

    time_col_name = get_datetime_col_of_dataframe(df)
    if time_col_name == -1:
        return df.sort_index(ascending=True)
    else:
        return df.sort_values(time_col_name, ascending=True)


def cut_time_period_of_dataframe(df: pd.DataFrame, start_time, end_time, time_col_idx=None):
    """
    从一个DataFrame对象中剪切出指定时间段内的值，需要时间按列排列，如果时间按行排列，请转置后调用该方法。

    :param df:
    :param start_time:
    :param end_time:
    :param time_col_idx: 时间所在的列，如果日期和时间分为两列，需要先合并
    :return:
    """
    if len(df) <= 0:
        return df
    if start_time == "all" and end_time == "all":  # 不裁剪直接输出
        return df
    if time_col_idx is not None:
        data_v = df[between_time(df.iloc[:, time_col_idx], start_time, end_time)]
    else:
        time_col_name = get_datetime_col_of_dataframe(df)
        if time_col_name == -1:
            data_v = df[between_time(df.index, start_time, end_time)]
        else:
            data_v = df[between_time(df[time_col_name], start_time, end_time)]
    data_v = data_v.copy()
    return data_v


def execute_function_every_day(func, day="*", day_of_week=None, hour=16, minute=0, second=0, daemon=False):
    """
    定时执行一次函数func，默认每天的16：40执行。

    :param second:
    :param day_of_week:
    :param day:
    :param minute: 每天什么时候执行
    :param hour: 每天什么时候执行
    :param func:
    :return:
    """
    from apscheduler.schedulers.background import BackgroundScheduler, BlockingScheduler
    from yangke.common.config import logger
    scheduler = BlockingScheduler(timezone='Asia/Shanghai') if daemon else BackgroundScheduler(timezone='Asia/Shanghai')
    if day_of_week is None:
        scheduler.add_job(func, 'cron', hour=hour, minute=minute, second=second, day=day)  # 每天的16：00运行
        logger.debug(f"execute job every day：每天{hour}:{minute}:{second}执行任务{func}")
    else:
        scheduler.add_job(func, 'cron', day_of_week=day_of_week, hour=hour, minute=minute, second=second)
        logger.debug(f"execute job every week：每周{day_of_week} {hour}:{minute}:{second}执行任务{func}")
    scheduler.start()


def execute_function_by_interval(func, day=0, hour=0, minute=1, second=0, daemon=False):
    """
    每隔time_interval秒执行一次函数func

    :param func:
    :param day:
    :param hour:
    :param minute:
    :param second:
    :param daemon: 是否自己为守护线程，不守护，则会直接退出
    :return:
    """
    from apscheduler.schedulers.background import BackgroundScheduler, BlockingScheduler
    func()  # 先执行一次，因为BackgroundScheduler刚开始不会执行，而是会等第一个间隔时间结束后才开始执行
    scheduler = BlockingScheduler(timezone='Asia/Shanghai') if daemon else BackgroundScheduler(timezone='Asia/Shanghai')
    scheduler.add_job(func, 'interval', hours=hour, minutes=minute, seconds=second)
    scheduler.start()
    # scheduler.shutdown()
    return scheduler


def yield_all_file(folder, filter_=None, ignore_temp_file: bool = True):
    """
    遍历folder下的所有文件

    :param ignore_temp_file: 忽略临时文件，因为office打开会占用文件，产生临时文件，默认忽略该文件
    :param filter_: 需要遍历的文件后缀名列表，不在该列表的文件类型会被略过，后缀名一律使用小写，例如[".dat", ".xlsx"]
    :param folder:
    :return:
    """
    for root, ds, fs in os.walk(folder):
        for f in fs:
            fullname = os.path.join(root, f)
            if f.startswith("~$") and ignore_temp_file:  # ~$开头的文件是word、excel的临时文件
                continue
            if filter_ is not None:
                if isinstance(filter_, str):
                    filter_ = [filter_]
                if os.path.splitext(fullname)[-1].lower() in filter_:
                    yield fullname
                else:
                    continue
            else:
                yield fullname


def complete_line(line_slices: list, symbol='"'):
    """
    判断传入的字符串片段连接后是否构成完整的行，因为有些用双引号或括号括起来的元素会跨行，如果只发现元素边界标识符的前一个，找不到后一个，
    则认为数据不完整，例如：
    如果：line_slices=['"完整元素1"','"元素2-partial1']
    则返回False，因为元素2中只找到一个双引号，其收尾的双引号没有找到，因此其后续元素中可能存在后一个双引号。

    如果：line_slices=['"完整元素1"','"元素2-partial1','\r\n','元素2-partial2"']
    则返回True，因为该列表连接后发现了成对出现的双引号。

    :param symbol:
    :param line_slices:
    :return:
    """
    line = "".join(line_slices)
    pattern1 = r'("[^"]*)'  # 找第一个双引号，一对会出现两次
    # pattern2 = pattern2 = r'("[^"]*")'  # 找成对出现的双引号
    num = re.findall(pattern1, line)
    if len(num) % 2 == 0:
        return True
    else:
        return False


def merge_dataframes_simple(dfs: list):
    """
    合并多个dataframe，自动判断按行还是按列合并。
    本方法只做简单的合并拼接操作，不会判断是否有重复列，重复行或按时间求平均等。

    合并的多个dataframe必须具有相同行名或列名，列或行顺序可以不同。

    :param dfs:
    :return:
    """
    result = None
    if len(dfs) == 0:
        return None
    elif len(dfs) == 1:
        return dfs[0]

    # 判断列名是否相同
    col1 = set(dfs[0].columns)
    col2 = set(dfs[1].columns)
    add_rows = True if col1 == col2 else False  # 如果列名相同就拼接行，否则拼接列
    for df in dfs:
        if result is None:
            result = df
        else:
            if add_rows:
                result = pd.concat([result, df], axis=0, join="inner")
            else:
                result = pd.concat([result, df], axis=1, join="inner")
    return copy.deepcopy(result)


def interpolate_df_timestamp(df: pd.DataFrame, timestamp: pd.Timestamp, _timeseries: list | None = None):
    """
    根据指定的时间戳，在df中插值求取该时间戳对应的数值，返回该时间戳下每一列的插值结果组成的数组
    :param df:
    :param _timeseries: 如果指定了时间序列，则默认使用该时间序列作为x轴进行插值，从而加速该方法执行速度，该时间序列可以是已经转换为整形的时间
    :param timestamp:
    """
    if _timeseries is None:
        time_col = get_datetime_col_of_dataframe(df)
        if time_col == -1:
            _timeseries = df.index
        else:
            _timeseries = df[time_col]
    elif isinstance(_timeseries, pd.Series):
        _timeseries = list(_timeseries)

    if not isinstance(_timeseries[0], int):
        _timeseries = [t.value if isinstance(t, pd.Timestamp) else pd.Timestamp(t).value for t in _timeseries]
    ys = df.values
    res = interpolate_value_complex(timestamp.value, x_list=_timeseries, y_list=ys, need_sort=False)
    return res


def interpolate_df(df: pd.DataFrame, time_list=None, time_interval=None):
    """
    将dataframe中的数据根据时间进行插值，如果time_list非空，则根据time_list提供的时间序列进行插值，
    否则，根据time_interval提供的时间间隔进行插值。需要确保数据已按时间进行排序。因为排序操作耗时较长，本方法
    不再排序。
    本方法不要求df中的时间标签是等间距的。但df必须包含2条以上的数据行。该方法极为耗时，尤其是在数据量较大的情况下。

    :param df:
    :param time_list:
    :param time_interval: 如果是整数，则代表间隔多少秒
    :return:
    """
    time_col = get_datetime_col_of_dataframe(df)
    if time_col == -1:
        time_series = df.index
    elif time_col is None:
        return df
    else:
        time_series = df[time_col]

    start_time = pd.Timestamp(time_series[0])
    end_time = pd.Timestamp(time_series[-1])
    res_list = []
    if time_list is None:
        if isinstance(time_interval, int):
            time_interval = pd.Timedelta(seconds=time_interval)
        end_t = start_time
        time_list = list(time_series)
        time_list = [t.value if isinstance(t, pd.Timestamp) else pd.Timestamp(t).value for t in time_list]
        i = 0
        while end_t < end_time:
            inter_value = interpolate_df_timestamp(df, end_t, time_list)
            res_list.append([end_t, *inter_value])
            end_t = end_t + time_interval
            i += 1
            if i % 100 == 0:
                logger.debug(f"进行第{i}行插值...")
        res = pd.DataFrame(res_list)
        res = res.set_index(0)
        res = res.set_axis(labels=df.columns, axis=1)
        return res
    else:
        ...


def get_datetime_format(date_time_str: str):
    """
    判断日期时间字符串的格式，支持形如以下型式的字符串：
    2023/8/23 08:10
    2023/8/23 08:10:00
    2023/8/23 08:10:00.000  %Y/%m/%d %H:%M:%S.%f
    2023/8/23 08:10 AM
    2023/8/23 08:10:00 AM
    2023/8/23 08:10:00.000 AM
    2023/8/23 08:10 PM
    ...
    2023-8-23 08:10
    2023-8-23 08:10:00
    2023-8-23 08:10:00.000 PM
    ...
    08:10
    08:10:00
    08:10:00.000
    08:10 AM
    ...

    """
    _s = date_time_str.split(" ")  # 将字符串用空格分成及部分
    _s = [i.strip() for i in _s]
    # ------------------ 找出日期字符串 -------------------------
    date_index = None  # 日期字符串的索引
    date_sep = None  # 日期字符串的分割字符
    time_index = None
    type_index = None
    date_format = None
    time_format = None
    if "/" in _s[0]:
        date_index = 0
        date_sep = "/"
    elif "-" in _s[0]:
        date_index = 0
        date_sep = "-"
    # ------------------ 找出日期字符串 -------------------------
    # ------------------ 找出时间字符串 -------------------------
    if ":" in _s[0]:
        time_index = 0
    elif ":" in _s[1]:
        time_index = 1
    # ------------------ 找出时间字符串 -------------------------
    # ------------------ 判断时12小时制还是24小时制----------------
    if len(_s) == 2:
        if _s[1].lower() == "am" or _s[1].lower() == "pm":
            type_index = 1
    elif len(_s) == 3:
        _1 = _s[1].lower()
        _2 = _s[2].lower()
        if _1 == "am" or _1 == "pm":
            type_index = 1
        elif _2 == "am" or _2 == "pm":
            type_index = 2
    # ------------------ 判断时12小时制还是24小时制----------------
    if date_index is not None:
        _dates = _s[date_index].split(date_sep)
        if len(_dates[0]) == 4:
            date_format = f"%Y{date_sep}%m{date_sep}%d"
        elif len(_dates[2]) == 4:
            date_format = f"%m{date_sep}%d{date_sep}%Y"
        else:
            date_format = ""
    if time_index is not None:
        if "." in _s[time_index]:
            time_format = "%H:%M:%S.%f"
        else:
            _t = _s[time_index].split(":")
            if len(_t) == 2:
                time_format = "%H:%M"
            elif len(_t) == 3:
                time_format = "%H:%M:%S"
    if type_index is not None:
        if date_index < time_index:
            res = f"{date_format} {time_format} AM/PM"
        else:
            res = f"{time_format} {date_format} AM/PM"
    else:
        if date_index < time_index:
            res = f"{date_format} {time_format}"
        else:
            res = f"{time_format} {date_format}"
    res = res.replace("  ", " ")
    res = res.strip()
    return res


def merge_two_dataframes(data1, data2, time_col_index: int | bool | str | None = None):
    """
    合并两个dataframe，自动判断按行还是按列合并。返回结果按照时间进行排序，时间列不能是行索引，如果没有时间列，则强制只能按行合并
    如果两个dataframe的index相同，则横向拼接，axis=1，合并结果的index不变，相当于插入了很多列数据
    如果两个dataframe的columns相同，则竖向拼接，axis=0，合并结果的columns不变，相当于插入了很多行数据

    如果dataframe中有非数值列，在groupby()时非数值列会丢失，如果需要保留非数值列而无需groupby()，尝试使用merge_dataframes_simple方法

    如果数据中包含数据品质的标记性字符（P、B,poor,bad），则该方法会去掉字符后尝试进一步合并数据列，非数据列会被丢弃。

    合并的两种情况：(按列和按行合并利用了groupby方法)
        1. 两个data的列名相同，但时间段不同，则将data2续到data1的最后一行之后，作为新行
        2. 两个data的时间段相同，但列名（即参数不同，一般来自DCS系统中导出的不同的趋势组数据）不同，则将data1
           和data2的列拼接起来。可能还存在更复杂的情况，目前已测试完成。

    :param data1: 需要合并的dataframe
    :param data2:
    :param time_col_index: 时间列的标题，除了可以取列标题以外，也可以取值False，表示合并的df中不存在时间列，也可以取值None，表示有时间列，但由系统自动判断时间列位置
    :return: tuple(dataframe, dropped_lines)
    """
    if data2 is None or data2.shape[0] == 0:
        return data1, []
    if data1 is None or data1.shape[0] == 0:
        return data2, []
    if time_col_index is None or time_col_index:  # 如果有时间列，即使time_col_index，也是有时间列，只有为false时表示无时间列
        data1 = sort_dataframe_by_datetime(data1, time_col=time_col_index)
        data2 = sort_dataframe_by_datetime(data2, time_col=time_col_index)
        if isinstance(time_col_index, str):
            time_col = time_col_index
        else:
            time_col = get_datetime_col_of_dataframe(data1, need_datetime_format=False)  # 时间列不能是索引列
        # time_col = get_datetime_col_of_dataframe(data2, need_datetime_format=False)  # 时间列不能是索引列
        try:
            data1[time_col] = pd.to_datetime(data1[time_col])
            data2[time_col] = pd.to_datetime(data2[time_col])
        # except UserWarning:  # python默认不会捕获warning，因此该语句无效
        #     print(f"时间格式未识别，请检查：{data1[time_col]}\n{data2[time_col]}")
        except:
            print("合并的dataframe中不存在时间列或时间列无法转换为时间类型")

        data4 = pd.concat([data1, data2], axis=0).sort_values(time_col)  # 看起来是按行合并，实际上结合groupby方法同时实现了按列和按行
        data5 = data4.groupby(time_col).mean()  # 合并相同时间行的项，会丢失非数值列
        # 在pd.DataFrame对象求sum()时，其中不可求和的列会丢失，这里检测下是否有丢失的列，如果有则记录
        set1 = set(data1.columns) - (set(data5.columns) & set(data1.columns))
        set2 = set(data2.columns) - (set(data5.columns) & set(data2.columns))
        dropped_col = set1.union(set2) - {time_col}
        try:
            if len(dropped_col) > 0:
                for col in dropped_col:
                    values = []
                    data4.reset_index(inplace=True)
                    data4.drop(columns="index", inplace=True)
                    for idx, value in enumerate(data4[col]):
                        value = str(value).replace("P", "")
                        value = value.replace("B", "")
                        value = value.replace("p", "")
                        value = value.replace("b", "")
                        if value.strip() == "" or value.strip() == "nan":
                            values.append(np.nan)
                        else:
                            values.append(float(value))
                    data4[col + "_poor"] = values  # 只能给新列赋值列表，不能赋值Series，原因未知
                data5: pd.DataFrame = data4.groupby(time_col).mean()  # groupby会自动将time_col设置为行标题

        except ValueError:
            print(f"base.py DCS导出文件中存在非数据的列，请检查：{dropped_col}")
    else:
        data4 = pd.concat([data1, data2], axis=0)  # 看起来是按行合并，实际上结合groupby方法同时实现了按列和按行
        return data4, []  # 这里的data4不能reset_index()

    return data5.reset_index(), list(dropped_col)


def add_sep_to_csv(file, sep=",", to_file=None, encoding="utf-8", delete_quote=False):
    """
    向csv文件中的每一行按需添加分隔符，使得每一行的元素个数相同，便于pandas读取。
    会自动合并以双引号括起来的跨行的元素所在的行
    -----------------------

    :param file:
    :param sep:
    :param to_file: 输出到新文件，为None则覆盖源文件
    :param encoding: 文件的编码方式
    :param delete_quote: 是否删除原文件中的双引号，因为有些软件生成的csv文件，会使用双引号将元素括起来，但双引号跨行时会导致pd.read_csv
    方法报错，删除后该方法会将每行单独处理，以使pandas可以正常读取。使用时需要注意，该参数为True时，不会区分双引号是元素的实际内容还是边界标识符，
    只要遇到双引号就会删除。
    :return: 返回修改后的文件

    -----------------------

    """
    if sep is None:
        sep = ","
    n = 0
    quoted = False
    if file[-3:] == "txt":
        temp = 0
        number_of_lines = 0
        with open(file, "r", encoding=encoding) as f:
            for line in f:
                number_of_lines = number_of_lines + 1
                if '"' in line:
                    temp = temp + 1
        if temp / number_of_lines > 0.5 and number_of_lines > 10:  # 有些数据区元素以双引号引起来的文件，前面有几行说明并不使用双引号
            quoted = True

    # ------------------------ 合并元素跨行的行，以双引号为元素边界标记 -------------------------------------
    lines = []
    flag = False
    with open(file, "r", encoding=encoding) as f:
        temp_line = ""
        for line in f:
            if temp_line == "" and complete_line([line]):
                lines.append(line)
            else:
                flag = True
                temp_line = temp_line + line.rstrip() + " "
                if complete_line(temp_line):
                    lines.append(temp_line + os.linesep)
                    temp_line = ""
    if flag:
        file = to_file or file
        with open(file, mode="w", encoding=encoding) as f:
            f.writelines(lines)
    # ------------------------ 合并元素跨行的行，以双引号为元素边界标记 -------------------------------------
    # ------------------------将"\s+"的分隔符替换为"\t"-------------------------------------
    if sep == r"\s+" and not quoted:  # 当文件以多个空白字符分割的，替换多个空白字符为\t
        lines = []
        with open(file, "r", encoding=encoding) as f:
            for line in f:
                line = line.rstrip()  # 左边的多个空格视作一个分隔符，最右边的删除
                line = re.sub(r'(\s{2,})(\S+)', r"\t\2", line)  # 将左边的多个空白字符替换为一个分隔符
                if line == "":
                    continue
                lines.append(line + os.linesep)
        file = to_file or file
        with open(file, mode="w", encoding=encoding) as f:
            f.writelines(lines)
    elif sep == "\\s+" and quoted:  # 处理元素被双引号括起来的txt文件
        lines = []
        with open(file, "r", encoding=encoding) as f:
            for line in f:
                line = line.rstrip()
                line = re.sub(r'(\s+)("[^"]*")', r"\t\2", line)
                if line == "":
                    continue
                lines.append(line + os.linesep)
        file = to_file or file
        with open(file, mode="w", encoding=encoding) as f:
            f.writelines(lines)
    # ------------------------将"\s+"的分隔符替换为"\t"-------------------------------------

    # ------------------------ 去掉行中的双引号 -------------------------------------
    lines = []
    if delete_quote:  # 如果分隔符是逗号，则双引号可以去掉，否则单独出现的双引号会导致pd.read_csv(sep=",")方法出错，如dcs2.csv文件
        with open(file, "r", encoding=encoding) as f:
            for line in f:
                line = line.replace('"', "")
                lines.append(line)
        file = to_file or file
        with open(file, mode="w", encoding=encoding) as f:
            f.writelines(lines)
    # ------------------------ 去掉行中的双引号 -------------------------------------
    if sep == r"\s+":  # .csv格式文件不会满足该条件
        sep = "\t"
    with open(file, "r", encoding=encoding) as f:
        for line in f:
            line = line.strip()
            m = line.count(sep)
            n = m if m > n else n

    lines = []
    with open(file, "r", encoding=encoding) as f:
        for line in f:
            if line.strip() == "":
                continue
            m = line.count(sep)
            line = list(line.rstrip())  # 因为一行可以是以空白字符开始的分隔符，因此不能删除左边的空白字符
            line.extend(sep * (n - m))
            line = "".join(line)
            line = line + "\n"  # 貌似os.linesep 方法会换两行，因此这里不需要换行符
            lines.append(line)
    file = to_file or file
    with open(file, mode="w", encoding=encoding) as f:
        f.writelines(lines)
    return file


def set_dataframe_header(df):
    """
    重置dataframe的表头

    :param df:
    :return:
    """
    arr = df.values
    if len(arr) == 0:
        print("给定的DataFrame对象没有任何数据，无法设置表头")
        return df
    new_df = pd.DataFrame(arr[1:, 1:], index=arr[1:, 0], columns=arr[0, 1:])
    new_df.index.title = arr[0, 0]
    return new_df


def is_contain_chinese(check_str):
    """
    判断字符串中是否包含中文
    :param check_str: {str} 需要检测的字符串
    :return: {bool} 包含返回True， 不包含返回False
    """
    for ch in check_str:
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
    return False


def import_module(file_path):
    """
    根据<module>.py的绝对路径导入模块，返回导入的模块

    :param file_path:
    :return:
    """
    import importlib.util
    module_name = Path(file_path).stem
    module_spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return module


def kill_process(name_or_pid):
    """
    结束某进程

    :param name_or_pid: 进程名
    :return:
    """
    if isinstance(name_or_pid, str):
        import psutil
        pids = psutil.pids()
        for pid in pids:
            p = psutil.Process(pid)
            # get process name according to pid
            process_name = p.name()
            if name_or_pid == process_name:
                print("kill specific process: name(%s)-pid(%s)" % (process_name, pid))
                os.popen('taskkill.exe /pid:' + str(p.pid))
    else:
        if name_or_pid == 0:
            return
        print(f"kill specific process: pid({name_or_pid})")
        os.popen('taskkill.exe /pid:' + str(name_or_pid))


def get_clipboard():
    """
    获取操作系统剪切板中的内容

    :return:
    """
    import pyperclip
    content = pyperclip.paste()
    return content


def clipboard_to_dataframe():
    """
    获取剪切板内容，并转为DataFrame
        '	DCS1.12PAB10CT105
    描述:	凝汽器循环水出口A侧温度
    平均值	30.429377
    最小值	20.430946
    最大值	42.50288
    '

    :return:
    """
    content: str = get_clipboard()
    # content = content[1:-1]  # 前后各去掉一个单引号
    lines = content.split("\r\n")
    data = []
    for line in lines:
        cell = line.split("\t")
        data.append(cell)
    res = pd.DataFrame(data=data)
    res.dropna(how='any', axis=0, inplace=True)
    return res


def sound_beep(频率=500, 持续时间=1000, 间隔=1000, 次数=1):
    """
    使电脑发出提示声音

    :param 频率:
    :param 持续时间: 单位ms
    :param 间隔: 时间，单位ms
    :param 次数:
    :return:
    """
    import winsound
    for i in range(次数):
        winsound.Beep(频率, 持续时间)
        time.sleep(int(间隔 / 1000))


def yield_every_day(year, month=None):
    """
    逐步返回指定年或指定月的每一天，自动判断2月29日是否存在。

    :param year:
    :param month:
    :return:
    """
    import datetime
    if month is None:
        start_day = datetime.datetime(year=year, month=1, day=1)
    else:
        start_day = datetime.datetime(year=year, month=month, day=1)

    all_days = [start_day]
    delta_time = datetime.timedelta(days=1)
    cur_time = copy.deepcopy(start_day)
    if month is None:
        for i in range(370):
            cur_time = cur_time + delta_time
            if cur_time.year == start_day.year:
                all_days.append(cur_time)
    else:
        for i in range(31):
            cur_time = cur_time + delta_time
            if cur_time.month == start_day.month:
                all_days.append(cur_time)
    return all_days


def cal_cumulative_value(df: pd.DataFrame = None, titles: list | str | None = None,
                         start_time=None, end_time=None,
                         ) -> float | pd.Series | None:
    """
    计算某个参数的时间累积值，如果传入的是df，则df中必须有时间列。
    需要注意的时，累积值是按秒积分计算的。因此，传入参数和累积值单位的对应关系为：kg/s -> kg;  kW -> kJ; MW -> MJ;

    :param df:
    :param titles: 使用df计算时，需要计算累积值的变量的名称。对应df中的列标题
    :return:
    """
    time_col = get_datetime_col_of_dataframe(df)
    df = df.copy()
    if start_time is not None and end_time is not None:
        df = cut_time_period_of_dataframe(df, start_time, end_time, time_col_idx=time_col)
    df.set_index(time_col, inplace=True)
    _last_time = None
    _last_val = None
    if titles is None:
        return None
    elif not isinstance(titles, list):
        titles = [titles]
    res = [0] * len(titles)  # 初始化计算结果为0
    for idx, row in df.iterrows():  # d
        _cur_time: pd.Timestamp = idx
        _cur_val = row[titles]
        if _last_time is None:
            _last_time = _cur_time
            _last_val = _cur_val
        else:
            delta_time = (_cur_time - _last_time).seconds  # 单位转换为秒
            res = res + delta_time * (_cur_val + _last_val) / 2
            _last_time = _cur_time
            _last_val = _cur_val

    if len(titles) == 1:
        res = res.values[0]
    return res


def dynamic_for(data, cur_y_idx=0, lst_rst=[], lst_tmp=[]):
    """
    动态for循环，根据data中的参数个数嵌套for循环的层数，例如：
    data = [
        [1,2,3],
        [2,3]
    ]
    则以下代码是等价的：
    代码1：
    for _ in dynamic(data):
        i,j = _
    代码2：
    for i in [1,2,3]:
        for j in [2,3]:
    但代码1的写法在data在第一个维度的长度增加时，for循环仍为1层，而代码2的写法就需要动态嵌套
    """
    max_y_idx = len(data) - 1  # 获取Y 轴最大索引值
    for x_idx in range(len(data[cur_y_idx])):  # 遍历当前层的X 轴
        lst_tmp.append(data[cur_y_idx][x_idx])  # 将当前层X 轴的元素追加到lst_tmp 中
        if cur_y_idx == max_y_idx:  # 如果当前层是最底层则将lst_tmp 作为元素追加到lst_rst 中
            lst_rst.append([*lst_tmp])
        else:  # 如果当前还不是最底层则Y 轴+1 继续往下递归，所以递归最大层数就是Y 轴的最大值
            # lst_rst 和lst_tmp 的地址也传到下次递归中，这样不论在哪一层中修改的都是同一个list 对象
            dynamic_for(data, cur_y_idx + 1, lst_rst, lst_tmp)
        lst_tmp.pop()  # 在本次循环最后，不管是递归回来的，还是最底层循环的，都要将lst_tmp 最后一个元素移除
    return lst_rst


def get_relative_path(js_file, html_file):
    """
    获取js文件相对html的相对路径字符串，用以在html中引入js文件时使用
    """
    path1 = os.path.abspath(js_file)
    path2 = os.path.abspath(html_file)
    res = os.path.relpath(path1, path2)
    return res


def is_file_locked(file_path):
    """
    判断文件是否占用或锁定
    """
    try:
        with open(file_path, 'w'):
            return False
    except IOError:
        return True


def unlock_file(file_path):
    if is_file_locked(file_path):
        with open(file_path, 'r') as file:
            file.close()
        file = os.open(file_path, os.O_RDONLY)
        os.close(file)


def str2ascii(code):
    """
    将字符串转换成ascii码的列表
    """
    res = []
    for i in code:
        res.append(ord(i))
    return res


def encrypt(username: str, passwd: str):
    """
    加密用户对应的密码，密码不超过30个字符，最大30个字符
    """
    # 将用户名加密为32位的md5码
    user_code = md5(username).lower()

    # 将密码补齐30个字符
    length = len(passwd)
    makeup = 30 - length
    passwd = passwd + ''.join(['A'] * makeup)
    pass_code = f"{passwd}{length:02}"

    # 将用户名和密码都转换为ascii码
    user_code1 = str2ascii(user_code)
    pass_code1 = str2ascii(pass_code)

    # 将二者的ascii码求和
    add = []
    for i, j in zip(user_code1, pass_code1):
        add.append(f"{(i + j):03}")

    # 将求和结果拼接起来
    res = "".join(add)
    return res


def decrypt(username: str, crypt_code: str):
    """
    解密
    """
    # 将用户名加密为32位的md5码后转换成ascii码
    user_code = md5(username)
    user_code1 = str2ascii(user_code)

    # 将密文分割为32份
    pass_code1 = "".join([chr(int(crypt_code[i * 3:i * 3 + 3]) - user_code1[i]) for i in range(32)])
    length = int(pass_code1[-2:])
    return pass_code1[:length]


def md5(code):
    """
    返回字符串的32位md5加密结果
    """
    import hashlib
    m = hashlib.md5()
    m.update(code.encode("utf8"))
    return m.hexdigest()


if __name__ == "__main__":
    df = pd.read_excel(r"C:\Users\YangKe\PycharmProjects\lib4python\yangke\sis\历史数据库.xlsx")
    总发电量 = cal_cumulative_value(df, ["全厂总功率"])
    logger.debug("x")
