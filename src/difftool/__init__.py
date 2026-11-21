"""difftool —— 零依赖的文本差异命令行工具(标准库 difflib)。

::

    from difftool import similarity, structured_diff, unified_diff, word_diff

    print(similarity("hello world", "hello brave world"))
"""

from difftool.core.differ import (similarity, stats, structured_diff,
                                  unified_diff, word_diff)

__version__ = "1.0.0"

__all__ = ["similarity", "stats", "structured_diff", "unified_diff",
           "word_diff", "__version__"]
