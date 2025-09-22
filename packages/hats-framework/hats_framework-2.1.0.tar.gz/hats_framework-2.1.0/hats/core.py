"""
Core execution engine for HATS framework.
Handles tool execution, orchestration, and workflow management.
"""

import asyncio
import subprocess
import threading
import time
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
from .utils.logger import get_logger
from .tool_manager import ToolManager
from .security import ArgumentSanitizer, SecurityContext, validate_tool_exists
from .plugin_loader import load_plugins


class ExecutionMode(Enum):
    """Execution mode enumeration."""
    SYNC = "sync"
    ASYNC = "async"
    BACKGROUND = "background"


class OutputFormat(Enum):
    """Output format enumeration."""
    DICT = "dict"
    LIST = "list"
    RAW = "raw"
    JSON = "json"
    XML = "xml"


@dataclass
class ToolResult:
    """Standardized tool execution result."""
    tool: str
    command: str
    returncode: int
    stdout: str
    stderr: str
    execution_time: float
    parsed_data: Optional[Dict[str, Any]] = None
    raw_output: Optional[str] = None
    success: bool = False


class HATSEngine:
    """Enhanced execution engine with security and performance."""
    
    def __init__(self, config_path: str = "configs/tools.yaml"):
        """
        Initialize the HATS engine.
        
        Args:
            config_path (str): Path to the tool configuration file
        """
        self.logger = get_logger(__name__)
        self.tool_manager = ToolManager(config_path)
        self.sanitizer = ArgumentSanitizer()
        self.running_tasks = {}
        self.task_counter = 0
        self.active_processes = {}
        # Load plugins
        load_plugins(self)

    def register_tool(self, name, command, category, argument_patterns=None, parser=None):
        """
        Register a new tool at runtime (for plugins).
        """
        self.tool_manager.register_tool(name, command, category, argument_patterns or [], parser)
        self.logger.info(f"Plugin tool registered: {name}")
    
    def detect_argument_type(self, arg: Any) -> str:
        """
        Smart argument type detection using sanitizer.
        
        Args:
            arg (Any): Argument to analyze
            
        Returns:
            str: Detected argument type
        """
        return self.sanitizer.detect_argument_type(arg)
    
    def build_command(self, tool: str, *args, **kwargs) -> List[str]:
        """
        Build secure command with comprehensive argument validation.
        
        Args:
            tool (str): Tool name
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            List[str]: Secure command list
            
        Raises:
            ValueError: If arguments are invalid or dangerous
        """
        # Validate tool exists and is safe
        if not validate_tool_exists(tool):
            raise ValueError(f"Tool '{tool}' is not available or not safe to execute")
        
        cmd = [tool]
        
        # Process positional arguments with type detection
        for arg in args:
            arg_type = self.detect_argument_type(arg)
            
            if arg_type == "ip":
                sanitized_ip = self.sanitizer.sanitize_ip(str(arg))
                cmd.append(sanitized_ip)
            elif arg_type == "port":
                sanitized_port = self.sanitizer.sanitize_port(arg)
                cmd.extend(["-p", sanitized_port])
            elif arg_type == "port_range":
                if isinstance(arg, range):
                    port_range = f"{arg.start}-{arg.stop-1}"
                    cmd.extend(["-p", port_range])
                else:
                    sanitized_port = self.sanitizer.sanitize_port(arg)
                    cmd.extend(["-p", sanitized_port])
            elif arg_type == "domain":
                sanitized_domain = self.sanitizer.sanitize_domain(str(arg))
                cmd.append(sanitized_domain)
            elif arg_type == "url":
                sanitized_url = self.sanitizer.sanitize_url(str(arg))
                cmd.append(sanitized_url)
            elif arg_type == "filename":
                sanitized_filename = self.sanitizer.sanitize_filename(str(arg))
                cmd.append(sanitized_filename)
            elif arg_type == "flag":
                cmd.append(str(arg))
            else:
                cmd.append(str(arg))
        
        # Process keyword arguments
        for key, value in kwargs.items():
            if key == "arg":
                # Custom arguments - sanitize heavily
                if value:
                    sanitized_args = self.sanitizer.sanitize_args(str(value))
                    cmd.extend(sanitized_args)
            elif key == "mode":
                # Predefined safe modes
                mode_args = self._get_mode_arguments(value)
                cmd.extend(mode_args)
            elif key == "output_format":
                # Output format specification
                if value in ["xml", "json", "normal", "greppable"]:
                    format_flag = self._get_output_format_flag(tool, value)
                    if format_flag:
                        cmd.extend(format_flag)
            elif key == "threads":
                # Thread/parallel execution
                thread_count = max(1, min(int(value), 100))  # Limit threads
                cmd.extend(["-t" if tool == "hydra" else "--max-parallelism", str(thread_count)])
            elif key == "timing":
                # Timing templates (nmap specific)
                if tool == "nmap" and value in ["T0", "T1", "T2", "T3", "T4", "T5"]:
                    cmd.append(f"-{value}")
        
        return cmd
    
    def _get_mode_arguments(self, mode: str) -> List[str]:
        """
        Get arguments for predefined modes.
        
        Args:
            mode (str): Mode name
            
        Returns:
            List[str]: Mode arguments
        """
        modes = {
            "aggressive": ["-T4", "-A"],
            "stealth": ["-T1", "-f"],
            "fast": ["-T4", "--min-rate", "1000"],
            "comprehensive": ["-sS", "-sV", "-sC", "-O"],
            "safe": ["-T2", "--max-rate", "100"]
        }
        return modes.get(mode, [])
    
    def _get_output_format_flag(self, tool: str, format_type: str) -> List[str]:
        """
        Get output format flags for specific tools.
        
        Args:
            tool (str): Tool name
            format_type (str): Format type
            
        Returns:
            List[str]: Format flags
        """
        format_maps = {
            "nmap": {
                "xml": ["-oX", "-"],
                "json": ["-oJ", "-"],  # If supported
                "greppable": ["-oG", "-"],
                "normal": ["-oN", "-"]
            },
            "masscan": {
                "xml": ["--output-format", "xml"],
                "json": ["--output-format", "json"]
            }
        }
        
        tool_formats = format_maps.get(tool, {})
        return tool_formats.get(format_type, [])
    
    async def execute_tool_async(self, tool: str, *args, mode: str = "sync", 
                                output_format: str = "dict", **kwargs) -> ToolResult:
        """
        Asynchronous tool execution with security context.
        
        Args:
            tool (str): Tool name
            *args: Tool arguments
            mode (str): Execution mode
            output_format (str): Output format
            **kwargs: Additional options
            
        Returns:
            ToolResult: Execution result
        """
        start_time = time.time()
        
        with SecurityContext(tool) as ctx:
            try:
                # Build secure command
                cmd = self.build_command(tool, *args, **kwargs)
                self.logger.info(f"Executing: {' '.join(cmd)}")
                
                # Create subprocess with security constraints
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd="/tmp",  # Sandbox execution directory
                    env=self._get_safe_environment()
                )
                
                # Wait for completion with timeout
                try:
                    stdout, stderr = await asyncio.wait_for(
                        process.communicate(), 
                        timeout=kwargs.get('timeout', 300)
                    )
                except asyncio.TimeoutError:
                    process.kill()
                    raise Exception(f"Tool {tool} execution timed out")
                
                execution_time = time.time() - start_time
                
                # Create result object
                result = ToolResult(
                    tool=tool,
                    command=' '.join(cmd),
                    returncode=process.returncode,
                    stdout=stdout.decode('utf-8', errors='ignore'),
                    stderr=stderr.decode('utf-8', errors='ignore'),
                    execution_time=execution_time,
                    raw_output=stdout.decode('utf-8', errors='ignore'),
                    success=(process.returncode == 0)
                )
                
                # Parse output based on tool and format
                if output_format == "dict":
                    result.parsed_data = self.parse_output(tool, result.stdout)
                
                self.logger.info(f"Tool {tool} completed in {execution_time:.2f}s")
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                self.logger.error(f"Tool {tool} execution failed after {execution_time:.2f}s: {str(e)}")
                
                return ToolResult(
                    tool=tool,
                    command=' '.join(cmd) if 'cmd' in locals() else f"{tool} [failed to build]",
                    returncode=-1,
                    stdout="",
                    stderr=str(e),
                    execution_time=execution_time,
                    success=False
                )
    
    def execute_tool_sync(self, tool: str, *args, **kwargs) -> ToolResult:
        """
        Synchronous tool execution wrapper.
        
        Args:
            tool (str): Tool name
            *args: Tool arguments
            **kwargs: Additional options
            
        Returns:
            ToolResult: Execution result
        """
        return asyncio.run(self.execute_tool_async(tool, *args, **kwargs))
    
    def _get_safe_environment(self) -> Dict[str, str]:
        """
        Get a safe environment for subprocess execution.
        
        Returns:
            Dict[str, str]: Safe environment variables
        """
        import os
        
        safe_env = {
            'PATH': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin',
            'HOME': '/tmp',
            'USER': 'hats',
            'SHELL': '/bin/bash',
            'LANG': 'C.UTF-8'
        }
        
        # Preserve some necessary variables
        preserve_vars = ['DISPLAY', 'TERM']
        for var in preserve_vars:
            if var in os.environ:
                safe_env[var] = os.environ[var]
        
        return safe_env
    
    def parse_output(self, tool: str, output: str) -> Dict[str, Any]:
        """
        Enhanced tool-specific output parsing.
        
        Args:
            tool (str): Tool name
            output (str): Raw output
            
        Returns:
            Dict[str, Any]: Parsed output
        """
        parsers = {
            'nmap': self._parse_nmap,
            'masscan': self._parse_masscan,
            'nikto': self._parse_nikto,
            'hydra': self._parse_hydra,
            'sqlmap': self._parse_sqlmap,
            'dirb': self._parse_dirb,
            'gobuster': self._parse_gobuster
        }
        
        parser = parsers.get(tool, self._parse_generic)
        return parser(output)
    
    def _parse_nmap(self, output: str) -> Dict[str, Any]:
        """Enhanced nmap output parsing with XML support."""
        # Try XML parsing first
        if "<nmaprun" in output:
            try:
                root = ET.fromstring(output)
                hosts = []
                
                for host in root.findall('host'):
                    host_data = {
                        'ip': host.find('address').get('addr'),
                        'state': host.find('status').get('state'),
                        'ports': [],
                        'os': {},
                        'services': []
                    }
                    
                    # Parse ports
                    ports_elem = host.find('ports')
                    if ports_elem:
                        for port in ports_elem.findall('port'):
                            port_data = {
                                'port': int(port.get('portid')),
                                'protocol': port.get('protocol'),
                                'state': port.find('state').get('state')
                            }
                            
                            service = port.find('service')
                            if service is not None:
                                port_data['service'] = service.get('name', '')
                                port_data['version'] = service.get('version', '')
                                port_data['product'] = service.get('product', '')
                            
                            host_data['ports'].append(port_data)
                            if port_data['state'] == 'open':
                                host_data['services'].append(port_data['service'])
                    
                    # Parse OS detection
                    os_elem = host.find('os')
                    if os_elem:
                        osmatch = os_elem.find('osmatch')
                        if osmatch is not None:
                            host_data['os'] = {
                                'name': osmatch.get('name', ''),
                                'accuracy': osmatch.get('accuracy', '0')
                            }
                    
                    hosts.append(host_data)
                
                return {
                    'hosts': hosts,
                    'total_hosts': len(hosts),
                    'format': 'xml'
                }
            except ET.ParseError:
                pass
        
        # Fallback to text parsing
        return self._parse_nmap_text(output)
    
    def _parse_nmap_text(self, output: str) -> Dict[str, Any]:
        """Parse nmap text output."""
        lines = output.split('\n')
        hosts = []
        current_host = None
        
        for line in lines:
            line = line.strip()
            
            # Host detection
            if 'Nmap scan report for' in line:
                if current_host:
                    hosts.append(current_host)
                
                import re
                host_match = re.search(r'Nmap scan report for (.+)', line)
                if host_match:
                    current_host = {
                        'target': host_match.group(1),
                        'ports': [],
                        'state': 'up'
                    }
            
            # Port detection
            elif '/' in line and 'open' in line and current_host:
                import re
                port_match = re.search(r'(\d+)/(tcp|udp)\s+open\s+(.+)', line)
                if port_match:
                    port_info = {
                        'port': int(port_match.group(1)),
                        'protocol': port_match.group(2),
                        'service': port_match.group(3).strip(),
                        'state': 'open'
                    }
                    current_host['ports'].append(port_info)
        
        if current_host:
            hosts.append(current_host)
        
        return {
            'hosts': hosts,
            'total_hosts': len(hosts),
            'format': 'text'
        }
    
    def _parse_masscan(self, output: str) -> Dict[str, Any]:
        """Parse masscan output."""
        lines = output.split('\n')
        hosts = []
        
        for line in lines:
            if 'open' in line and 'tcp' in line:
                import re
                match = re.search(r'(\d+)/tcp\s+open\s+(\S+)', line)
                if match:
                    hosts.append({
                        'port': int(match.group(1)),
                        'protocol': 'tcp',
                        'state': 'open',
                        'ip': match.group(2)
                    })
        
        return {
            'hosts': hosts,
            'total_ports': len(hosts),
            'format': 'masscan'
        }
    
    def _parse_nikto(self, output: str) -> Dict[str, Any]:
        """Parse nikto output."""
        lines = output.split('\n')
        vulnerabilities = []
        
        for line in lines:
            if '+ ' in line and any(word in line.lower() for word in ['osvdb', 'cve', 'vulnerable']):
                vulnerabilities.append({
                    'description': line.strip().replace('+ ', ''),
                    'severity': 'info'  # Default severity
                })
        
        return {
            'vulnerabilities': vulnerabilities,
            'total_issues': len(vulnerabilities),
            'format': 'nikto'
        }
    
    def _parse_hydra(self, output: str) -> Dict[str, Any]:
        """Parse hydra output."""
        lines = output.split('\n')
        credentials = []
        
        for line in lines:
            if 'login:' in line and 'password:' in line:
                import re
                match = re.search(r'login:\s*(\S+)\s+password:\s*(\S+)', line)
                if match:
                    credentials.append({
                        'username': match.group(1),
                        'password': match.group(2),
                        'service': 'unknown'
                    })
        
        return {
            'credentials': credentials,
            'total_found': len(credentials),
            'format': 'hydra'
        }
    
    def _parse_sqlmap(self, output: str) -> Dict[str, Any]:
        """Parse sqlmap output."""
        lines = output.split('\n')
        vulnerabilities = []
        databases = []
        
        for line in lines:
            if 'vulnerable' in line.lower():
                vulnerabilities.append({
                    'type': 'sql_injection',
                    'description': line.strip()
                })
            elif 'database:' in line.lower():
                import re
                match = re.search(r'database:\s*(\S+)', line, re.IGNORECASE)
                if match:
                    databases.append(match.group(1))
        
        return {
            'vulnerabilities': vulnerabilities,
            'databases': databases,
            'total_vulns': len(vulnerabilities),
            'format': 'sqlmap'
        }
    
    def _parse_dirb(self, output: str) -> Dict[str, Any]:
        """Parse dirb output."""
        lines = output.split('\n')
        directories = []
        
        for line in lines:
            if '==> DIRECTORY:' in line:
                directory = line.replace('==> DIRECTORY:', '').strip()
                directories.append({
                    'path': directory,
                    'type': 'directory'
                })
            elif '+ ' in line and 'http' in line:
                directories.append({
                    'path': line.strip().replace('+ ', ''),
                    'type': 'file'
                })
        
        return {
            'directories': directories,
            'total_found': len(directories),
            'format': 'dirb'
        }
    
    def _parse_gobuster(self, output: str) -> Dict[str, Any]:
        """Parse gobuster output."""
        lines = output.split('\n')
        paths = []
        
        for line in lines:
            if '(Status:' in line:
                import re
                match = re.search(r'(\S+)\s+\(Status:\s*(\d+)\)', line)
                if match:
                    paths.append({
                        'path': match.group(1),
                        'status_code': int(match.group(2)),
                        'type': 'endpoint'
                    })
        
        return {
            'paths': paths,
            'total_found': len(paths),
            'format': 'gobuster'
        }

    def _parse_generic(self, output: str) -> Dict[str, Any]:
        """Generic output parser for unknown tools."""
        lines = output.split('\n')
        return {
            'raw': output,
            'lines': [line.strip() for line in lines if line.strip()],
            'line_count': len(lines),
            'format': 'text'
        }
    
    def execute_tool(self, tool_name: str, *args, **kwargs) -> Union[Dict, ToolResult]:
        """
        Main tool execution interface (backward compatibility).
        
        Args:
            tool_name (str): Name of the tool to execute
            *args: Tool arguments
            **kwargs: Additional options
            
        Returns:
            Union[Dict, ToolResult]: Execution result
        """
        result = self.execute_tool_sync(tool_name, *args, **kwargs)
        
        # Return dict format for backward compatibility
        return {
            'tool': result.tool,
            'command': result.command,
            'success': result.success,
            'output': result.stdout,
            'error': result.stderr,
            'return_code': result.returncode,
            'execution_time': result.execution_time,
            'parsed_data': result.parsed_data
        }
    
    def execute_workflow(self, workflow: List[Dict]) -> List[Dict]:
        """
        Execute a workflow of multiple tools with enhanced error handling.
        
        Args:
            workflow (List[Dict]): List of tool configurations
            
        Returns:
            List[Dict]: Results from each tool
        """
        results = []
        
        for step_num, step in enumerate(workflow, 1):
            tool_name = step.get('tool')
            target = step.get('target')
            options = step.get('options', {})
            args = step.get('args', [])
            
            self.logger.info(f"Executing workflow step {step_num}: {tool_name}")
            
            try:
                # Prepare arguments
                if target:
                    args = [target] + list(args)
                
                result = self.execute_tool(tool_name, *args, **options)
                result['step'] = step_num
                results.append(result)
                
                # Check for stop conditions
                if not result['success'] and step.get('stop_on_error', False):
                    self.logger.warning(f"Workflow stopped at step {step_num} due to error")
                    break
                
                # Add delay between steps if specified
                delay = step.get('delay', 0)
                if delay > 0:
                    time.sleep(delay)
                    
            except Exception as e:
                self.logger.error(f"Workflow step {step_num} failed: {str(e)}")
                error_result = {
                    'tool': tool_name,
                    'step': step_num,
                    'success': False,
                    'error': str(e)
                }
                results.append(error_result)
                
                if step.get('stop_on_error', False):
                    break
                
        return results
    
    def execute_async(self, tool_name: str, *args, **kwargs) -> str:
        """
        Execute a tool asynchronously and return task ID.
        
        Args:
            tool_name (str): Name of the tool to execute
            *args: Tool arguments
            **kwargs: Additional options
            
        Returns:
            str: Task ID for tracking
        """
        task_id = f"task_{self.task_counter}"
        self.task_counter += 1
        
        async def run_async_task():
            result = await self.execute_tool_async(tool_name, *args, **kwargs)
            self.running_tasks[task_id] = result
        
        # Start the task
        asyncio.create_task(run_async_task())
        
        return task_id
    
    def get_task_result(self, task_id: str) -> Optional[ToolResult]:
        """
        Get the result of an async task.
        
        Args:
            task_id (str): Task ID
            
        Returns:
            Optional[ToolResult]: Task result if completed
        """
        return self.running_tasks.get(task_id)
    
    def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a running async task.
        
        Args:
            task_id (str): Task ID to cancel
            
        Returns:
            bool: True if task was cancelled
        """
        if task_id in self.active_processes:
            try:
                process = self.active_processes[task_id]
                process.terminate()
                del self.active_processes[task_id]
                return True
            except Exception as e:
                self.logger.error(f"Error cancelling task {task_id}: {str(e)}")
        
        return False
    
    def list_running_tasks(self) -> List[str]:
        """
        List all running task IDs.
        
        Returns:
            List[str]: List of running task IDs
        """
        return list(self.active_processes.keys())
    
    # Legacy methods for backward compatibility
    def _build_command(self, tool_config: Dict, target: str, options: Dict) -> List[str]:
        """Legacy command building (deprecated)."""
        self.logger.warning("_build_command is deprecated, use build_command instead")
        return self.build_command(tool_config['command'], target, **options)
    
    def _run_command(self, command: List[str]) -> Dict:
        """Legacy command execution (deprecated)."""
        self.logger.warning("_run_command is deprecated, use execute_tool_sync instead")
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            return {
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                'stdout': '',
                'stderr': 'Command timed out',
                'return_code': -1
            }
        except Exception as e:
            return {
                'stdout': '',
                'stderr': str(e),
                'return_code': -1
            }
