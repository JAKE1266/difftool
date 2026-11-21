# difftool

> 零依赖的文本差异工具:unified / 并排 / 词级三种模式,相似度与统计一行看全。
> 标准库 `difflib` 封装,左列 CJK 对齐来自同系列微库 cjktable。

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Dependencies](https://img.shields.io/badge/dependencies-cjktable%20%28self--built%29-blue)
![Tests](https://img.shields.io/badge/tests-21%20passing-success)

## ✨ 特性

- 🧱 **三种模式**:unified(上下文行数可调)/ 并排(左旧右新)/ 词级(`[-旧] [+新]`)
- 📊 **相似度与统计**:相同/替换/删除/新增行数、变更块数、SequenceMatcher ratio
- 🈶 **中文友好**:并排左列按显示宽度截断对齐(全角 2 列)
- 🚫 **二进制检测**:含 NUL 字节即拒绝文本对比并说明
- 📤 **`--json`**:opcodes + 统计 + 相似度,结构化输出
- 🚦 **退出码约定**:`0` 相同 · `1` 有差异 · `2` 用法/IO 错误(脚本可直接判断)
- 🧪 **21 个单元测试**(已知输入→输出锚定);三系统 × 三 Python 版本 CI

## 📦 安装

```bash
git clone https://github.com/JAKE1266/difftool.git
cd difftool
python -m difftool --help      # 克隆即用

pip install .                  # 或安装为命令(获得 difftool 命令)
```

## 🚀 快速上手

```bash
difftool old.txt new.txt                    # unified diff
difftool old.txt new.txt --mode side        # 并排
difftool old.txt new.txt --mode word        # 词级内联
difftool old.txt new.txt --stat             # 相似度 + 行数统计
difftool old.txt new.txt --json             # 结构化输出
```

### 效果预览

```
$ difftool old.txt new.txt --mode side
                                旧文件  │  新文件
------------------------------  ╪  ------------------------------
  apple                         │    apple
  banana                        │    banana
- cherry                        │  + grape
  date                          │    date
-                               │  + elderberry

$ difftool old.txt new.txt --mode word
apple banana [-cherry] [+grape] date [+elderberry]
```

## ❓ 常见问题

**Q: 为什么「有差异」的退出码是 1?**
沿用 diff / git 的约定:0 = 相同,1 = 有差异,2 = 用法/IO 错误——脚本可以直接
用退出码分支,不需要解析输出。

**Q: 词级模式怎么切词?**
按空白与常见标点切 token;连续的删除/新增合并展示为 `[-旧] [+新]`。

**Q: 二进制文件怎么办?**
检测到 NUL 字节即视为二进制,拒绝文本对比并说明(退出码 2)。

**Q: 想发布到 PyPI?**
`difftool` 是占位名,发布前请在 `pyproject.toml` 换一个未被占用的名字。

## 📁 项目结构

```
difftool/
├── .github/workflows/ci.yml   # CI:三系统 × Python 3.9-3.13
├── src/difftool/
│   ├── core/
│   │   ├── differ.py          # unified / 结构化 / 词级 / 相似度 / 统计
│   │   └── render.py          # 并排渲染(排版来自 cjktable)
│   └── cli.py                 # 命令行入口
├── tests/                     # 21 个单元测试
└── pyproject.toml
```

## 🧪 开发与测试

```bash
PYTHONPATH="src;../cjktable/src" python -m unittest discover -s tests -v
```

## 🗺 路线图

- [ ] `--color` ANSI 高亮
- [ ] 目录级对比(多文件批量)
- [ ] 忽略空白/大小写选项

## 📄 许可证

[MIT](LICENSE) —— 可自由使用、修改与分发。

---

*同系列项目:[PyToolBox](https://github.com/JAKE1266/py-toolbox) · [CashBook](https://github.com/JAKE1266/cashbook) · [gitdash](https://github.com/JAKE1266/gitdash) · [DevBox](https://github.com/JAKE1266/devbox) · [csvq](https://github.com/JAKE1266/csvq) · [cjktable](https://github.com/JAKE1266/cjktable) · [duviz](https://github.com/JAKE1266/duviz) · [httpoke](https://github.com/JAKE1266/httpoke) · [mdown](https://github.com/JAKE1266/mdown) · [msite](https://github.com/JAKE1266/msite) · [crony](https://github.com/JAKE1266/crony) · [pomo](https://github.com/JAKE1266/pomo) · [termplot](https://github.com/JAKE1266/termplot) · [filewatch](https://github.com/JAKE1266/filewatch) · [packpeek](https://github.com/JAKE1266/packpeek) · [statline](https://github.com/JAKE1266/statline)*
