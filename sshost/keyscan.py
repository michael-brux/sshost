import subprocess
from shutil import which

MAX_PARAMETERS = 256
CMDPATH = which('ssh-keyscan')

def run_keyscan(hosts, port=22, ipv6=None, ipv4=None):

    if isinstance(hosts, str):
        hosts = [hosts]

    cmd = [CMDPATH, '-p', str(port)]

    if ipv4:
        cmd.append('-4')
    if ipv6:
        cmd.append('-6')

    if len(hosts) > MAX_PARAMETERS:
        host_input = "\n".join(hosts) + "\n"
        cmd.extend(['-f', '-'])
        result = subprocess.run(cmd,
                                input=host_input,
                                text=True,
                                capture_output=True)
    else:
        cmd.extend(hosts)
        result = subprocess.run(cmd,
                                text=True,
                                capture_output=True)

    output = result.stdout.splitlines()
    error = result.stderr.splitlines()

    return result.returncode, output, error
