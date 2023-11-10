import os

from pypinyin.style._utils import get_initials, get_finals


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
    initials_dict = create_dict(os.path.join('./double_pinyin', double_pinyin_type, 'initials.txt'))
    finals1_dict = create_dict(os.path.join('./double_pinyin', double_pinyin_type, 'finals1.txt'))
    finals2_dict = create_dict(os.path.join('./double_pinyin', double_pinyin_type, 'finals2.txt'))

    results = {}
    for cn, py_list in record_dict.items():
        words = []
        for py in py_list.split(' '):
            word_initials = get_initials(py, False)
            word_finals = get_finals(py, False)
            if word_initials == '':
                # 零声母
                words.append(finals2_dict[word_finals])
            else:
                words.append(initials_dict[word_initials] + finals1_dict[word_finals])
        results[cn] = ''.join(words)

    return results
