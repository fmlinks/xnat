#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""One-click entrypoint.

This repo keeps package sources under ./src.
To run without installing the package, we add ./src to sys.path here.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from xnat_shiny_uploader.main import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
