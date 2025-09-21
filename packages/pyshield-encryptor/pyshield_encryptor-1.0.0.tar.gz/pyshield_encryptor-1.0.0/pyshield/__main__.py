"""
PyShield CLI Entry Point
========================

Entry point for running PyShield as a module: python -m pyshield
"""

import sys
from .cli import main

if __name__ == '__main__':
    sys.exit(main())
