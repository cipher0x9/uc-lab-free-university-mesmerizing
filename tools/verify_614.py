#!/usr/bin/env python3
"""Compatibility wrapper. The real command is tools/verify_campus.py."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

print("note: tools/verify_614.py is a compatibility wrapper for tools/verify_campus.py")
target = Path(__file__).resolve().parent / "verify_campus.py"
sys.argv[0] = str(target)
runpy.run_path(str(target), run_name="__main__")
