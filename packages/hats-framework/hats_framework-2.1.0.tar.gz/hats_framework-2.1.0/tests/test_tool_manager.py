"""
Unit tests for HATS tool manager module.
"""

import unittest
from unittest.mock import Mock, patch, mock_open
import sys
import os

# Add the parent directory to the path so we can import hats
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from hats.tool_manager import ToolManager


class TestToolManager(unittest.TestCase):
    """Test cases for ToolManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock config loader
        with patch('hats.tool_manager.ConfigLoader') as mock_config:
            mock_config.return_value.load_tools.return_value = {
                'nmap': {
                    'command': 'nmap',
                    'category': 'scanning',
                    'description': 'Network scanner',
                    'args': ['-sS']
                },
                'nikto': {
                    'command': 'nikto',
                    'category': 'scanning',
                    'description': 'Web scanner',
                    'args': ['-h']
                }
            }
            self.tool_manager = ToolManager("test_config.yaml")
    
    def test_get_tool_exists(self):
        """Test getting an existing tool."""
        tool = self.tool_manager.get_tool('nmap')
        
        self.assertIsNotNone(tool)
        self.assertEqual(tool['command'], 'nmap')
        self.assertEqual(tool['category'], 'scanning')
    
    def test_get_tool_not_exists(self):
        """Test getting a non-existent tool."""
        tool = self.tool_manager.get_tool('nonexistent')
        
        self.assertIsNone(tool)
    
    def test_get_tools_by_category(self):
        """Test getting tools by category."""
        scanning_tools = self.tool_manager.get_tools_by_category('scanning')
        
        self.assertEqual(len(scanning_tools), 2)
        tool_names = [tool['command'] for tool in scanning_tools]
        self.assertIn('nmap', tool_names)
        self.assertIn('nikto', tool_names)
    
    def test_get_tools_by_nonexistent_category(self):
        """Test getting tools by non-existent category."""
        tools = self.tool_manager.get_tools_by_category('nonexistent')
        
        self.assertEqual(len(tools), 0)
    
    def test_list_available_tools(self):
        """Test listing all available tools."""
        tools = self.tool_manager.list_available_tools()
        
        self.assertEqual(len(tools), 2)
        self.assertIn('nmap', tools)
        self.assertIn('nikto', tools)
    
    def test_list_categories(self):
        """Test listing all categories."""
        categories = self.tool_manager.list_categories()
        
        self.assertEqual(len(categories), 1)
        self.assertIn('scanning', categories)
    
    @patch('hats.tool_manager.shutil.which')
    def test_is_tool_available_true(self, mock_which):
        """Test tool availability check when tool is available."""
        mock_which.return_value = '/usr/bin/nmap'
        
        available = self.tool_manager.is_tool_available('nmap')
        
        self.assertTrue(available)
        mock_which.assert_called_with('nmap')
    
    @patch('hats.tool_manager.shutil.which')
    def test_is_tool_available_false(self, mock_which):
        """Test tool availability check when tool is not available."""
        mock_which.return_value = None
        
        available = self.tool_manager.is_tool_available('nmap')
        
        self.assertFalse(available)
    
    def test_is_tool_available_not_configured(self):
        """Test tool availability check for non-configured tool."""
        available = self.tool_manager.is_tool_available('nonexistent')
        
        self.assertFalse(available)
    
    @patch('hats.tool_manager.shutil.which')
    def test_get_tool_info(self, mock_which):
        """Test getting tool information."""
        mock_which.return_value = '/usr/bin/nmap'
        
        with patch.object(self.tool_manager, '_get_tool_version', return_value='7.80'):
            info = self.tool_manager.get_tool_info('nmap')
        
        self.assertIsNotNone(info)
        self.assertEqual(info['name'], 'nmap')
        self.assertEqual(info['category'], 'scanning')
        self.assertTrue(info['available'])
        self.assertEqual(info['version'], '7.80')
    
    def test_get_tool_info_not_exists(self):
        """Test getting info for non-existent tool."""
        info = self.tool_manager.get_tool_info('nonexistent')
        
        self.assertIsNone(info)
    
    @patch('hats.tool_manager.subprocess.run')
    def test_get_tool_version_success(self, mock_subprocess):
        """Test getting tool version successfully."""
        mock_result = Mock()
        mock_result.stdout = "Nmap version 7.80"
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result
        
        # Create a tool config with version command
        tool_config = {'version_cmd': 'nmap --version'}
        version = self.tool_manager._get_tool_version(tool_config)
        
        self.assertEqual(version, "Nmap version 7.80")
    
    @patch('hats.tool_manager.subprocess.run')
    def test_get_tool_version_failure(self, mock_subprocess):
        """Test getting tool version with failure."""
        mock_subprocess.side_effect = Exception("Command failed")
        
        tool_config = {'version_cmd': 'nonexistent --version'}
        version = self.tool_manager._get_tool_version(tool_config)
        
        self.assertEqual(version, 'unknown')
    
    def test_get_tool_version_no_command(self):
        """Test getting tool version with no version command."""
        tool_config = {}
        version = self.tool_manager._get_tool_version(tool_config)
        
        self.assertEqual(version, 'unknown')
    
    def test_refresh_tools(self):
        """Test refreshing tool configurations."""
        # Mock config loader to return different tools
        with patch.object(self.tool_manager.config_loader, 'load_tools') as mock_load:
            mock_load.return_value = {
                'sqlmap': {
                    'command': 'sqlmap',
                    'category': 'exploitation'
                }
            }
            
            self.tool_manager.refresh_tools()
            
            # Check that tools were refreshed
            self.assertEqual(len(self.tool_manager.tools), 1)
            self.assertIn('sqlmap', self.tool_manager.tools)
            self.assertNotIn('nmap', self.tool_manager.tools)


if __name__ == '__main__':
    unittest.main()
