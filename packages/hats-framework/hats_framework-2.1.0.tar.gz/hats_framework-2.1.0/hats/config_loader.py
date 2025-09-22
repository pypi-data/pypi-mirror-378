"""
Configuration loader for HATS framework.
Handles YAML parsing and tool configuration loading.
"""

import yaml
import os
from typing import Dict, List, Any
from .utils.logger import get_logger


class ConfigLoader:
    """Loads and manages HATS configuration files."""
    
    def __init__(self, config_path: str = "configs/tools.yaml"):
        """
        Initialize the Config Loader.
        
        Args:
            config_path (str): Path to the configuration file
        """
        self.logger = get_logger(__name__)
        self.config_path = config_path
        self._ensure_config_exists()
    
    def load_tools(self) -> Dict[str, Dict]:
        """
        Load tool configurations from YAML file.
        
        Returns:
            Dict[str, Dict]: Dictionary of tool configurations
        """
        try:
            with open(self.config_path, 'r') as file:
                config = yaml.safe_load(file)
                
            tools = config.get('tools', {})
            self.logger.info(f"Loaded {len(tools)} tools from configuration")
            
            return tools
            
        except FileNotFoundError:
            self.logger.error(f"Configuration file not found: {self.config_path}")
            return {}
        except yaml.YAMLError as e:
            self.logger.error(f"Error parsing YAML configuration: {str(e)}")
            return {}
        except Exception as e:
            self.logger.error(f"Error loading configuration: {str(e)}")
            return {}
    
    def save_tools(self, tools: Dict[str, Dict]) -> bool:
        """
        Save tool configurations to YAML file.
        
        Args:
            tools (Dict[str, Dict]): Tool configurations to save
            
        Returns:
            bool: True if save successful
        """
        try:
            config = {'tools': tools}
            
            with open(self.config_path, 'w') as file:
                yaml.dump(config, file, default_flow_style=False, indent=2)
            
            self.logger.info(f"Saved {len(tools)} tools to configuration")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving configuration: {str(e)}")
            return False
    
    def add_tool(self, tool_name: str, tool_config: Dict) -> bool:
        """
        Add a new tool to the configuration.
        
        Args:
            tool_name (str): Name of the tool
            tool_config (Dict): Tool configuration
            
        Returns:
            bool: True if tool added successfully
        """
        try:
            tools = self.load_tools()
            tools[tool_name] = tool_config
            return self.save_tools(tools)
        except Exception as e:
            self.logger.error(f"Error adding tool {tool_name}: {str(e)}")
            return False
    
    def remove_tool(self, tool_name: str) -> bool:
        """
        Remove a tool from the configuration.
        
        Args:
            tool_name (str): Name of the tool to remove
            
        Returns:
            bool: True if tool removed successfully
        """
        try:
            tools = self.load_tools()
            if tool_name in tools:
                del tools[tool_name]
                return self.save_tools(tools)
            else:
                self.logger.warning(f"Tool {tool_name} not found in configuration")
                return False
        except Exception as e:
            self.logger.error(f"Error removing tool {tool_name}: {str(e)}")
            return False
    
    def update_tool(self, tool_name: str, tool_config: Dict) -> bool:
        """
        Update an existing tool configuration.
        
        Args:
            tool_name (str): Name of the tool
            tool_config (Dict): Updated tool configuration
            
        Returns:
            bool: True if tool updated successfully
        """
        try:
            tools = self.load_tools()
            if tool_name in tools:
                tools[tool_name].update(tool_config)
                return self.save_tools(tools)
            else:
                self.logger.warning(f"Tool {tool_name} not found in configuration")
                return False
        except Exception as e:
            self.logger.error(f"Error updating tool {tool_name}: {str(e)}")
            return False
    
    def validate_config(self) -> List[str]:
        """
        Validate the configuration file.
        
        Returns:
            List[str]: List of validation errors
        """
        errors = []
        
        try:
            tools = self.load_tools()
            
            for tool_name, tool_config in tools.items():
                # Check required fields
                if 'command' not in tool_config:
                    errors.append(f"Tool '{tool_name}' missing required 'command' field")
                
                if 'category' not in tool_config:
                    errors.append(f"Tool '{tool_name}' missing required 'category' field")
                
                # Check field types
                if 'args' in tool_config and not isinstance(tool_config['args'], list):
                    errors.append(f"Tool '{tool_name}' 'args' field must be a list")
                
                if 'dependencies' in tool_config and not isinstance(tool_config['dependencies'], list):
                    errors.append(f"Tool '{tool_name}' 'dependencies' field must be a list")
        
        except Exception as e:
            errors.append(f"Error validating configuration: {str(e)}")
        
        return errors
    
    def _ensure_config_exists(self):
        """Ensure configuration file exists, create default if not."""
        if not os.path.exists(self.config_path):
            self.logger.info(f"Configuration file not found, creating default: {self.config_path}")
            self._create_default_config()
    
    def _create_default_config(self):
        """Create a default configuration file."""
        default_config = {
            'tools': {
                'nmap': {
                    'command': 'nmap',
                    'category': 'scanning',
                    'description': 'Network discovery and security auditing',
                    'args': ['-sS', '-O'],
                    'version_cmd': 'nmap --version'
                },
                'nikto': {
                    'command': 'nikto',
                    'category': 'scanning',
                    'description': 'Web server scanner',
                    'args': ['-h'],
                    'version_cmd': 'nikto -Version'
                }
            }
        }
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        
        try:
            with open(self.config_path, 'w') as file:
                yaml.dump(default_config, file, default_flow_style=False, indent=2)
            self.logger.info("Default configuration created successfully")
        except Exception as e:
            self.logger.error(f"Error creating default configuration: {str(e)}")
