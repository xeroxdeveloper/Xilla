#!/usr/bin/env python3
import sys
import os

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    os.system(f"{sys.executable} -m xilla")
