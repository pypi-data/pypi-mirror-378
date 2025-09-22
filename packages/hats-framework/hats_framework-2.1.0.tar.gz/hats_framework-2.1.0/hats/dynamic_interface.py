"""
Dynamic tool interface for HATS framework.
Provides the simple function-like interface for tools.
"""
from datetime import datetime
import asyncio
from typing import Any, Dict, List, Union, Optional, Callable
from .core import HATSEngine, ToolResult
from .security import ArgumentSanitizer
from .utils.logger import get_logger


class DynamicToolInterface:
    """
    Creates dynamic tool functions that can be called like:
    hats.nmap("192.168.1.1", range(1, 1000), mode="aggressive")
    """
    
    def __init__(self, config_path: str = "configs/tools.yaml"):
        """Initialize the dynamic tool interface."""
        self.engine = HATSEngine(config_path)
        self.sanitizer = ArgumentSanitizer()
        self.logger = get_logger(__name__)
        self._create_tool_functions()
    
    def _create_tool_functions(self):
        """Create dynamic tool functions based on available tools."""
        available_tools = self.engine.tool_manager.list_available_tools()
        
        for tool_name in available_tools:
            # Create a dynamic function for each tool
            tool_function = self._create_tool_function(tool_name)
            setattr(self, tool_name, tool_function)
    
    def _create_tool_function(self, tool_name: str) -> Callable:
        """
        Create a dynamic function for a specific tool with smart argument mapping.
        """
        def tool_function(*args, mode: str = "sync", output_format: str = "dict", 
                         save_to: str = None, append_to: str = None, **kwargs):
            """
            Dynamic tool function with intelligent argument processing.
            Users can just pass values (IP, ports, timing, files, etc.) and the system will auto-detect and assign them.
            """
            try:
                # Smart argument mapping
                mapped_args = []
                mapped_kwargs = dict(kwargs)
                for arg in args:
                    arg_type = self.sanitizer.detect_argument_type(arg)
                    if arg_type == "ip" or arg_type == "domain" or arg_type == "url":
                        mapped_kwargs.setdefault("target", arg)
                    elif arg_type == "port" or arg_type == "port_range":
                        mapped_kwargs.setdefault("ports", arg)
                    elif arg_type == "filename":
                        mapped_kwargs.setdefault("file", arg)
                    elif arg_type == "flag":
                        mapped_args.append(arg)
                    elif arg_type == "string":
                        # Try to detect timing template (e.g., T4)
                        if arg.upper() in [f"T{i}" for i in range(6)]:
                            mapped_kwargs.setdefault("timing", arg.upper())
                        else:
                            mapped_args.append(arg)
                    else:
                        mapped_args.append(arg)
                # Remove duplicates (if user passed both positional and kwarg)
                for k in list(mapped_kwargs.keys()):
                    if k in ["target", "ports", "file"] and mapped_kwargs[k] in mapped_args:
                        mapped_args.remove(mapped_kwargs[k])
                # Compose final argument list
                final_args = []
                if "target" in mapped_kwargs:
                    final_args.append(mapped_kwargs.pop("target"))
                if "ports" in mapped_kwargs:
                    final_args.append(mapped_kwargs.pop("ports"))
                if "file" in mapped_kwargs:
                    final_args.append(mapped_kwargs.pop("file"))
                final_args.extend(mapped_args)
                # Execute the tool
                if mode == "async":
                    task_id = self.engine.execute_async(tool_name, *final_args, **mapped_kwargs)
                    return task_id
                else:
                    result = self.engine.execute_tool_sync(
                        tool_name, *final_args, 
                        output_format=output_format, 
                        **mapped_kwargs
                    )
                
                # Process the result based on output format
                if output_format == "dict":
                    processed_result = result.parsed_data or {}
                elif output_format == "raw":
                    processed_result = result.stdout
                elif output_format == "result":
                    processed_result = result
                else:
                    processed_result = result.parsed_data or {}
                
                # Handle file saving
                if save_to or append_to:
                    self._save_result(processed_result, save_to, append_to)
                
                return processed_result
                
            except Exception as e:
                self.logger.error(f"Error executing {tool_name}: {str(e)}")
                return {
                    'error': str(e),
                    'tool': tool_name,
                    'success': False
                }
        
        # Add metadata to the function
        tool_function.__name__ = tool_name
        tool_function.__doc__ = f"Execute {tool_name} with intelligent argument detection"
        
        return tool_function
    
    def _save_result(self, result: Any, save_to: str = None, append_to: str = None):
        """
        Save or append results to file.
        
        Args:
            result (Any): Result to save
            save_to (str): File to save to (overwrites)
            append_to (str): File to append to
        """
        import json
        from datetime import datetime
        
        if save_to:
            try:
                filename = self.sanitizer.sanitize_filename(save_to)
                with open(filename, 'w') as f:
                    if isinstance(result, (dict, list)):
                        json.dump(result, f, indent=2, default=str)
                    else:
                        f.write(str(result))
                self.logger.info(f"Results saved to {filename}")
            except Exception as e:
                self.logger.error(f"Error saving to {save_to}: {str(e)}")
        
        if append_to:
            try:
                filename = self.sanitizer.sanitize_filename(append_to)
                with open(filename, 'a') as f:
                    timestamp = datetime.now().isoformat()
                    f.write(f"\n\n=== {timestamp} ===\n")
                    if isinstance(result, (dict, list)):
                        json.dump(result, f, indent=2, default=str)
                    else:
                        f.write(str(result))
                self.logger.info(f"Results appended to {filename}")
            except Exception as e:
                self.logger.error(f"Error appending to {append_to}: {str(e)}")
    
    def report(self, *results, format: str = "html", output: str = "report", 
              template: str = "default") -> str:
        """
        Generate comprehensive report from multiple tool results.
        
        Args:
            *results: Tool results to include in report
            format (str): Report format (html/json/xml/csv/pdf)
            output (str): Output filename
            template (str): Report template
            
        Returns:
            str: Path to generated report
        """
        from .categories.reporting import ReportingCategory
        
        reporter = ReportingCategory()
        
        # Combine all results
        combined_results = {
            'scan_results': [],
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'tool_count': len(results),
                'format': format
            }
        }
        
        for i, result in enumerate(results):
            if isinstance(result, dict):
                combined_results['scan_results'].append({
                    'index': i,
                    'data': result
                })
        
        # Generate report based on format
        try:
            if format.lower() == "html":
                report_content = reporter.generate_html_report(combined_results, template)
                output_file = f"{output}.html"
            elif format.lower() == "json":
                report_content = reporter.generate_json_report(combined_results)
                output_file = f"{output}.json"
            elif format.lower() == "xml":
                report_content = reporter.generate_xml_report(combined_results)
                output_file = f"{output}.xml"
            elif format.lower() == "csv":
                report_content = reporter.generate_csv_report(combined_results)
                output_file = f"{output}.csv"
            else:
                raise ValueError(f"Unsupported report format: {format}")
            
            # Save report
            with open(output_file, 'w') as f:
                f.write(report_content)
            
            self.logger.info(f"Report generated: {output_file}")
            return output_file
            
        except Exception as e:
            self.logger.error(f"Error generating report: {str(e)}")
            return ""
    
    def get_task_result(self, task_id: str) -> Optional[Any]:
        """Get result of async task."""
        return self.engine.get_task_result(task_id)
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel running async task."""
        return self.engine.cancel_task(task_id)
    
    def list_tools(self, category: str = None) -> List[str]:
        """List available tools."""
        if category:
            tools = self.engine.tool_manager.get_tools_by_category(category)
            return [tool.get('command', '') for tool in tools]
        return self.engine.tool_manager.list_available_tools()
    
    def tool_info(self, tool_name: str) -> Optional[Dict]:
        """Get information about a specific tool."""
        return self.engine.tool_manager.get_tool_info(tool_name)


# Category-specific interfaces for organized access
class ReconTools(DynamicToolInterface):
    """Reconnaissance tools interface."""
    
    def __init__(self, config_path: str = "configs/tools.yaml"):
        super().__init__(config_path)
        self.category = "scanning"
    
    def __getattr__(self, name):
        """Only return tools in the recon category."""
        if hasattr(super(), name):
            tool_info = self.engine.tool_manager.get_tool(name)
            if tool_info and tool_info.get('category') == 'scanning':
                return getattr(super(), name)
        raise AttributeError(f"Recon tool '{name}' not found")


class ExploitTools(DynamicToolInterface):
    """Exploitation tools interface."""
    
    def __init__(self, config_path: str = "configs/tools.yaml"):
        super().__init__(config_path)
        self.category = "exploitation"
    
    def __getattr__(self, name):
        """Only return tools in the exploitation category."""
        if hasattr(super(), name):
            tool_info = self.engine.tool_manager.get_tool(name)
            if tool_info and tool_info.get('category') == 'exploitation':
                return getattr(super(), name)
        raise AttributeError(f"Exploitation tool '{name}' not found")


class PostExploitTools(DynamicToolInterface):
    """Post-exploitation tools interface."""
    
    def __init__(self, config_path: str = "configs/tools.yaml"):
        super().__init__(config_path)
        self.category = "post_exploit"
    
    def __getattr__(self, name):
        """Only return tools in the post-exploitation category."""
        if hasattr(super(), name):
            tool_info = self.engine.tool_manager.get_tool(name)
            if tool_info and tool_info.get('category') == 'post_exploit':
                return getattr(super(), name)
        raise AttributeError(f"Post-exploitation tool '{name}' not found")


# Main HATS interface
class HATS(DynamicToolInterface):
    """
    Main HATS interface providing the simple API:
    
    hats = HATS()
    nmap_result = hats.nmap("192.168.1.1", range(1, 1000), mode="aggressive")
    nikto_result = hats.nikto("http://example.com", mode="fast")
    hats.report(nmap_result, nikto_result, format="html", output="security_report")
    """
    
    def __init__(self, config_path: str = "configs/tools.yaml"):
        """Initialize HATS with all tools available."""
        super().__init__(config_path)
        
        # Create category-specific interfaces
        self.recon = ReconTools(config_path)
        self.exploit = ExploitTools(config_path)
        self.post_exploit = PostExploitTools(config_path)
        
        # Aliases for common tool categories
        self.scanning = self.recon
        self.exploitation = self.exploit
        self.initaccess = self.exploit  # Initial access
        self.execution = self.exploit
        self.escalation = self.post_exploit
        self.clear_tracks = self.post_exploit
    
    def workflow(self, steps: List[Dict]) -> List[Dict]:
        """
        Execute a workflow of tools.
        
        Args:
            steps (List[Dict]): Workflow steps
            
        Returns:
            List[Dict]: Results from each step
        """
        return self.engine.execute_workflow(steps)
    
    def batch_scan(self, targets: List[str], tools: List[str], **kwargs) -> Dict[str, Any]:
        """
        Perform batch scanning on multiple targets.
        
        Args:
            targets (List[str]): List of targets
            tools (List[str]): List of tools to run
            **kwargs: Additional options
            
        Returns:
            Dict[str, Any]: Batch scan results
        """
        results = {}
        
        for target in targets:
            target_results = {}
            
            for tool in tools:
                try:
                    tool_func = getattr(self, tool)
                    result = tool_func(target, **kwargs)
                    target_results[tool] = result
                except Exception as e:
                    self.logger.error(f"Error running {tool} on {target}: {str(e)}")
                    target_results[tool] = {'error': str(e)}
            
            results[target] = target_results
        
        return results
