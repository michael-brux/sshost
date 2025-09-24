#!/usr/bin/env python3
import shutil
import subprocess

def check_command(cmd, version_arg='-V', print_output=True):
    path = shutil.which(cmd)
    if path:
        try:
            # ssh uses -V, ssh-keygen uses -V (newer) or -v (older)
            result = subprocess.run([cmd, version_arg], capture_output=True, text=True)
            output = result.stderr if result.stderr else result.stdout
            print(f"{cmd} found: {path}")
            if print_output:
                print(f"{cmd} version: {output.strip()}")
        except Exception as e:
            print(f"Error running {cmd}: {e}")
    else:
        print(f"{cmd} not found in PATH.\n")

check_command('ssh')
check_command('ssh-keygen', print_output=False)
check_command('python', '--version')