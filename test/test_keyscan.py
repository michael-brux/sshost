import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sshost.keyscan import run_keyscan

def run_keyscan_simple(hosts='github.com'):
    return run_keyscan(hosts)

def run_public_keyscan():
    public_servers = Path(__file__).parent.parent / 'config' / 'public_servers.txt'
    with open(public_servers, 'r') as f:
        hosts = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        print(hosts)
        return run_keyscan(hosts)

#print(run_keyscan_simple())
returncode, output, error = run_public_keyscan()
print('Returncode:', returncode)
print('Output:')
for line in output:
    print(line)
print('Error:')
for line in error:
    print(line)