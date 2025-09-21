import os
import sys


def res_dir() -> str:
    return os.path.join(sys.prefix, "..", ".pypp", "resources")
