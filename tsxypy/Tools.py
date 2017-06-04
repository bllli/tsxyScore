# -*- coding: utf-8 -*-
# 为了使实现主要功能的文件更加清爽, 特将几个不涉及对象的工具函数单独提出
import pickle
import requests
from datetime import date
from tsxypy.Config import Config
from tsxypy.Exception import WrongScheduleException


def md5password(password, rand_number):
    """
    获取经password/验证码混合加密所得的password
    该”加密算法“来自官网登录页的JS脚本
    ###感谢师兄 旺哥将其翻译成了py版本###
        我以为js加法是16进制直接相加- -
        害得我在py里把两个16进制的转成10进制相加后再转成16进制- -
        马丹原来加号就是连接字符串啊- -
    :param password: 用户密码
    :param rand_number: 验证码
    :return: 登陆所需的已加密密码
    """
    def md5_encode(string):
        import hashlib
        m = hashlib.md5(string.encode(encoding='utf-8'))
        return m.hexdigest()

    password = md5_encode(md5_encode(password) + md5_encode(rand_number))
    return password


def rand_ok(rand_text):
    """
    确认图像识别所得验证码为四位数字
    如果为四位数字 则说明验证码很大几率是正确的
    :param rand_text: 需要识别的验证码字符串
    :return: 是否为四位数字
    """
    rep = {'O': '0', 'C': '0', 'I': '1', 'J': '1', 'L': '1', 'Z': '2', 'S': '8',
           'o': '0', 'c': '0', 'i': '1', 'j': '1', 'l': '1', 'z': '2', 's': '8',
           ' ': ''}
    for litter in rep:
        rand_text = rand_text.replace(litter, rep[litter])
    if len(rand_text) != 4:
        return False
    try:
        num = int(rand_text)
    except ValueError:
        return False
    return True if 1000 < num < 9999 else False


def save_cookies(cookies):
    with open(Config.cookies_file, 'wb') as f:
        pickle.dump(requests.utils.dict_from_cookiejar(cookies), f)


def load_cookies():
    try:
        with open(Config.cookies_file, 'rb') as f:
            cookies = requests.utils.cookiejar_from_dict(pickle.load(f))
    except (IOError, ValueError):
        return None
    return cookies


def week_info_to_week_list(week_info, parity):
    """
    那几周上课
    :param week_info: 上课周次信息
    :param parity: 单双周
    逗号分隔
    横线指[A-B]
    :return:
    """
    if week_info is None:
        return []
    week_info = week_info.strip(u"周").strip(u'[').strip(u']')
    week = []
    for one in week_info.split(u','):
        if '-' in one:
            range_param = one.split(u'-')
            for a in range(int(range_param[0]), int(range_param[1]) + 1):
                week.append(a)
        else:
            week.append(int(one))
    if parity:
        p = 0 if parity == u'双周' else 1
        for w in week:
            if w % 2 != p:
                week.remove(w)
    return week


def translate(name):
    d = {
        u'毛泽东思想和中国特色社会主义理论体系概论': u'毛概',
        u'数字电路与逻辑设计': u'数电',
    }
    for key in d:
        if key in name:
            return d[key]
    return None


def this_school_year():
    today = date.today()
    return today.year if today.month >= 9 else today.year - 1


def this_semester():
    """
    钦定一年的9月前未下半学期, 9月后为上半学期
    :return: '1':下学期, '0':上学期
    """
    today = date.today()
    return 1 if today.month < 9 else 0
