# 更新日志

本项目遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 格式,
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [1.0.0] - 2026-11-21

### 新增
- 三种对比模式:unified(上下文行数可调)、并排(左旧右新,CJK 对齐)、
  词级(`[-旧] [+新]` 内联标记)
- 结构化 opcodes(JSON):tag / 起止 / 行内容,与 difflib 一致
- 统计与相似度:相同 / 替换 / 删除 / 新增行数、变更块数、SequenceMatcher ratio
- 二进制文件检测(含 NUL 字节即拒绝文本对比)
- 退出码约定:`0` 相同 · `1` 有差异 · `2` 用法/IO 错误
- 21 个单元测试(已知输入→输出锚定);GitHub Actions 三系统 × 三 Python 版本 CI
