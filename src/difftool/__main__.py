"""支持 ``python -m difftool`` 直接运行。"""

import sys

from difftool.cli import main

if __name__ == "__main__":
    sys.exit(main())
