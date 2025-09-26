import subprocess
from shutil import which
import socket
import subprocess
from shutil import which
import socket
from typing import Dict, List, Union, Literal
from sshost.get_config import get_ssh_config  # Import moved to module level

MAX_PARAMETERS = 256
CMDPATH = which('ssh-keyscan')


def run_keyscan(hosts: list | str, port: int = 22) -> subprocess.CompletedProcess:
    hosts = [hosts] if isinstance(hosts, str) else hosts
    cmd = [CMDPATH, '-p', str(port)]
    input_data = None

    if len(hosts) > MAX_PARAMETERS:
        cmd += ['-f', '-']
        input_data = "\n".join(hosts) + "\n"
    else:
        cmd += hosts

    return subprocess.run(cmd,
                          input=input_data,
                          text=True,
                          capture_output=True)


def resolve_hostname(hostname: str, ip_version: Literal['ipv4', 'ipv6', 'both'] = 'both') -> List[str]:
    """
    Resolve hostname to IP addresses based on the specified IP version.

    Args:
        hostname: The hostname to resolve
        ip_version: 'ipv4', 'ipv6', or 'both' to specify which IP version to resolve

    Returns:
        List of resolved IP addresses
    """
    addresses = []

    # Skip resolution if the input is already an IP address matching the requested version
    if ip_version in ['ipv4', 'both'] and is_valid_ipv4(hostname):
        return [hostname]
    if ip_version in ['ipv6', 'both'] and is_valid_ipv6(hostname):
        return [hostname]

    try:
        if ip_version in ['ipv4', 'both']:
            try:
                ipv4_info = socket.getaddrinfo(hostname, None, socket.AF_INET)
                for info in ipv4_info:
                    if info[4][0] not in addresses:
                        addresses.append(info[4][0])
            except socket.gaierror:
                pass  # No IPv4 address available

        if ip_version in ['ipv6', 'both']:
            try:
                ipv6_info = socket.getaddrinfo(hostname, None, socket.AF_INET6)
                for info in ipv6_info:
                    # Extract just the IPv6 address part from the address info tuple
                    ipv6_addr = info[4][0]
                    if ipv6_addr not in addresses:
                        addresses.append(ipv6_addr)
            except socket.gaierror:
                pass  # No IPv6 address available
    except Exception as e:
        # Handle any other exceptions during resolution
        print(f"Error resolving {hostname}: {e}")

    return addresses


def is_valid_ipv4(address: str) -> bool:
    """Check if the given string is a valid IPv4 address."""
    try:
        socket.inet_pton(socket.AF_INET, address)
        return True
    except (socket.error, ValueError):
        return False


def is_valid_ipv6(address: str) -> bool:
    """Check if the given string is a valid IPv6 address."""
    try:
        socket.inet_pton(socket.AF_INET6, address)
        return True
    except (socket.error, ValueError):
        return False


def keyscan(hosts: Union[str, List[str]],
            config_file: str = None,
            ip_version: Literal['ipv4', 'ipv6', 'both'] = 'both') -> List[Dict]:
    """
    Performs a higher level keyscan operation including hostname resolution and availability checking.

    Args:
        hosts: Hostname or list of hostnames to scan
        config_file: Optional path to SSH config file to get port information
        ip_version: Restrict to 'ipv4', 'ipv6', or 'both' (default)

    Returns:
        List of dictionaries with scan results, each containing:
        - hostname: Original hostname
        - ip: Resolved IP address (if successful)
        - port: Port used for the scan
        - status: "alive" or "unreachable"
    """
    # Remove the import from here since it's now at the module level

    if isinstance(hosts, str):
        hosts = [hosts]

    results = []

    for hostname in hosts:
        # Get port from config if available
        port = 22
        try:
            if config_file:
                config = get_ssh_config(hostname, config_file=config_file)
                if 'port' in config:
                    port = int(config['port'])
        except Exception as e:
            print(f"Error getting config for {hostname}: {e}")

        # Resolve hostname to IPs
        ip_addresses = resolve_hostname(hostname, ip_version)

        # If no IP addresses were resolved for the requested version,
        # skip this host (don't mark as unreachable)
        if not ip_addresses:
            continue

        for ip in ip_addresses:
            # Run keyscan on the resolved IP
            scan_result = run_keyscan(ip, port)

            result = {
                "hostname": hostname,
                "ip": ip,
                "port": port
            }

            # Check if scan was successful
            if scan_result.returncode == 0 and scan_result.stdout.strip():
                result["status"] = "alive"
            else:
                result["status"] = "unreachable"

            results.append(result)

    return results