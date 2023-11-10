import os
import sys

from scel_tools import get_records_from_scel
from double_pinyin import convert_double
from dict_writter import write_dict

def save_text(records, fout):
    records_translated = list(map(lambda x: "%s\t%s" % (x[1], x[0]), records))
    fout.write("\n".join(records_translated))



def convert_dict(record_dict, double_pinyin_type, out_format):
    """
    转换成指定格式的词库
    :param record_dict: 词典 dict
    :param double_pinyin_type: 双拼类型
    :param out_format: 输出格式
    :return:
    """
    py_dict = record_dict
    if double_pinyin_type is not None:
        py_dict = convert_double(record_dict, double_pinyin_type)

    if out_format == 'gboard':
        write_dict(py_dict, './out', out_format, double_pinyin_type)


def main():
    scel_files = list(filter(lambda x: x.endswith('.scel'), os.listdir('./scel')))
    scel_names = list(map(lambda x: x[:-5], scel_files))

    if not os.path.exists("./out"):
        os.mkdir("./out")

    all_records = []  # 全量词库 list

    for scel_file in scel_files:
        scel_file_path = os.path.join("./scel", scel_file)
        records = get_records_from_scel(scel_file_path)
        print("%s: %s 个词" % (scel_file, len(records)))

        with open(os.path.join("./out", scel_file.replace(".scel", ".txt")), "w") as fout:
            save_text(records, fout)
            all_records.extend(records)
        print("-" * 80)

    record_dict = {item[1]: item[0] for item in all_records}  # 全量词库 dict
    print("合并后 %s 个词" % (len(record_dict)))

    convert_dict(record_dict, 'xiaohe', 'gboard')


if __name__ == '__main__':
    main()
