import os

from dict_writter import write_dict
from pinyin_tools import convert_double, get_pinyin
from scel_tools import get_records_from_scel
import re


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


def load_custom_dicts():
    all_records = []
    custom_files = list(filter(lambda x: x.endswith('.txt'), os.listdir('./im_dicts/custom')))
    for custom_file in custom_files:
        custom_file_path = os.path.join("./im_dicts/custom", custom_file)
        records = []
        with open(custom_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            lines = list(map(lambda x: x.strip(), lines))
            lines = list(filter(lambda x: x != '', lines))
            lines = list(filter(lambda x: not x.startswith('#'), lines))
            lines = list(map(lambda x: x.split('|'), lines))

            for line in lines:
                if len(line) == 1:
                    # 只写了中文, 没写拼音
                    py_list = get_pinyin(line[0])
                    for py in py_list:
                        records.append((py, line[0]))
                else:
                    # 写了中文和拼音
                    records.append((line[1], line[0]))
        all_records.extend(records)
        print("custom 词库 [%s]: %s 个词" % (custom_file, len(records)))
    return all_records


def load_secl_dicts():
    all_records = []
    scel_files = list(filter(lambda x: x.endswith('.scel'), os.listdir('./im_dicts/scel')))
    for scel_file in scel_files:
        scel_file_path = os.path.join("./im_dicts/scel", scel_file)
        records = get_records_from_scel(scel_file_path)
        print("sougou 词库 [%s]: %s 个词" % (scel_file, len(records)))

        with open(os.path.join("./out", scel_file.replace(".scel", ".txt")), "w") as fout:
            save_text(records, fout)
            all_records.extend(records)
    return all_records


def load_tsinghua_dicts():
    all_records = []
    files = list(filter(lambda x: x.endswith('.txt'), os.listdir('./im_dicts/tsinghua')))
    for file in files:
        file_path = os.path.join("./im_dicts/tsinghua", file)
        records = []
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            lines = list(map(lambda x: x.strip(), lines))
            lines = list(filter(lambda x: x != '', lines))
            lines = list(filter(lambda x: not x.startswith('#'), lines))

            for line in lines:
                try:
                    (cn, score) = line.split()
                    if int(score) < 600 or len(cn) > 5:
                        continue
                    if re.search(r'[0-9a-zA-Z]', cn) is not None:
                        continue

                    py_list = get_pinyin(cn)
                    for py in py_list:
                        records.append((py, cn))
                except Exception as e:
                    print("skip: %s" % line)
                    continue

        all_records.extend(records)
        print("tsinghua 词库 [%s]: %s 个词" % (file, len(records)))
    return all_records


def load_baidu_export_dicts():
    all_records = []
    pattern = re.compile(r'(\S+)\(([\w|]+)\)')
    baidu_export_files = list(filter(lambda x: x.endswith('.txt'), os.listdir('./im_dicts/baidu_export')))
    for baidu_export_file in baidu_export_files:
        baidu_export_file_path = os.path.join("./im_dicts/baidu_export", baidu_export_file)
        records = []
        with open(baidu_export_file_path, 'rb') as f:
            lines = f.read().decode('utf-16-le').split('\n')
            lines = list(map(lambda x: x.strip(), lines))
            lines = list(filter(lambda x: x != '', lines))
            lines = list(filter(lambda x: not x.startswith('#'), lines))
            # skip 含有字母的行

            for line in lines:
                matches = pattern.findall(line)
                for match in matches:
                    cn = match[0]
                    py = match[1].replace('|', ' ')
                    if re.search(r'[0-9a-zA-Z]', cn) is not None:
                        print("skip: %s" % line)
                        continue
                    else:
                        records.append((py, cn))
        all_records.extend(records)
        print("baidu_export 词库 [%s]: %s 个词" % (baidu_export_file, len(records)))
    return all_records


def main():
    if not os.path.exists("./out"):
        os.mkdir("./out")
    if not os.path.exists("./im_dicts"):
        os.mkdir("./im_dicts")

    all_records = []  # 全量词库 list

    # load scel dicts
    scel_records = load_secl_dicts()
    print('>> found %s records in scel dicts' % len(scel_records))
    all_records.extend(scel_records)
    print("-" * 80)

    # load custom dicts
    custom_records = load_custom_dicts()
    print('>> found %s records in custom dicts' % len(custom_records))
    all_records.extend(custom_records)
    print("-" * 80)

    # load baidu im export dicts
    baidu_export_records = load_baidu_export_dicts()
    print('>> found %s records in baidu export dicts' % len(baidu_export_records))
    all_records.extend(baidu_export_records)
    print("-" * 80)

    record_dict = {item[1]: item[0] for item in all_records}  # 明确拼音的

    # load tsinghua dicts
    tsinghua_records = load_tsinghua_dicts()
    print('>> found %s records in tsinghua dicts' % len(tsinghua_records))
    # 根据已知的确认的拼音词库，过滤掉 tsinghua 词库中的重复词
    tsinghua_new_records = []
    for (py, cn) in tsinghua_records:
        if cn in record_dict:
            continue
        else:
            tsinghua_new_records.append((py, cn))
    print('>> found %s new records in tsinghua dicts' % len(tsinghua_new_records))
    all_records.extend(tsinghua_new_records)
    print("-" * 80)

    print(">> 合并后 %s 个词" % (len(all_records)))
    print("-" * 80)

    convert_dict(all_records, 'xiaohe', 'gboard')


if __name__ == '__main__':
    main()
