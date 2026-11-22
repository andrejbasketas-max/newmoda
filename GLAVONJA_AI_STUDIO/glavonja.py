"""GLAVONJA AI STUDIO entry point:  python glavonja.py <command>   (see: python glavonja.py -h)"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from studio.cli import main  # noqa: E402

if __name__ == "__main__":
    main()
