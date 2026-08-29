"""Put the vendored trespass package on sys.path so its tests run in place."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
