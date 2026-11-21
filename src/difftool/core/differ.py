"""差异计算(纯函数):unified / 结构化 / 词级 / 相似度 / 统计。"""

from __future__ import annotations

import difflib
import re


def split_lines(text: str) -> list:
    """按行拆分(兼容 \\r\\n),保留内容不含换行符。"""
    return text.replace("\r\n", "\n").replace("\r", "\n").split("\n")


def unified_diff(a_lines: list, b_lines: list, a_name: str = "a",
                 b_name: str = "b", context: int = 3) -> list:
    """标准 unified diff(行级),返回行列表;两序列相同时为空。"""
    return list(difflib.unified_diff(a_lines, b_lines, fromfile=a_name,
                                     tofile=b_name, n=context, lineterm=""))


def structured_diff(a_lines: list, b_lines: list) -> list:
    """SequenceMatcher 的 opcode 列表,每项::

        {"tag", "a_start", "a_end", "b_start", "b_end", "a_lines", "b_lines"}
    """
    matcher = difflib.SequenceMatcher(a=a_lines, b=b_lines)
    result = []
    for tag, a_start, a_end, b_start, b_end in matcher.get_opcodes():
        result.append({
            "tag": tag,
            "a_start": a_start, "a_end": a_end,
            "b_start": b_start, "b_end": b_end,
            "a_lines": a_lines[a_start:a_end],
            "b_lines": b_lines[b_start:b_end],
        })
    return result


def stats(operations: list) -> dict:
    """按 opcode 统计:相同行数、替换 / 删除 / 新增行数与变更块数。"""
    equal = replaced = deleted = inserted = blocks = 0
    for op in operations:
        a_count = op["a_end"] - op["a_start"]
        b_count = op["b_end"] - op["b_start"]
        if op["tag"] == "equal":
            equal += a_count
            continue
        blocks += 1
        if a_count and b_count:  # replace:重叠部分算替换,余量算删/增
            overlap = min(a_count, b_count)
            replaced += overlap
            deleted += a_count - overlap
            inserted += b_count - overlap
        elif a_count:
            deleted += a_count
        else:
            inserted += b_count
    return {"equal_lines": equal, "replaced_lines": replaced,
            "deleted_lines": deleted, "inserted_lines": inserted,
            "changed_blocks": blocks}


def similarity(a_text: str, b_text: str) -> float:
    """整体相似度 0.0-1.0(按行比较的 SequenceMatcher ratio)。"""
    return difflib.SequenceMatcher(a=split_lines(a_text),
                                   b=split_lines(b_text)).ratio()


def word_diff(a_text: str, b_text: str) -> list:
    """词级差异:返回 ``(标记, 词)`` 列表,标记为 ``"="`` / ``"-"`` / ``"+"``。

    词按空白与常见标点切分(保留作为独立 token)。
    """
    tokens_a = re.findall(r"\w+|[^\w\s]", a_text)
    tokens_b = re.findall(r"\w+|[^\w\s]", b_text)
    matcher = difflib.SequenceMatcher(a=tokens_a, b=tokens_b)
    result: list = []
    for tag, a_start, a_end, b_start, b_end in matcher.get_opcodes():
        for token in tokens_a[a_start:a_end]:
            result.append(("-" if tag != "equal" else "=", token))
        if tag != "equal":
            for token in tokens_b[b_start:b_end]:
                result.append(("+" if tag != "equal" else "=", token))
    return result
