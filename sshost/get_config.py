import subprocess
from pathlib import Path
#import os

# no longer needed
# def get_null_file():
#    return 'NUL' if os.name == 'nt' else '/dev/null'

def normalize_config_file(config_file: str | Path | bool | None) -> str | None:
    if config_file is True:
        return None  # normalize True to None for default behavior
    elif config_file in [False, "", "/dev/null", "NUL", "none"]:
        return "none"  # special case for no config file
    elif isinstance(config_file, Path):
        return str(config_file)  # convert Path to str
    else:
        return config_file  # return as-is

def get_ssh_config(host, user=None, config_file: str | Path | bool = None):
    """
    Get SSH configuration for a given host and user using `ssh -G`.
    Returns a dict of config options.
    """
    config_file = normalize_config_file(config_file)
    cmd = ['ssh', '-G', host]
    if user:
        cmd += ['-l', user]

    # optional config_file parameter
    if config_file:
        cmd += ['-F', config_file]  # alternative per-user configuration file
    # the default is:
    #  ~/.ssh/config is the per-user configuration file
    #  /etc/ssh/ssh_config is the system-wide configuration file

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ssh -G failed: {result.stderr.strip()}")
    config = {}
    for line in result.stdout.splitlines():
        if line.strip():
            key, value = line.split(None, 1)
            config[key] = value
    return config




