"""difftool 命令行入口。

::

    difftool old.txt new.txt                       # unified diff
    difftool old.txt new.txt --mode side           # 并排对比
    difftool old.txt new.txt --mode word           # 词级内联差异
    difftool old.txt new.txt --stat --json
"""

from __future__ import annotations

import argparse
import json
import sys

from . import __version__
from .core.differ import (similarity, split_lines, stats, structured_diff,
                          unified_diff, word_diff)
from .core.render import render_side_by_side, render_stats

_BINARY_MARK = b"\x00"


def _read_text(path: str) -> str:
    from pathlib import Path

    file = Path(path)
    if not file.is_file():
        raise FileNotFoundError(f"文件不存在:{file}")
    data = file.read_bytes()
    if _BINARY_MARK in data[:4096]:
        raise ValueError(f"二进制文件不支持文本对比:{file}")
    return data.decode("utf-8-sig", errors="replace")


def cmd_diff(args) -> int:
    a_text = _read_text(args.a)
    b_text = _read_text(args.b)
    a_lines, b_lines = split_lines(a_text), split_lines(b_text)
    operations = structured_diff(a_lines, b_lines)
    summary = stats(operations)
    same = all(op["tag"] == "equal" for op in operations)

    if args.json:
        print(json.dumps({
            "same": same,
            "similarity": round(similarity(a_text, b_text), 6),
            "stats": summary,
            "operations": operations,
        }, ensure_ascii=False, indent=2))
        return 0 if same else 1

    if args.stat:
        print(render_stats(summary, similarity(a_text, b_text)))
        return 0 if same else 1

    if same:
        print("(两个文件内容相同)")
        return 0

    if args.mode == "unified":
        lines = unified_diff(a_lines, b_lines, a_name=args.a, b_name=args.b,
                             context=args.context)
        print("\n".join(lines) if lines else "(无差异)")
    elif args.mode == "side":
        print(render_side_by_side(operations, width=args.width))
    else:  # word
        tokens = word_diff(a_text, b_text)
        pieces = []
        for mark, token in tokens:
            if mark == "=":
                pieces.append(token)
            elif mark == "-":
                pieces.append(f"[-{token}]")
            else:
                pieces.append(f"[+{token}]")
        print(" ".join(pieces))
    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="difftool",
        description="difftool —— 零依赖的文本差异工具:unified / 并排 / 词级,基于标准库 difflib",
    )
    parser.add_argument("--version", action="version", version=f"difftool {__version__}")
    parser.add_argument("a", help="旧文件")
    parser.add_argument("b", help="新文件")
    parser.add_argument("-m", "--mode", choices=("unified", "side", "word"),
                        default="unified", help="对比模式(默认 unified)")
    parser.add_argument("-c", "--context", type=int, default=3,
                        help="unified 模式上下文行数(默认 3)")
    parser.add_argument("--width", type=int, default=38,
                        help="side 模式单列显示宽度(默认 38)")
    parser.add_argument("--stat", action="store_true", help="只输出相似度与行数统计")
    parser.add_argument("--json", action="store_true",
                        help="JSON 输出(opcodes / 统计 / 相似度)")
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.context < 0 or args.width < 8:
        print("错误:--context 不能为负,--width 至少为 8", file=sys.stderr)
        return 2
    try:
        return cmd_diff(args)
    except KeyboardInterrupt:
        print("\n已取消。")
        return 130
    except BrokenPipeError:
        return 0
    except (ValueError, TypeError, OSError) as exc:
        print(f"错误:{exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
