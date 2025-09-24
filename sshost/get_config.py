import subprocess

def get_ssh_config(host, user=None, config_file=None):
    """
    Get SSH configuration for a given host and user using `ssh -G`.
    Returns a dict of config options.
    """
    cmd = ['ssh', '-G', host]
    if user:
        cmd += ['-l', user]
    if config_file:
        cmd += ['-F', config_file]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ssh -G failed: {result.stderr.strip()}")
    config = {}
    for line in result.stdout.splitlines():
        if line.strip():
            key, value = line.split(None, 1)
            config[key] = value
    return config

