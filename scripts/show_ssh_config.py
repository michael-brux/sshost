#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
from shutil import which
from subprocess import run

HOME = Path.home()
CONFIG_DIR = HOME / '.ssh'
CONFIG_FILE = CONFIG_DIR / 'config'

print(f'Config file: {CONFIG_FILE}')
if not CONFIG_FILE.exists():
    print('Config file does not exist.')
    exit(0)

if input('show? (y/n) ') == 'y':
    less_path = which('less')
    if not less_path:
        less_path = which('more')
    if less_path:
        with open(CONFIG_FILE, 'r') as f:
            run([less_path], stdin=f, text=True)
    else:
        print('*** No pager found.')
        with open(CONFIG_FILE, 'r') as f:
            print(f.read())

input('Press Enter to exit.')