"""
Tool detection and dependency checking module for HATS framework.
Handles path detection and dependency validation.
"""

import os
import shutil
import subprocess
import platform
from typing import Dict, List, Optional, Tuple
from .logger import get_logger


class ToolDetector:
    """Detects tools and their dependencies on the system."""
    
    def __init__(self):
        """Initialize the tool detector."""
        self.logger = get_logger(__name__)
        self.os_type = platform.system().lower()
        self.architecture = platform.machine().lower()
    
    def detect_tool(self, tool_name: str) -> Dict:
        """
        Detect if a tool is available on the system.
        
        Args:
            tool_name (str): Name of the tool to detect
            
        Returns:
            Dict: Detection results including path, version, etc.
        """
        result = {
            'name': tool_name,
            'available': False,
            'path': None,
            'version': None,
            'platform_supported': True
        }
        
        try:
            # Check if tool is in PATH
            tool_path = shutil.which(tool_name)
            
            if tool_path:
                result['available'] = True
                result['path'] = tool_path
                result['version'] = self._get_tool_version(tool_name)
                self.logger.debug(f"Tool {tool_name} found at {tool_path}")
            else:
                # Try common installation paths
                common_paths = self._get_common_paths(tool_name)
                for path in common_paths:
                    if os.path.exists(path):
                        result['available'] = True
                        result['path'] = path
                        result['version'] = self._get_tool_version(path)
                        self.logger.debug(f"Tool {tool_name} found at {path}")
                        break
                
                if not result['available']:
                    self.logger.warning(f"Tool {tool_name} not found on system")
        
        except Exception as e:
            self.logger.error(f"Error detecting tool {tool_name}: {str(e)}")
        
        return result
    
    def detect_multiple_tools(self, tool_list: List[str]) -> Dict[str, Dict]:
        """
        Detect multiple tools at once.
        
        Args:
            tool_list (List[str]): List of tool names to detect
            
        Returns:
            Dict[str, Dict]: Detection results for each tool
        """
        results = {}
        
        for tool in tool_list:
            results[tool] = self.detect_tool(tool)
        
        return results
    
    def check_dependencies(self, tool_name: str, dependencies: List[str]) -> Dict:
        """
        Check if tool dependencies are available.
        
        Args:
            tool_name (str): Name of the main tool
            dependencies (List[str]): List of dependency names
            
        Returns:
            Dict: Dependency check results
        """
        result = {
            'tool': tool_name,
            'all_dependencies_met': True,
            'missing_dependencies': [],
            'available_dependencies': []
        }
        
        for dep in dependencies:
            dep_result = self.detect_tool(dep)
            
            if dep_result['available']:
                result['available_dependencies'].append(dep)
            else:
                result['missing_dependencies'].append(dep)
                result['all_dependencies_met'] = False
        
        return result
    
    def get_installation_suggestions(self, tool_name: str) -> List[str]:
        """
        Get installation suggestions for a tool based on the OS.
        
        Args:
            tool_name (str): Name of the tool
            
        Returns:
            List[str]: Installation suggestions
        """
        suggestions = []
        
        if self.os_type == "linux":
            # Detect distribution
            distro = self._detect_linux_distro()
            
            if distro in ["ubuntu", "debian"]:
                suggestions.append(f"sudo apt-get install {tool_name}")
                suggestions.append(f"sudo apt update && sudo apt install {tool_name}")
            elif distro in ["centos", "rhel", "fedora"]:
                suggestions.append(f"sudo yum install {tool_name}")
                suggestions.append(f"sudo dnf install {tool_name}")
            elif distro == "arch":
                suggestions.append(f"sudo pacman -S {tool_name}")
            
            # Generic suggestions
            suggestions.append(f"pip install {tool_name}")
            suggestions.append(f"git clone and compile {tool_name}")
            
        elif self.os_type == "darwin":  # macOS
            suggestions.append(f"brew install {tool_name}")
            suggestions.append(f"pip install {tool_name}")
            suggestions.append(f"port install {tool_name}")
            
        elif self.os_type == "windows":
            suggestions.append(f"choco install {tool_name}")
            suggestions.append(f"pip install {tool_name}")
            suggestions.append("Download from official website")
        
        # Tool-specific suggestions
        tool_specific = self._get_tool_specific_suggestions(tool_name)
        suggestions.extend(tool_specific)
        
        return suggestions
    
    def verify_tool_functionality(self, tool_name: str, test_command: str = None) -> bool:
        """
        Verify that a tool is functional by running a test command.
        
        Args:
            tool_name (str): Name of the tool
            test_command (str): Test command to run (optional)
            
        Returns:
            bool: True if tool is functional
        """
        try:
            if not test_command:
                test_command = f"{tool_name} --help"
            
            result = subprocess.run(
                test_command.split(),
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Tool is functional if it doesn't crash
            return result.returncode != 127  # 127 = command not found
            
        except subprocess.TimeoutExpired:
            # If it times out, the tool probably exists but the command is wrong
            return True
        except Exception as e:
            self.logger.debug(f"Tool functionality test failed for {tool_name}: {str(e)}")
            return False
    
    def _get_tool_version(self, tool_path: str) -> Optional[str]:
        """
        Get version of a tool.
        
        Args:
            tool_path (str): Path to the tool
            
        Returns:
            Optional[str]: Tool version or None
        """
        version_commands = [
            f"{tool_path} --version",
            f"{tool_path} -version",
            f"{tool_path} -V",
            f"{tool_path} version"
        ]
        
        for cmd in version_commands:
            try:
                result = subprocess.run(
                    cmd.split(),
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0 and result.stdout.strip():
                    # Extract version from output (first line, first version-like string)
                    import re
                    version_match = re.search(r'(\d+\.[\d\.]+)', result.stdout)
                    if version_match:
                        return version_match.group(1)
                    return result.stdout.split('\n')[0].strip()
                    
            except Exception:
                continue
        
        return None
    
    def _get_common_paths(self, tool_name: str) -> List[str]:
        """
        Get common installation paths for a tool.
        
        Args:
            tool_name (str): Name of the tool
            
        Returns:
            List[str]: List of possible paths
        """
        paths = []
        
        if self.os_type == "linux":
            paths.extend([
                f"/usr/bin/{tool_name}",
                f"/usr/local/bin/{tool_name}",
                f"/opt/{tool_name}/bin/{tool_name}",
                f"/home/{os.getenv('USER', 'user')}/bin/{tool_name}",
                f"/snap/bin/{tool_name}"
            ])
        elif self.os_type == "darwin":
            paths.extend([
                f"/usr/local/bin/{tool_name}",
                f"/opt/homebrew/bin/{tool_name}",
                f"/usr/bin/{tool_name}"
            ])
        elif self.os_type == "windows":
            paths.extend([
                f"C:\\Program Files\\{tool_name}\\{tool_name}.exe",
                f"C:\\Program Files (x86)\\{tool_name}\\{tool_name}.exe",
                f"C:\\Tools\\{tool_name}\\{tool_name}.exe"
            ])
        
        return paths
    
    def _detect_linux_distro(self) -> str:
        """
        Detect Linux distribution.
        
        Returns:
            str: Distribution name
        """
        try:
            # Try reading /etc/os-release
            if os.path.exists("/etc/os-release"):
                with open("/etc/os-release", 'r') as f:
                    for line in f:
                        if line.startswith("ID="):
                            return line.split("=")[1].strip().strip('"')
            
            # Try other methods
            if os.path.exists("/etc/debian_version"):
                return "debian"
            elif os.path.exists("/etc/redhat-release"):
                return "rhel"
            elif os.path.exists("/etc/arch-release"):
                return "arch"
                
        except Exception:
            pass
        
        return "unknown"
    
    def _get_tool_specific_suggestions(self, tool_name: str) -> List[str]:
        """
        Get tool-specific installation suggestions.
        
        Args:
            tool_name (str): Name of the tool
            
        Returns:
            List[str]: Tool-specific suggestions
        """
        suggestions = {
            "nmap": [
                "Download from https://nmap.org/download.html",
                "Compile from source: https://nmap.org/download.html#source"
            ],
            "nikto": [
                "git clone https://github.com/sullo/nikto.git",
                "Download from https://cirt.net/Nikto2"
            ],
            "metasploit": [
                "curl https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb > msfinstall && chmod 755 msfinstall && ./msfinstall"
            ],
            "sqlmap": [
                "git clone --depth 1 https://github.com/sqlmapproject/sqlmap.git",
                "pip install sqlmap"
            ]
        }
        
        return suggestions.get(tool_name, [])
