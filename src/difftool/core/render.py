"""渲染:并排对比与统计(对齐借助同系列微库 cjktable)。"""

from __future__ import annotations

from cjktable import pad, truncate

_COLUMN_WIDTH = 38


def render_side_by_side(operations: list, width: int = _COLUMN_WIDTH) -> str:
    """并排对比:左 = 旧文件,右 = 新文件;左列按显示宽度截断对齐。"""
    lines = [f"{pad('旧文件', width, 'right')}  │  {pad('新文件', width)}",
             "-" * width + "  ╪  " + "-" * width]
    for op in operations:
        a_lines, b_lines = list(op["a_lines"]), list(op["b_lines"])
        rows = max(len(a_lines), len(b_lines))
        for i in range(rows):
            left = a_lines[i] if i < len(a_lines) else ""
            right = b_lines[i] if i < len(b_lines) else ""
            if op["tag"] == "equal":
                mark_left, mark_right = "  ", "  "
            else:
                mark_left, mark_right = "- ", "+ "
            left_cell = mark_left + truncate(left, width - 2)
            right_cell = mark_right + truncate(right, width - 2)
            lines.append(pad(left_cell, width + 2) + "│  " + right_cell)
    return "\n".join(lines)


def render_stats(summary: dict, similarity: float) -> str:
    lines = [
        f"相似度    {similarity * 100:.1f}%",
        f"相同行    {summary['equal_lines']}",
        f"替换行    {summary['replaced_lines']}",
        f"删除行    {summary['deleted_lines']}",
        f"新增行    {summary['inserted_lines']}",
        f"变更块    {summary['changed_blocks']}",
    ]
    return "\n".join(lines)
