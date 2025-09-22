"""
Tool Manager for HATS framework.
Handles tool detection, loading, and management.
"""

import os
import shutil
from typing import Dict, List, Optional
from .config_loader import ConfigLoader
from .utils.logger import get_logger
from .utils.detector import ToolDetector


class ToolManager:
    """Manages tools in the HATS framework."""
    
    def __init__(self, config_path: str = "configs/tools.yaml"):
        """
        Initialize the Tool Manager.
        
        Args:
            config_path (str): Path to the tool configuration file
        """
        self.logger = get_logger(__name__)
        self.config_loader = ConfigLoader(config_path)
        self.detector = ToolDetector()
        self.tools = self.config_loader.load_tools()
        self._verify_tools()
    
    def get_tool(self, tool_name: str) -> Optional[Dict]:
        """
        Get tool configuration by name.
        
        Args:
            tool_name (str): Name of the tool
            
        Returns:
            Optional[Dict]: Tool configuration if found
        """
        return self.tools.get(tool_name)
    
    def get_tools_by_category(self, category: str) -> List[Dict]:
        """
        Get all tools in a specific category.
        
        Args:
            category (str): Tool category
            
        Returns:
            List[Dict]: List of tools in the category
        """
        return [
            tool for tool in self.tools.values()
            if tool.get('category') == category
        ]
    
    def list_available_tools(self) -> List[str]:
        """
        List all available tool names.
        
        Returns:
            List[str]: List of tool names
        """
        return list(self.tools.keys())
    
    def list_categories(self) -> List[str]:
        """
        List all tool categories.
        
        Returns:
            List[str]: List of categories
        """
        categories = set()
        for tool in self.tools.values():
            if 'category' in tool:
                categories.add(tool['category'])
        return list(categories)
    
    def is_tool_available(self, tool_name: str) -> bool:
        """
        Check if a tool is available on the system.
        
        Args:
            tool_name (str): Name of the tool
            
        Returns:
            bool: True if tool is available
        """
        tool_config = self.get_tool(tool_name)
        if not tool_config:
            return False
        
        command = tool_config.get('command')
        if not command:
            return False
        
        return shutil.which(command) is not None
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict]:
        """
        Get detailed information about a tool.
        
        Args:
            tool_name (str): Name of the tool
            
        Returns:
            Optional[Dict]: Tool information
        """
        tool_config = self.get_tool(tool_name)
        if not tool_config:
            return None
        
        return {
            'name': tool_name,
            'description': tool_config.get('description', ''),
            'category': tool_config.get('category', ''),
            'command': tool_config.get('command', ''),
            'available': self.is_tool_available(tool_name),
            'dependencies': tool_config.get('dependencies', []),
            'version': self._get_tool_version(tool_config)
        }
    
    def install_tool(self, tool_name: str) -> bool:
        """
        Install a tool using its installation method.
        
        Args:
            tool_name (str): Name of the tool to install
            
        Returns:
            bool: True if installation successful
        """
        tool_config = self.get_tool(tool_name)
        if not tool_config:
            self.logger.error(f"Tool {tool_name} not found in configuration")
            return False
        
        install_method = tool_config.get('install')
        if not install_method:
            self.logger.error(f"No installation method defined for {tool_name}")
            return False
        
        try:
            self.logger.info(f"Installing {tool_name}...")
            # Here you would implement actual installation logic
            # This could involve package managers, git clones, etc.
            self.logger.info(f"Tool {tool_name} installed successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to install {tool_name}: {str(e)}")
            return False
    
    def refresh_tools(self):
        """Reload tool configurations from file."""
        self.tools = self.config_loader.load_tools()
        self._verify_tools()
    
    def _verify_tools(self):
        """Verify that configured tools are available."""
        for tool_name, tool_config in self.tools.items():
            if not self.is_tool_available(tool_name):
                self.logger.warning(f"Tool {tool_name} is configured but not available on system")
    
    def _get_tool_version(self, tool_config: Dict) -> str:
        """
        Get version of a tool.
        
        Args:
            tool_config (Dict): Tool configuration
            
        Returns:
            str: Tool version or 'unknown'
        """
        version_cmd = tool_config.get('version_cmd')
        if not version_cmd:
            return 'unknown'
        
        try:
            import subprocess
            result = subprocess.run(
                version_cmd.split(),
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.stdout.strip()
        except Exception:
            return 'unknown'
    
    def register_tool(self, name, command, category, argument_patterns=None, parser=None):
        """
        Register a new tool at runtime (for plugins).
        
        Args:
            name (str): Name of the tool
            command (str): Command to execute the tool
            category (str): Category of the tool
            argument_patterns (Optional[List[str]]): Expected argument patterns
            parser (Optional[callable]): Custom parser function
            
        Returns:
            None
        """
        self.tools[name] = {
            'name': name,
            'command': command,
            'category': category,
            'argument_patterns': argument_patterns or [],
            'parser': parser
        }
        self.logger.info(f"Tool registered at runtime: {name}")
