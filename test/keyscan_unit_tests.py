import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import socket
from sshost.keyscan import keyscan, resolve_hostname, is_valid_ipv4, is_valid_ipv6


class TestKeyscan(unittest.TestCase):
    """Test class for the higher level keyscan function."""

    @patch('sshost.keyscan.get_ssh_config')
    @patch('sshost.keyscan.run_keyscan')
    @patch('sshost.keyscan.resolve_hostname')
    def test_keyscan_with_config(self, mock_resolve, mock_run_keyscan, mock_get_config):
        # Setup mocks
        mock_get_config.return_value = {'port': '2222'}
        mock_resolve.return_value = ['192.168.1.1']
        
        # Mock successful keyscan
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = '192.168.1.1 ssh-rsa AAAAB3NzaC...'
        mock_run_keyscan.return_value = mock_result

        # Run keyscan with config
        result = keyscan('example.com', config_file='ssh_config')
        
        # Verify
        mock_get_config.assert_called_once_with('example.com', config_file='ssh_config')
        mock_resolve.assert_called_once_with('example.com', 'both')
        mock_run_keyscan.assert_called_once_with('192.168.1.1', 2222)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['hostname'], 'example.com')
        self.assertEqual(result[0]['ip'], '192.168.1.1')
        self.assertEqual(result[0]['port'], 2222)
        self.assertEqual(result[0]['status'], 'alive')

    @patch('sshost.keyscan.get_ssh_config')
    @patch('sshost.keyscan.run_keyscan')
    @patch('sshost.keyscan.resolve_hostname')
    def test_keyscan_unreachable(self, mock_resolve, mock_run_keyscan, mock_get_config):
        # Setup mocks
        mock_get_config.return_value = {'port': '22'}
        mock_resolve.return_value = ['192.168.1.2']
        
        # Mock failed keyscan
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ''
        mock_run_keyscan.return_value = mock_result

        # Run keyscan
        result = keyscan('unreachable.host', config_file='ssh_config')
        
        # Verify
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['status'], 'unreachable')

    @patch('sshost.keyscan.get_ssh_config')
    @patch('sshost.keyscan.run_keyscan')
    @patch('sshost.keyscan.resolve_hostname')
    def test_keyscan_multiple_hosts(self, mock_resolve, mock_run_keyscan, mock_get_config):
        # Setup mocks
        mock_get_config.side_effect = [{'port': '22'}, {'port': '2222'}]
        mock_resolve.side_effect = [['192.168.1.1'], ['192.168.1.2']]
        
        # Mock successful keyscan
        mock_result1 = MagicMock()
        mock_result1.returncode = 0
        mock_result1.stdout = '192.168.1.1 ssh-rsa AAAAB3NzaC...'
        
        mock_result2 = MagicMock()
        mock_result2.returncode = 0
        mock_result2.stdout = '192.168.1.2 ssh-rsa AAAAB3NzaC...'
        
        mock_run_keyscan.side_effect = [mock_result1, mock_result2]

        # Run keyscan with multiple hosts
        result = keyscan(['host1.example.com', 'host2.example.com'], config_file='ssh_config')
        
        # Verify
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['hostname'], 'host1.example.com')
        self.assertEqual(result[1]['hostname'], 'host2.example.com')

    @patch('socket.getaddrinfo')
    def test_resolve_hostname_ipv4_only(self, mock_getaddrinfo):
        # Setup mock for getaddrinfo
        mock_getaddrinfo.side_effect = [
            [(socket.AF_INET, socket.SOCK_STREAM, 6, '', ('192.168.1.1', 0))],  # IPv4 response
            socket.gaierror  # IPv6 would raise error
        ]
        
        # Test resolving to IPv4 only
        result = resolve_hostname('example.com', 'ipv4')
        self.assertEqual(result, ['192.168.1.1'])
        
        # Try with 'both' - should still get only IPv4
        mock_getaddrinfo.reset_mock()
        mock_getaddrinfo.side_effect = [
            [(socket.AF_INET, socket.SOCK_STREAM, 6, '', ('192.168.1.1', 0))],  # IPv4 response
            socket.gaierror  # IPv6 would raise error
        ]
        
        result = resolve_hostname('example.com', 'both')
        self.assertEqual(result, ['192.168.1.1'])

    @patch('socket.getaddrinfo')
    def test_resolve_hostname_ipv6_only(self, mock_getaddrinfo):
        # Check if IPv6 is available in the current environment
        has_ipv6 = False
        try:
            socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
            has_ipv6 = True
        except (socket.error, OSError):
            self.skipTest("IPv6 not available in the current environment")

        # Only run the test if IPv6 is available
        if has_ipv6:
            # Setup mock for getaddrinfo
            mock_getaddrinfo.side_effect = [
                socket.gaierror,  # IPv4 would raise error
                [(socket.AF_INET6, socket.SOCK_STREAM, 6, '', ('2001:db8::1', 0, 0, 0))]  # IPv6 response
            ]

            # Test resolving to IPv6 only
            result = resolve_hostname('example.com', 'ipv6')
            self.assertEqual(result, ['2001:db8::1'])

    @patch('sshost.keyscan.get_ssh_config')
    @patch('sshost.keyscan.run_keyscan')
    @patch('sshost.keyscan.resolve_hostname')
    def test_keyscan_ip_version_filter(self, mock_resolve, mock_run_keyscan, mock_get_config):
        # Setup mocks
        mock_get_config.return_value = {'port': '22'}
        mock_resolve.return_value = []  # No IPs found for the requested version
        
        # Run keyscan with IPv4 only
        result = keyscan('ipv6-only.host', ip_version='ipv4')
        
        # Verify the host was skipped (not marked unreachable)
        self.assertEqual(result, [])
        mock_resolve.assert_called_once_with('ipv6-only.host', 'ipv4')

    def test_is_valid_ipv4(self):
        self.assertTrue(is_valid_ipv4('192.168.1.1'))
        self.assertTrue(is_valid_ipv4('127.0.0.1'))
        self.assertFalse(is_valid_ipv4('2001:db8::1'))
        self.assertFalse(is_valid_ipv4('not-an-ip'))

    def test_is_valid_ipv6(self):
        self.assertTrue(is_valid_ipv6('2001:db8::1'))
        self.assertTrue(is_valid_ipv6('::1'))
        self.assertFalse(is_valid_ipv6('192.168.1.1'))
        self.assertFalse(is_valid_ipv6('not-an-ip'))

    @patch('sshost.keyscan.get_ssh_config')
    @patch('sshost.keyscan.run_keyscan')
    def test_keyscan_with_ip_address(self, mock_run_keyscan, mock_get_config):
        # Run with an IP address directly (should skip DNS resolution)
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = '192.168.1.1 ssh-rsa AAAAB3NzaC...'
        mock_run_keyscan.return_value = mock_result
        
        with patch('sshost.keyscan.resolve_hostname', wraps=resolve_hostname) as mock_resolve:
            result = keyscan('192.168.1.1')
            
            # The IP address should be directly returned without extra DNS lookups
            self.assertEqual(result[0]['ip'], '192.168.1.1')
            mock_resolve.assert_called_once()


if __name__ == '__main__':
    unittest.main()
