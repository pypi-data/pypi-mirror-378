"""
Security module for HATS framework.
Provides argument sanitization and command injection prevention.
"""

import re
import shlex
import ipaddress
from typing import Any, Dict, List, Union
from .utils.logger import get_logger


class ArgumentSanitizer:
    """Military-grade argument validation and sanitization."""
    
    # Regex patterns for validation
    IP_PATTERN = re.compile(r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}(?:/[0-9]{1,2})?$')
    PORT_PATTERN = re.compile(r'^[0-9]{1,5}$')
    DOMAIN_PATTERN = re.compile(r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$')
    URL_PATTERN = re.compile(r'^https?://[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*(?::[0-9]{1,5})?(?:/.*)?$')
    
    # Security blacklists
    DANGEROUS_CHARS = [';', '&', '|', '`', '$', '(', ')', '{', '}', '<', '>', '\n', '\r', '\\']
    DANGEROUS_COMMANDS = [
        'rm', 'del', 'format', 'dd', 'mkfs', 'shutdown', 'reboot', 'halt',
        'poweroff', 'init', 'kill', 'killall', 'pkill', 'chmod', 'chown',
        'sudo', 'su', 'passwd', 'adduser', 'deluser', 'userdel', 'useradd'
    ]
    
    # Whitelisted argument patterns
    SAFE_ARG_PATTERNS = [
        r'^-[a-zA-Z0-9]+$',  # Single dash flags
        r'^--[a-zA-Z0-9\-]+$',  # Double dash flags
        r'^-[a-zA-Z0-9]+ .+$',  # Flag with value
        r'^--[a-zA-Z0-9\-]+[= ].+$',  # Long flag with value
    ]
    
    def __init__(self):
        """Initialize the sanitizer."""
        self.logger = get_logger(__name__)
    
    @classmethod
    def sanitize_ip(cls, ip: str) -> str:
        """
        Validate and sanitize IP address or CIDR notation.
        
        Args:
            ip (str): IP address to validate
            
        Returns:
            str: Validated IP address
            
        Raises:
            ValueError: If IP is invalid
        """
        try:
            # Handle CIDR notation
            if '/' in ip:
                network = ipaddress.ip_network(ip, strict=False)
                return str(network)
            else:
                address = ipaddress.ip_address(ip)
                return str(address)
        except (ipaddress.AddressValueError, ipaddress.NetmaskValueError) as e:
            raise ValueError(f"Invalid IP address: {ip} - {str(e)}")
    
    @classmethod
    def sanitize_port(cls, port: Union[str, int]) -> str:
        """
        Validate port number.
        
        Args:
            port (Union[str, int]): Port number to validate
            
        Returns:
            str: Validated port number
            
        Raises:
            ValueError: If port is invalid
        """
        port_str = str(port)
        
        # Handle port ranges
        if '-' in port_str:
            parts = port_str.split('-')
            if len(parts) != 2:
                raise ValueError(f"Invalid port range format: {port}")
            
            start_port = int(parts[0])
            end_port = int(parts[1])
            
            if not (1 <= start_port <= 65535) or not (1 <= end_port <= 65535):
                raise ValueError(f"Port range out of bounds: {port}")
            
            if start_port >= end_port:
                raise ValueError(f"Invalid port range: start >= end")
            
            return port_str
        
        # Single port validation
        if not cls.PORT_PATTERN.match(port_str):
            raise ValueError(f"Invalid port format: {port}")
        
        port_num = int(port_str)
        if not (1 <= port_num <= 65535):
            raise ValueError(f"Port out of range (1-65535): {port}")
        
        return port_str
    
    @classmethod
    def sanitize_domain(cls, domain: str) -> str:
        """
        Validate domain name.
        
        Args:
            domain (str): Domain to validate
            
        Returns:
            str: Validated domain
            
        Raises:
            ValueError: If domain is invalid
        """
        if not cls.DOMAIN_PATTERN.match(domain):
            raise ValueError(f"Invalid domain format: {domain}")
        
        if len(domain) > 253:
            raise ValueError(f"Domain too long: {domain}")
        
        return domain.lower()
    
    @classmethod
    def sanitize_url(cls, url: str) -> str:
        """
        Validate URL format.
        
        Args:
            url (str): URL to validate
            
        Returns:
            str: Validated URL
            
        Raises:
            ValueError: If URL is invalid
        """
        if not cls.URL_PATTERN.match(url):
            raise ValueError(f"Invalid URL format: {url}")
        
        return url
    
    @classmethod
    def sanitize_args(cls, args: str) -> List[str]:
        """
        Safely parse and validate command arguments.
        
        Args:
            args (str): Argument string to parse
            
        Returns:
            List[str]: Sanitized argument list
            
        Raises:
            ValueError: If arguments contain dangerous content
        """
        if not args:
            return []
        
        # Check for dangerous characters
        for char in cls.DANGEROUS_CHARS:
            if char in args:
                raise ValueError(f"Dangerous character detected: '{char}' in arguments")
        
        # Parse with shlex for proper shell escaping
        try:
            parsed_args = shlex.split(args)
        except ValueError as e:
            raise ValueError(f"Invalid argument format: {e}")
        
        # Validate each argument
        for arg in parsed_args:
            # Check for dangerous commands
            for cmd in cls.DANGEROUS_COMMANDS:
                if cmd in arg.lower():
                    raise ValueError(f"Dangerous command detected: '{cmd}' in argument '{arg}'")
            
            # Validate argument patterns (for flags)
            if arg.startswith('-'):
                is_safe = any(re.match(pattern, arg) for pattern in cls.SAFE_ARG_PATTERNS)
                if not is_safe:
                    raise ValueError(f"Potentially unsafe argument pattern: '{arg}'")
        
        return parsed_args
    
    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        """
        Sanitize filename for safe file operations.
        
        Args:
            filename (str): Filename to sanitize
            
        Returns:
            str: Sanitized filename
            
        Raises:
            ValueError: If filename is unsafe
        """
        # Remove path traversal attempts
        if '..' in filename or '/' in filename or '\\' in filename:
            raise ValueError(f"Path traversal detected in filename: {filename}")
        
        # Check for dangerous characters
        dangerous_file_chars = ['<', '>', ':', '"', '|', '?', '*', '\0']
        for char in dangerous_file_chars:
            if char in filename:
                raise ValueError(f"Dangerous character in filename: '{char}'")
        
        # Limit filename length
        if len(filename) > 255:
            raise ValueError(f"Filename too long: {filename}")
        
        return filename
    
    def detect_argument_type(self, arg: Any) -> str:
        """
        Intelligently detect argument type for smart processing.
        Enhanced: Recognizes port lists, timing templates, user/pass files, and more.
        
        Args:
            arg (Any): Argument to analyze
            
        Returns:
            str: Detected argument type
        """
        if isinstance(arg, int):
            return "port"
        elif isinstance(arg, range):
            return "port_range"
        elif isinstance(arg, str):
            arg = arg.strip()
            # Check for IP address
            try:
                self.sanitize_ip(arg)
                return "ip"
            except ValueError:
                pass
            # Check for URL
            if arg.startswith(('http://', 'https://')):
                try:
                    self.sanitize_url(arg)
                    return "url"
                except ValueError:
                    pass
            # Check for domain
            if '.' in arg and not arg.startswith('-'):
                try:
                    self.sanitize_domain(arg)
                    return "domain"
                except ValueError:
                    pass
            # Check for port or port list
            if arg.isdigit() or '-' in arg or (',' in arg and all(p.strip().isdigit() for p in arg.split(','))):
                try:
                    if ',' in arg:
                        # Port list
                        ports = [int(p.strip()) for p in arg.split(',')]
                        if all(1 <= p <= 65535 for p in ports):
                            return "port_list"
                    self.sanitize_port(arg)
                    return "port"
                except ValueError:
                    pass
            # Check for timing template (e.g., T0-T5)
            if arg.upper() in [f"T{i}" for i in range(6)]:
                return "timing"
            # Check for user/pass file
            if arg.endswith('.txt') or arg.endswith('.lst'):
                if 'user' in arg.lower():
                    return "user_file"
                if 'pass' in arg.lower():
                    return "pass_file"
                return "filename"
            # Check for command flag
            if arg.startswith('-'):
                return "flag"
            # Check for filename (simple heuristic)
            if '.' in arg and len(arg.split('.')) == 2:
                return "filename"
            return "string"
        return "unknown"


class SecurityContext:
    """Security context manager for tool execution."""
    
    def __init__(self, tool_name: str, max_execution_time: int = 300):
        """
        Initialize security context.
        
        Args:
            tool_name (str): Name of the tool being executed
            max_execution_time (int): Maximum execution time in seconds
        """
        self.tool_name = tool_name
        self.max_execution_time = max_execution_time
        self.logger = get_logger(__name__)
        self.start_time = None
    
    def __enter__(self):
        """Enter security context."""
        import time
        self.start_time = time.time()
        self.logger.info(f"Starting secure execution of {self.tool_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit security context."""
        import time
        execution_time = time.time() - self.start_time
        
        if exc_type is None:
            self.logger.info(f"Secure execution of {self.tool_name} completed in {execution_time:.2f}s")
        else:
            self.logger.error(f"Secure execution of {self.tool_name} failed after {execution_time:.2f}s: {exc_val}")
        
        return False  # Don't suppress exceptions


def validate_tool_exists(tool_name: str) -> bool:
    """
    Validate that a tool exists and is safe to execute.
    
    Args:
        tool_name (str): Name of the tool
        
    Returns:
        bool: True if tool is safe to execute
    """
    import shutil
    
    # Check if tool is in PATH
    if not shutil.which(tool_name):
        return False
    
    # Check against known dangerous tools
    dangerous_tools = ['rm', 'dd', 'format', 'fdisk', 'mkfs']
    if tool_name.lower() in dangerous_tools:
        return False
    
    return True
