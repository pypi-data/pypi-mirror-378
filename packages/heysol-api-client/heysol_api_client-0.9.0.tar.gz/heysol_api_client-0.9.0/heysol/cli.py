#!/usr/bin/env python3
"""
CLI module for HeySol API client.
"""

import sys
from pathlib import Path

# Add parent directory to sys.path to import cli package
sys.path.insert(0, str(Path(__file__).parent.parent))

from cli import cli, main

__all__ = ["cli", "main"]

if __name__ == "__main__":
    main()
