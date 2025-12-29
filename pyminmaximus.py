#!/usr/bin/env python3
"""
PyMinMaximus Chess Engine
Main launcher script
"""

import sys
from uci import main as uci_main

if __name__ == "__main__":
    # Check for command line arguments
    if len(sys.argv) > 1:
        print(sys.argv)
        if sys.argv[1] == '--help' or sys.argv[1] == '-h':
            print("PyMinMaximus Chess Engine")
            print("Usage:")
            print("  python pyminmaximus.py           # Run in UCI mode")
            print("  python pyminmaximus.py --help    # Show this help")
            print("\nUCI mode is used by chess GUIs and tournament managers.")
            sys.exit(0)
    
    # Run in UCI mode
    uci_main()
