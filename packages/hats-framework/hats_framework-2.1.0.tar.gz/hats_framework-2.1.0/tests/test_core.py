"""
Unit tests for HATS core module.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the parent directory to the path so we can import hats
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from hats.core import HATSEngine


class TestHATSCore(unittest.TestCase):
    """Test cases for HATSEngine class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.engine = HATSEngine("configs/tools.yaml")
    
    @patch('hats.core.subprocess.run')
    def test_execute_tool_success(self, mock_subprocess):
        """Test successful tool execution."""
        # Mock subprocess result
        mock_result = Mock()
        mock_result.stdout = "Nmap scan completed"
        mock_result.stderr = ""
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result
        
        # Mock tool manager
        self.engine.tool_manager.get_tool = Mock(return_value={
            'command': 'nmap',
            'args': ['-sS']
        })
        
        result = self.engine.execute_tool('nmap', '192.168.1.1')
        
        self.assertTrue(result['success'])
        self.assertEqual(result['tool'], 'nmap')
        self.assertEqual(result['target'], '192.168.1.1')
        self.assertEqual(result['output'], "Nmap scan completed")
    
    @patch('hats.core.subprocess.run')
    def test_execute_tool_failure(self, mock_subprocess):
        """Test tool execution failure."""
        # Mock subprocess failure
        mock_subprocess.side_effect = Exception("Command failed")
        
        # Mock tool manager
        self.engine.tool_manager.get_tool = Mock(return_value={
            'command': 'nmap',
            'args': ['-sS']
        })
        
        result = self.engine.execute_tool('nmap', '192.168.1.1')
        
        self.assertFalse(result['success'])
        self.assertEqual(result['tool'], 'nmap')
        self.assertIn('Command failed', result['error'])
    
    def test_execute_tool_not_found(self):
        """Test execution of non-existent tool."""
        # Mock tool manager to return None
        self.engine.tool_manager.get_tool = Mock(return_value=None)
        
        result = self.engine.execute_tool('nonexistent', '192.168.1.1')
        
        self.assertFalse(result['success'])
        self.assertIn('not found', result['error'])
    
    def test_execute_workflow(self):
        """Test workflow execution."""
        workflow = [
            {'tool': 'nmap', 'target': '192.168.1.1'},
            {'tool': 'nikto', 'target': 'http://192.168.1.1'}
        ]
        
        # Mock execute_tool method
        self.engine.execute_tool = Mock(side_effect=[
            {'success': True, 'tool': 'nmap', 'target': '192.168.1.1'},
            {'success': True, 'tool': 'nikto', 'target': 'http://192.168.1.1'}
        ])
        
        results = self.engine.execute_workflow(workflow)
        
        self.assertEqual(len(results), 2)
        self.assertTrue(all(r['success'] for r in results))
    
    def test_execute_workflow_stop_on_error(self):
        """Test workflow execution with stop on error."""
        workflow = [
            {'tool': 'nmap', 'target': '192.168.1.1', 'stop_on_error': True},
            {'tool': 'nikto', 'target': 'http://192.168.1.1'}
        ]
        
        # Mock execute_tool method - first tool fails
        self.engine.execute_tool = Mock(side_effect=[
            {'success': False, 'tool': 'nmap', 'target': '192.168.1.1', 'error': 'Failed'},
            {'success': True, 'tool': 'nikto', 'target': 'http://192.168.1.1'}
        ])
        
        results = self.engine.execute_workflow(workflow)
        
        # Should only have one result (workflow stopped after first failure)
        self.assertEqual(len(results), 1)
        self.assertFalse(results[0]['success'])
    
    def test_build_command(self):
        """Test command building."""
        tool_config = {
            'command': 'nmap',
            'args': ['-sS', '-T4']
        }
        
        command = self.engine._build_command(tool_config, '192.168.1.1', {'p': '80,443'})
        
        expected = ['nmap', '-sS', '-T4', '192.168.1.1', '--p', '80,443']
        self.assertEqual(command, expected)
    
    def test_build_command_no_args(self):
        """Test command building without default args."""
        tool_config = {
            'command': 'nikto'
        }
        
        command = self.engine._build_command(tool_config, 'example.com', {})
        
        expected = ['nikto', 'example.com']
        self.assertEqual(command, expected)
    
    @patch('hats.core.subprocess.run')
    def test_run_command_timeout(self, mock_subprocess):
        """Test command execution with timeout."""
        # Mock timeout exception
        mock_subprocess.side_effect = Exception("Timeout")
        
        result = self.engine._run_command(['sleep', '10'])
        
        self.assertEqual(result['return_code'], -1)
        self.assertIn('Timeout', result['stderr'])
    
    def test_async_execution(self):
        """Test asynchronous tool execution."""
        # Mock execute_tool method
        self.engine.execute_tool = Mock(return_value={
            'success': True, 'tool': 'nmap', 'target': '192.168.1.1'
        })
        
        task_id = self.engine.execute_async('nmap', '192.168.1.1')
        
        self.assertIsNotNone(task_id)
        self.assertTrue(task_id.startswith('task_'))
        
        # Wait a bit for the task to complete
        import time
        time.sleep(0.1)
        
        result = self.engine.get_task_result(task_id)
        self.assertIsNotNone(result)


if __name__ == '__main__':
    unittest.main()
