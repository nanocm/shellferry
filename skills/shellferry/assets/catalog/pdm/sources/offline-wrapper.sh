#!/bin/sh
set -eu
python3 -c 'import sys,venv,ensurepip; assert sys.version_info[:2] == (3,10), "requires Python 3.10"'
python3 "$OFFLINE_ROOT/resources/installer.py" --version 2.29.7 --path "$OFFLINE_PREFIX" --skip-add-to-path
