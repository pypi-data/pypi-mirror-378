if __name__ != '__main__': raise ImportError("__main__ not importable")

from sys import argv
from os import path
from typing import List

from . import run

run()