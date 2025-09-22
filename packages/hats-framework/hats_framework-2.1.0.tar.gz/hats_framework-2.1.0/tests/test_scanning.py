"""
Unit tests for HATS scanning category module.
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add the parent directory to the path so we can import hats
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from hats.categories.scanning import ScanningCategory


class TestScanningCategory(unittest.TestCase):
    """Test cases for ScanningCategory class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.scanner = ScanningCategory()
    
    def test_parse_nmap_output(self):
        """Test parsing nmap output."""
        nmap_output = """
        Nmap scan report for example.com (192.168.1.1)
        Host is up (0.001s latency).
        
        PORT     STATE SERVICE VERSION
        22/tcp   open  ssh     OpenSSH 7.4
        80/tcp   open  http    Apache httpd 2.4.6
        443/tcp  open  https   Apache httpd 2.4.6
        
        OS details: Linux 3.2 - 4.9
        """
        
        result = self.scanner.parse_nmap_output(nmap_output)
        
        self.assertEqual(len(result['hosts']), 1)
        self.assertIn('example.com (192.168.1.1)', result['hosts'])
        
        self.assertEqual(len(result['open_ports']), 3)
        ports = [port['port'] for port in result['open_ports']]
        self.assertIn(22, ports)
        self.assertIn(80, ports)
        self.assertIn(443, ports)
        
        self.assertEqual(len(result['os_detection']), 1)
        self.assertIn('Linux 3.2 - 4.9', result['os_detection'][0]['os'])
    
    def test_parse_nikto_output(self):
        """Test parsing nikto output."""
        nikto_output = """
        - Nikto v2.1.6
        ---------------------------------------------------------------------------
        + Target IP:          192.168.1.1
        + Target Hostname:    example.com
        + Target Port:        80
        + Start Time:         2023-01-01 12:00:00 (GMT-5)
        ---------------------------------------------------------------------------
        + Server: Apache/2.4.6 (CentOS)
        + Retrieved x-powered-by header: PHP/5.4.16
        + The anti-clickjacking X-Frame-Options header is not present.
        + The X-XSS-Protection header is not defined.
        + OSVDB-3268: /config/: Directory indexing found.
        + OSVDB-3092: /admin/: This might be interesting...
        """
        
        result = self.scanner.parse_nikto_output(nikto_output)
        
        self.assertEqual(result['target'], '192.168.1.1')
        self.assertEqual(result['server_info']['server'], 'Apache/2.4.6 (CentOS)')
        
        self.assertEqual(len(result['findings']), 4)
        findings_text = ' '.join(result['findings'])
        self.assertIn('X-Frame-Options', findings_text)
        self.assertIn('X-XSS-Protection', findings_text)
    
    def test_generate_port_scan_command(self):
        """Test generating port scan command."""
        command = self.scanner.generate_port_scan_command(
            target='192.168.1.1',
            scan_type='syn',
            ports='80,443',
            timing='T4'
        )
        
        expected = ['nmap', '-sS', '-T4', '-p', '80,443', '192.168.1.1']
        self.assertEqual(command, expected)
    
    def test_generate_port_scan_command_defaults(self):
        """Test generating port scan command with defaults."""
        command = self.scanner.generate_port_scan_command('192.168.1.1')
        
        expected = ['nmap', '-sS', '-T3', '192.168.1.1']
        self.assertEqual(command, expected)
    
    def test_generate_port_scan_command_tcp(self):
        """Test generating TCP port scan command."""
        command = self.scanner.generate_port_scan_command(
            target='192.168.1.1',
            scan_type='tcp'
        )
        
        expected = ['nmap', '-sT', '-T3', '192.168.1.1']
        self.assertEqual(command, expected)
    
    def test_generate_port_scan_command_udp(self):
        """Test generating UDP port scan command."""
        command = self.scanner.generate_port_scan_command(
            target='192.168.1.1',
            scan_type='udp'
        )
        
        expected = ['nmap', '-sU', '-T3', '192.168.1.1']
        self.assertEqual(command, expected)
    
    def test_generate_web_scan_command(self):
        """Test generating web scan command."""
        command = self.scanner.generate_web_scan_command('http://example.com')
        
        expected = ['nikto', '-h', 'http://example.com']
        self.assertEqual(command, expected)
    
    def test_generate_web_scan_command_ssl(self):
        """Test generating web scan command with SSL."""
        command = self.scanner.generate_web_scan_command('https://example.com', ssl=True)
        
        expected = ['nikto', '-h', 'https://example.com', '-ssl']
        self.assertEqual(command, expected)
    
    def test_validate_target_ip(self):
        """Test target validation with IP address."""
        valid_ips = ['192.168.1.1', '10.0.0.1', '172.16.0.1', '8.8.8.8']
        
        for ip in valid_ips:
            self.assertTrue(self.scanner.validate_target(ip))
    
    def test_validate_target_hostname(self):
        """Test target validation with hostname."""
        valid_hostnames = ['example.com', 'www.example.com', 'sub.domain.com']
        
        for hostname in valid_hostnames:
            self.assertTrue(self.scanner.validate_target(hostname))
    
    def test_validate_target_cidr(self):
        """Test target validation with CIDR notation."""
        valid_cidrs = ['192.168.1.0/24', '10.0.0.0/8', '172.16.0.0/16']
        
        for cidr in valid_cidrs:
            self.assertTrue(self.scanner.validate_target(cidr))
    
    def test_validate_target_invalid(self):
        """Test target validation with invalid targets."""
        invalid_targets = ['256.256.256.256', 'invalid..domain', '192.168.1.0/33']
        
        for target in invalid_targets:
            self.assertFalse(self.scanner.validate_target(target))
    
    def test_get_common_ports(self):
        """Test getting common port lists."""
        ports = self.scanner.get_common_ports()
        
        self.assertIn('web', ports)
        self.assertIn('database', ports)
        self.assertIn('email', ports)
        
        # Check specific ports
        self.assertIn(80, ports['web'])
        self.assertIn(443, ports['web'])
        self.assertIn(3306, ports['database'])
        self.assertIn(22, ports['remote_access'])
    
    def test_parse_nmap_output_empty(self):
        """Test parsing empty nmap output."""
        result = self.scanner.parse_nmap_output("")
        
        self.assertEqual(len(result['hosts']), 0)
        self.assertEqual(len(result['open_ports']), 0)
        self.assertEqual(len(result['services']), 0)
        self.assertEqual(len(result['os_detection']), 0)
    
    def test_parse_nikto_output_empty(self):
        """Test parsing empty nikto output."""
        result = self.scanner.parse_nikto_output("")
        
        self.assertEqual(result['target'], '')
        self.assertEqual(len(result['findings']), 0)
        self.assertEqual(len(result['server_info']), 0)


if __name__ == '__main__':
    unittest.main()
