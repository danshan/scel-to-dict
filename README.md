# scel-to-dict

> sougou 细胞词库 (.scel) 转成其他格式的字典, 用于手工导入.

# 为什么会有这个 Repo?

最近换了 android 手机, 想找一个顺手的双拼输入法, 国内的输入法功能太臃肿, 也不想让收集过多的个人输入信息上云.
所以聚焦在了 gboard.
gboard 具有非常方便的双拼纠错能力. 但词库实在太拉, 研究了很多网友方案, 大部分都是使用 sougou 词库导入进去.
但 gboard 的词库用的是按键映射, 我自己用的又是小鹤双拼, 所以需要一个转换工具, 把全拼转成对应的双拼方案.

# 功能特性

* 支持 sougou 细胞词库 (.scel) 转成其他格式的字典, 用于手工导入;
* 支持自定义词库, 若出现多音字主动提示;
* 支持自定义双拼方案, 用于转换成对应的双拼方案;
* 导出时多个词库会合并成一个, 去重后输出最终一个文件;
* 

# 支持的格式

* 支持的输出格式有:

- [x] gboard (Google Keyboard)

* 目前支持的双拼方案有:

- [x] 小鹤双拼
- [ ] 微软双拼
- [ ] 自然码

理论上可以用户自己配置自己的双拼方案, 不限于市面上常见的各种双拼方案.

# 目录使用方式

```
├── README.md
├── double_pinyin  # 双拼方案配置文件 
│     └── xiaohe  # 小鹤双拼
│         ├── finals1.txt  # 韵母映射
│         ├── finals2.txt  # 零声母时的韵母映射
│         └── initials.txt  # 声母映射
├── out  # 词典文件的输出目录
│     ├── gboard_xiaohe.txt  # 生成的 gboard 词库文件
│     └── 开发大神专用词库【官方推荐】.txt  # scel 词库转换后的结果
├── im_dicts
│     ├── baidu_export
│     │       └── macmini-2021_2023_11_22.txt
│     ├── custom
│     │       ├── name.txt
│     │       └── words.txt
│     ├── scel
│     │       ├── README.md
│     │       ├── 三字成语【官方推荐】.scel
│     │       └── 鲁迅经典语【官方推荐】.scel
│     └── tsinghua
│             └── THUOCL_poem.txt
└── scel2dict.py  # 程序启动入口
```

# scel-2-dict.py 使用方式

安装好 python3 环境后, 需安装依赖:

```bash
python -m pip install pypinyin
```

然后到此文件夹运行：

```bash
python3 scel2dict.py
```

生成的文件放在 out 文件夹下.

```bash
➜   python3 scel2dict.py

title: 上海地名街道名
category: 道路交通地名
desc: 上海地名、街道名、主要建筑、公园、重要地点等，大家一起完善！
samples: 八号桥 巴林路 白城路 白渡桥 白龙港 白杨路
sougou 词库 [上海地名街道名.scel]: 21179 个词
--------------------------------------------------------------------------------
custom 词库 [name.txt]: 9 个词
--------------------------------------------------------------------------------
>> 合并后 23188 个词
```

# 如何添加更多词库

* sougou 细胞词库

sougou 词库可以从这里添加: https://pinyin.sogou.com/dict/

下载后的 .scel 文件, 放在 scel 文件夹下.

* 自定义词库
 
自定义词库, 以 utf-8 编码的 txt 文件放到 custom 目录下.

格式为: 一行一个词, 中文和拼音之间用 `|` 分隔, 拼音之间用 `空格` 分隔.

如果中文词语中不存在多音字, 可以不用写拼音. 

```
中国
美国
```

但如果存在多音字, 生成时会提示, 这时生成的词典可能拼音和期望不同.

```
单元格
```
```
# 生成时会提示
词语存在多音字, 建议手动指定: 单元格
custom 词库 [name.txt]: 10 个词
```

这时则建议写上对应的拼音:

```
单元格|dan yuan ge
```