import os

from pypinyin import pinyin, Style
from pypinyin.style._utils import get_initials, get_finals
import itertools

_double_pinyin_dicts = {}


def get_double_pinyin_dict(double_pinyin_type):
    if not _double_pinyin_dicts.__contains__(double_pinyin_type):
        _double_pinyin_dicts[double_pinyin_type] = {
            'initials': create_dict(os.path.join('./double_pinyin', double_pinyin_type, 'initials.txt')),
            'finals1': create_dict(os.path.join('./double_pinyin', double_pinyin_type, 'finals1.txt')),
            'finals2': create_dict(os.path.join('./double_pinyin', double_pinyin_type, 'finals2.txt'))
        }
    return _double_pinyin_dicts[double_pinyin_type]


def create_dict(textfile):
    dict = {}
    with open(textfile, "r", encoding="utf-8") as file:
        for line in file:
            if line.strip().startswith('#'):
                continue
            (key, value) = line.split()
            dict[key] = value
    # print(dict)
    return dict


def convert_double(record_dict, double_pinyin_type):
    """
    转换成双拼词库
    :param record_dict:
    :param double_pinyin_type:
    :return:
    """
    double_pinyin_dict = get_double_pinyin_dict(double_pinyin_type)

    results = {}
    for (py_list, cn) in record_dict:
        words = []
        for py in py_list.split(' '):
            try:
                word_initials = get_initials(py, False)
                word_finals = get_finals(py, False)
                if word_initials == '':
                    # 零声母
                    words.append(double_pinyin_dict['finals2'][word_finals])
                else:
                    words.append(double_pinyin_dict['initials'][word_initials] + double_pinyin_dict['finals1'][word_finals])
            except KeyError:
                print("拼音转换失败: %s" % py)
                continue
        results[cn] = ''.join(words)

    return results


def get_pinyin(word):
    """
    获取单个词的拼音
    :param word:
    :return:
    """
    pinyin_list = pinyin(word, style=Style.NORMAL, strict=False, heteronym=True)
    multi_py = False
    for py in pinyin_list:
        if py.__len__() > 1:
            multi_py = True

    if multi_py:
#        print("词语存在多音字, 建议手动指定: %s" % word)
        all_py_list = list(itertools.product(*pinyin_list))
        results = []
        for py in all_py_list:
            results.append(' '.join(py))
        return results
    else:
        return [' '.join(list(map(lambda x: x[0], pinyin_list)))]
