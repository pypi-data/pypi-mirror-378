"""
Scanning category implementation for HATS framework.
Handles network scanners, web scanners, and vulnerability scanners.
"""

import re
from typing import Dict, List, Optional
from ..utils.logger import get_logger


class ScanningCategory:
    """Handles scanning tools like nmap, nikto, masscan, etc."""
    
    def __init__(self):
        """Initialize the scanning category."""
        self.logger = get_logger(__name__)
        self.category = "scanning"
    
    def parse_nmap_output(self, output: str) -> Dict:
        """
        Parse nmap scan output.
        
        Args:
            output (str): Raw nmap output
            
        Returns:
            Dict: Parsed scan results
        """
        results = {
            'hosts': [],
            'open_ports': [],
            'services': [],
            'os_detection': []
        }
        
        lines = output.split('\n')
        current_host = None
        
        for line in lines:
            line = line.strip()
            
            # Extract host information
            if 'Nmap scan report for' in line:
                host_match = re.search(r'Nmap scan report for (.+)', line)
                if host_match:
                    current_host = host_match.group(1)
                    results['hosts'].append(current_host)
            
            # Extract open ports
            if '/' in line and 'open' in line:
                port_match = re.search(r'(\d+)/(tcp|udp)\s+open\s+(.+)', line)
                if port_match and current_host:
                    port_info = {
                        'host': current_host,
                        'port': int(port_match.group(1)),
                        'protocol': port_match.group(2),
                        'service': port_match.group(3).strip()
                    }
                    results['open_ports'].append(port_info)
                    results['services'].append(port_match.group(3).strip())
            
            # Extract OS detection
            if 'OS details:' in line:
                os_match = re.search(r'OS details: (.+)', line)
                if os_match and current_host:
                    results['os_detection'].append({
                        'host': current_host,
                        'os': os_match.group(1)
                    })
        
        return results
    
    def parse_nikto_output(self, output: str) -> Dict:
        """
        Parse nikto scan output.
        
        Args:
            output (str): Raw nikto output
            
        Returns:
            Dict: Parsed scan results
        """
        results = {
            'target': '',
            'findings': [],
            'server_info': {}
        }
        
        lines = output.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Extract target
            if 'Target IP:' in line:
                target_match = re.search(r'Target IP:\s+(.+)', line)
                if target_match:
                    results['target'] = target_match.group(1)
            
            # Extract server information
            if 'Server:' in line:
                server_match = re.search(r'Server:\s+(.+)', line)
                if server_match:
                    results['server_info']['server'] = server_match.group(1)
            
            # Extract findings (vulnerabilities)
            if line.startswith('+'):
                finding = line[1:].strip()
                if finding:
                    results['findings'].append(finding)
        
        return results
    
    def generate_port_scan_command(self, target: str, scan_type: str = "syn", 
                                 ports: str = None, timing: str = "T3") -> List[str]:
        """
        Generate nmap command for port scanning.
        
        Args:
            target (str): Target IP or hostname
            scan_type (str): Type of scan (syn, tcp, udp)
            ports (str): Port range or specific ports
            timing (str): Timing template
            
        Returns:
            List[str]: Command as list of strings
        """
        command = ['nmap']
        
        # Add scan type
        if scan_type == "syn":
            command.append('-sS')
        elif scan_type == "tcp":
            command.append('-sT')
        elif scan_type == "udp":
            command.append('-sU')
        
        # Add timing
        command.append(f'-{timing}')
        
        # Add port specification
        if ports:
            command.extend(['-p', ports])
        
        # Add target
        command.append(target)
        
        return command
    
    def generate_web_scan_command(self, target: str, ssl: bool = False) -> List[str]:
        """
        Generate nikto command for web scanning.
        
        Args:
            target (str): Target URL or IP
            ssl (bool): Whether to use SSL
            
        Returns:
            List[str]: Command as list of strings
        """
        command = ['nikto', '-h', target]
        
        if ssl:
            command.extend(['-ssl'])
        
        return command
    
    def validate_target(self, target: str) -> bool:
        """
        Validate scan target format.
        
        Args:
            target (str): Target to validate
            
        Returns:
            bool: True if target is valid
        """
        # Basic IP address pattern
        ip_pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        
        # Basic hostname pattern
        hostname_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
        
        # CIDR pattern
        cidr_pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)/(?:[0-2]?[0-9]|3[0-2])$'
        
        return (re.match(ip_pattern, target) or 
                re.match(hostname_pattern, target) or 
                re.match(cidr_pattern, target)) is not None
    
    def get_common_ports(self) -> Dict[str, List[int]]:
        """
        Get common port lists for different services.
        
        Returns:
            Dict[str, List[int]]: Port lists by service type
        """
        return {
            'web': [80, 443, 8080, 8443, 8000, 8888],
            'database': [3306, 5432, 1433, 1521, 27017],
            'email': [25, 110, 143, 993, 995, 587],
            'file_transfer': [21, 22, 23, 69, 115],
            'remote_access': [22, 23, 3389, 5900, 5901],
            'dns': [53],
            'dhcp': [67, 68],
            'snmp': [161, 162],
            'top_1000': list(range(1, 1001))  # Top 1000 ports
        }
