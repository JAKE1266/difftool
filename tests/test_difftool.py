"""差异计算、渲染与 CLI 端到端测试(输入→输出锚定)。"""

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from difftool import similarity, stats, structured_diff, unified_diff, word_diff
from difftool.cli import main
from difftool.core.render import render_side_by_side, render_stats
from cjktable import width as display_width

A_TEXT = "apple\nbanana\ncherry\ndate"
B_TEXT = "apple\nbanana\ngrape\ndate\nelderberry"


class UnifiedTest(unittest.TestCase):
    def test_anchor_output(self):
        lines = unified_diff(A_TEXT.split("\n"), B_TEXT.split("\n"), "a", "b", 1)
        self.assertEqual(lines[0], "--- a")
        self.assertEqual(lines[1], "+++ b")
        self.assertIn("@@", lines[2])
        self.assertIn("-cherry", lines)
        self.assertIn("+grape", lines)
        self.assertIn("+elderberry", lines)

    def test_context_zero(self):
        lines = unified_diff(["1", "2", "3", "4", "5"],
                             ["1", "9", "3", "4", "5"], context=0)
        changed = [l for l in lines
                   if l.startswith(("-", "+")) and not l.startswith(("---", "+++"))]
        self.assertEqual(changed, ["-2", "+9"])  # 无上下文行

    def test_identical_is_empty(self):
        self.assertEqual(unified_diff(["x"], ["x"]), [])


class StructuredTest(unittest.TestCase):
    def test_opcode_sequence(self):
        ops = structured_diff(["a", "b", "c"], ["a", "x", "c"])
        self.assertEqual([op["tag"] for op in ops], ["equal", "replace", "equal"])
        self.assertEqual(ops[1]["a_lines"], ["b"])
        self.assertEqual(ops[1]["b_lines"], ["x"])

    def test_insert_and_delete(self):
        ops = structured_diff(["a", "c"], ["a", "b", "c"])
        self.assertEqual([op["tag"] for op in ops], ["equal", "insert", "equal"])
        ops = structured_diff(["a", "b", "c"], ["a", "c"])
        self.assertEqual([op["tag"] for op in ops], ["equal", "delete", "equal"])

    def test_stats_counts(self):
        summary = stats(structured_diff(A_TEXT.split("\n"), B_TEXT.split("\n")))
        self.assertEqual(summary["equal_lines"], 3)     # apple/banana/date
        self.assertEqual(summary["replaced_lines"], 1)  # cherry → grape
        self.assertEqual(summary["inserted_lines"], 1)  # elderberry
        self.assertEqual(summary["changed_blocks"], 2)  # replace + insert 两个块


class SimilarityTest(unittest.TestCase):
    def test_identical_and_disjoint(self):
        self.assertEqual(similarity("a\nb", "a\nb"), 1.0)
        self.assertEqual(similarity("a", "b"), 0.0)

    def test_partial(self):
        value = similarity("a\nb\nc", "a\nx\nc")
        self.assertTrue(0.0 < value < 1.0)


class WordDiffTest(unittest.TestCase):
    def test_word_level(self):
        tokens = word_diff("the quick brown fox", "the quick red fox")
        marks = {token: mark for mark, token in tokens}
        self.assertEqual(marks.get("the"), "=")
        self.assertEqual(marks.get("brown"), "-")
        self.assertEqual(marks.get("red"), "+")
        self.assertEqual(marks.get("fox"), "=")

    def test_render_form(self):
        tokens = word_diff("the quick brown fox", "the quick red fox")
        rendered = " ".join(f"[-{t}]" if m == "-" else f"[+{t}]" if m == "+" else t
                            for m, t in tokens)
        self.assertEqual(rendered, "the quick [-brown] [+red] fox")


class RenderTest(unittest.TestCase):
    def test_side_by_side_alignment(self):
        ops = structured_diff(["apple", "banana"], ["apple", "香蕉很长很长"])
        out = render_side_by_side(ops, width=20)
        # 不变式:每行左列(含标记)显示宽度恒定 → 进度/右列起始位置对齐
        lines = out.splitlines()
        self.assertEqual(len({display_width(l.split("│")[0]) for l in lines[2:]}), 1)

    def test_stats_render(self):
        out = render_stats({"equal_lines": 3, "replaced_lines": 1,
                            "deleted_lines": 0, "inserted_lines": 1,
                            "changed_blocks": 1}, 0.75)
        self.assertIn("相似度    75.0%", out)
        self.assertIn("新增行    1", out)


class CliTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = Path(tmp.name)
        self.a = self.dir / "a.txt"
        self.b = self.dir / "b.txt"
        self.a.write_text(A_TEXT, encoding="utf-8")
        self.b.write_text(B_TEXT, encoding="utf-8")

    def run_cli(self, *args):
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = main(list(args))
        return code, stdout.getvalue(), stderr.getvalue()

    def test_unified_mode(self):
        code, out, _ = self.run_cli(str(self.a), str(self.b))
        self.assertEqual(code, 1)  # 有差异 → 退出码 1
        self.assertIn("a.txt", out)
        self.assertIn("-cherry", out)
        self.assertIn("+grape", out)

    def test_same_files_exit_zero(self):
        code, out, _ = self.run_cli(str(self.a), str(self.a))
        self.assertEqual(code, 0)
        self.assertIn("内容相同", out)

    def test_side_mode(self):
        code, out, _ = self.run_cli(str(self.a), str(self.b), "--mode", "side")
        self.assertEqual(code, 1)
        self.assertIn("│", out)
        self.assertIn("- cherry", out)
        self.assertIn("+ grape", out)

    def test_word_mode(self):
        left = self.dir / "w1.txt"
        right = self.dir / "w2.txt"
        left.write_text("the quick brown fox", encoding="utf-8")
        right.write_text("the quick red fox", encoding="utf-8")
        code, out, _ = self.run_cli(str(left), str(right), "--mode", "word")
        self.assertEqual(code, 1)
        self.assertIn("[-brown]", out)
        self.assertIn("[+red]", out)

    def test_stat_mode(self):
        code, out, _ = self.run_cli(str(self.a), str(self.b), "--stat")
        self.assertEqual(code, 1)
        self.assertIn("相似度", out)

    def test_json_output(self):
        code, out, _ = self.run_cli(str(self.a), str(self.b), "--json")
        self.assertEqual(code, 1)
        data = json.loads(out)
        self.assertFalse(data["same"])
        self.assertEqual(data["stats"]["replaced_lines"], 1)

    def test_identical_json(self):
        code, out, _ = self.run_cli(str(self.a), str(self.a), "--json")
        self.assertEqual(code, 0)
        self.assertTrue(json.loads(out)["same"])

    def test_binary_rejected(self):
        binary = self.dir / "bin.dat"
        binary.write_bytes(b"\x00\x01\x02binary")
        code, _, err = self.run_cli(str(binary), str(self.b))
        self.assertEqual(code, 2)
        self.assertIn("二进制", err)

    def test_missing_file_exit_code(self):
        code, _, err = self.run_cli(str(self.dir / "ghost.txt"), str(self.b))
        self.assertEqual(code, 2)
        self.assertIn("文件不存在", err)


if __name__ == "__main__":
    unittest.main()
