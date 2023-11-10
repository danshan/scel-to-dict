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
    hz_offset = get_hz_offset(f)
    py_map = get_py_map(f)

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
    '''
    获取词库元数据
    :param f:
    :return:
    '''
    title = read_utf16_str(f, 0x130, 0x338 - 0x130).rstrip('\0')
    category = read_utf16_str(f, 0x338, 0x540 - 0x338).rstrip('\0')
    desc = read_utf16_str(f, 0x540, 0xd40 - 0x540).rstrip('\0')
    samples = read_utf16_str(f, 0xd40, 0x1540 - 0xd40).rstrip('\0')
    return title, category, desc, samples
