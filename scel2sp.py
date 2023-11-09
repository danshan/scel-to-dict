import os
import struct
import sys


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


def save(records, f):
    records_translated = list(map(lambda x: "%s\t%s" % (
        x[1], x[0]), records))
    f.write("\n".join(records_translated))
    return records_translated


def main():
    scel_files = list(filter(lambda x: x.endswith('.scel'), os.listdir('./scel')))
    scel_names = list(map(lambda x: x[:-5], scel_files))

    if not os.path.exists("./out"):
        os.mkdir("./out")

    dict_file = "luna_pinyin.sogou.dict.yaml"
    dict_file_content = []

    for scel_file in scel_files:
        scel_file_path = os.path.join("./scel", scel_file)
        records = get_words_from_scel(scel_file_path)
        print("%s: %s 个词" % (scel_file, len(records)))

        with open(os.path.join("./out", scel_file.replace(".scel", ".txt")), "w") as fout:
            dict_file_content.extend(save(records, fout))
        print("-" * 80)

    print("合并后 %s: %s 个词" % (dict_file, len(dict_file_content) - 1))
    with open(os.path.join("./out", dict_file), "w") as dictfout:
        dictfout.write("\n".join(dict_file_content))


if __name__ == '__main__':
    main()
