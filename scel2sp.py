import os
import struct
import sys

from pypinyin.style._utils import get_initials, get_finals


def read_utf16_str(f, offset=-1, len=2):
    if offset >= 0:
        f.seek(offset)
    string = f.read(len)
    return string.decode('UTF-16LE')


def read_uint16(f):
    return struct.unpack('<H', f.read(2))[0]


def get_hz_offset(f):
    mask = f.read(128)[4]
    if mask == 0x44:
        return 0x2628
    elif mask == 0x45:
        return 0x26c4
    else:
        print("不支持的文件类型(无法获取汉语词组的偏移量)")
        sys.exit(1)


def get_py_map(f):
    py_map = {}
    f.seek(0x1540 + 4)

    while True:
        py_idx = read_uint16(f)
        py_len = read_uint16(f)
        py_str = read_utf16_str(f, -1, py_len)

        if py_idx not in py_map:
            py_map[py_idx] = py_str

        # 如果拼音为 zuo，说明是最后一个了
        if py_str == 'zuo':
            break
    return py_map


def get_records(f, file_size, hz_offset, py_map):
    f.seek(hz_offset)
    records = []
    while f.tell() != file_size:
        word_count = read_uint16(f)
        py_idx_count = int(read_uint16(f) / 2)

        py_set = []
        for i in range(py_idx_count):
            py_idx = read_uint16(f)
            if (py_map.get(py_idx, None) == None):
                return records
            py_set.append(py_map[py_idx])
        py_str = " ".join(py_set)

        for i in range(word_count):
            word_len = read_uint16(f)
            word_str = read_utf16_str(f, -1, word_len)

            # 跳过 ext_len 和 ext 共 12 个字节
            f.read(12)
            records.append((py_str, word_str))
    return records


def get_dict_meta(f):
    title = read_utf16_str(f, 0x130, 0x338 - 0x130).rstrip('\0')
    category = read_utf16_str(f, 0x338, 0x540 - 0x338).rstrip('\0')
    desc = read_utf16_str(f, 0x540, 0xd40 - 0x540).rstrip('\0')
    samples = read_utf16_str(f, 0xd40, 0x1540 - 0xd40).rstrip('\0')
    return title, category, desc, samples


def get_words_from_scel(scel_file_path):
    with open(scel_file_path, 'rb') as scel_file:
        hz_offset = get_hz_offset(scel_file)

        (title, category, desc, samples) = get_dict_meta(scel_file)
        print("title: %s\ncategory: %s\ndesc: %s\nsamples: %s" % (title, category, desc, samples))

        py_map = get_py_map(scel_file)

        file_size = os.path.getsize(scel_file_path)
        words = get_records(scel_file, file_size, hz_offset, py_map)
        return words


def save(records, fout):
    records_translated = list(map(lambda x: "%s\t%s" % (x[1], x[0]), records))
    fout.write("\n".join(records_translated))


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


def convert_double(record_dict, type_folder):
    initials_dict = create_dict(os.path.join('./double', type_folder, 'initials.txt'))
    finals1_dict = create_dict(os.path.join('./double', type_folder, 'finals1.txt'))
    finals2_dict = create_dict(os.path.join('./double', type_folder, 'finals2.txt'))

    results = {}
    for cn, py_list in record_dict.items():
        words = []
        for py in py_list.split(' '):
            word_initials = get_initials(py, False)
            word_finals = get_finals(py, False)
            if word_initials == '':
                words.append(finals2_dict[word_finals])
            else:
                words.append(initials_dict[word_initials] + finals1_dict[word_finals])
        results[cn] = ''.join(words)

    return results


def convert_dict(record_dict, double_type, out_format):
    '''
    转换成指定格式的词库
    :param record_dict: 词典 dict
    :param fout: 输入文件
    :param double_type: 双拼类型
    :param out_format: 输出格式
    :return:
    '''
    fout = out_format + '.txt'
    py_dict = record_dict
    if double_type is not None:
        py_dict = convert_double(record_dict, double_type)

    if out_format == 'gboard':
        with open(os.path.join("./out", fout), "w", encoding='utf-8') as dictfout:
            dictfout.write('# Gboard Dictionary version:1\n')
            dictfout.write('# From OS\n')
            for cn, py in py_dict.items():
                dictfout.write("%s\t%s\tzh-CN\n" % (py, cn))


def main():
    scel_files = list(filter(lambda x: x.endswith('.scel'), os.listdir('./scel')))
    scel_names = list(map(lambda x: x[:-5], scel_files))

    if not os.path.exists("./out"):
        os.mkdir("./out")

    dict_file = "luna_pinyin.sogou.dict.yaml"
    all_records = []  # 全量词库 list

    for scel_file in scel_files:
        scel_file_path = os.path.join("./scel", scel_file)
        records = get_words_from_scel(scel_file_path)
        print("%s: %s 个词" % (scel_file, len(records)))

        with open(os.path.join("./out", scel_file.replace(".scel", ".txt")), "w") as fout:
            save(records, fout)
            all_records.extend(records)
        print("-" * 80)

    record_dict = {item[1]: item[0] for item in all_records}  # 全量词库 dict
    print("合并后 %s 个词" % (len(record_dict)))

    convert_dict(record_dict, 'xiaohe', 'gboard')


if __name__ == '__main__':
    main()
