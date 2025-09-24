import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sshost.get_config import get_ssh_config

def test_get_config():
    config_file = Path(__file__).parent.parent / 'config' / '443.github.config'
    config = get_ssh_config('443.github.com', config_file=config_file)
    assert config['port'] == '443'
    assert config['hostname'] == 'ssh.github.com'
    print("Test passed!")

test_get_config()