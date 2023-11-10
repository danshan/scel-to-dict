import os


def write_gboard(py_dict, out_folder, double_pinyin_type):
    filename = 'gboard' + ('_' + double_pinyin_type if double_pinyin_type is not None else '') + '.txt'
    with open(os.path.join(out_folder, filename), "w", encoding='utf-8') as dictfout:
        dictfout.write('# Gboard Dictionary version:1\n')
        dictfout.write('# From OS\n')
        for cn, py in py_dict.items():
            dictfout.write("%s\t%s\tzh-CN\n" % (py, cn))


def write_dict(py_dict, out_folder, out_format, double_pinyin_type):
    if out_format == 'gboard':
        write_gboard(py_dict, out_folder, double_pinyin_type)
