"""Entry point for MCP Diagrams Server when run as a module"""

import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from .server import run_server


def main():
    """Main entry point for the CLI"""
    run_server()


if __name__ == "__main__":
    main()